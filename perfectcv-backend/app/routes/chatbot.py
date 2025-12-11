# app/blueprints/chatbot.py
import os
import io
import re
import json
from functools import wraps
from typing import Any, Dict, Optional

from dotenv import load_dotenv
load_dotenv()  # ensure environment variables are loaded

from flask import Blueprint, request, jsonify, current_app, session, send_file
import logging

logger = logging.getLogger(__name__)
from flask_login import login_required, current_user

# External AI SDK (Google Generative AI)
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

# Groq AI SDK
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq library not available")

# GridFS for storing CV text/files
import gridfs
from bson import ObjectId

# utils (assumed present in your project)
from app.utils.cv_utils import extract_text_from_pdf, allowed_file, extract_text_from_any
from app.utils.ai_utils import (
    extract_personal_info, detect_missing_sections, improve_sentence,
    suggest_achievements, check_ats_compatibility, suggest_keywords_for_role,
    generate_improved_cv, analyze_cv, get_generative_model,
    suggest_courses, suggest_qualifications,
    DEFAULT_GENERATION_MODELS
)

# Optional RAG dependencies - keep them guarded
RAG_AVAILABLE = False
try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_community.vectorstores import FAISS
    RAG_AVAILABLE = True
except Exception as e:
    RAG_AVAILABLE = False
    # Avoid accessing current_app at import time; use module logger instead
    logger.warning("RAG deps not available: %s", e)

chatbot = Blueprint("chatbot", __name__)

# --------- Constants ----------
CHAT_HISTORY_LIMIT = 10    # store last 10 messages
CONTEXT_CHARS = 50000      # Increased context limit for Gemini 1.5 Flash
EMBEDDING_MODEL = "models/embedding-001"  # change if needed
def _unique_model_candidates():
    seen = set()
    for name in [os.getenv("GENAI_MODEL_OVERRIDE"), *DEFAULT_GENERATION_MODELS]:
        if name and name not in seen:
            seen.add(name)
            yield name


def get_embeddings_instance():
    """Return an embeddings object compatible with LangChain FAISS operations if available.
    Tries GoogleGenerativeAIEmbeddings (if API key present) then HuggingFaceEmbeddings.
    Returns None if no embedding provider is available.
    """
    # Try Google generative embeddings if API key present
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("API_KEY")
    if api_key:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        except Exception as e:
            logger.debug("GoogleGenerativeAIEmbeddings not available: %s", e)

    # Try HuggingFace / sentence-transformers via LangChain
    try:
        from langchain.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    except Exception as e:
        logger.debug("HuggingFaceEmbeddings not available: %s", e)

    logger.info("No embeddings provider available (install langchain-google-genai or sentence-transformers for embeddings)")
    return None


def load_or_build_vectorstore_for_user(user_id: str, cv_text: str):
    """Load existing FAISS index for user or build it from cv_text. Returns vectorstore or None."""
    try:
        embeddings = get_embeddings_instance()
        if not embeddings or FAISS is None or RecursiveCharacterTextSplitter is None:
            logger.info("Vectorstore unavailable: missing embeddings provider or FAISS/text-splitter")
            return None

        index_path = os.path.join("vectorstores", f"{user_id}_cv_index")
        # If index exists, load it
        if os.path.isdir(index_path):
            try:
                return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            except Exception:
                logger.exception("Failed to load existing vectorstore; rebuilding")

        # Build new index
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_text(cv_text)
        if not chunks:
            return None
        vectorstore = FAISS.from_texts(chunks, embeddings)
        os.makedirs(index_path, exist_ok=True)
        try:
            vectorstore.save_local(index_path)
        except Exception:
            logger.exception("Failed to save FAISS index locally")
        return vectorstore
    except Exception:
        logger.exception("Error building or loading vectorstore")
        return None

# --------- Helpers ----------

def gridfs_instance():
    """Return GridFS instance for current app's mongo DB."""
    try:
        return gridfs.GridFS(current_app.mongo.db)
    except Exception:
        current_app.logger.exception("Failed to create GridFS instance")
        raise

