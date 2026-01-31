"""
FastAPI Chatbot Routes
Handles chatbot interactions with JWT authentication and Groq AI
"""
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import gridfs
from bson import ObjectId
from datetime import datetime
import os

from app.auth.jwt_handler import get_current_active_user
from app.services.unified_cv_extractor import CVExtractor
from app.services.cv_scoring_service import CVScoringService
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

def get_db():
    """Get MongoDB database instance"""
    from app_fastapi import get_mongo_db
    return get_mongo_db()

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

@router.get("/cv-info")
async def get_cv_info(current_user: dict = Depends(get_current_active_user)):
    """
    Get CV information for the current user
    """
    try:
        db = get_db()
        fs = gridfs.GridFS(db)
        
        user_id = current_user.get('id')
        
        # Find the most recent CV file for this user
        files = list(fs.find({"user_id": user_id}).sort([("uploadDate", -1)]).limit(1))
        
        if not files:
            return JSONResponse({
                "success": True,
                "has_cv": False,
                "message": "No CV uploaded yet"
            })
        
        file = files[0]
        cv_data = getattr(file, 'cv_data', {})
        raw_text = getattr(file, 'raw_text', '')
        ats_score = getattr(file, 'ats_score', None)
        
        return JSONResponse({
            "success": True,
            "has_cv": True,
            "cv_data": cv_data,
            "raw_text": raw_text[:500] if raw_text else None,  # First 500 chars
            "ats_score": ats_score,
            "filename": getattr(file, 'original_filename', file.filename),
            "uploaded_at": file.upload_date.isoformat() if file.upload_date else None
        })
        
    except Exception as e:
        logger.error(f"Error getting CV info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(
    message: ChatMessage,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Chat with the AI assistant about CV
    """
    try:
        # This is a placeholder - implement actual chatbot logic
        return JSONResponse({
            "success": True,
            "response": "Chatbot functionality is being migrated to FastAPI. Please check back soon.",
            "message": message.message
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class QuestionRequest(BaseModel):
    question: str


def get_user_cv_data(user_id: str) -> Dict[str, Any]:
    """Get the user's CV data from GridFS."""
    db = get_db()
    fs = gridfs.GridFS(db)
    
    # Find the most recent CV file for this user
    files = list(fs.find({"user_id": user_id}).sort([("uploadDate", -1)]).limit(1))
    
    if not files:
        return None
    
    file = files[0]
    return {
        "cv_data": getattr(file, 'cv_data', {}),
        "raw_text": getattr(file, 'raw_text', ''),
        "ats_score": getattr(file, 'ats_score', None),
        "score_details": getattr(file, 'score_details', {}),
        "filename": getattr(file, 'original_filename', file.filename),
    }


def build_cv_context(cv_info: Dict[str, Any]) -> str:
    """Build a context string from CV data for AI prompt."""
    cv_data = cv_info.get('cv_data', {})
    ats_score = cv_info.get('ats_score', 0)
    
    context_parts = []
    context_parts.append(f"ATS Score: {ats_score}%")
    
    if cv_data.get('name'):
        context_parts.append(f"Name: {cv_data['name']}")
    if cv_data.get('email'):
        context_parts.append(f"Email: {cv_data['email']}")
    if cv_data.get('phone'):
        context_parts.append(f"Phone: {cv_data['phone']}")
    if cv_data.get('location'):
        context_parts.append(f"Location: {cv_data['location']}")
    
    if cv_data.get('summary'):
        context_parts.append(f"\nProfessional Summary:\n{cv_data['summary'][:500]}")
    
    if cv_data.get('skills'):
        skills = cv_data['skills'][:20] if isinstance(cv_data['skills'], list) else []
        context_parts.append(f"\nSkills: {', '.join(skills)}")
    
    if cv_data.get('technical_skills'):
        tech_skills = cv_data['technical_skills'][:15] if isinstance(cv_data['technical_skills'], list) else []
        context_parts.append(f"Technical Skills: {', '.join(tech_skills)}")
    
    if cv_data.get('experience'):
        context_parts.append(f"\nWork Experience ({len(cv_data['experience'])} positions):")
        for exp in cv_data['experience'][:3]:
            if isinstance(exp, dict):
                title = exp.get('title', exp.get('position', ''))
                company = exp.get('company', exp.get('organization', ''))
                dates = exp.get('dates', exp.get('duration', ''))
                context_parts.append(f"  - {title} at {company} ({dates})")
    
    if cv_data.get('education'):
        context_parts.append(f"\nEducation ({len(cv_data['education'])} entries):")
        for edu in cv_data['education'][:3]:
            if isinstance(edu, dict):
                degree = edu.get('degree', edu.get('qualification', ''))
                institution = edu.get('institution', edu.get('school', ''))
                year = edu.get('year', '')
                context_parts.append(f"  - {degree} from {institution} ({year})")
    
    if cv_data.get('projects'):
        context_parts.append(f"\nProjects ({len(cv_data['projects'])}):")
        for proj in cv_data['projects'][:3]:
            if isinstance(proj, dict):
                name = proj.get('name', proj.get('title', ''))
                context_parts.append(f"  - {name}")
    
    if cv_data.get('certifications'):
        certs = cv_data['certifications'][:5]
        cert_names = [c.get('name', str(c)) if isinstance(c, dict) else str(c) for c in certs]
        context_parts.append(f"\nCertifications: {', '.join(cert_names)}")
    
    return '\n'.join(context_parts)


def ask_groq_ai(question: str, cv_context: str) -> Optional[str]:
    """Use Groq AI to generate a response about the CV."""
    if not GROQ_AVAILABLE or not groq_client:
        return None
    
    try:
        system_prompt = """You are PerfectCV Assistant, an expert AI career advisor and CV consultant. 
Your role is to help users understand and improve their CVs/resumes.

Guidelines:
- Be helpful, professional, and encouraging
- Provide specific, actionable advice based on the CV data
- Use emojis sparingly to make responses engaging (📊, 💡, ✅, ⚠️, 🎯)
- Format responses with markdown (bold, lists) for readability
- Keep responses concise but comprehensive (max 300 words)
- If asked about something not in the CV, suggest they add it
- Focus on ATS optimization and professional presentation"""

        user_prompt = f"""Here is the user's CV information:

{cv_context}

User's question: {question}

Please provide a helpful, personalized response based on this CV data."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"Groq AI error: {e}")
        return None


def generate_cv_response(question: str, cv_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a response to user's question about their CV using Groq AI or fallback."""
    cv_data = cv_info.get('cv_data', {})
    ats_score = cv_info.get('ats_score', 0)
    score_details = cv_info.get('score_details', {})
    
    # Try Groq AI first
    if GROQ_AVAILABLE:
        cv_context = build_cv_context(cv_info)
        ai_response = ask_groq_ai(question, cv_context)
        
        if ai_response:
            logger.info(f"✓ Groq AI generated response for: '{question[:50]}...'")
            
            # Detect query type for metadata
            question_lower = question.lower()
            query_type = "general"
            if any(word in question_lower for word in ['score', 'ats']):
                query_type = "ats_score"
            elif any(word in question_lower for word in ['skill']):
                query_type = "skills"
            elif any(word in question_lower for word in ['experience', 'work']):
                query_type = "experience"
            elif any(word in question_lower for word in ['education']):
                query_type = "education"
            elif any(word in question_lower for word in ['improve', 'suggestion']):
                query_type = "suggestions"
            
            return {
                "success": True,
                "answer": ai_response,
                "query_type": query_type,
                "ai_powered": True,
                "ats_result": {"score": ats_score} if query_type == "ats_score" else None,
                "keywords": cv_data.get('skills', [])[:10] if query_type == "skills" else None
            }
    
    # Fallback to rule-based responses
    logger.info("Using rule-based response (Groq not available)")
    return generate_rule_based_response(question, cv_info)


def generate_rule_based_response(question: str, cv_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a rule-based response (fallback when AI is not available)."""
    question_lower = question.lower()
    cv_data = cv_info.get('cv_data', {})
    ats_score = cv_info.get('ats_score', 0)
    score_details = cv_info.get('score_details', {})
    
    # Detect query type and generate appropriate response
    if any(word in question_lower for word in ['score', 'ats', 'rating', 'how good', 'how is my']):
        # ATS Score query
        category_scores = score_details.get('category_scores', {})
        strengths = [cat for cat, score in category_scores.items() if score >= 8]
        weaknesses = [cat for cat, score in category_scores.items() if score < 5]
        
        response = f"📊 **Your ATS Score: {ats_score}%**\n\n"
        
        if ats_score >= 80:
            response += "🎉 Excellent! Your CV is well-optimized for ATS systems.\n\n"
        elif ats_score >= 60:
            response += "👍 Good job! Your CV is fairly well-structured, but there's room for improvement.\n\n"
        else:
            response += "⚠️ Your CV needs some improvements to pass ATS screenings effectively.\n\n"
        
        if strengths:
            response += f"**Strengths:** {', '.join(strengths)}\n"
        if weaknesses:
            response += f"**Areas to Improve:** {', '.join(weaknesses)}\n"
        
        return {
            "success": True,
            "answer": response,
            "query_type": "ats_score",
            "ats_result": {"score": ats_score, "details": score_details}
        }
    
    elif any(word in question_lower for word in ['skill', 'skills', 'competenc', 'expertise']):
        # Skills query
        skills = cv_data.get('skills', [])
        technical_skills = cv_data.get('technical_skills', [])
        soft_skills = cv_data.get('soft_skills', [])
        
        response = "📋 **Skills Found in Your CV:**\n\n"
        
        if technical_skills:
            response += f"**Technical Skills ({len(technical_skills)}):** {', '.join(technical_skills[:15])}"
            if len(technical_skills) > 15:
                response += f" +{len(technical_skills) - 15} more"
            response += "\n\n"
        
        if soft_skills:
            response += f"**Soft Skills ({len(soft_skills)}):** {', '.join(soft_skills[:10])}\n\n"
        
        if skills and skills != technical_skills:
            response += f"**Core Skills ({len(skills)}):** {', '.join(skills[:15])}\n\n"
        
        if not skills and not technical_skills and not soft_skills:
            response += "⚠️ No skills detected. Consider adding a dedicated Skills section.\n"
        
        return {
            "success": True,
            "answer": response,
            "query_type": "skills",
            "keywords": skills[:20]
        }
    
    elif any(word in question_lower for word in ['experience', 'work', 'job', 'employment']):
        # Experience query
        experience = cv_data.get('experience', [])
        
        if experience:
            response = f"💼 **Work Experience ({len(experience)} positions):**\n\n"
            for i, exp in enumerate(experience[:5], 1):
                if isinstance(exp, dict):
                    title = exp.get('title', exp.get('position', 'Position'))
                    company = exp.get('company', exp.get('organization', ''))
                    dates = exp.get('dates', exp.get('duration', ''))
                    response += f"{i}. **{title}**"
                    if company:
                        response += f" at {company}"
                    if dates:
                        response += f" ({dates})"
                    response += "\n"
                else:
                    response += f"{i}. {str(exp)[:100]}\n"
        else:
            response = "⚠️ No work experience found in your CV. Consider adding a Work Experience section."
        
        return {
            "success": True,
            "answer": response,
            "query_type": "experience"
        }
    
    elif any(word in question_lower for word in ['education', 'degree', 'university', 'college', 'school']):
        # Education query
        education = cv_data.get('education', [])
        
        if education:
            response = f"🎓 **Education ({len(education)} entries):**\n\n"
            for i, edu in enumerate(education[:5], 1):
                if isinstance(edu, dict):
                    degree = edu.get('degree', edu.get('qualification', 'Degree'))
                    institution = edu.get('institution', edu.get('school', edu.get('university', '')))
                    year = edu.get('year', edu.get('graduation_year', ''))
                    response += f"{i}. **{degree}**"
                    if institution:
                        response += f" - {institution}"
                    if year:
                        response += f" ({year})"
                    response += "\n"
                else:
                    response += f"{i}. {str(edu)[:100]}\n"
        else:
            response = "⚠️ No education found in your CV. Consider adding an Education section."
        
        return {
            "success": True,
            "answer": response,
            "query_type": "education"
        }
    
    elif any(word in question_lower for word in ['project', 'portfolio']):
        # Projects query
        projects = cv_data.get('projects', [])
        
        if projects:
            response = f"🚀 **Projects ({len(projects)}):**\n\n"
            for i, proj in enumerate(projects[:5], 1):
                if isinstance(proj, dict):
                    name = proj.get('name', proj.get('title', 'Project'))
                    desc = proj.get('description', '')[:100]
                    response += f"{i}. **{name}**"
                    if desc:
                        response += f": {desc}"
                    response += "\n"
                else:
                    response += f"{i}. {str(proj)[:100]}\n"
        else:
            response = "⚠️ No projects found in your CV. Adding projects can strengthen your profile!"
        
        return {
            "success": True,
            "answer": response,
            "query_type": "projects"
        }
    
    elif any(word in question_lower for word in ['improve', 'better', 'enhance', 'optimize', 'suggestion', 'recommendation', 'tip']):
        # Improvement suggestions
        suggestions = []
        
        if not cv_data.get('summary'):
            suggestions.append("📝 Add a professional summary at the top of your CV")
        if len(cv_data.get('skills', [])) < 5:
            suggestions.append("💡 Add more relevant skills (aim for 10-15 key skills)")
        if not cv_data.get('experience'):
            suggestions.append("💼 Add work experience with quantifiable achievements")
        if not cv_data.get('education'):
            suggestions.append("🎓 Include your educational background")
        if not cv_data.get('projects'):
            suggestions.append("🚀 Add projects to showcase your practical skills")
        if not cv_data.get('certifications'):
            suggestions.append("📜 Consider adding relevant certifications")
        if ats_score < 70:
            suggestions.append("🎯 Use more industry keywords to improve ATS compatibility")
        
        if suggestions:
            response = "💡 **Suggestions to Improve Your CV:**\n\n"
            for i, suggestion in enumerate(suggestions, 1):
                response += f"{i}. {suggestion}\n"
        else:
            response = "🎉 Your CV looks great! It has all the key sections. Keep it updated with your latest achievements."
        
        return {
            "success": True,
            "answer": response,
            "query_type": "suggestions"
        }
    
    elif any(word in question_lower for word in ['summary', 'profile', 'about', 'objective']):
        # Summary query
        summary = cv_data.get('summary', '')
        
        if summary:
            response = f"📋 **Your Professional Summary:**\n\n{summary}"
        else:
            response = "⚠️ No professional summary found. A strong summary at the top of your CV can make a great first impression!"
        
        return {
            "success": True,
            "answer": response,
            "query_type": "summary"
        }
    
    elif any(word in question_lower for word in ['contact', 'email', 'phone', 'info']):
        # Contact info query
        name = cv_data.get('name', 'Not found')
        email = cv_data.get('email', 'Not found')
        phone = cv_data.get('phone', 'Not found')
        location = cv_data.get('location', '')
        linkedin = cv_data.get('linkedin', '')
        github = cv_data.get('github', '')
        
        response = "📧 **Contact Information:**\n\n"
        response += f"**Name:** {name}\n"
        response += f"**Email:** {email}\n"
        response += f"**Phone:** {phone}\n"
        if location:
            response += f"**Location:** {location}\n"
        if linkedin:
            response += f"**LinkedIn:** {linkedin}\n"
        if github:
            response += f"**GitHub:** {github}\n"
        
        return {
            "success": True,
            "answer": response,
            "query_type": "contact"
        }
    
    else:
        # General/fallback response
        name = cv_data.get('name', 'there')
        response = f"👋 Hi {name}! Here's what I can help you with:\n\n"
        response += "• **\"What's my ATS score?\"** - Check your CV's ATS compatibility\n"
        response += "• **\"Show my skills\"** - View extracted skills\n"
        response += "• **\"Show my experience\"** - View work history\n"
        response += "• **\"Show my education\"** - View educational background\n"
        response += "• **\"Show my projects\"** - View projects\n"
        response += "• **\"How can I improve my CV?\"** - Get improvement suggestions\n\n"
        response += f"Your CV: **{cv_info.get('filename', 'Uploaded CV')}** | ATS Score: **{ats_score}%**"
        
        return {
            "success": True,
            "answer": response,
            "query_type": "general"
        }


@router.post("/ask")
async def ask_about_cv(
    request: QuestionRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Answer questions about the user's CV
    """
    try:
        user_id = current_user.get('id')
        
        # Get user's CV data
        cv_info = get_user_cv_data(user_id)
        
        if not cv_info:
            return JSONResponse({
                "success": False,
                "message": "No CV found. Please upload your CV first."
            }, status_code=404)
        
        # Generate response based on question
        response = generate_cv_response(request.question, cv_info)
        
        logger.info(f"Chatbot question: '{request.question}' -> type: {response.get('query_type')}")
        
        return JSONResponse(response)
        
    except Exception as e:
        logger.error(f"Error in chatbot ask: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_cv_for_chat(
    files: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Upload a CV file for chatbot interaction
    """
    try:
        db = get_db()
        fs = gridfs.GridFS(db)
        
        user_id = current_user.get('id')
        filename = files.filename
        
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
        
        raw_text = cv_data.get('raw_text', '')
        
        # Score the CV
        scoring_service = CVScoringService()
        score_result = scoring_service.score_cv(cv_data)
        ats_score = score_result.get('overall_score', 0)
        
        # Delete old CV files for this user (keep only latest)
        old_files = list(fs.find({"user_id": user_id, "source": "chatbot"}))
        for old_file in old_files:
            fs.delete(old_file._id)
        
        # Store in GridFS with metadata
        file_id = fs.put(
            file_bytes,
            filename=filename,
            user_id=user_id,
            original_filename=filename,
            cv_data=cv_data,
            raw_text=raw_text,
            ats_score=ats_score,
            score_details=score_result,
            source="chatbot",
            upload_date=datetime.utcnow()
        )
        
        logger.info(f"✓ CV uploaded for chatbot: {filename} (user: {user_id})")
        
        return JSONResponse({
            "success": True,
            "message": f"CV '{filename}' uploaded successfully! I've analyzed your CV and found an ATS score of {ats_score}%. How can I help you improve it?",
            "file_id": str(file_id),
            "ats_score": ats_score,
            "cv_data": {
                "name": cv_data.get("name"),
                "email": cv_data.get("email"),
                "skills_count": len(cv_data.get("skills", [])),
                "experience_count": len(cv_data.get("experience", [])),
                "education_count": len(cv_data.get("education", []))
            }
        })
        
    except Exception as e:
        logger.error(f"Error uploading CV for chatbot: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
