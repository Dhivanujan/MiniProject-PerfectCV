"""
Advanced AI-powered CV parsing using OpenAI GPT-4, Groq, and other AI services.
This module provides intelligent extraction and structuring of CV data.
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional, Any
from config.config import Config

logger = logging.getLogger(__name__)

# Try to import OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not installed. Install with: pip install openai")

# Try to import Groq (ultra-fast inference)
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq library not installed. Install with: pip install groq")

# Try to import pytesseract for OCR
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR libraries not installed. Install with: pip install pytesseract pillow pdf2image")


class AICVParser:
    """Advanced CV parser using AI models (Groq, OpenAI GPT-4, etc.) for intelligent extraction."""
    
    def __init__(self, openai_api_key: Optional[str] = None, groq_api_key: Optional[str] = None):
        """Initialize AI CV parser with API credentials."""
        self.openai_api_key = openai_api_key or getattr(Config, "OPENAI_API_KEY", None)
        self.groq_api_key = groq_api_key or getattr(Config, "GROQ_API_KEY", None)
        self.openai_client = None
        self.groq_client = None
        
        # Initialize Groq client (prioritized for speed and free tier)
        if GROQ_AVAILABLE and self.groq_api_key:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        
        # Initialize OpenAI client as fallback
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def is_available(self) -> bool:
        """Check if AI parsing is available (either Groq or OpenAI)."""
        return self.groq_client is not None or self.openai_client is not None
    
    def extract_structured_cv_data(self, cv_text: str, use_ai: bool = True) -> Dict[str, Any]:
        """
        Extract structured data from CV text using AI.
        
        Args:
            cv_text: Raw text extracted from CV
            use_ai: Whether to use AI for parsing (falls back to rule-based if False)
            
        Returns:
            Dictionary with structured CV data
        """
        if not cv_text or not cv_text.strip():
            return self._get_empty_cv_structure()
        
        if use_ai and self.is_available():
            try:
                return self._ai_extract(cv_text)
            except Exception as e:
                logger.error(f"AI extraction failed, falling back to rule-based: {e}")
                return self._get_empty_cv_structure()
        else:
            logger.info("AI not available or disabled, using rule-based extraction")
            return self._get_empty_cv_structure()
    
    def _preprocess_cv_text(self, cv_text: str) -> str:
        """Preprocess CV text to improve extraction accuracy."""
        # Remove excessive whitespace and newlines
        text = re.sub(r'\n{3,}', '\n\n', cv_text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'\f', ' ', text)  # Form feed
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\xff]', '', text)  # Control chars
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    def _ai_extract(self, cv_text: str) -> Dict[str, Any]:
        """Use AI (Groq or OpenAI GPT-4) to intelligently extract CV data."""
        
        # Preprocess text for better parsing
        cv_text = self._preprocess_cv_text(cv_text)
        
        system_prompt = """You are an expert CV/Resume parser with deep understanding of document structure. Extract ONLY the actual information present in the CV text with high accuracy.

CRITICAL EXTRACTION RULES:
1. NEVER generate placeholder text like "Your Name", "Company", "Position", "Institution", "Degree", "Certification Name"
2. ONLY extract information that is explicitly stated - DO NOT INFER OR GUESS
3. Use empty strings or arrays if information is not found
4. Preserve exact formatting from CV (dates, numbers, titles)
5. For skills, extract ONLY actual skills - ignore headers like "SKILLS:", "COURSE", "Technical Skills:"
6. Distinguish between job title and company name carefully - they are NOT interchangeable
7. For contact info, extract from header/footer sections first (usually at top of CV)
8. Parse email, phone, LinkedIn, GitHub URLs accurately using patterns
9. Handle multi-line addresses and locations properly
10. For experience: title=job role, company=employer name, NOT the reverse
11. Extract dates in their original format (e.g., "Jan 2020 - Present", "2018-2020")
12. For education: degree name first, then institution, then year
13. Skills should be individual items, not sentences
14. Separate technical skills from soft skills
15. Look for name in the first few lines of the CV (usually header)

