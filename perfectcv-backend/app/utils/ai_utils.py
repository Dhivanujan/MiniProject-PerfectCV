import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from config.config import Config
import logging
import json
import time
import random
from typing import Iterable, List, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Prefer fast, affordable models first; fall back to any model that supports generateContent
# Updated to use Gemini 1.5 Flash/Pro which support JSON mode natively
DEFAULT_GENERATION_MODELS: List[str] = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro",
    "models/gemini-pro",
]


def generate_with_retry(model, prompt, **kwargs):
    """Generate content with exponential backoff retry logic."""
    retries = 3
    backoff = 1
    last_exception = None
    
    for i in range(retries + 1):
        try:
            return model.generate_content(prompt, **kwargs)
        except Exception as e:
            last_exception = e
            # Check if it's a retryable error (network, rate limit, server error)
            is_retryable = isinstance(e, (google_exceptions.ServiceUnavailable, 
                                        google_exceptions.ResourceExhausted,
                                        google_exceptions.Aborted,
                                        google_exceptions.DeadlineExceeded,
                                        google_exceptions.InternalServerError))
            
            if not is_retryable and i < retries:
                # If it's not obviously retryable, we might still want to retry for generic connection issues
                # but maybe log it differently. For now, let's retry most exceptions as API can be flaky.
                pass
                
            if i == retries:
                logger.error(f"AI generation failed after {retries} retries: {e}")
                break
            
            sleep_time = backoff * (2 ** i) + random.uniform(0, 1)
            logger.warning(f"AI generation failed (attempt {i+1}/{retries+1}), retrying in {sleep_time:.2f}s... Error: {e}")
            time.sleep(sleep_time)
            
    if last_exception:
        raise last_exception
    return None


def setup_gemini():
    """Configure the genai client if an API key is available.

    Returns True if configured, False otherwise.
    """
    api_key = getattr(Config, "API_KEY", None)
    if not api_key:
        logger.info("No API key found for Gemini/generative AI.")
        return False

    try:
        genai.configure(api_key=api_key)
        logger.info("Gemini genai configured with provided API key.")
        return True
    except Exception as e:
        logger.exception("Failed to configure Gemini genai: %s", e)
        return False


def get_valid_model():
    """Return a model name that supports generation or None.

    This function is safe to call at runtime; it catches exceptions and
    returns None if models cannot be listed (e.g., no credentials).
    """
    try:
        # Ensure client configured
        if not setup_gemini():
            return None

        for m in genai.list_models():
            name = getattr(m, "name", None)
            methods = getattr(m, "supported_generation_methods", [])
            if methods and "generateContent" in methods:
                return name
    except Exception as e:
        logger.debug("get_valid_model failed: %s", e)
    return None


def _merge_models(preferred: Optional[Iterable[str]]) -> List[str]:
    """Build an ordered list of unique model names to try."""
    ordered: List[str] = []

    def _append(name: Optional[str]):
        if name and name not in ordered:
            ordered.append(name)

    if isinstance(preferred, str):
        _append(preferred)
    elif preferred:
        for name in preferred:
            _append(name)

    for name in DEFAULT_GENERATION_MODELS:
        _append(name)

    fallback = get_valid_model()
    _append(fallback)
    return ordered


def get_generative_model(preferred: Optional[Iterable[str]] = None):
    """Return the first available GenerativeModel instance.

    preferred may be a string or iterable of model names (in priority order).
    Returns None if no model can be instantiated.
    """
    if not setup_gemini():
        return None

    last_error: Optional[Exception] = None
    for name in _merge_models(preferred):
        try:
            return genai.GenerativeModel(name)
        except Exception as exc:
            last_error = exc
            logger.debug("Gemini model %s unavailable: %s", name, exc)

    if last_error:
        logger.error("No Gemini models available. Last error: %s", last_error)
    return None


import re