def require_cv(func):
    """Decorator to ensure a CV has been uploaded (GridFS id in session)."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("cv_file_id"):
            return jsonify({"success": False, "message": "Please upload a CV first"}), 400
        return func(*args, **kwargs)
    return wrapper

def fetch_cv_text_from_gridfs() -> Optional[str]:
    """Get CV text from GridFS using file id in session. Returns None if not available."""
    file_id = session.get("cv_file_id")
    if not file_id:
        return None
    try:
        fs = gridfs_instance()
        file_obj = fs.get(ObjectId(file_id))
        # stored as text/plain bytes
        raw = file_obj.read()
        if isinstance(raw, bytes):
            try:
                return raw.decode("utf-8", errors="ignore")
            except Exception:
                return raw.decode("latin-1", errors="ignore")
        return str(raw)
    except Exception:
        current_app.logger.exception("Failed to fetch CV from GridFS")
        return None

def get_cached_analysis_data() -> Optional[Dict]:
    """Get cached analysis from GridFS if available."""
    analysis_file_id = session.get('cv_analysis_file_id')
    if analysis_file_id:
        try:
            fs = gridfs_instance()
            f = fs.get(ObjectId(analysis_file_id))
            raw = f.read()
            return json.loads(raw.decode('utf-8'))
        except Exception:
            current_app.logger.warning("Failed to load cached analysis")
    return None

def cache_analysis_data(analysis: Dict):
    """Cache analysis data to GridFS."""
    try:
        fs = gridfs_instance()
        fid = fs.put(json.dumps(analysis).encode('utf-8'), filename=f"analysis_{current_user.get_id()}.json", content_type='application/json', user_id=str(current_user.get_id()))
        session['cv_analysis_file_id'] = str(fid)
    except Exception:
        current_app.logger.exception("Failed to cache analysis")

def _extract_genai_text(resp: Any) -> str:
    """Safely extract text from Google Generative AI responses (robust to shape changes)."""
    try:
        # SDK object-like responses
        if hasattr(resp, "candidates") and getattr(resp, "candidates"):
            cand = resp.candidates[0]
            # cand.content might be nested parts
            if hasattr(cand, "content"):
                content = cand.content
                # Some SDKs put parts array
                if hasattr(content, "parts") and content.parts:
                    part0 = content.parts[0]
                    # part0 may have text attr
                    if hasattr(part0, "text"):
                        return part0.text
                    # part0 may be string
                    if isinstance(part0, str):
                        return part0
                # or content may have text directly
                if hasattr(content, "text"):
                    return content.text
        # dict-shaped responses
        if isinstance(resp, dict):
            # try common keys
            for key in ("text", "output", "content"):
                v = resp.get(key)
                if isinstance(v, str) and v.strip():
                    return v.strip()
                if isinstance(v, list) and v:
                    first = v[0]
                    if isinstance(first, dict):
                        for subk in ("text", "content", "output"):
                            if subk in first and isinstance(first[subk], str):
                                return first[subk].strip()
                    elif isinstance(first, str):
                        return first.strip()
            # special 'candidates' structure
            cand = resp.get("candidates")
            if cand and isinstance(cand, list):
                first = cand[0]
                if isinstance(first, dict):
                    for subk in ("content", "text", "output"):
                        if subk in first and isinstance(first[subk], str):
                            return first[subk].strip()
        # last fallback
        return str(resp)
    except Exception:
        current_app.logger.exception("Failed to parse genai response")
        return str(resp)

def get_chat_history():
    return session.get("chat_history", [])

def update_chat_history(user_msg: str, bot_msg: str):
    history = get_chat_history()
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": bot_msg})
    # store only last N messages
    session['chat_history'] = history[-(CHAT_HISTORY_LIMIT*2):]

def safe_generate_with_groq(prompt: str) -> Optional[str]:
    """Call Groq API safely and return text. Returns None if unavailable or fails."""
    if not GROQ_AVAILABLE:
        logger.debug("Groq library not available")
        return None
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.debug("GROQ_API_KEY not set in environment")
        return None
    
    try:
        client = Groq(api_key=groq_api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",  # Updated to current supported model
            temperature=0.7,
            max_tokens=2048,
        )
        response_text = chat_completion.choices[0].message.content.strip()
        logger.info("Groq API call successful")
        return response_text
    except Exception as e:
        logger.error(f"Groq API call failed: {type(e).__name__}: {str(e)}")
        return None


def safe_generate_with_gemini(prompt: str) -> str:
    """Call Gemini safely and return text; raises on missing API key."""
    # Try Groq first if available
    logger.info("Attempting to generate response with AI...")
    groq_response = safe_generate_with_groq(prompt)
    if groq_response:
        logger.info("Using Groq response")
        return groq_response
    
    # Fallback to Gemini
    logger.info("Groq unavailable, falling back to Gemini")
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY/API_KEY not set in environment")
        raise RuntimeError("Server is missing GOOGLE_API_KEY")

    genai.configure(api_key=api_key)
    last_error: Optional[Exception] = None

    for model_name in _unique_model_candidates():
        try:
            logger.info(f"Trying Gemini model: {model_name}")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            text = _extract_genai_text(response).strip()
            if text:
                logger.info(f"Gemini model {model_name} succeeded")
                return text
        except google_exceptions.ResourceExhausted as exc:
            logger.warning("Gemini quota exceeded for %s: %s", model_name, exc)
            raise
        except google_exceptions.NotFound as exc:
            logger.warning("Gemini model %s not available: %s", model_name, exc)
            last_error = exc
        except Exception as exc:
            logger.warning("Gemini model %s failed: %s", model_name, exc)
            last_error = exc

    # Final fallback using ai_utils helper (may discover newly added models)
    logger.info("Trying final fallback model from ai_utils")
    fallback_model = get_generative_model([])
    if fallback_model:
        response = fallback_model.generate_content(prompt)
        text = _extract_genai_text(response).strip()
        logger.info("Fallback model succeeded")
        return text

    if last_error:
        logger.error(f"All models failed, raising last error: {last_error}")
        raise last_error
    logger.error("No Gemini models available to handle the request")
    raise RuntimeError("No Gemini models available to handle the request")

# Improved classifier using word boundaries
def classify_query(question: str) -> str:
    q = question.lower()
    # tokenized words plus some phrase checks
    words = re.findall(r"\w+", q)

    if any(k in q for k in ['ats', 'applicant tracking', 'ats friendly', 'ats score']):
        return 'ats_check'
    if any(word in words for word in ['missing', 'gaps', 'lack']) or "what am i missing" in q or "what's missing" in q:
        return 'missing_info'
    if any(word in words for word in ['improve', 'enhance', 'better', 'rewrite', 'fix', 'update', 'upgrade', 'improved']):
        return 'improvement'
    if any(word in words for word in ['keywords', 'skills', 'skill', 'keyword']):
        return 'keywords'
    if any(word in words for word in ['summary', 'experience', 'education', 'projects', 'achievements', 'skills']):
        return 'section_specific'
    if any(k in q for k in ['generate', 'create cv', 'updated cv', 'download', 'final version', 'export', 'save']):
        return 'generate'
    if any(word in words for word in ['extract', 'list', 'show', 'what are my', 'what is my']):
        return 'extraction'
    if any(word in words for word in ['course', 'courses', 'certification', 'certifications', 'certificate', 'learning', 'study', 'training', 'learn']):
        return 'courses'
    if any(word in words for word in ['qualification', 'qualifications', 'degree', 'education', 'master', 'bachelor', 'phd']):
        return 'qualifications'
    return 'general'

# --------- Route handlers (small modular functions) ----------

def handle_ats_check(cv_text: str, payload: Dict) -> Dict:
    job_desc = payload.get('job_description', '')
    try:
        ats_result = check_ats_compatibility(cv_text, job_desc)
    except Exception:
        current_app.logger.exception("ATS check failed")
        ats_result = None

    if ats_result:
        issues = ats_result.get('issues', [])
        keyword_found = ats_result.get('keyword_analysis', {}).get('found', [])
        keyword_missing = ats_result.get('keyword_analysis', {}).get('missing', [])
        formatting = ats_result.get('formatting_suggestions', []) or []
        return {
            "answer": (
                f"**ATS Compatibility Analysis**\n\n"
                f"Score: {ats_result.get('ats_score', 'N/A')}/100\n\n"
                f"Issues:\n" + "\n".join(f"• {i}" for i in issues) + "\n\n"
                f"Keywords Found: {', '.join(keyword_found[:10])}\n"
                f"Keywords Missing: {', '.join(keyword_missing[:10])}\n\n"
                f"Formatting Suggestions:\n" + "\n".join(f"• {s}" for s in formatting) + "\n\n"
                f"Recommendation: {ats_result.get('overall_recommendation', 'Consider improving keywords and formatting.')}"
            ),
            "ats_result": ats_result
        }
    else:
        return {"answer": "I couldn't perform a full ATS analysis. Ensure you provided a job description and try again."}

def handle_missing_info(cv_text: str) -> Dict:
    try:
        missing_analysis = detect_missing_sections(cv_text)
    except Exception:
        current_app.logger.exception("Missing sections detection failed")
        missing_analysis = None

    if missing_analysis:
        missing_sections = missing_analysis.get('missing_sections', [])
        missing_prof = missing_analysis.get('missing_professional_elements', [])
        formatting_gaps = missing_analysis.get('formatting_gaps', [])
        return {
            "answer": (
                f"**Missing Elements Analysis**\n\n"
                f"Completeness Score: {missing_analysis.get('completeness_score','N/A')}/100\n\n"
                f"Missing Sections:\n" + "\n".join(f"• {s}" for s in missing_sections) + "\n\n"
                f"Missing Professional Elements:\n" + "\n".join(f"• {p.get('issue','')} - {p.get('suggestion','')}" for p in missing_prof) + "\n\n"
                f"Formatting Gaps:\n" + "\n".join(f"• {g}" for g in formatting_gaps) + "\n\n"
                f"Would you like me to add any of these missing elements?"
            ),
            "missing_analysis": missing_analysis
        }
    else:
        return {"answer": "I couldn't detect specific missing elements. Consider adding a professional summary, quantifiable achievements, and a clear skills section."}

def handle_improvement(cv_text: str, question: str) -> Dict:
    # detect section
    section_match = re.search(r'\b(summary|experience|education|skills|projects|achievements)\b', question, re.I)
    section = section_match.group(1).lower() if section_match else None

    # Check if user wants advice/suggestions vs a rewrite
    is_advice_request = any(w in question.lower() for w in ['how to', 'suggest', 'advice', 'tips', 'recommend', 'what should i'])

    try:
        if section:
            if is_advice_request:
                # Provide advice for the section
                prompt = f"""Analyze the {section} section of this CV and provide specific advice on how to improve it.
                Focus on:
                - Content quality
                - Formatting
                - Impact and clarity
                
                CV TEXT:
                {cv_text}
                """
                advice = safe_generate_with_gemini(prompt)
                return {"answer": advice}
            else:
                # Rewrite the section
                improved_section = generate_improved_cv(cv_text, focus_areas=[section])
                if improved_section:
                    return {
                        "answer": f"**Improved {section.title()} Section:**\n\n{improved_section}\n\nWould you like me to apply these?",
                        "improved_text": improved_section
                    }
                else:
                    return {"answer": f"I couldn't generate an improved {section} automatically. Please paste the section content and I'll rewrite it."}
        else:
            if is_advice_request:
                # Provide overall improvement advice based on defects
                analysis = get_cached_analysis_data()
                if not analysis:
                    analysis = analyze_cv(cv_text)
                    if analysis:
                        cache_analysis_data(analysis)
                
                if analysis and 'analysis' in analysis:
                    weaknesses = analysis['analysis'].get('weaknesses', [])
                    suggestions = analysis['analysis'].get('improvement_suggestions', [])
                    return {
                        "answer": (
                            f"**CV Improvement Plan**\n\n"
                            f"**Identified Weaknesses:**\n" + "\n".join(f"• {w}" for w in weaknesses) + "\n\n"
                            f"**Suggestions for Improvement:**\n" + "\n".join(f"• {s}" for s in suggestions) + "\n\n"
                            f"Would you like me to rewrite the CV incorporating these changes?"
                        )
                    }
                else:
                    return {"answer": "I couldn't analyze the CV for improvements. Please try again."}
            else:
                # Rewrite the whole CV
                improved_cv = generate_improved_cv(cv_text)
                if improved_cv:
                    preview = improved_cv if len(improved_cv) < 1200 else improved_cv[:1200] + "..."
                    # store generated in GridFS instead of session? We store in session id only (for download), but keep small text
                    session['generated_cv_preview'] = preview
                    session['generated_cv_text'] = improved_cv[:10000]  # safe partial store; avoid storing full long text if too large
                    return {"answer": f"**Improved CV (preview):**\n\n{preview}\n\nWould you like the full version?", "generated_cv": improved_cv}
                else:
                    return {"answer": "I couldn't generate an improved CV automatically. Try again or provide the specific part you want improved."}
    except Exception:
        current_app.logger.exception("CV improvement failed")
        return {"answer": "An error occurred while generating improvements. Try again later."}

def handle_keywords(cv_text: str, question: str, payload: Dict) -> Dict:
    role_match = re.search(r'(?:for|as a|as an|in)\s+([a-z\s]+?)(?:\s+role|\s+position|job|\?|$)', question, re.I)
    role = role_match.group(1).strip() if role_match else payload.get('target_role', 'software engineer')
    try:
        ks = suggest_keywords_for_role(role, cv_text)
    except Exception:
        current_app.logger.exception("Keyword suggestion failed")
        ks = None

    if ks:
        return {
            "answer": (
                f"**Keywords for {role.title()}**\n\n"
                f"Priority additions:\n" + "\n".join(f"• {k}" for k in ks.get('priority_additions', [])) + "\n\n"
                f"Suggested keywords:\n" + "\n".join(f"• {k}" for k in ks.get('suggested_keywords', [])[:15]) + "\n\n"
                f"Already present:\n" + "\n".join(f"• {k}" for k in ks.get('existing_keywords', [])[:10]) + "\n\n"
                f"Would you like me to integrate these?"
            ),
            "keywords": ks
        }
    else:
        return {"answer": f"For a {role.title()} role, consider adding role-specific tools, frameworks, and measurable achievements."}

def handle_section_specific(cv_text: str, question: str) -> Dict:
    # Prefer RAG if available and index exists, else fallback to direct CV slice + Gemini
    context = ""
    try:
        if RAG_AVAILABLE:
            try:
                vectorstore = load_or_build_vectorstore_for_user(str(current_user.get_id()), cv_text)
                if vectorstore:
                    results = vectorstore.similarity_search(question, k=3)
                    context = "\n\n".join([r.page_content for r in results])
                else:
                    context = cv_text[:CONTEXT_CHARS]
            except Exception:
                logger.warning("RAG similarity search failed; falling back to plain context")
                context = cv_text[:CONTEXT_CHARS]
        else:
            context = cv_text[:CONTEXT_CHARS]

        prompt = f"""You are an expert CV consultant specializing in resume optimization.