Return a JSON object with this exact structure:

{
    "contact_information": {
        "name": "Actual full name from CV or empty string",
        "email": "Actual email or empty string",
        "phone": "Actual phone number or empty string",
        "location": "Actual location or empty string",
        "linkedin": "Actual LinkedIn URL or empty string",
        "github": "Actual GitHub URL or empty string",
        "website": "Actual website or empty string",
        "address": "Actual address or empty string"
    },
    "professional_summary": "Actual summary/objective text or empty string",
    "skills": {
        "technical": ["Only actual technical skills"],
        "soft": ["Only actual soft skills"],
        "tools": ["Only actual tools"],
        "frameworks": ["Only actual frameworks"],
        "languages_programming": ["Only actual programming languages"]
    },
    "work_experience": [
        {
            "title": "Actual job title (NOT 'Position' or 'Job Title')",
            "company": "Actual company name (NOT 'Company' or 'Company Name')",
            "location": "Actual location or empty string",
            "dates": "Actual date range from CV",
            "start_date": "Start date or empty string",
            "end_date": "End date or 'Present'",
            "is_current": true/false,
            "description": "Actual role description or empty string",
            "achievements": ["Only actual achievements listed"],
            "technologies": ["Only actual technologies mentioned"]
        }
    ],
    "education": [
        {
            "degree": "Actual degree name (NOT 'Degree Name')",
            "field": "Actual field of study or empty string",
            "institution": "Actual university/school name (NOT 'Institution' or 'University Name')",
            "location": "Actual location or empty string",
            "graduation_date": "Actual graduation year or empty string",
            "gpa": "Actual GPA if mentioned or empty string",
            "honors": "Actual honors if mentioned or empty string"
        }
    ],
    "projects": [
        {
            "name": "Actual project name",
            "description": "Actual project description",
            "technologies": ["Only actual technologies used"],
            "url": "Actual URL or empty string",
            "highlights": ["Only actual highlights"]
        }
    ],
    "certifications": [
        {
            "name": "Actual certification name (NOT 'Certification Name')",
            "issuer": "Actual issuing organization or empty string",
            "date": "Actual certification date or empty string",
            "credential_id": "Actual ID or empty string",
            "url": "Actual URL or empty string"
        }
    ],
    "languages": [
        {
            "language": "Actual language name",
            "proficiency": "Actual proficiency level"
        }
    ],
    "achievements": ["Only actual achievements/awards"],
    "volunteer_experience": [
        {
            "role": "Actual volunteer role",
            "organization": "Actual organization name",
            "dates": "Actual dates",
            "description": "Actual description"
        }
    ],
    "publications": [
        {
            "title": "Actual publication title",
            "venue": "Actual conference/journal name",
            "date": "Actual publication date",
            "url": "Actual URL or empty string"
        }
    ],
    "interests": ["Only actual interests listed"]
}

Remember: Extract ONLY what is actually in the CV. Empty values are better than placeholders."""

        # Add extraction hints based on text content
        hints = []
        if '@' in cv_text:
            hints.append("Email found in CV")
        if 'linkedin.com' in cv_text.lower():
            hints.append("LinkedIn URL present")
        if 'github.com' in cv_text.lower():
            hints.append("GitHub URL present")
        
        hints_text = " | ".join(hints) if hints else "No obvious markers"
        
        user_prompt = f"""Parse this CV and extract ONLY the actual information present (no placeholders, no guesses).

Extraction hints: {hints_text}

IMPORTANT:
- The person's name is usually in the FIRST LINE or at the very top
- Look for email address pattern (someone@example.com)
- Phone numbers have digits and may include country codes
- Extract skills as individual items from sections labeled "Skills", "Technical Skills", "Core Competencies", etc.