def clean_json_response(text):
    """Clean JSON response from LLM by removing markdown code blocks."""
    if not text:
        return text
    
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Find the first '{' or '[' and the last '}' or ']'
    start_brace = text.find('{')
    start_bracket = text.find('[')
    
    start = -1
    if start_brace != -1 and start_bracket != -1:
        start = min(start_brace, start_bracket)
    elif start_brace != -1:
        start = start_brace
    elif start_bracket != -1:
        start = start_bracket
        
    if start != -1:
        # Find the corresponding end
        end_brace = text.rfind('}')
        end_bracket = text.rfind(']')
        end = max(end_brace, end_bracket)
        
        if end != -1 and end >= start:
            return text[start:end+1]
            
    return text.strip()


def structure_cv_sections(cv_text):
    """Extract and structure key sections from CV text."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for structure_cv_sections")
            return None
        prompt = f"""Given the following CV text, identify and structure its key sections. 
        Format the response as a JSON object with these sections (if present):
        - personal_info: Basic information like name, contact details
        - summary: Professional summary or objective
        - education: Academic qualifications
        - experience: Work experience
        - skills: Technical and soft skills
        - certifications: Professional certifications
        - projects: Notable projects
        - achievements: Key accomplishments
        
        Preserve the original text formatting within each section.
        
        CV TEXT:
        {cv_text}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        # Ensure response is valid JSON
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning("Generated CV structure is not valid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error in structuring CV: %s", e)
        return None


def extract_ats_keywords(cv_text):
    """Extract important keywords and phrases for ATS optimization."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for extract_ats_keywords")
            return None
        prompt = f"""Analyze this CV text and extract key ATS-relevant keywords and phrases.
        Format the response as a JSON object with these categories:
        1. Technical skills: Programming languages, tools, frameworks
        2. Industry terminology: Domain-specific terms
        3. Action verbs: Words describing achievements and responsibilities
        4. Certifications: Professional certifications and qualifications
        5. Core competencies: Key professional skills and abilities
        
        CV TEXT:
        {cv_text}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        # Ensure response is valid JSON
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning("Generated ATS keywords are not valid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error extracting ATS keywords: %s", e)
        return None


def analyze_cv_content(cv_text, question):
    """Analyze CV content and answer questions about it with improved context understanding."""
    try:
        # First, structure the CV content into sections
        structured_cv = structure_cv_sections(cv_text)
        
        # Extract ATS-relevant keywords
        ats_keywords = extract_ats_keywords(cv_text)
        model = get_generative_model()
        if not model:
            return "Service unavailable. Please try again later."
        chat = model.start_chat(history=[])
        
        prompt = f"""Analyze the CV content below and answer the following question.
        Use the structured sections and ATS keywords to provide accurate, specific answers.
        If the information is not present in the CV, say so honestly.

        STRUCTURED CV SECTIONS:
        {structured_cv if structured_cv else "Section structuring unavailable"}

        ATS KEYWORDS:
        {ats_keywords if ats_keywords else "Keyword extraction unavailable"}

        ORIGINAL CV TEXT (for reference):
        {cv_text}

        QUESTION: {question}
        
        Please provide a clear, specific answer focusing only on relevant information from the CV.
        If asked about skills or qualifications not mentioned in the CV, state that explicitly.
        """
        
        response = chat.send_message(prompt)
        return response.text.strip()
        
    except Exception as e:
        logger.exception("Error in CV analysis: %s", e)
        return "Sorry, I'm having trouble analyzing the CV right now. Please try again."


def extract_personal_info(cv_text):
    """Extract personal information from CV."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for extract_personal_info")
            return None
        prompt = f"""Extract personal information from this CV and return as JSON.
        Include: name, email, phone, location, linkedin, github, website (if available).
        Return ONLY valid JSON, no additional text.
        
        CV TEXT:
        {cv_text}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning("Personal info extraction returned invalid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error extracting personal info: %s", e)
        return None


