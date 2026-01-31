"""
FastAPI Chatbot Routes - Refactored
Handles chatbot interactions with JWT authentication and Groq AI
Uses in-memory session storage for reliable CV data access
"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from app.auth.jwt_handler import get_current_active_user
from app.services.unified_cv_extractor import CVExtractor
from config.config import Config

logger = logging.getLogger(__name__)

# Initialize Groq client
GROQ_AVAILABLE = False
groq_client = None

try:
    from groq import Groq
    if Config.GROQ_API_KEY:
        groq_client = Groq(api_key=Config.GROQ_API_KEY)
        GROQ_AVAILABLE = True
        logger.info("✓ Groq AI client initialized for chatbot")
    else:
        logger.warning("GROQ_API_KEY not configured - using rule-based responses")
except ImportError:
    logger.warning("Groq library not installed - using rule-based responses")
except Exception as e:
    logger.error(f"Failed to initialize Groq: {e}")

router = APIRouter()

# In-memory session storage for CV data (keyed by user_id)
# This avoids GridFS lookup issues and ensures reliable data access
cv_sessions: Dict[str, Dict[str, Any]] = {}


class QuestionRequest(BaseModel):
    question: str


class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


def get_cv_session(user_id: str) -> Optional[Dict[str, Any]]:
    """Get CV session data for user."""
    return cv_sessions.get(user_id)


def set_cv_session(user_id: str, cv_data: Dict[str, Any], filename: str):
    """Store CV session data for user."""
    cv_sessions[user_id] = {
        "cv_data": cv_data,
        "filename": filename,
        "uploaded_at": datetime.utcnow().isoformat()
    }
    logger.info(f"✓ CV session stored for user {user_id[:8] if user_id else 'unknown'}...")


def build_cv_context(cv_data: Dict[str, Any]) -> str:
    """Build a context string from CV data for AI prompt."""
    context_parts = []
    
    # Always add name if available
    name = cv_data.get('name') or cv_data.get('full_name') or 'Unknown'
    context_parts.append(f"Name: {name}")
    
    if cv_data.get('email'):
        context_parts.append(f"Email: {cv_data['email']}")
    if cv_data.get('phone'):
        context_parts.append(f"Phone: {cv_data['phone']}")
    if cv_data.get('location'):
        context_parts.append(f"Location: {cv_data['location']}")
    
    if cv_data.get('summary'):
        summary = cv_data['summary']
        if isinstance(summary, str):
            context_parts.append(f"\nSummary: {summary[:500]}")
    
    # Handle skills - check multiple possible field names
    skills = cv_data.get('skills') or cv_data.get('technical_skills') or []
    if skills and isinstance(skills, list):
        context_parts.append(f"\nSkills: {', '.join(str(s) for s in skills[:20])}")
    
    # Handle experience
    experience = cv_data.get('experience') or cv_data.get('work_experience') or []
    if experience and isinstance(experience, list):
        context_parts.append(f"\nWork Experience ({len(experience)} positions):")
        for exp in experience[:5]:
            if isinstance(exp, dict):
                title = exp.get('title') or exp.get('position') or exp.get('role') or ''
                company = exp.get('company') or exp.get('organization') or exp.get('employer') or ''
                dates = exp.get('dates') or exp.get('duration') or exp.get('period') or ''
                desc = exp.get('description') or exp.get('responsibilities') or ''
                if isinstance(desc, list):
                    desc = '; '.join(desc[:2])
                line = f"  - {title}"
                if company:
                    line += f" at {company}"
                if dates:
                    line += f" ({dates})"
                context_parts.append(line)
                if desc and isinstance(desc, str):
                    context_parts.append(f"    {desc[:150]}")
            elif isinstance(exp, str):
                context_parts.append(f"  - {exp[:100]}")
    
    # Handle education
    education = cv_data.get('education') or []
    if education and isinstance(education, list):
        context_parts.append(f"\nEducation ({len(education)} entries):")
        for edu in education[:3]:
            if isinstance(edu, dict):
                degree = edu.get('degree') or edu.get('qualification') or edu.get('title') or ''
                institution = edu.get('institution') or edu.get('school') or edu.get('university') or ''
                year = edu.get('year') or edu.get('graduation_year') or ''
                line = f"  - {degree}"
                if institution:
                    line += f" from {institution}"
                if year:
                    line += f" ({year})"
                context_parts.append(line)
            elif isinstance(edu, str):
                context_parts.append(f"  - {edu[:100]}")
    
    # Handle projects
    projects = cv_data.get('projects') or []
    if projects and isinstance(projects, list):
        context_parts.append(f"\nProjects ({len(projects)}):")
        for proj in projects[:5]:
            if isinstance(proj, dict):
                name = proj.get('name') or proj.get('title') or 'Project'
                desc = proj.get('description') or ''
                if isinstance(desc, str):
                    desc = desc[:100]
                line = f"  - {name}"
                if desc:
                    line += f": {desc}"
                context_parts.append(line)
            elif isinstance(proj, str):
                context_parts.append(f"  - {proj[:100]}")
    
    # Handle certifications
    certs = cv_data.get('certifications') or cv_data.get('certificates') or []
    if certs and isinstance(certs, list):
        cert_names = []
        for c in certs[:5]:
            if isinstance(c, dict):
                cert_names.append(c.get('name') or c.get('title') or str(c))
            else:
                cert_names.append(str(c))
        context_parts.append(f"\nCertifications: {', '.join(cert_names)}")
    
    # If we have raw_text and very little structured data, include some of it
    if len(context_parts) <= 2 and cv_data.get('raw_text'):
        raw_text = cv_data['raw_text']
        if isinstance(raw_text, str) and raw_text.strip():
            context_parts.append(f"\nCV Content:\n{raw_text[:1500]}")
    
    result = '\n'.join(context_parts)
    logger.info(f"Built CV context ({len(result)} chars): {result[:200]}...")
    return result


def ask_groq_ai(question: str, cv_context: str) -> Optional[str]:
    """Use Groq AI to generate a medium-length helpful response about the CV."""
    if not GROQ_AVAILABLE or not groq_client:
        return None
    
    try:
        system_prompt = """You are PerfectCV Assistant, a friendly CV advisor.