CV TEXT:
{cv_text}"""
        
        try:
            # Try Groq first (faster and often free)
            if self.groq_client:
                try:
                    logger.info("Using Groq for CV parsing (ultra-fast)")
                    response = self.groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",  # Updated: was llama-3.1-70b-versatile (deprecated)
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.1,
                        response_format={"type": "json_object"}
                    )
                    
                    result = json.loads(response.choices[0].message.content)
                    logger.info("Successfully parsed CV with Groq")
                    # Validate and clean the extracted data
                    return self._validate_and_clean_data(result)
                except Exception as e:
                    logger.warning(f"Groq extraction failed, trying OpenAI: {e}")
            
            # Fallback to OpenAI if Groq fails or unavailable
            if self.openai_client:
                logger.info("Using OpenAI GPT-4 for CV parsing")
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                logger.info("Successfully parsed CV with OpenAI")
                # Validate and clean the extracted data
                return self._validate_and_clean_data(result)
            
            raise Exception("No AI client available")
            
        except Exception as e:
            logger.error(f"AI extraction error: {e}")
            raise
    
    def enhance_experience_bullets(self, bullets: List[str], job_title: str = "") -> List[str]:
        """Use AI to enhance and strengthen experience bullet points."""
        if not self.is_available() or not bullets:
            return bullets
        
        try:
            bullets_text = "\n".join(f"- {b}" for b in bullets)
            
            prompt = f"""Improve these resume bullet points to be more impactful and ATS-friendly.
Use action verbs, quantify achievements where possible, and make them concise.
Job Title: {job_title or 'Not specified'}

Original bullets:
{bullets_text}

Return improved bullets in the same format (one per line with - prefix)."""

            # Use the appropriate client
            client = self.groq_client or self.openai_client
            model = "llama-3.3-70b-versatile" if self.groq_client else "gpt-4-turbo-preview"
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer. Improve bullet points to be impactful and ATS-friendly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            enhanced_text = response.choices[0].message.content.strip()
            enhanced_bullets = [
                line.strip().lstrip('- •*').strip() 
                for line in enhanced_text.split('\n') 
                if line.strip() and not line.strip().startswith('#')
            ]
            
            return enhanced_bullets if enhanced_bullets else bullets
            
        except Exception as e:
            logger.error(f"Failed to enhance bullets: {e}")
            return bullets
    
    def categorize_skills_ai(self, skills: List[str]) -> Dict[str, List[str]]:
        """Use AI to intelligently categorize skills."""
        if not self.is_available() or not skills:
            return {"technical": skills, "soft": [], "tools": [], "frameworks": [], "other": []}
        
        try:
            skills_text = ", ".join(skills)
            
            prompt = f"""Categorize these skills into: technical (programming languages, technologies), soft (communication, leadership), tools (software/applications), frameworks (React, Django, etc), and other.

Skills: {skills_text}

Return JSON with structure: {{"technical": [], "soft": [], "tools": [], "frameworks": [], "other": []}}"""

            client = self.groq_client or self.openai_client
            model = "llama-3.3-70b-versatile" if self.groq_client else "gpt-4-turbo-preview"
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a skill categorization expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            categorized = json.loads(response.choices[0].message.content)
            return categorized
            
        except Exception as e:
            logger.error(f"Failed to categorize skills: {e}")
            return {"technical": skills, "soft": [], "tools": [], "frameworks": [], "other": []}
    
    def suggest_missing_skills(self, current_skills: List[str], job_title: str = "", industry: str = "") -> List[str]:
        """Suggest relevant skills that might be missing based on role and industry."""
        if not self.is_available():
            return []
        
        try:
            context = f"Job Title: {job_title}, Industry: {industry}" if job_title or industry else "General"
            skills_text = ", ".join(current_skills)
            
            prompt = f"""Based on this person's current skills and role, suggest 5-10 relevant skills they might want to add to their resume.
{context}
Current skills: {skills_text}

