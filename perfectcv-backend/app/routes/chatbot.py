from flask import Blueprint, request, jsonify, current_app, session
from flask_login import login_required, current_user
import google.generativeai as genai
from app.utils.cv_utils import extract_text_from_pdf, allowed_file
from app.utils.ai_utils import (
    extract_personal_info, detect_missing_sections, improve_sentence,
    suggest_achievements, check_ats_compatibility, suggest_keywords_for_role,
    generate_improved_cv, analyze_cv_comprehensively
)
from werkzeug.utils import secure_filename
import gridfs
from bson import ObjectId
import os
import io
import re

# LangChain Imports for RAG (optional)
RAG_AVAILABLE = True
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_community.vectorstores import FAISS
except Exception as e:
    RAG_AVAILABLE = False
    print(f"Warning: RAG dependencies import failed: {e}")

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


def get_cv_analysis():
    """Get or create CV analysis stored in session."""
    analysis = session.get('cv_analysis')
    if not analysis:
        cv_text = get_cv_context()
        if cv_text:
            # Perform initial analysis
            analysis = analyze_cv_comprehensively(cv_text)
            if analysis:
                session['cv_analysis'] = analysis
    return analysis


def get_conversation_context():
    """Get conversation context for maintaining state."""
    return session.get('conversation_context', {})


def update_conversation_context(key, value):
    """Update conversation context."""
    context = get_conversation_context()
    context[key] = value
    session['conversation_context'] = context


def classify_query(question):
    """Classify the type of query to provide appropriate response."""
    question_lower = question.lower()
    
    # ATS Check queries
    if any(keyword in question_lower for keyword in ['ats', 'applicant tracking', 'ats friendly', 'ats score']):
        return 'ats_check'
    
    # Missing information queries
    if any(keyword in question_lower for keyword in ['missing', 'what\'s missing', 'what am i missing', 'gaps']):
        return 'missing_info'
    
    # Improvement/enhancement queries
    if any(keyword in question_lower for keyword in ['improve', 'enhance', 'better', 'rewrite', 'fix']):
        return 'improvement'
    
    # Keyword/skills queries
    if any(keyword in question_lower for keyword in ['keywords', 'skills to add', 'what skills', 'add skills']):
        return 'keywords'
    
    # Section-specific queries
    if any(keyword in question_lower for keyword in ['summary', 'experience', 'education', 'projects', 'achievements']):
        return 'section_specific'
    
    # Generate/download queries
    if any(keyword in question_lower for keyword in ['generate', 'create cv', 'updated cv', 'download', 'final version']):
        return 'generate'
    
    # Extraction queries (personal info, skills, etc.)
    if any(keyword in question_lower for keyword in ['extract', 'what are my', 'list my', 'show my']):
        return 'extraction'
    
    # General Q&A
    return 'general'


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

        # ---- Optional: Build FAISS Vector Store (skip if quota exceeded) ----
        vector_store_created = False
        if RAG_AVAILABLE:
            try:
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
                chunks = text_splitter.split_text(cv_text)

                embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                vectorstore = FAISS.from_texts(chunks, embeddings)
                os.makedirs("vectorstores", exist_ok=True)
                index_path = os.path.join("vectorstores", f"{current_user.get_id()}_cv_index")
                vectorstore.save_local(index_path)
                vector_store_created = True
                current_app.logger.info("Vector store created successfully")
            except Exception as e:
                current_app.logger.warning(f"Could not create vector store (quota may be exceeded): {e}")
                # Continue anyway - we can work without RAG

        return jsonify({
            "success": True,
            "message": "CV uploaded and processed successfully! You can now ask me questions about your CV.",
            "rag_enabled": vector_store_created
        })
    except Exception as e:
        current_app.logger.exception("Error processing CV upload")
        return jsonify({"success": False, "message": str(e)}), 500