def detect_missing_sections(cv_text):
    """Detect missing sections and elements in CV."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for detect_missing_sections")
            return None
        prompt = f"""Analyze this CV and identify missing elements. Return as JSON with these keys:
        - missing_sections: array of missing standard sections (e.g., "Summary", "Skills", "Projects", "Achievements")
        - missing_professional_elements: array of objects with "issue" and "suggestion" 
          (e.g., no action verbs, no measurable achievements, no dates, no role descriptions, no technologies)
        - formatting_gaps: array of formatting issues (e.g., "Too long", "Too short", "Not ATS friendly", "Inconsistent formatting")
        - completeness_score: number 0-100 indicating how complete the CV is
        
        Return ONLY valid JSON, no additional text.
        
        CV TEXT:
        {cv_text}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning("Missing sections detection returned invalid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error detecting missing sections: %s", e)
        return None


def improve_sentence(sentence, context="work experience"):
    """Improve a CV sentence to be more impactful."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for improve_sentence")
            return None
        prompt = f"""Improve this CV sentence to be more professional and impactful.
        - Add action verbs
        - Add measurable achievements where possible
        - Make it specific and quantifiable
        - Keep it concise (1-2 lines)
        
        Context: {context}
        Original: {sentence}
        
        Return ONLY the improved sentence, no explanations.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
            
    except Exception as e:
        logger.exception("Error improving sentence: %s", e)
        return None


def suggest_achievements(cv_text, role_context=""):
    """Suggest achievement-oriented bullet points."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for suggest_achievements")
            return None
        prompt = f"""Based on this CV content, suggest 5 achievement-oriented bullet points.
        Focus on:
        - Measurable outcomes (reduced time, increased sales, improved efficiency)
        - Leadership and impact
        - Technical accomplishments
        - Team collaboration
        
        {f"Role context: {role_context}" if role_context else ""}
        
        Return as JSON array of strings. Return ONLY valid JSON.
        
        CV TEXT:
        {cv_text}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Try to extract array from text
            text = clean_json_response(response.text)
            if text.startswith('[') and text.endswith(']'):
                return json.loads(text)
            logger.warning("Achievement suggestions returned invalid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error suggesting achievements: %s", e)
        return None


def check_ats_compatibility(cv_text, job_description=""):
    """Check ATS compatibility and suggest improvements."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for check_ats_compatibility")
            return None
        prompt = f"""Analyze this CV for ATS (Applicant Tracking System) compatibility.
        Return as JSON with these keys:
        - ats_score: number 0-100
        - issues: array of ATS compatibility issues
        - keyword_analysis: object with "found" and "missing" arrays
        - formatting_suggestions: array of formatting improvements
        - overall_recommendation: string with overall advice
        
        {f"Job Description: {job_description}" if job_description else ""}
        
        Return ONLY valid JSON, no additional text.
        
        CV TEXT:
        {cv_text}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning("ATS check returned invalid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error checking ATS compatibility: %s", e)
        return None


def suggest_keywords_for_role(role, cv_text):
    """Suggest keywords to add based on target role."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for suggest_keywords_for_role")
            return None
        prompt = f"""Suggest relevant keywords and skills for a {role} position.
        Compare with the current CV and identify gaps.
        Return as JSON with these keys:
        - suggested_keywords: array of keywords to add
        - existing_keywords: array of relevant keywords already present
        - priority_additions: array of high-priority keywords to add
        
        Return ONLY valid JSON, no additional text.
        
        Target Role: {role}
        
        Current CV:
        {cv_text}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning("Keyword suggestions returned invalid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error suggesting keywords: %s", e)
        return None