Return only a JSON array of skill names: ["Skill1", "Skill2", ...]"""

            client = self.groq_client or self.openai_client
            model = "llama-3.3-70b-versatile" if self.groq_client else "gpt-4-turbo-preview"
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a career development expert. Suggest relevant skills."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            # Handle both array and object responses
            suggestions = result if isinstance(result, list) else result.get('skills', [])
            return suggestions[:10]  # Limit to 10 suggestions
            
        except Exception as e:
            logger.error(f"Failed to suggest skills: {e}")
            return []
    
    def extract_with_ocr(self, pdf_path: str) -> str:
        """Extract text from scanned PDF using OCR."""
        if not OCR_AVAILABLE:
            logger.warning("OCR not available. Install: pip install pytesseract pillow pdf2image")
            return ""
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path)
            
            # Extract text from each page
            text_parts = []
            for i, image in enumerate(images):
                logger.info(f"Performing OCR on page {i+1}/{len(images)}")
                text = pytesseract.image_to_string(image, lang='eng')
                text_parts.append(text)
            
            full_text = "\n\n".join(text_parts)
            logger.info(f"OCR extraction complete: {len(full_text)} characters")
            return full_text
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    def generate_professional_summary(self, cv_data: Dict[str, Any]) -> str:
        """Generate a compelling professional summary from CV data."""
        if not self.is_available():
            return ""
        
        try:
            # Extract key info
            experience = cv_data.get('work_experience', [])
            skills = cv_data.get('skills', {})
            education = cv_data.get('education', [])
            
            years_exp = len(experience)
            latest_role = experience[0].get('title', '') if experience else ''
            top_skills = skills.get('technical', [])[:5] if isinstance(skills, dict) else []
            
            prompt = f"""Write a compelling 2-3 sentence professional summary for a resume.
            
Context:
- Years of experience: {years_exp}+
- Latest role: {latest_role}
- Top skills: {', '.join(top_skills)}
- Education: {education[0].get('degree', '') if education else ''}