@chatbot.route("/ask", methods=["POST"])
@login_required
def ask():
    """Answer CV-based question using intelligent query classification and context awareness"""
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    
    if not question:
        return jsonify({"success": False, "message": "No question provided"}), 400
        
    cv_text = get_cv_context()
    if not cv_text:
        return jsonify({"success": False, "message": "Please upload a CV first to enable Q&A"}), 400
    
    try:
        # Classify the query type
        query_type = classify_query(question)
        current_app.logger.info(f"Query classified as: {query_type}")
        
        answer = ""
        response_data = {"success": True, "hasCV": True}
        
        # Handle different query types
        if query_type == 'ats_check':
            # Check ATS compatibility
            job_desc = data.get('job_description', '')
            ats_result = check_ats_compatibility(cv_text, job_desc)
            
            if ats_result:
                answer = f"""**ATS Compatibility Analysis**

**Score:** {ats_result.get('ats_score', 'N/A')}/100

**Issues Found:**
{chr(10).join(['• ' + issue for issue in ats_result.get('issues', [])])}

**Keyword Analysis:**
- Found: {', '.join(ats_result.get('keyword_analysis', {}).get('found', [])[:10])}
- Missing: {', '.join(ats_result.get('keyword_analysis', {}).get('missing', [])[:10])}

**Formatting Suggestions:**
{chr(10).join(['• ' + suggestion for suggestion in ats_result.get('formatting_suggestions', [])])}

**Recommendation:** {ats_result.get('overall_recommendation', 'Continue improving your CV for better ATS compatibility.')}
"""
                response_data['ats_result'] = ats_result
            else:
                answer = "I couldn't perform a complete ATS analysis. Let me check basic compatibility..."
                # Fallback to basic analysis
                answer += "\n\nYour CV should include clear section headers, use standard fonts, and include relevant keywords for your target role."
        
        elif query_type == 'missing_info':
            # Detect missing sections and elements
            missing_analysis = detect_missing_sections(cv_text)
            
            if missing_analysis:
                answer = f"""**Missing Elements Analysis**

**Completeness Score:** {missing_analysis.get('completeness_score', 'N/A')}/100

**Missing Sections:**
{chr(10).join(['• ' + section for section in missing_analysis.get('missing_sections', [])])}

**Missing Professional Elements:**
{chr(10).join(['• ' + elem.get('issue', '') + ' - ' + elem.get('suggestion', '') for elem in missing_analysis.get('missing_professional_elements', [])])}

**Formatting Gaps:**
{chr(10).join(['• ' + gap for gap in missing_analysis.get('formatting_gaps', [])])}

Would you like me to help you add any of these missing elements?
"""
                response_data['missing_analysis'] = missing_analysis
            else:
                answer = "I couldn't detect specific missing elements. Your CV appears to have the basic sections, but consider adding a professional summary, quantifiable achievements, and relevant skills."
        
        elif query_type == 'improvement':
            # Handle improvement requests
            # Check if it's a specific section or sentence
            context = get_conversation_context()
            
            # Check for specific section mentions
            section_match = re.search(r'\b(summary|experience|education|skills|projects|achievements)\b', question, re.I)
            
            if section_match:
                section = section_match.group(1).lower()
                update_conversation_context('last_section', section)
                
                # Generate improved version of that section
                improved = generate_improved_cv(cv_text, focus_areas=[section])
                if improved:
                    # Extract the specific section from improved CV
                    answer = f"""**Improved {section.title()} Section:**

{improved}

Would you like me to apply these improvements or make any adjustments?
"""
                    response_data['improved_text'] = improved
                else:
                    answer = f"Let me help improve your {section} section. Can you share the current content?"
            else:
                # General improvement
                improved = generate_improved_cv(cv_text)
                if improved:
                    answer = f"""**Improved CV:**

{improved[:1000]}...

I've rewritten your CV to be more professional and ATS-friendly. Would you like to see the full version or make specific adjustments?
"""
                    response_data['improved_text'] = improved
                else:
                    answer = "I can help improve your CV! Which section would you like me to focus on? (summary, experience, skills, etc.)"
        
        elif query_type == 'keywords':
            # Suggest keywords for a specific role
            role_match = re.search(r'(?:for|as a?|in)\s+([a-z\s]+?)(?:\s+role|\s+position|job|\?|$)', question, re.I)
            role = role_match.group(1).strip() if role_match else data.get('target_role', 'software engineer')
            
            keyword_suggestions = suggest_keywords_for_role(role, cv_text)
            
            if keyword_suggestions:
                answer = f"""**Keywords for {role.title()} Role**

**Priority Additions:**
{chr(10).join(['• ' + kw for kw in keyword_suggestions.get('priority_additions', [])])}

**Suggested Keywords:**
{chr(10).join(['• ' + kw for kw in keyword_suggestions.get('suggested_keywords', [])[:15]])}

**Already Present:**
{chr(10).join(['• ' + kw for kw in keyword_suggestions.get('existing_keywords', [])[:10]])}

Would you like me to help integrate these keywords into your CV?
"""
                response_data['keywords'] = keyword_suggestions
            else:
                answer = f"For a {role} position, consider adding technical skills, tools, and industry-specific terms relevant to the field."
        
        elif query_type == 'section_specific':
            # Handle section-specific queries using RAG or fallback to direct analysis
            try:
                if RAG_AVAILABLE:
                    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                    index_path = os.path.join("vectorstores", f"{current_user.get_id()}_cv_index")
                    
                    if os.path.isdir(index_path):
                        vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
                        results = vectorstore.similarity_search(question, k=3)
                        context = "\n\n".join([r.page_content for r in results])
                    else:
                        # Fallback: use full CV text
                        context = cv_text[:2000]  # Use first 2000 chars
                else:
                    # Fallback: use full CV text
                    context = cv_text[:2000]
                
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                prompt = f"""You are a CV enhancement assistant.
                Answer the user's question using the CV context below.
                Provide specific, actionable advice.

                CV Context:
                {context}

                Question: {question}
                
                Provide a helpful answer with specific examples and suggestions.
                """
                
                response = model.generate_content(prompt)
                answer = _extract_genai_text(response).strip()
            except Exception as e:
                current_app.logger.warning(f"RAG query failed, using direct analysis: {e}")
                # Fallback to direct Gemini analysis
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"""You are a CV enhancement assistant.
                Answer this question about the CV: {question}
                
                CV Content (first 2000 chars):
                {cv_text[:2000]}
                """
                response = model.generate_content(prompt)
                answer = _extract_genai_text(response).strip()
        
        elif query_type == 'extraction':
            # Extract specific information
            if 'personal' in question.lower() or 'contact' in question.lower():
                personal_info = extract_personal_info(cv_text)
                if personal_info:
                    answer = f"""**Personal Information:**

• Name: {personal_info.get('name', 'Not found')}
• Email: {personal_info.get('email', 'Not found')}
• Phone: {personal_info.get('phone', 'Not found')}
• Location: {personal_info.get('location', 'Not found')}
• LinkedIn: {personal_info.get('linkedin', 'Not found')}
• GitHub: {personal_info.get('github', 'Not found')}
"""
                    response_data['personal_info'] = personal_info
                else:
                    answer = "I couldn't extract complete personal information. Please ensure your CV includes name, email, phone, and location."
            
            elif 'skill' in question.lower():
                # Extract skills from CV analysis
                analysis = get_cv_analysis()
                if analysis and 'skills' in str(analysis):
                    answer = "**Skills Found in Your CV:**\n\n"
                    answer += "I've identified your skills. Would you like me to suggest additional relevant skills to add?"
                else:
                    answer = "Let me analyze your skills section. Consider organizing skills by category (Technical, Soft Skills, Tools, etc.)"
            
            else:
                # General extraction - use RAG
                answer = "I can help extract information from your CV. What specifically would you like to know?"
        
        elif query_type == 'generate':
            # Generate final/updated CV
            improved = generate_improved_cv(cv_text)
            
            if improved:
                answer = """**Your Updated CV is Ready!**

I've generated an improved version of your CV with:
• Enhanced formatting for ATS compatibility
• Stronger action verbs and quantifiable achievements
• Better section organization
• Relevant keywords

You can download the updated version. Would you like me to make any specific adjustments?
"""
                response_data['generated_cv'] = improved
                # Store for potential download
                session['generated_cv'] = improved
            else:
                answer = "I'm preparing your updated CV. This includes improvements to formatting, content, and ATS optimization."
        
        else:
            # General Q&A - try RAG first, fallback to direct analysis
            try:
                if RAG_AVAILABLE:
                    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
                    index_path = os.path.join("vectorstores", f"{current_user.get_id()}_cv_index")
                    
                    if os.path.isdir(index_path):
                        vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
                        results = vectorstore.similarity_search(question, k=3)
                        context = "\n\n".join([r.page_content for r in results])
                    else:
                        # Fallback: use full CV text
                        context = cv_text[:2000]
                else:
                    # Fallback: use full CV text
                    context = cv_text[:2000]
                
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Check conversation context for continuity
                conv_context = get_conversation_context()
                context_note = ""
                if conv_context.get('last_section'):
                    context_note = f"\nNote: We were previously discussing the {conv_context['last_section']} section."
                
                prompt = f"""You are a helpful CV assistant.
                Answer the user's question using the CV context below.
                If the information is not available, say so.{context_note}

                CV Context:
                {context}

                Question: {question}
                """
                
                response = model.generate_content(prompt)
                answer = _extract_genai_text(response).strip()
            except Exception as e:
                current_app.logger.warning(f"RAG/embeddings failed, using direct analysis: {e}")
                # Fallback to direct Gemini analysis without embeddings
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                conv_context = get_conversation_context()
                context_note = ""
                if conv_context.get('last_section'):
                    context_note = f"\nNote: We were previously discussing the {conv_context['last_section']} section."
                
                prompt = f"""You are a helpful CV assistant.
                Answer the user's question based on this CV content.
                If the information is not available, say so.{context_note}

                CV Content (first 2000 chars):
                {cv_text[:2000]}

                Question: {question}
                """
                
                response = model.generate_content(prompt)
                answer = _extract_genai_text(response).strip()
        
        # Update chat history
        update_chat_history(question, answer)
        
        response_data['answer'] = answer
        response_data['query_type'] = query_type
        
        return jsonify(response_data)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        current_app.logger.error(f"Error during CV Q&A: {str(e)}\n{error_details}")
        print(f"ERROR in /ask endpoint: {str(e)}\n{error_details}")
        return jsonify({"success": False, "message": str(e), "error_type": type(e).__name__}), 500


