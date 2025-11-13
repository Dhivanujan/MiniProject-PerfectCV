import google.generativeai as genai
from config.config import Config
import logging
import json

logger = logging.getLogger(__name__)


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


def structure_cv_sections(cv_text):
    """Extract and structure key sections from CV text."""
    try:
        if not setup_gemini():
            return None

        model = genai.GenerativeModel('gemini-pro')
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
        
        response = model.generate_content(prompt)
        # Ensure response is valid JSON
        try:
            json.loads(response.text)
            return response.text
        except json.JSONDecodeError:
            logger.warning("Generated CV structure is not valid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error in structuring CV: %s", e)
        return None


def extract_ats_keywords(cv_text):
    """Extract important keywords and phrases for ATS optimization."""
    try:
        if not setup_gemini():
            return None

        model = genai.GenerativeModel('gemini-pro')
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
        
        response = model.generate_content(prompt)
        # Ensure response is valid JSON
        try:
            json.loads(response.text)
            return response.text
        except json.JSONDecodeError:
            logger.warning("Generated ATS keywords are not valid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error extracting ATS keywords: %s", e)
        return None


def analyze_cv_content(cv_text, question):
    """Analyze CV content and answer questions about it with improved context understanding."""
    try:
        if not setup_gemini():
            return "Service unavailable. Please try again later."

        # First, structure the CV content into sections
        structured_cv = structure_cv_sections(cv_text)
        
        # Extract ATS-relevant keywords
        ats_keywords = extract_ats_keywords(cv_text)
        
        model = genai.GenerativeModel('gemini-pro')
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
        if not setup_gemini():
            return None

        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""Extract personal information from this CV and return as JSON.
        Include: name, email, phone, location, linkedin, github, website (if available).
        Return ONLY valid JSON, no additional text.
        
        CV TEXT:
        {cv_text}
        """
        
        response = model.generate_content(prompt)
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
        if not setup_gemini():
            return None

        model = genai.GenerativeModel('gemini-pro')
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
        
        response = model.generate_content(prompt)
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
        if not setup_gemini():
            return None

        model = genai.GenerativeModel('gemini-pro')
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
        if not setup_gemini():
            return None

        model = genai.GenerativeModel('gemini-pro')
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
        
        response = model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Try to extract array from text
            text = response.text.strip()
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
        if not setup_gemini():
            return None

        model = genai.GenerativeModel('gemini-pro')
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
        
        response = model.generate_content(prompt)
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
        if not setup_gemini():
            return None

        model = genai.GenerativeModel('gemini-pro')
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
        
        response = model.generate_content(prompt)
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
        if not setup_gemini():
            return None

        model = genai.GenerativeModel('gemini-pro')
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


def analyze_cv_comprehensively(cv_text):
    """Perform comprehensive CV analysis including all aspects."""
    try:
        if not setup_gemini():
            return None

        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""Perform a comprehensive analysis of this CV. Return as JSON with these keys:
        - personal_info: object with extracted personal details
        - sections_present: array of sections found in CV
        - missing_sections: array of important missing sections
        - strengths: array of CV strengths
        - weaknesses: array of CV weaknesses
        - improvement_suggestions: array of specific improvement suggestions
        - ats_score: number 0-100
        - overall_rating: number 0-10
        - summary: brief overall assessment
        
        Return ONLY valid JSON, no additional text.
        
        CV TEXT:
        {cv_text}
        """
        
        response = model.generate_content(prompt)
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            logger.warning("Comprehensive analysis returned invalid JSON")
            return None
            
    except Exception as e:
        logger.exception("Error in comprehensive CV analysis: %s", e)
        return None