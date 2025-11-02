from flask import Blueprint, request, jsonify, current_app, session
from flask_login import login_required, current_user
import google.generativeai as genai
from app.utils.ai_utils import setup_gemini, get_valid_model
from app.utils.cv_utils import extract_text_from_pdf, allowed_file
from werkzeug.utils import secure_filename
import gridfs
from bson import ObjectId
import io
import json

chatbot = Blueprint("chatbot", __name__)

def get_cv_context():
    """Get the CV text stored in user's session or GridFS."""
    cv_text = session.get('cv_text')
    if not cv_text and session.get('cv_file_id'):
        try:
            fs = gridfs.GridFS(current_app.mongo.db)
            file_obj = fs.get(ObjectId(session['cv_file_id']))
            cv_text = file_obj.read().decode('utf-8')
            session['cv_text'] = cv_text
        except Exception:
            current_app.logger.exception("Failed to retrieve CV text")
    return cv_text

def get_chat_history():
    """Get chat history from session."""
    return session.get('chat_history', [])

def update_chat_history(user_msg, bot_msg):
    """Update chat history in session."""
    history = get_chat_history()
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": bot_msg})
    session['chat_history'] = history[-10:]  # Keep last 10 messages


def simple_cv_answer(cv_text: str, question: str) -> str:
    """Provide a simple rule-based answer based on keyword matching in the CV text.

    This is used as a fallback when the AI model is not available or fails.
    """
    if not cv_text:
        return "I don't have the CV content to answer that. Please upload your CV first."

    q = question.lower()
    # quick checks for common fields
    import re

    # name
    if any(word in q for word in ("name", "who", "candidate")):
        # try to find a name as the first non-empty line
        first_lines = [ln.strip() for ln in cv_text.splitlines() if ln.strip()]
        if first_lines:
            return f"The CV appears to belong to: {first_lines[0]}"

    # email
    m = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", cv_text)
    if m and any(k in q for k in ("email", "contact", "mail")):
        return f"Email on the CV: {m.group(0)}"

    # phone
    p = re.search(r"\+?\d[\d \-()]{7,}\d", cv_text)
    if p and any(k in q for k in ("phone", "mobile", "contact", "call")):
        return f"Phone number on the CV: {p.group(0)}"

    # keyword-based sentence search
    # split into sentences/lines and score by keyword matches
    tokens = re.findall(r"\w+", q)
    if not tokens:
        return "I couldn't understand the question. Please ask more simply."

    sentences = [s.strip() for s in re.split(r"[\.\n]", cv_text) if s.strip()]
    scored = []
    for s in sentences:
        s_low = s.lower()
        score = sum(1 for t in tokens if t in s_low)
        if score > 0:
            scored.append((score, s))
    if scored:
        scored.sort(key=lambda x: x[0], reverse=True)
        top = [s for _, s in scored[:3]]
        return " \n\n".join(top)

    return "I couldn't find information related to your question in the CV."

@chatbot.route("/upload", methods=["POST"])
@login_required
def upload_cv():
    if 'files' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400
    
    file = request.files['files']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
        
    if not file or not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Invalid file type"}), 400
        
    try:
        # Read and store CV content
        if file.filename.lower().endswith('.pdf'):
            cv_text = extract_text_from_pdf(file)
        else:
            cv_text = file.read().decode('utf-8')
            
        # Store in GridFS
        fs = gridfs.GridFS(current_app.mongo.db)
        filename = secure_filename(f"chat_{current_user.get_id()}_{file.filename}")
        file_id = fs.put(
            cv_text.encode('utf-8'),
            filename=filename,
            content_type='text/plain',
            user_id=str(current_user.get_id()),
        )

        # Store in session (use string because ObjectId is not JSON serializable)
        session['cv_file_id'] = str(file_id)
        session['cv_text'] = cv_text
        session['chat_history'] = []  # Reset chat history for new CV
        
        return jsonify({
            "success": True,
            "message": "CV uploaded and processed successfully! You can now ask me questions about your CV."
        })
    except Exception as e:
        current_app.logger.exception("Error processing CV upload")
        return jsonify({"success": False, "message": str(e)}), 500

@chatbot.route("/ask", methods=["POST"])
@login_required
def ask():
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    
    if not question:
        return jsonify({"success": False, "message": "No question provided"}), 400
        
    cv_text = get_cv_context()
    if not cv_text:
        return jsonify({"success": False, 
                       "message": "Please upload a CV first to enable Q&A"}), 400
    
    # Try to use AI model; if unavailable or it fails, fall back to rule-based answer
    configured = setup_gemini()
    model_name = get_valid_model() if configured else None

    prompt = f"""You are an AI assistant analyzing a CV/resume. You have access to the CV content and will answer questions about it.

CV Content:
{cv_text}

Question: {question}

Provide a helpful, accurate response based only on the information in the CV. If asked about information not present in the CV, politely indicate that it's not mentioned. Keep responses concise but informative."""

    answer = None
    if model_name:
        try:
            model = genai.GenerativeModel(model_name)
            # use list form per other usages in the codebase
            response = model.generate_content([prompt])
            answer = getattr(response, "text", None) or str(response)
        except Exception:
            current_app.logger.exception("AI model failed; falling back to rule-based answer")

    # Fallback when AI not configured or failed
    if not answer:
        try:
            answer = simple_cv_answer(cv_text, question)
        except Exception:
            current_app.logger.exception("Fallback answer generation failed")
            return jsonify({"success": False, "error": "Failed to produce an answer."}), 500

    # Update chat history and respond
    try:
        update_chat_history(question, answer)
    except Exception:
        current_app.logger.exception("Failed to update chat history, continuing")

    return jsonify({
        "success": True,
        "answer": answer,
        "hasCV": bool(cv_text)
    })