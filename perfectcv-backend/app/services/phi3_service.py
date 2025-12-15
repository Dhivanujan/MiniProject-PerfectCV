"""
Phi-3 Service - Local AI Engine via Ollama
Uses Microsoft Phi-3 model running locally for CV extraction and improvement.
"""

import json
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "phi3"
OLLAMA_TIMEOUT = 60  # seconds


class Phi3Service:
    """Service for interacting with Phi-3 model via Ollama"""
    
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL
        self.timeout = OLLAMA_TIMEOUT
    
    def call_phi3(self, prompt: str, temperature: float = 0.1) -> Optional[str]:
        """
        Call Phi-3 model with a prompt and return the response.
        
        Args:
            prompt: The prompt to send to the model
            temperature: Sampling temperature (lower = more deterministic)
            
        Returns:
            Model response as string, or None if error occurs
        """
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
                "options": {
                    "num_predict": 2048,  # Max tokens to generate
                }
            }
            
            logger.info(f"🤖 Calling Phi-3 model via Ollama...")
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            model_response = result.get("response", "")
            
            logger.info(f"✅ Phi-3 response received ({len(model_response)} chars)")
            return model_response.strip()
            
        except requests.exceptions.Timeout:
            logger.error(f"⏱️ Phi-3 request timed out after {self.timeout}s")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"🔌 Cannot connect to Ollama at {self.base_url}. Is Ollama running?")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Phi-3 request failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Unexpected error calling Phi-3: {str(e)}")
            return None
    
    def check_availability(self) -> bool:
        """
        Check if Ollama is running and Phi-3 model is available.
        
        Returns:
            True if available, False otherwise
        """
        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models]
            
            if self.model in model_names:
                logger.info(f"✅ Phi-3 model is available")
                return True
            else:
                logger.warning(f"⚠️ Phi-3 model not found. Available: {', '.join(model_names)}")
                return False
                
        except Exception as e:
            logger.warning(f"⚠️ Cannot check Phi-3 availability: {str(e)}")
            return False
    
    def extract_cv_data(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract CV data using Phi-3 as fallback extraction method.
        
        Args:
            text: Raw CV text content
            
        Returns:
            Extracted CV data as dictionary, or None if extraction fails
        """
        prompt = f"""You are a CV/resume data extraction expert. Extract information from the following CV text and return ONLY a valid JSON object with this exact structure:

{{
  "name": "",
  "email": "",
  "phone": "",
  "location": "",
  "skills": [],
  "experience": [
    {{
      "title": "",
      "company": "",
      "dates": "",
      "description": ""
    }}
  ],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "year": ""
    }}
  ],
  "certifications": [],
  "summary": ""
}}

CRITICAL RULES:
1. Return ONLY the JSON object, no explanations or markdown
2. Do NOT invent or hallucinate data
3. Use empty strings "" for missing text fields
4. Use empty arrays [] for missing list fields
5. Extract only what is explicitly stated in the CV
6. For experience and education, only include entries that have clear information

CV TEXT:
{text}

JSON OUTPUT:"""

        try:
            logger.info("🔍 Using Phi-3 for CV data extraction (fallback mode)")
            response = self.call_phi3(prompt, temperature=0.1)
            
            if not response:
                logger.error("❌ Phi-3 returned no response for extraction")
                return None
            
            # Extract JSON from response (handle markdown code blocks)
            json_str = self._extract_json_from_response(response)
            
            # Parse JSON
            data = json.loads(json_str)
            logger.info(f"✅ Phi-3 extraction successful: {list(data.keys())}")
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Phi-3 JSON response: {str(e)}")
            logger.debug(f"Raw response: {response[:500]}")
            return None
        except Exception as e:
            logger.error(f"❌ Phi-3 extraction failed: {str(e)}")
            return None
    
    def improve_cv_content(self, cv_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Improve CV content using Phi-3 (rewrite summary, enhance descriptions).
        
        Args:
            cv_data: Existing CV data dictionary
            
        Returns:
            Improved CV data dictionary, or None if improvement fails
        """
        prompt = f"""You are a professional CV writing expert. Improve the following CV content by:

1. Rewriting the summary to be more professional and impactful
2. Enhancing job descriptions to use stronger action verbs and quantifiable achievements
3. Improving the language while keeping ALL factual information unchanged

CRITICAL RULES:
- Do NOT change names, companies, job titles, dates, schools, or degrees
- Do NOT invent new jobs, education, or skills
- Do NOT add information that wasn't in the original
- Only improve the LANGUAGE and PRESENTATION of existing content
- Return ONLY a valid JSON object with the same structure as input

INPUT CV DATA:
{json.dumps(cv_data, indent=2)}

Return the improved CV as a JSON object:"""

        try:
            logger.info("✨ Using Phi-3 for CV content improvement")
            response = self.call_phi3(prompt, temperature=0.3)
            
            if not response:
                logger.error("❌ Phi-3 returned no response for improvement")
                return None
            
            # Extract JSON from response
            json_str = self._extract_json_from_response(response)
            
            # Parse JSON
            improved_data = json.loads(json_str)
            logger.info(f"✅ Phi-3 improvement successful")
            
            # Validate that critical fields weren't changed
            if not self._validate_factual_integrity(cv_data, improved_data):
                logger.warning("⚠️ Phi-3 changed factual data, returning original")
                return cv_data
            
            return improved_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Phi-3 JSON response: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Phi-3 improvement failed: {str(e)}")
            return None
    
    def _extract_json_from_response(self, response: str) -> str:
        """
        Extract JSON string from model response (handles markdown code blocks).
        
        Args:
            response: Raw model response
            
        Returns:
            Cleaned JSON string
        """
        # Remove markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1]
            response = response.split("```")[0]
        elif "```" in response:
            response = response.split("```")[1]
            response = response.split("```")[0]
        
        # Find JSON object boundaries
        start = response.find("{")
        end = response.rfind("}") + 1
        
        if start >= 0 and end > start:
            return response[start:end].strip()
        
        return response.strip()
    
    def _validate_factual_integrity(self, original: Dict[str, Any], improved: Dict[str, Any]) -> bool:
        """
        Validate that critical factual information wasn't changed during improvement.
        
        Args:
            original: Original CV data
            improved: Improved CV data
            
        Returns:
            True if factual integrity maintained, False otherwise
        """
        try:
            # Check name (allow minor variations in formatting)
            if original.get("name") and improved.get("name"):
                orig_name = original["name"].lower().replace(".", "").replace(",", "")
                impr_name = improved["name"].lower().replace(".", "").replace(",", "")
                if orig_name != impr_name:
                    logger.warning(f"⚠️ Name changed: {original['name']} → {improved['name']}")
                    return False
            
            # Check number of experience entries
            orig_exp_count = len(original.get("experience", []))
            impr_exp_count = len(improved.get("experience", []))
            if orig_exp_count != impr_exp_count:
                logger.warning(f"⚠️ Experience count changed: {orig_exp_count} → {impr_exp_count}")
                return False
            
            # Check number of education entries
            orig_edu_count = len(original.get("education", []))
            impr_edu_count = len(improved.get("education", []))
            if orig_edu_count != impr_edu_count:
                logger.warning(f"⚠️ Education count changed: {orig_edu_count} → {impr_edu_count}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Validation error: {str(e)}")
            return False


# Singleton instance
_phi3_service = None

def get_phi3_service() -> Phi3Service:
    """Get singleton instance of Phi3Service"""
    global _phi3_service
    if _phi3_service is None:
        _phi3_service = Phi3Service()
    return _phi3_service