Make it impactful and professional."""

            client = self.groq_client or self.openai_client
            model = "llama-3.3-70b-versatile" if self.groq_client else "gpt-4-turbo-preview"
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert resume writer. Write concise, impactful professional summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return ""
    
    def _validate_and_clean_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted CV data to remove placeholders and ensure quality."""
        # Placeholder patterns to filter out
        placeholder_patterns = [
            "your name", "name", "full name", "[name]", "candidate name",
            "your email", "email", "[email]", "email@example.com",
            "your phone", "phone", "[phone]", "123-456-7890",
            "company", "company name", "[company]", "employer",
            "position", "job title", "[position]", "role", "title",
            "degree", "degree name", "[degree]", "certification",
            "institution", "university", "school name", "[institution]",
            "your location", "city, state", "location", "[location]",
            "skill", "skills", "course", "technology", "tool",
            "n/a", "tbd", "null", "none", "not specified"
        ]
        
        def is_placeholder(value: str) -> bool:
            """Check if a value is a placeholder."""
            if not value or not isinstance(value, str):
                return True
            value_lower = value.lower().strip()
            return (value_lower in placeholder_patterns or 
                    len(value) < 2 or 
                    value.strip() in ["—", "-", "*", "•", "[]", "()", "{}"])
        
        # Clean contact information
        if "contact_information" in data and isinstance(data["contact_information"], dict):
            contact = data["contact_information"]
            
            # Validate name (must have at least first and last name)
            if "name" in contact:
                name = contact.get("name", "").strip()
                logger.info(f"🔍 Validating name: '{name}' (has space: {' ' in name}, is_placeholder: {is_placeholder(name)})")
                # Allow single-word names (international names) - just check it's not a placeholder
                if is_placeholder(name):
                    logger.warning(f"⚠ Name '{name}' detected as placeholder, clearing")
                    contact["name"] = ""
                else:
                    logger.info(f"✓ Name '{name}' passed validation")
            
            # Validate email
            if "email" in contact:
                email = contact.get("email", "").strip()
                if is_placeholder(email) or "@" not in email or "." not in email:
                    contact["email"] = ""
            
            # Validate phone
            if "phone" in contact:
                phone = contact.get("phone", "").strip()
                if is_placeholder(phone) or not any(c.isdigit() for c in phone):
                    contact["phone"] = ""
        
        # Clean skills
        if "skills" in data and isinstance(data["skills"], dict):
            for skill_type in ["technical", "soft", "tools", "frameworks", "languages_programming"]:
                if skill_type in data["skills"] and isinstance(data["skills"][skill_type], list):
                    data["skills"][skill_type] = [
                        s for s in data["skills"][skill_type]
                        if s and not is_placeholder(str(s)) and len(str(s)) > 1 and len(str(s)) < 50
                    ]
        
        # Clean work experience
        if "work_experience" in data and isinstance(data["work_experience"], list):
            cleaned_exp = []
            for exp in data["work_experience"]:
                if not isinstance(exp, dict):
                    continue
                
                title = exp.get("title", "").strip()
                company = exp.get("company", "").strip()
                
                # Skip if title or company are placeholders
                if is_placeholder(title):
                    title = ""
                if is_placeholder(company):
                    company = ""
                
                # Only keep if we have at least title OR company
                if title or company:
                    exp["title"] = title
                    exp["company"] = company
                    cleaned_exp.append(exp)
            
            data["work_experience"] = cleaned_exp
        
        # Clean education
        if "education" in data and isinstance(data["education"], list):
            cleaned_edu = []
            for edu in data["education"]:
                if not isinstance(edu, dict):
                    continue
                
                degree = edu.get("degree", "").strip()
                institution = edu.get("institution", "").strip()
                
                # Skip if both are placeholders
                if is_placeholder(degree):
                    degree = ""
                if is_placeholder(institution):
                    institution = ""
                
                # Only keep if we have at least degree OR institution
                if degree or institution:
                    edu["degree"] = degree
                    edu["institution"] = institution
                    cleaned_edu.append(edu)
            
            data["education"] = cleaned_edu
        
        # Clean certifications
        if "certifications" in data and isinstance(data["certifications"], list):
            data["certifications"] = [
                cert for cert in data["certifications"]
                if isinstance(cert, dict) and not is_placeholder(cert.get("name", ""))
            ]
        
        # Clean projects
        if "projects" in data and isinstance(data["projects"], list):
            data["projects"] = [
                proj for proj in data["projects"]
                if isinstance(proj, dict) and not is_placeholder(proj.get("name", ""))
            ]
        
        # Clean achievements (simple list)
        if "achievements" in data and isinstance(data["achievements"], list):
            data["achievements"] = [
                ach for ach in data["achievements"]
                if ach and not is_placeholder(str(ach)) and len(str(ach)) > 10
            ]
        
        logger.info(f"Data validation complete - Name: {data.get('contact_information', {}).get('name', 'EMPTY')}, "
                   f"Skills: {sum(len(v) for v in data.get('skills', {}).values() if isinstance(v, list))}, "
                   f"Experience: {len(data.get('work_experience', []))}")
        
        return data
    
    def _get_empty_cv_structure(self) -> Dict[str, Any]:
        """Return empty CV structure."""
        return {
            "contact_information": {
                "name": "",
                "email": "",
                "phone": "",
                "location": "",
                "linkedin": "",
                "github": "",
                "website": "",
                "address": ""
            },
            "professional_summary": "",
            "skills": {
                "technical": [],
                "soft": [],
                "tools": [],
                "frameworks": [],
                "languages_programming": []
            },
            "work_experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "languages": [],
            "achievements": [],
            "volunteer_experience": [],
            "publications": [],
            "interests": []
        }


def get_ai_parser() -> AICVParser:
    """Factory function to create AI CV parser instance."""
    return AICVParser()


# Convenience functions for easy use
def ai_parse_cv(cv_text: str, use_ai: bool = True) -> Dict[str, Any]:
    """Parse CV text with AI. Convenience wrapper."""
    parser = get_ai_parser()
    return parser.extract_structured_cv_data(cv_text, use_ai=use_ai)


def ai_enhance_bullets(bullets: List[str], job_title: str = "") -> List[str]:
    """Enhance bullet points with AI. Convenience wrapper."""
    parser = get_ai_parser()
    return parser.enhance_experience_bullets(bullets, job_title)


def ai_categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    """Categorize skills with AI. Convenience wrapper."""
    parser = get_ai_parser()
    return parser.categorize_skills_ai(skills)
