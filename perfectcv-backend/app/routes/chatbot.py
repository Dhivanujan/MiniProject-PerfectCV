from flask import Blueprint, request, jsonify, current_app, session
from flask_login import login_required, current_user
import google.generativeai as genai
from app.utils.cv_utils import extract_text_from_pdf, allowed_file
from werkzeug.utils import secure_filename
import gridfs
from bson import ObjectId
import os
import io

# LangChain Imports for RAG (optional)
RAG_AVAILABLE = True
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import GoogleGenerativeAIEmbeddings
    from langchain_community.vectorstores import FAISS
except Exception:
    RAG_AVAILABLE = False

from typing import Any

chatbot = Blueprint("chatbot", __name__)

# ---------- HELPER FUNCTIONS ----------

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


def _extract_genai_text(resp: Any) -> str:
    """Try to extract text content from various genai response shapes."""
    try:
        # genai SDK response object sometimes exposes text or candidates
        if hasattr(resp, "text") and isinstance(resp.text, str):
            return resp.text
        # some responses expose 'candidates' or 'outputs'
        if isinstance(resp, dict):
            # common keys
            for key in ("text", "output", "content", "candidates", "outputs"):
                if key in resp and resp[key]:
                    v = resp[key]
                    if isinstance(v, list) and len(v) > 0:
                        first = v[0]
                        # nested structure
                        if isinstance(first, dict):
                            for subk in ("text", "output", "content"):
                                if subk in first and isinstance(first[subk], str):
                                    return first[subk]
                        elif isinstance(first, str):
                            return first
                    elif isinstance(v, str):
                        return v
        # fallback to string representation
        return str(resp)
    except Exception:
        current_app.logger.exception("Failed to parse genai response")
        return str(resp)

def get_chat_history():
    return session.get('chat_history', [])

def update_chat_history(user_msg, bot_msg):
    history = get_chat_history()
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": bot_msg})
    session['chat_history'] = history[-10:]

# ---------- ROUTES ----------

@chatbot.route("/upload", methods=["POST"])
@login_required
def upload_cv():
    """Upload and process CV + Create FAISS vector index"""
    if 'files' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400
    
    file = request.files['files']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400
        
    if not file or not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Invalid file type"}), 400
        
    try:
        # Extract CV text
        if file.filename.lower().endswith('.pdf'):
            cv_text = extract_text_from_pdf(file)
        else:
            cv_text = file.read().decode('utf-8')

        # Store in GridFS
        fs = gridfs.GridFS(current_app.mongo.db)
        filename = secure_filename(f"chat_{current_user.get_id()}_{file.filename}")
        file_id = fs.put(cv_text.encode('utf-8'), filename=filename, content_type='text/plain', user_id=str(current_user.get_id()))

        # Save in session
        session['cv_file_id'] = str(file_id)
        session['cv_text'] = cv_text
        session['chat_history'] = []

        # ---- NEW: Build FAISS Vector Store ----
        if not RAG_AVAILABLE:
            current_app.logger.warning("RAG dependencies not available; skipping vector index build.")
            return jsonify({
                "success": False,
                "message": "RAG support (langchain/faiss) is not installed on the server. Install optional dependencies to enable CV&A." 
            }), 501

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = text_splitter.split_text(cv_text)

        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vectorstore = FAISS.from_texts(chunks, embeddings)
        os.makedirs("vectorstores", exist_ok=True)
        index_path = os.path.join("vectorstores", f"{current_user.get_id()}_cv_index")
        # Save local index
        try:
            vectorstore.save_local(index_path)
        except Exception:
            current_app.logger.exception("Failed to save FAISS vectorstore locally")
            # attempt to remove any incomplete files and raise
            raise

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
    """Answer CV-based question using RAG + Gemini"""
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    
    if not question:
        return jsonify({"success": False, "message": "No question provided"}), 400
        
    cv_text = get_cv_context()
    if not cv_text:
        return jsonify({"success": False, "message": "Please upload a CV first to enable Q&A"}), 400
    
    try:
        # Ensure RAG deps are available
        if not RAG_AVAILABLE:
            return jsonify({"success": False, "message": "RAG support (langchain/faiss) is not installed on the server."}), 501

        # Load vectorstore for this user
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        index_path = os.path.join("vectorstores", f"{current_user.get_id()}_cv_index")
        if not os.path.isdir(index_path):
            return jsonify({"success": False, "message": "No vector index found for this user. Please upload your CV again."}), 400

        vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

        # Retrieve top 3 relevant CV chunks
        results = vectorstore.similarity_search(question, k=3)
        context = "\n\n".join([r.page_content for r in results])

        # Initialize Gemini
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Prompt
        prompt = f"""
        You are a helpful CV assistant.
        Answer the user's question strictly using the information in the CV context below.
        If the information is not available, say "Information not available in the CV."

        CV Context:
        {context}

        Question:
        {question}
        """

        response = model.generate_content(prompt)
        answer = _extract_genai_text(response).strip()

        update_chat_history(question, answer)
        return jsonify({"success": True, "answer": answer, "hasCV": True})

    except Exception as e:
        current_app.logger.exception("Error during CV Q&A")
        return jsonify({"success": False, "message": str(e)}), 500
