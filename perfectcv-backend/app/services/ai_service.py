"""
AI service for CV processing using OpenAI, Google Gemini, or Groq.
Handles fallback extraction and content improvement.
"""
import json
import logging
import os
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Try importing AI libraries
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI library not available")

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.warning("Google Generative AI library not available")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq library not available")


class AIService:
    """Service for AI-powered CV processing and enhancement."""
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 google_api_key: Optional[str] = None,
                 groq_api_key: Optional[str] = None,
                 provider: str = "openai"):
        """
        Initialize AI service with API credentials.
        
        Args:
            openai_api_key: OpenAI API key
            google_api_key: Google API key
            groq_api_key: Groq API key
            provider: AI provider to use ("openai", "google", or "groq")
        """
        self.provider = provider
        self.client = None
        
        # Initialize based on provider
        if provider == "openai" and OPENAI_AVAILABLE and openai_api_key:
            try:
                self.client = OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
        
        elif provider == "google" and GOOGLE_AVAILABLE and google_api_key:
            try:
                genai.configure(api_key=google_api_key)
                self.client = genai.GenerativeModel('gemini-pro')
                logger.info("Google Gemini client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Gemini: {e}")
        
        elif provider == "groq" and GROQ_AVAILABLE and groq_api_key:
            try:
                self.client = Groq(api_key=groq_api_key)
                logger.info("Groq client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
    
    def is_available(self) -> bool:
        """Check if AI service is available."""
        return self.client is not None
    
    def extract_missing_fields(self, text: str, missing_fields: List[str]) -> Dict:
        """
        Use AI to extract missing fields from CV text.
        IMPORTANT: AI should only extract, not hallucinate data.
        
        Args:
            text: CV text
            missing_fields: List of missing field names
            
        Returns:
            Dictionary with extracted fields
        """
        if not self.is_available():
            logger.warning("AI service not available for field extraction")
            return {}
        
        logger.info(f"Using AI to extract missing fields: {missing_fields}")
        
        prompt = self._build_extraction_prompt(text, missing_fields)
        
        try:
            response = self._call_ai(prompt, max_tokens=500, temperature=0.1)
            extracted = self._parse_json_response(response)
            
            logger.info(f"AI extracted fields: {list(extracted.keys())}")
            return extracted
            
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return {}
    
    def improve_cv_content(self, sections: Dict, job_domain: Optional[str] = None) -> Dict:
        """
        Use AI to improve CV content (summary, experience descriptions).
        IMPORTANT: AI should improve existing content, not invent new information.
        
        Args:
            sections: CV sections dictionary
            job_domain: Target job domain (optional)
            
        Returns:
            Dictionary with improved sections
        """
        if not self.is_available():
            logger.warning("AI service not available for content improvement")
            return sections
        
        logger.info(f"Using AI to improve CV content (domain: {job_domain})")
        
        improved_sections = sections.copy()
        
        # Improve summary if present
        if 'summary' in sections and sections['summary']:
            try:
                improved_summary = self._improve_summary(sections['summary'], job_domain)
                improved_sections['summary'] = improved_summary
                logger.info("Summary improved by AI")
            except Exception as e:
                logger.error(f"Failed to improve summary: {e}")
        
        # Improve experience descriptions if present
        if 'experience' in sections and sections['experience']:
            try:
                improved_experience = self._improve_experience(sections['experience'], job_domain)
                improved_sections['experience'] = improved_experience
                logger.info("Experience section improved by AI")
            except Exception as e:
                logger.error(f"Failed to improve experience: {e}")
        
        return improved_sections
    
    def _build_extraction_prompt(self, text: str, missing_fields: List[str]) -> str:
        """Build prompt for extracting missing fields - strict extraction only, no hallucination."""
        fields_desc = {
            'name': 'full name of the person (exactly as written)',
            'email': 'email address (exactly as written)',
            'phone': 'phone number (exactly as written)',
            'location': 'city and country/state (exactly as written)',
            'skills': 'list of technical skills (only those explicitly mentioned)',
        }
        
        field_descriptions = [f"- {field}: {fields_desc.get(field, field)}" 
                            for field in missing_fields]
        
        prompt = f"""CRITICAL: Extract ONLY information that is EXPLICITLY present in the CV text below.
Do NOT invent, assume, or generate any information. If a field is not clearly present, return null.

Your task is to act as a STRICT EXTRACTOR, not a generator.

Fields to extract:
{chr(10).join(field_descriptions)}

CV Text:
{text[:3000]}

RULES:
1. Return ONLY a valid JSON object
2. Use exact text from the CV - no paraphrasing
3. If a field is not found, use null
4. Do not add example data
5. Skills must be explicitly listed in the CV

Example valid response:
{{"name": "John Doe", "email": "john@example.com", "phone": null}}

JSON Response:"""
        
        return prompt
    
    def _improve_summary(self, summary: str, job_domain: Optional[str]) -> str:
        """Improve professional summary."""
        domain_context = f" for a {job_domain} position" if job_domain else ""
        
        prompt = f"""Improve this professional summary{domain_context}. 
Keep all factual information exactly as stated. Only improve the writing quality, clarity, and impact.
Do NOT add new achievements, skills, or experience that aren't mentioned.

Original Summary:
{summary}

Improved Summary:"""
        
        return self._call_ai(prompt, max_tokens=300, temperature=0.3)
    
    def _improve_experience(self, experience: str, job_domain: Optional[str]) -> str:
        """Improve experience descriptions."""
        domain_context = f" for a {job_domain} role" if job_domain else ""
        
        prompt = f"""Improve these work experience descriptions{domain_context}.
Keep all factual information (companies, dates, roles, achievements) exactly as stated.
Only improve the writing quality by:
- Using stronger action verbs
- Quantifying achievements where already mentioned
- Improving clarity and impact
Do NOT add new responsibilities or achievements that aren't mentioned.

Original Experience:
{experience[:2000]}

Improved Experience:"""
        
        return self._call_ai(prompt, max_tokens=800, temperature=0.3)
    
    def _call_ai(self, prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
        """
        Call AI provider with prompt.
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            AI response text
        """
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        
        elif self.provider == "google":
            response = self.client.generate_content(prompt)
            return response.text.strip()
        
        elif self.provider == "groq":
            # Use latest Llama model available on Groq (fast inference)
            # Alternative models: "llama-3.3-70b-versatile", "llama-3.1-8b-instant"
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    @staticmethod
    def _parse_json_response(response: str) -> Dict:
        """Parse JSON from AI response."""
        try:
            # Try to find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in AI response")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from AI response: {e}")
            logger.debug(f"Response was: {response}")
            return {}
