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