Response rules:
- Keep answers MEDIUM length (2-4 sentences)
- Be helpful and conversational
- Reference specific details from the CV when relevant
- Use 1-2 emojis max (💼 🎓 💡 ✅)
- No long lists - summarize instead
- Be direct but friendly

Example good responses:
- "Your CV shows strong Python and React skills 💡 Combined with your 2 years at TechCorp, you have a solid full-stack foundation."
- "I see you studied at XYZ University and have 3 projects listed. Adding more technical details to your projects would strengthen your profile."

Always base answers on the CV data provided."""

        user_prompt = f"""CV Data:
{cv_context}

Question: {question}

Give a medium-length helpful answer (2-4 sentences):"""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"Groq AI error: {e}")
        return None


def generate_rule_based_response(question: str, cv_data: Dict[str, Any]) -> str:
    """Generate a medium-length rule-based response when AI is not available."""
    question_lower = question.lower()
    
    name = cv_data.get('name') or 'the candidate'
    
    # Name query
    if any(word in question_lower for word in ['name', 'who', 'whose']):
        email = cv_data.get('email', '')
        response = f"This CV belongs to {name}."
        if email:
            response += f" Contact: {email}"
        return response
    
    # Skills query
    elif any(word in question_lower for word in ['skill', 'skills', 'technology', 'technologies', 'tech stack']):
        skills = cv_data.get('skills', []) or cv_data.get('technical_skills', [])
        if skills and isinstance(skills, list):
            top_skills = ', '.join(str(s) for s in skills[:8])
            return f"💡 Skills found: {top_skills}. Total {len(skills)} skills identified."
        return "No skills detected. Consider adding a Skills section."
    
    # Experience query
    elif any(word in question_lower for word in ['experience', 'work', 'job', 'career', 'employment']):
        exp = cv_data.get('experience', [])
        if exp and isinstance(exp, list) and len(exp) > 0:
            first = exp[0]
            if isinstance(first, dict):
                title = first.get('title') or first.get('position') or 'Position'
                company = first.get('company') or ''
                response = f"💼 Most recent: {title}"
                if company:
                    response += f" at {company}"
                response += f". Total {len(exp)} position(s) listed."
                return response
        return "No work experience found. Adding experience would strengthen this CV."
    
    # Education query
    elif any(word in question_lower for word in ['education', 'degree', 'study', 'university', 'college', 'qualification']):
        edu = cv_data.get('education', [])
        if edu and isinstance(edu, list) and len(edu) > 0:
            first = edu[0]
            if isinstance(first, dict):
                degree = first.get('degree') or first.get('qualification') or 'Degree'
                inst = first.get('institution') or first.get('school') or ''
                response = f"🎓 Education: {degree}"
                if inst:
                    response += f" from {inst}"
                if len(edu) > 1:
                    response += f". Plus {len(edu)-1} more entry(ies)."
                return response
        return "No education details found."
    
    # Contact query
    elif any(word in question_lower for word in ['email', 'phone', 'contact', 'reach']):
        email = cv_data.get('email', 'Not provided')
        phone = cv_data.get('phone', 'Not provided')
        return f"📧 Contact: Email - {email}, Phone - {phone}"
    
    # Projects query
    elif any(word in question_lower for word in ['project', 'portfolio', 'built', 'created']):
        projects = cv_data.get('projects', [])
        if projects and isinstance(projects, list):
            names = [p.get('name') or p.get('title') or 'Project' for p in projects[:3] if isinstance(p, dict)]
            return f"🚀 {len(projects)} project(s) found: {', '.join(names)}."
        return "No projects found. Adding projects would showcase practical skills."
    
    # Improvement suggestions
    elif any(word in question_lower for word in ['improve', 'better', 'suggestion', 'tip', 'advice', 'recommend']):
        missing = []
        if not cv_data.get('summary'):
            missing.append("professional summary")
        if not cv_data.get('skills') and not cv_data.get('technical_skills'):
            missing.append("skills section")
        if not cv_data.get('projects'):
            missing.append("projects")
        
        if missing:
            return f"💡 Suggestions: Consider adding {', '.join(missing)} to strengthen the CV."
        return f"✅ This CV looks good! Keep it updated with recent achievements."
    
    # Summary/overview
    elif any(word in question_lower for word in ['summary', 'overview', 'tell me about', 'describe']):
        summary = cv_data.get('summary', '')
        if summary and isinstance(summary, str):
            short_summary = summary[:200] + "..." if len(summary) > 200 else summary
            return f"📋 Summary: {short_summary}"
        
        # Build a quick overview
        skills_count = len(cv_data.get('skills', []) or [])
        exp_count = len(cv_data.get('experience', []) or [])
        return f"📊 {name}'s CV has {skills_count} skills and {exp_count} work experience entries."
    
    # Default helpful response
    else:
        skills_count = len(cv_data.get('skills', []) or [])
        exp_count = len(cv_data.get('experience', []) or [])
        return f"This is {name}'s CV with {skills_count} skills and {exp_count} positions. Ask about skills, experience, education, or improvements."


@router.post("/upload")
async def upload_cv_for_chat(
    files: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user)
):
    """Upload a CV file for chatbot interaction."""
    try:
        user_id = str(current_user.get('id', ''))
        filename = files.filename
        
        logger.info(f"📤 Chatbot upload: user={user_id[:8] if user_id else 'unknown'}..., file={filename}")
        
        # Check file type
        allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if file_ext not in allowed_extensions:
            return JSONResponse({
                "success": False,
                "message": f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            }, status_code=400)
        
        # Read file content
        file_bytes = await files.read()
        
        # Extract CV data
        extractor = CVExtractor()
        cv_data = extractor.extract_from_file(file_bytes, filename)
        
        # Log what we extracted for debugging
        logger.info(f"📋 CV data keys: {list(cv_data.keys())}")
        logger.info(f"📋 Name: {cv_data.get('name')}")
        logger.info(f"📋 Email: {cv_data.get('email')}")
        
        skills_count = len(cv_data.get('skills', []) or [])
        exp_count = len(cv_data.get('experience', []) or [])
        
        logger.info(f"✓ CV extracted: {skills_count} skills, {exp_count} experiences")
        
        # Store in session with user_id
        set_cv_session(user_id, cv_data, filename)
        logger.info(f"✓ Session stored. Total sessions: {len(cv_sessions)}, Keys: {list(cv_sessions.keys())}")
        
        # Build simple welcome message
        name = cv_data.get('name') or 'there'
        
        welcome_msg = f"Got it! I've loaded {name}'s CV. What would you like to know?"
        
        return JSONResponse({
            "success": True,
            "message": welcome_msg,
            "cv_data": {
                "name": cv_data.get("name"),
                "email": cv_data.get("email"),
                "skills_count": skills_count,
                "experience_count": exp_count,
                "education_count": len(cv_data.get("education", []))
            }
        })
        
    except Exception as e:
        logger.error(f"Error uploading CV: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "message": f"Error processing CV: {str(e)}"
        }, status_code=500)


@router.post("/ask")
async def ask_about_cv(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """Answer questions about the user's CV."""
    try:
        user_id = str(current_user.get('id', ''))
        question = request.question.strip()
        
        logger.info(f"📥 Chatbot ask: user={user_id[:8] if user_id else 'unknown'}..., question='{question[:50]}'")
        
        # Get CV session
        session = get_cv_session(user_id)
        
        if not session:
            logger.warning(f"No CV session found for user {user_id[:8] if user_id else 'unknown'}")
            logger.info(f"Active sessions: {list(cv_sessions.keys())}")
            return JSONResponse({
                "success": False,
                "answer": "❌ No CV found. Please upload your CV first using the upload button above.",
                "query_type": "error"
            })
        
        cv_data = session.get('cv_data', {})
        logger.info(f"✓ Found CV session. Keys: {list(cv_data.keys())}")
        
        # Try Groq AI first
        if GROQ_AVAILABLE:
            cv_context = build_cv_context(cv_data)
            logger.info(f"📋 CV context length: {len(cv_context)} chars")
            
            if not cv_context or len(cv_context) < 20:
                logger.warning("CV context is too short, using raw text fallback")
                # Try to get raw text directly
                raw = cv_data.get('raw_text', '')
                if raw:
                    cv_context = f"CV Content:\n{raw[:2000]}"
            
            ai_response = ask_groq_ai(question, cv_context)
            
            if ai_response:
                logger.info(f"✓ Groq AI response generated")
                return JSONResponse({
                    "success": True,
                    "answer": ai_response,
                    "query_type": "ai_response",
                    "ai_powered": True
                })
        
        # Fallback to rule-based
        logger.info("Using rule-based response")
        response = generate_rule_based_response(question, cv_data)
        
        return JSONResponse({
            "success": True,
            "answer": response,
            "query_type": "rule_based",
            "ai_powered": False
        })
        
    except Exception as e:
        logger.error(f"Error in chatbot ask: {e}", exc_info=True)
        return JSONResponse({
            "success": False,
            "answer": f"Sorry, I encountered an error: {str(e)}",
            "query_type": "error"
        })


@router.get("/cv-info")
async def get_cv_info(current_user: dict = Depends(get_current_active_user)):
    """Get CV information for the current user from session."""
    try:
        user_id = str(current_user.get('id', ''))
        session = get_cv_session(user_id)
        
        if not session:
            return JSONResponse({
                "success": True,
                "has_cv": False,
                "message": "No CV uploaded yet"
            })
        
        cv_data = session.get('cv_data', {})
        
        return JSONResponse({
            "success": True,
            "has_cv": True,
            "cv_data": {
                "name": cv_data.get("name"),
                "email": cv_data.get("email"),
                "skills_count": len(cv_data.get("skills", [])),
                "experience_count": len(cv_data.get("experience", []))
            },
            "filename": session.get('filename'),
            "uploaded_at": session.get('uploaded_at')
        })
        
    except Exception as e:
        logger.error(f"Error getting CV info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat(
    message: ChatMessage,
    current_user: dict = Depends(get_current_active_user)
):
    """Legacy chat endpoint - redirects to /ask."""
    request = QuestionRequest(question=message.message)
    return await ask_about_cv(request, current_user)