@chatbot.route("/download-cv", methods=["GET"])
@login_required
def download_generated_cv():
    """Download the generated/improved CV"""
    try:
        generated_cv = session.get('generated_cv')
        
        if not generated_cv:
            return jsonify({"success": False, "message": "No generated CV available. Please generate one first."}), 404
        
        # Import here to avoid circular imports
        from app.utils.cv_utils import generate_pdf
        
        # Generate PDF from the improved text
        pdf_bytes = generate_pdf(generated_cv)
        
        from flask import send_file
        return send_file(
            pdf_bytes,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'improved_cv_{current_user.get_id()}.pdf'
        )
        
    except Exception as e:
        current_app.logger.exception("Error downloading generated CV")
        return jsonify({"success": False, "message": str(e)}), 500


@chatbot.route("/analysis", methods=["GET"])
@login_required
def get_analysis():
    """Get comprehensive CV analysis"""
    try:
        cv_text = get_cv_context()
        if not cv_text:
            return jsonify({"success": False, "message": "Please upload a CV first"}), 400
        
        # Get or create analysis
        analysis = get_cv_analysis()
        
        if not analysis:
            return jsonify({"success": False, "message": "Unable to analyze CV at this time"}), 500
        
        return jsonify({"success": True, "analysis": analysis})
        
    except Exception as e:
        current_app.logger.exception("Error getting CV analysis")
        return jsonify({"success": False, "message": str(e)}), 500