Analyze the CV section content below and provide detailed, actionable feedback for the user's question.

GUIDELINES:
- Reference specific content from the CV in your answer
- Provide concrete examples and suggestions
- Use professional but friendly language
- Format your response clearly with bullet points when appropriate
- Be specific about what's working well and what could be improved

CV SECTION CONTENT:
{context}

USER QUESTION: {question}

DETAILED RESPONSE:"""
        answer_text = safe_generate_with_gemini(prompt)
        return {"answer": answer_text}
    except Exception:
        current_app.logger.exception("Section-specific handling failed")
        return {"answer": "I encountered an error analyzing that section. Please try asking about a specific section (summary, experience, education, skills, etc.)."}

def handle_extraction(cv_text: str, question: str) -> Dict:
    q = question.lower()
    try:
        if 'personal' in q or 'contact' in q or 'email' in q or 'phone' in q:
            info = extract_personal_info(cv_text)
            if info:
                return {"answer": (
                    f"**Personal Information:**\n"
                    f"• Name: {info.get('name','Not found')}\n"
                    f"• Email: {info.get('email','Not found')}\n"
                    f"• Phone: {info.get('phone','Not found')}\n"
                    f"• Location: {info.get('location','Not found')}\n"
                    f"• LinkedIn: {info.get('linkedin','Not found')}\n"
                    f"• GitHub: {info.get('github','Not found')}\n"
                ), "personal_info": info}
            else:
                return {"answer": "I couldn't extract complete personal info. Ensure your CV includes contact details."}
        if 'skill' in q or 'skills' in q:
            analysis = analyze_cv_comprehensively(cv_text)
            skills = analysis.get('skills') if isinstance(analysis, dict) else None
            if skills:
                return {"answer": "**Skills Found in Your CV:**\n\n" + "\n".join(f"• {s}" for s in skills), "skills": skills}
            else:
                return {"answer": "I couldn't reliably extract a skills list. Consider listing skills under a clear 'Skills' heading."}
        # fallback generic extraction: use RAG-ish or gemini
        prompt = f"Extract the answer to: {question}\n\nFrom this CV: {cv_text[:CONTEXT_CHARS]}"
        txt = safe_generate_with_gemini(prompt)
        return {"answer": txt}
    except Exception:
        current_app.logger.exception("Extraction failed")
        return {"answer": "Extraction failed. Try again or paste the section you want extracted."}

def handle_courses(cv_text: str, question: str) -> Dict:
    try:
        # Extract potential career goal from question
        career_goal = None
        if "for" in question:
            parts = question.split("for")
            if len(parts) > 1:
                career_goal = parts[1].strip()
        
        suggestions = suggest_courses(cv_text, career_goal)
    except Exception:
        current_app.logger.exception("Course suggestion failed")
        suggestions = None

    if suggestions:
        courses = suggestions.get('recommended_courses', [])
        certs = suggestions.get('certifications', [])
        path = suggestions.get('learning_path', '')
        
        return {
            "answer": (
                f"**Recommended Courses & Certifications**\n\n"
                f"**Learning Path:**\n{path}\n\n"
                f"**Top Courses:**\n" + "\n".join(f"• **{c.get('title')}** ({c.get('provider')}): {c.get('reason')}" for c in courses[:5]) + "\n\n"
                f"**Key Certifications:**\n" + "\n".join(f"• **{c.get('name')}** ({c.get('issuer')}): {c.get('impact')}" for c in certs[:3]) + "\n\n"
                f"Would you like more details on any of these?"
            ),
            "courses": suggestions
        }
    else:
        return {"answer": "I couldn't generate specific course recommendations. Consider looking for courses on platforms like Coursera, Udemy, or edX related to your field."}

def handle_qualifications(cv_text: str, question: str) -> Dict:
    try:
        suggestions = suggest_qualifications(cv_text)
    except Exception:
        current_app.logger.exception("Qualification suggestion failed")
        suggestions = None

    if suggestions:
        edu = suggestions.get('education_recommendations', [])
        prof = suggestions.get('professional_development', [])
        advice = suggestions.get('strategic_advice', '')
        
        return {
            "answer": (
                f"**Qualification Improvement Strategy**\n\n"
                f"{advice}\n\n"
                f"**Education:**\n" + "\n".join(f"• {e}" for e in edu) + "\n\n"
                f"**Professional Development:**\n" + "\n".join(f"• {p}" for p in prof) + "\n\n"
                f"Would you like to discuss how to add these to your CV?"
            ),
            "qualifications": suggestions
        }
    else:
        return {"answer": "I couldn't generate specific qualification advice. Generally, consider advanced degrees or specialized certifications in your industry."}

def handle_generate(cv_text: str) -> Dict:
    try:
        improved = generate_improved_cv(cv_text)
    except Exception:
        current_app.logger.exception("Generate improved CV failed")
        improved = None

    if improved:
        # store full improved CV in GridFS so user can download safely later
        try:
            fs = gridfs_instance()
            file_id = fs.put(improved.encode('utf-8'), filename=f"generated_cv_{current_user.get_id()}.txt", content_type='text/plain', user_id=str(current_user.get_id()))
            session['generated_cv_file_id'] = str(file_id)
        except Exception:
            current_app.logger.exception("Failed to store generated CV in GridFS")
            # as fallback store a preview only
            session['generated_cv_preview'] = improved[:1000]

        return {
            "answer": (
                "**Your Updated CV is Ready!**\n\n"
                "I've generated an improved version of your CV with:\n"
                "• Enhanced formatting for ATS compatibility\n"
                "• Stronger action verbs and quantifiable achievements\n"
                "• Better section organization\n"
                "• Relevant keywords\n\n"
                "You can download the updated version. Would you like any specific adjustments?"
            ),
            "generated_cv": True
        }
    else:
        return {"answer": "I couldn't generate an improved CV at this time. Try again later."}

def handle_general(cv_text: str, question: str) -> Dict:
    # Use RAG first if available, otherwise fallback to Gemini with a short CV context
    try:
        # Try to use vectorstore retrieval for better answers
        context = None
        try:
            vectorstore = load_or_build_vectorstore_for_user(str(current_user.get_id()), cv_text)
            if vectorstore:
                results = vectorstore.similarity_search(question, k=4)
                context = "\n\n".join([r.page_content for r in results])
        except Exception:
            logger.debug("No vectorstore available for general handler; using short CV context")

        if not context:
            context = cv_text[:CONTEXT_CHARS]
        conv_context = session.get('conversation_context', {})
        context_note = f"\n\nPrevious context: We were discussing the {conv_context.get('last_section')} section." if conv_context.get('last_section') else ""
        prompt = f"""You are an expert CV/Resume consultant and career advisor. 

