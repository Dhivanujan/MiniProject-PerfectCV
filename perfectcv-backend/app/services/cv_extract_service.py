"""
CV Extraction Service
Extracts structured data from raw CV text using regex + AI fallback.
"""
import re
import logging
from typing import Dict, Any, Optional
from app.utils.extractor import extract_text_from_pdf
from app.utils.cleaner import clean_full_text, normalize_whitespace

logger = logging.getLogger(__name__)


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(email_pattern, text)
    return matches[0] if matches else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text."""
    # Match various phone formats
    phone_patterns = [
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US/International
        r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890
        r'\d{10}',  # 1234567890
        r'\+\d{10,15}',  # +12345678901
    ]
    
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0].strip()
    return None


def extract_skills_basic(text: str) -> list:
    """Extract skills using basic pattern matching."""
    skills = []
    
    # Common skill keywords
    common_skills = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 'rust',
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'fastapi',
        'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
        'git', 'agile', 'scrum', 'jira', 'ci/cd', 'jenkins',
        'machine learning', 'deep learning', 'nlp', 'data science',
        'html', 'css', 'sass', 'tailwind', 'bootstrap',
        'rest api', 'graphql', 'microservices', 'testing', 'tdd'
    ]
    
    text_lower = text.lower()
    for skill in common_skills:
        if skill in text_lower:
            skills.append(skill.title())
    
    return list(set(skills))  # Remove duplicates


def extract_cv_data(file_path: str, ai_client=None) -> Dict[str, Any]:
    """
    Extract structured CV data from a PDF or DOCX file.
    
    Args:
        file_path: Path to the CV file
        ai_client: Groq/OpenAI client for AI-powered extraction
        
    Returns:
        Dictionary with structured CV data
    """
    try:
        # Step 1: Extract raw text
        logger.info(f"Extracting text from {file_path}")
        
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as f:
                raw_text = extract_text_from_pdf(f)
        elif file_path.lower().endswith('.docx'):
            from docx import Document
            doc = Document(file_path)
            raw_text = '\n'.join([para.text for para in doc.paragraphs])
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
        
        # Step 2: Clean text
        logger.info("Cleaning extracted text")
        cleaned_text = clean_full_text(raw_text)
        cleaned_text = normalize_whitespace(cleaned_text)
        
        # Step 3: Extract basic info with regex
        email = extract_email(cleaned_text)
        phone = extract_phone(cleaned_text)
        basic_skills = extract_skills_basic(cleaned_text)
        
        # Step 4: Use AI to extract full structured data
        if ai_client:
            logger.info("Using AI to extract structured CV data")
            cv_data = _extract_with_ai(cleaned_text, ai_client)
            
            # Override with regex-extracted values if AI missed them
            if email and not cv_data.get('email'):
                cv_data['email'] = email
            if phone and not cv_data.get('phone'):
                cv_data['phone'] = phone
            if basic_skills and not cv_data.get('skills'):
                cv_data['skills'] = basic_skills
                
            return cv_data
        else:
            # Fallback: Return basic extracted data
            logger.warning("No AI client provided, returning basic extraction")
            return {
                'name': '',
                'email': email or '',
                'phone': phone or '',
                'summary': '',
                'skills': basic_skills,
                'experience': [],
                'education': [],
                'projects': [],
                'certifications': [],
                'raw_text': cleaned_text[:500]  # First 500 chars for reference
            }
            
    except Exception as e:
        logger.error(f"Error extracting CV data: {e}", exc_info=True)
        raise


def _extract_with_ai(text: str, ai_client) -> Dict[str, Any]:
    """
    Use AI model to extract structured data from CV text.
    """
    prompt = f"""Extract the following information from this CV/Resume text and return ONLY valid JSON.

DO NOT add any imaginary information. Only extract what is explicitly stated in the text.

Required JSON structure:
{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number",
  "summary": "Professional summary or objective",
  "skills": ["skill1", "skill2", "skill3"],
  "experience": [
    {{
      "role": "Job Title",
      "company": "Company Name",
      "years": "Start Date - End Date",
      "description": "Job responsibilities and achievements"
    }}
  ],
  "education": [
    {{
      "degree": "Degree Name",
      "institution": "University Name",
      "year": "Graduation Year",
      "details": "Additional details"
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Project description",
      "technologies": ["tech1", "tech2"]
    }}
  ],
  "certifications": ["Certification 1", "Certification 2"]
}}

CV Text:
{text[:4000]}

Return ONLY the JSON object, no additional text."""

    try:
        # Handle both Groq and OpenAI clients
        if hasattr(ai_client, 'chat'):
            # Groq client
            response = ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a CV parsing expert. Extract information accurately and return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            result = response.choices[0].message.content
        else:
            # OpenAI client
            response = ai_client.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a CV parsing expert. Extract information accurately and return only JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            result = response.choices[0].message.content
        
        # Parse JSON response
        import json
        # Remove markdown code blocks if present
        result = result.strip()
        if result.startswith('```json'):
            result = result[7:]
        if result.startswith('```'):
            result = result[3:]
        if result.endswith('```'):
            result = result[:-3]
        result = result.strip()
        
        cv_data = json.loads(result)
        logger.info("Successfully extracted CV data with AI")
        return cv_data
        
    except Exception as e:
        logger.error(f"AI extraction failed: {e}", exc_info=True)
        # Return minimal structure
        return {
            'name': '',
            'email': '',
            'phone': '',
            'summary': '',
            'skills': [],
            'experience': [],
            'education': [],
            'projects': [],
            'certifications': []
        }
