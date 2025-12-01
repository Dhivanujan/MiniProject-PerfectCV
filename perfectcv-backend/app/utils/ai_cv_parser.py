"""
Advanced AI-powered CV parsing using OpenAI GPT-4 and other AI services.
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
    """Advanced CV parser using OpenAI GPT-4 for intelligent extraction."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize AI CV parser with API credentials."""
        self.openai_api_key = openai_api_key or getattr(Config, "OPENAI_API_KEY", None)
        self.client = None
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def is_available(self) -> bool:
        """Check if AI parsing is available."""
        return self.client is not None
    
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
    
    def _ai_extract(self, cv_text: str) -> Dict[str, Any]:
        """Use OpenAI GPT-4 to intelligently extract CV data."""
        
        system_prompt = """You are an expert CV/Resume parser. Extract structured information from the provided CV text.
Return a JSON object with the following structure (all fields are required, use empty arrays/strings if data not found):

{
    "contact_information": {
        "name": "Full Name",
        "email": "email@example.com",
        "phone": "phone number",
        "location": "City, Country",
        "linkedin": "LinkedIn URL",
        "github": "GitHub URL",
        "website": "Personal website",
        "address": "Full address if available"
    },
    "professional_summary": "Brief professional summary or objective",
    "skills": {
        "technical": ["Python", "Java", "Docker"],
        "soft": ["Leadership", "Communication"],
        "tools": ["VS Code", "Git", "Jira"],
        "frameworks": ["React", "Django"],
        "languages_programming": ["Python", "JavaScript"]
    },
    "work_experience": [
        {
            "title": "Job Title",
            "company": "Company Name",
            "location": "City, Country",
            "dates": "Jan 2020 - Present",
            "start_date": "2020-01",
            "end_date": "Present",
            "is_current": true,
            "description": "Role description",
            "achievements": [
                "Achievement 1",
                "Achievement 2"
            ],
            "technologies": ["Tech1", "Tech2"]
        }
    ],
    "education": [
        {
            "degree": "Degree Name",
            "field": "Field of Study",
            "institution": "University Name",
            "location": "City, Country",
            "graduation_date": "2020",
            "gpa": "3.8/4.0",
            "honors": "Cum Laude"
        }
    ],
    "projects": [
        {
            "name": "Project Name",
            "description": "Project description",
            "technologies": ["Tech1", "Tech2"],
            "url": "Project URL if available",
            "highlights": ["Highlight 1", "Highlight 2"]
        }
    ],
    "certifications": [
        {
            "name": "Certification Name",
            "issuer": "Issuing Organization",
            "date": "2020",
            "credential_id": "ID if available",
            "url": "Verification URL"
        }
    ],
    "languages": [
        {
            "language": "English",
            "proficiency": "Native/Fluent/Professional/Basic"
        }
    ],
    "achievements": [
        "Achievement or award description"
    ],
    "volunteer_experience": [
        {
            "role": "Volunteer Role",
            "organization": "Organization Name",
            "dates": "2020 - 2021",
            "description": "What you did"
        }
    ],
    "publications": [
        {
            "title": "Publication Title",
            "venue": "Conference/Journal Name",
            "date": "2020",
            "url": "URL if available"
        }
    ],
    "interests": ["Interest 1", "Interest 2"]
}

Be thorough and accurate. Extract all information present in the CV."""

        user_prompt = f"Parse this CV and extract all information:\n\n{cv_text}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Successfully parsed CV with AI")
            return result
            
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

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
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

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
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

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
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

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
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