def generate_improved_cv(cv_text, focus_areas=None):
    """Generate an improved version of the entire CV."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for generate_improved_cv")
            return None
        focus = ", ".join(focus_areas) if focus_areas else "overall improvement"
        
        prompt = f"""Rewrite this CV to be more professional and ATS-friendly.
        Focus on: {focus}
        
        Improvements should include:
        - Strong action verbs
        - Quantifiable achievements
        - Clear section headers
        - Proper formatting
        - Relevant keywords
        
        Return the improved CV text in a professional format with clear sections.
        
        ORIGINAL CV:
        {cv_text}
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
            
    except Exception as e:
        logger.exception("Error generating improved CV: %s", e)
        return None


def analyze_cv(cv_text: str) -> Optional[Dict[str, Any]]:
    """
    Perform comprehensive CV analysis in a single optimized call.
    Returns structured JSON containing parsed data and analysis.
    """
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for analyze_cv")
            return None
            
        prompt = f"""
        You are an expert CV analyzer and parser. Your task is to extract structured data AND analyze the CV quality.
        
        CV TEXT:
        {cv_text}
        
        Return a SINGLE JSON object with the following structure:
        {{
            "language": "Detected language (e.g., English, French)",
            "parsed_data": {{
                "personal_info": {{ "name": "", "email": "", "phone": "", "linkedin": "", "location": "" }},
                "summary": "Professional summary text found in CV",
                "education": [ {{ "degree": "", "institution": "", "year": "", "details": "" }} ],
                "experience": [ {{ "role": "", "company": "", "duration": "", "details": [] }} ],
                "skills": {{ "technical": [], "soft": [], "tools": [], "languages": [] }},
                "projects": [ {{ "name": "", "description": "", "technologies": [] }} ],
                "certifications": [],
                "achievements": []
            }},
            "analysis": {{
                "ats_score": 0-100,
                "strengths": [],
                "weaknesses": [],
                "missing_sections": [],
                "improvement_suggestions": [],
                "summary": "Brief assessment of the CV"
            }}
        }}
        """
        
        response = generate_with_retry(model, prompt, generation_config={"response_mime_type": "application/json"})
        if not response:
            return None
            
        text = clean_json_response(response.text)
        return json.loads(text)
            
    except Exception as e:
        logger.exception("Error in analyze_cv: %s", e)
        return None


def suggest_courses(cv_text, career_goal=None):
    """Suggest courses and certifications to strengthen the CV."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for suggest_courses")
            return None
        prompt = f"""Analyze this CV and suggest relevant courses and certifications to strengthen it.
        Focus on:
        - Filling skill gaps
        - Industry-recognized certifications
        - Advanced topics relevant to the candidate's experience
        - Emerging technologies in their field
        
        {f"Career Goal: {career_goal}" if career_goal else ""}
        
        Return as JSON with these keys:
        - recommended_courses: array of objects with "title", "provider" (e.g., Coursera, edX, AWS), and "reason"
        - certifications: array of objects with "name", "issuer", and "impact"
        - learning_path: string describing a recommended learning path
        
        Return ONLY valid JSON, no additional text.
        
        CV TEXT:
        {cv_text}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning("Course suggestions returned invalid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error suggesting courses: %s", e)
        return None


def suggest_qualifications(cv_text, career_goal=None):
    """Suggest ways to improve qualifications."""
    try:
        model = get_generative_model()
        if not model:
            logger.warning("No Gemini model available for suggest_qualifications")
            return None
        prompt = f"""Analyze this CV and suggest how to improve the candidate's qualifications.
        Focus on:
        - Formal education (degrees, diplomas)
        - Professional designations
        - Specialized training
        - Portfolio development
        
        {f"Career Goal: {career_goal}" if career_goal else ""}
        
        Return as JSON with these keys:
        - education_recommendations: array of suggestions for formal education
        - professional_development: array of suggestions for professional growth
        - portfolio_ideas: array of project ideas to demonstrate skills
        - strategic_advice: string with overall advice on qualification improvement
        
        Return ONLY valid JSON, no additional text.
        
        CV TEXT:
        {cv_text}
        """
        
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning("Qualification suggestions returned invalid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error suggesting qualifications: %s", e)
        return None