Analyze the CV content below and provide a detailed, helpful answer to the user's question.

IMPORTANT INSTRUCTIONS:
- Be specific and reference actual content from the CV
- Provide actionable suggestions and concrete examples
- If the CV is missing information relevant to the question, point that out
- Be professional but conversational
- Use bullet points for clarity when listing multiple items{context_note}
- If the user asks a question unrelated to the CV or career advice, politely steer them back to the topic.

CV CONTENT:
{context}

USER QUESTION: {question}

DETAILED ANSWER:"""
        try:
            answer = safe_generate_with_gemini(prompt)
            return {"answer": answer}
        except Exception:
            logger.warning("Gemini generation unavailable, falling back to local QA")
            return {"answer": "I'm currently having trouble connecting to the AI service. Please try again in a moment."}
    except Exception:
        current_app.logger.exception("General handling failed")
        return {"answer": "I encountered an error processing your question. Please try rephrasing or ask something more specific about your CV."}

# --------- Routes ----------

@chatbot.route("/upload", methods=["POST"])
@login_required
def upload_cv():
    """Upload and store CV (text) to GridFS. Build optional vectorstore if possible."""
    if 'files' not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    file = request.files['files']
    if file.filename == '':
        return jsonify({"success": False, "message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "message": "Invalid file type"}), 400

    try:
        # Extract CV text (PDF, DOCX, or text)
        file_bytes = file.read()
        cv_text = extract_text_from_any(file_bytes, file.filename)

        # store cv_text in GridFS (NOT session) to avoid session cookie limits
        fs = gridfs_instance()
        filename = f"chat_{current_user.get_id()}_{file.filename}"
        file_id = fs.put(cv_text.encode('utf-8'), filename=filename, content_type='text/plain', user_id=str(current_user.get_id()))

        # Save only file-id in session
        session['cv_file_id'] = str(file_id)
        # clear previous generated content ids if any
        session.pop('generated_cv_file_id', None)
        session.pop('cv_analysis_file_id', None)
        session['chat_history'] = []
        session['conversation_context'] = {}

        # Optional: create or load vectorstore for RAG (tries Google embeddings then HF)
        vector_store_created = False
        try:
            vs = load_or_build_vectorstore_for_user(str(current_user.get_id()), cv_text)
            if vs is not None:
                vector_store_created = True
                logger.info("Vector store created or loaded successfully for user %s", current_user.get_id())
        except Exception:
            logger.exception("Could not create or load vector store; continuing without RAG")

        return jsonify({
            "success": True,
            "message": "CV uploaded and processed successfully. You can now ask questions about your CV.",
            "rag_enabled": vector_store_created
        })
    except Exception as e:
        current_app.logger.exception("Error processing CV upload")
        return jsonify({"success": False, "message": str(e)}), 500

@chatbot.route("/ask", methods=["POST"])
@login_required
@require_cv
def ask():
    """Answer CV-based question using classification + modular handlers."""
    data = request.get_json() or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"success": False, "message": "No question provided"}), 400

    cv_text = fetch_cv_text_from_gridfs()
    if not cv_text:
        return jsonify({"success": False, "message": "Could not read CV text from storage."}), 500

    try:
        qtype = classify_query(question)
        current_app.logger.info(f"Query classified as: {qtype}")

        # Dispatch to handlers
        if qtype == 'ats_check':
            result = handle_ats_check(cv_text, data)
        elif qtype == 'missing_info':
            result = handle_missing_info(cv_text)
        elif qtype == 'improvement':
            result = handle_improvement(cv_text, question)
            # set last_section context if applicable
            section_match = re.search(r'\b(summary|experience|education|skills|projects|achievements)\b', question, re.I)
            if section_match:
                conv = session.get('conversation_context', {})
                conv['last_section'] = section_match.group(1).lower()
                session['conversation_context'] = conv
        elif qtype == 'keywords':
            result = handle_keywords(cv_text, question, data)
        elif qtype == 'section_specific':
            result = handle_section_specific(cv_text, question)
        elif qtype == 'extraction':
            result = handle_extraction(cv_text, question)
        elif qtype == 'generate':
            result = handle_generate(cv_text)
        elif qtype == 'courses':
            result = handle_courses(cv_text, question)
        elif qtype == 'qualifications':
            result = handle_qualifications(cv_text, question)
        else:
            result = handle_general(cv_text, question)

        # Update chat history
        update_chat_history(question, result.get("answer", ""))
        response_payload = {"success": True, "answer": result.get("answer", ""), "query_type": qtype}
        # attach any extra data
        for k in ("ats_result", "missing_analysis", "keywords", "improved_text", "personal_info", "skills", "generated_cv"):
            if k in result:
                response_payload[k] = result[k]

        return jsonify(response_payload)
    except Exception as e:
        current_app.logger.exception("Error during /ask processing")
        return jsonify({"success": False, "message": str(e), "error_type": type(e).__name__}), 500

@chatbot.route("/download-cv", methods=["GET"])
@login_required
def download_generated_cv():
    """Download the generated/improved CV stored in GridFS (if available)."""
    try:
        file_id = session.get('generated_cv_file_id')
        if not file_id:
            # fallback: maybe preview stored
            preview = session.get('generated_cv_preview')
            if preview:
                # return text as file-like
                buf = io.BytesIO(preview.encode('utf-8'))
                buf.seek(0)
                return send_file(buf, mimetype='text/plain', as_attachment=True, download_name=f'improved_cv_{current_user.get_id()}.txt')
            return jsonify({"success": False, "message": "No generated CV available. Please generate one first."}), 404

        fs = gridfs_instance()
        file_obj = fs.get(ObjectId(file_id))
        content = file_obj.read()
        buf = io.BytesIO(content)
        buf.seek(0)
        # If you prefer PDF generation, ensure app.utils.cv_utils.generate_pdf exists and returns BytesIO
        return send_file(buf, mimetype='text/plain', as_attachment=True, download_name=f'improved_cv_{current_user.get_id()}.txt')
    except Exception:
        current_app.logger.exception("Error downloading generated CV")
        return jsonify({"success": False, "message": "Failed to download generated CV."}), 500

@chatbot.route("/analysis", methods=["GET"])
@login_required
@require_cv
def get_analysis():
    """Return a stored or freshly computed comprehensive analysis (store analysis in GridFS if large)."""
    try:
        # If we previously stored analysis in session as file id, try to fetch it
        analysis = get_cached_analysis_data()
        if analysis:
            return jsonify({"success": True, "analysis": analysis})

        # Otherwise run analysis now (and store result in GridFS)
        cv_text = fetch_cv_text_from_gridfs()
        if not cv_text:
            return jsonify({"success": False, "message": "Could not read CV text."}), 500

        analysis = analyze_cv(cv_text)
        if not analysis:
            return jsonify({"success": False, "message": "Analysis returned empty result."}), 500

        # store analysis in GridFS to avoid session bloat
        cache_analysis_data(analysis)

        return jsonify({"success": True, "analysis": analysis})
    except Exception:
        current_app.logger.exception("Error getting CV analysis")
        return jsonify({"success": False, "message": "Failed to produce analysis."}), 500
