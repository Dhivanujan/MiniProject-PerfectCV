"""
CV AI Enhancement Service
Improves CV content using AI models for ATS optimization.
"""
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def improve_cv_data(cv_json: Dict[str, Any], ai_client) -> Dict[str, Any]:
    """
    Improve and optimize CV data for ATS using AI.
    
    Args:
        cv_json: Structured CV data dictionary
        ai_client: Groq/OpenAI client for AI enhancement
        
    Returns:
        Enhanced CV data dictionary
    """
    try:
        logger.info("Starting CV enhancement with AI")
        
        prompt = f"""You are a professional CV writer and ATS optimization expert.

Improve this CV for ATS (Applicant Tracking System) optimization while maintaining factual accuracy.

RULES:
1. DO NOT invent jobs, companies, or qualifications
2. Rewrite the summary to be more professional and impactful
3. Expand experience descriptions with action verbs and quantifiable achievements
4. Add relevant ATS keywords naturally based on existing information
5. Improve formatting and clarity
6. Keep all factual information intact
7. Return ONLY valid JSON in the same structure

Current CV Data:
{json.dumps(cv_json, indent=2)}

Return the improved CV as JSON with this exact structure:
{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number",
  "summary": "Enhanced professional summary with impact statements",
  "skills": ["optimized skill list with ATS keywords"],
  "experience": [
    {{
      "role": "Job Title",
      "company": "Company Name",
      "years": "Start Date - End Date",
      "description": "Enhanced description with action verbs, quantifiable results, and ATS keywords"
    }}
  ],
  "education": [
    {{
      "degree": "Degree Name",
      "institution": "University Name",
      "year": "Graduation Year",
      "details": "Enhanced details"
    }}
  ],
  "projects": [
    {{
      "name": "Project Name",
      "description": "Enhanced project description with impact and technologies",
      "technologies": ["tech1", "tech2"]
    }}
  ],
  "certifications": ["Certification 1", "Certification 2"]
}}

Return ONLY the JSON, no additional text or explanations."""

        # Call AI model
        if hasattr(ai_client, 'chat'):
            # Groq client
            response = ai_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional CV writer specializing in ATS optimization. Improve CVs while maintaining factual accuracy. Return only JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Slightly higher for creative improvements
                max_tokens=3000
            )
            result = response.choices[0].message.content
        else:
            # OpenAI client
            response = ai_client.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional CV writer specializing in ATS optimization. Improve CVs while maintaining factual accuracy. Return only JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            result = response.choices[0].message.content
        
        # Parse and validate response
        result = result.strip()
        if result.startswith('```json'):
            result = result[7:]
        if result.startswith('```'):
            result = result[3:]
        if result.endswith('```'):
            result = result[:-3]
        result = result.strip()
        
        improved_cv = json.loads(result)
        
        # Ensure all required fields exist
        required_fields = ['name', 'email', 'phone', 'summary', 'skills', 'experience', 'education']
        for field in required_fields:
            if field not in improved_cv:
                improved_cv[field] = cv_json.get(field, '' if field not in ['skills', 'experience', 'education'] else [])
        
        logger.info("Successfully improved CV data with AI")
        return improved_cv
        
    except Exception as e:
        logger.error(f"CV improvement failed: {e}", exc_info=True)
        logger.warning("Returning original CV data due to improvement failure")
        return cv_json


def generate_ats_keywords(cv_json: Dict[str, Any], job_description: str = None) -> list:
    """
    Generate ATS-optimized keywords based on CV content and optional job description.
    
    Args:
        cv_json: Structured CV data
        job_description: Optional job description to tailor keywords
        
    Returns:
        List of ATS keywords
    """
    keywords = set()
    
    # Extract from skills
    if 'skills' in cv_json:
        keywords.update([s.lower() for s in cv_json['skills']])
    
    # Extract from experience
    if 'experience' in cv_json:
        for exp in cv_json['experience']:
            if 'role' in exp:
                keywords.add(exp['role'].lower())
    
    # Common ATS keywords by category
    general_keywords = {
        'team leadership', 'project management', 'collaboration', 'communication',
        'problem-solving', 'analytical', 'strategic planning', 'stakeholder management'
    }
    
    keywords.update(general_keywords)
    
    return sorted(list(keywords))


def score_ats_compatibility(cv_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Score the CV for ATS compatibility.
    
    Returns:
        Dictionary with score and suggestions
    """
    score = 0
    max_score = 100
    suggestions = []
    
    # Check for essential fields (40 points)
    if cv_json.get('name'):
        score += 10
    else:
        suggestions.append("Add full name")
    
    if cv_json.get('email'):
        score += 10
    else:
        suggestions.append("Add email address")
    
    if cv_json.get('phone'):
        score += 10
    else:
        suggestions.append("Add phone number")
    
    if cv_json.get('summary'):
        score += 10
    else:
        suggestions.append("Add professional summary")
    
    # Check for skills (20 points)
    skills = cv_json.get('skills', [])
    if len(skills) >= 10:
        score += 20
    elif len(skills) >= 5:
        score += 10
        suggestions.append("Add more skills (aim for 10+)")
    else:
        suggestions.append("Add technical and soft skills")
    
    # Check for experience (20 points)
    experience = cv_json.get('experience', [])
    if len(experience) >= 3:
        score += 20
    elif len(experience) >= 1:
        score += 10
        suggestions.append("Add more work experience entries")
    else:
        suggestions.append("Add work experience")
    
    # Check for education (10 points)
    education = cv_json.get('education', [])
    if len(education) >= 1:
        score += 10
    else:
        suggestions.append("Add education details")
    
    # Check for quantifiable achievements (10 points)
    has_numbers = False
    for exp in experience:
        if any(char.isdigit() for char in exp.get('description', '')):
            has_numbers = True
            break
    
    if has_numbers:
        score += 10
    else:
        suggestions.append("Add quantifiable achievements (metrics, percentages, etc.)")
    
    return {
        'score': score,
        'max_score': max_score,
        'percentage': round((score / max_score) * 100, 1),
        'suggestions': suggestions
    }


def extract_contact_with_ai(cv_text: str) -> Dict[str, str]:
    """Extract contact information using AI when basic extraction fails.
    
    This is a FALLBACK ONLY - triggered when name, email, or phone are missing.
    
    Args:
        cv_text: Full CV text
        
    Returns:
        Dictionary with name, email, phone, linkedin, github
        Returns empty dict if AI extraction fails
    """
    try:
        # Use Groq or OpenAI for extraction
        if not ai_client:
            logger.warning("⚠ AI client not available for contact extraction")
            return {}
        
        # Construct strict prompt for contact-only extraction
        system_prompt = """You are a contact information extractor. Extract ONLY contact details from CVs.
        
CRITICAL RULES:
1. Extract real data only - NO hallucinations
2. If a field is not found, leave it empty
3. Return ONLY valid JSON
4. Do not invent or guess information
5. Name must be actual person's name from CV
6. Email must be valid email format
7. Phone must include country code if present

Output format (JSON only):
{
  "name": "",
  "email": "",
  "phone": "",
  "linkedin": "",
  "github": ""
}"""
        
        user_prompt = f"""Extract contact information from this CV:

{cv_text[:1500]}

Return ONLY the JSON object with contact fields. No other text."""
        
        # Use AI parser's groq client
        if hasattr(parser, 'groq_client') and parser.groq_client:
            response = parser.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for factual extraction
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            contact_data = json.loads(content)
            
            # Validate extracted data
            validated = _validate_ai_contact(contact_data)
            
            if validated.get('name') or validated.get('email'):
                logger.info(f"✓ AI contact extraction successful: {list(validated.keys())}")
                return validated
            else:
                logger.warning("⚠ AI extraction returned no valid contact data")
                return {}
                
        else:
            logger.warning("⚠ Groq client not available")
            return {}
            
    except json.JSONDecodeError as e:
        logger.error(f"❌ AI response was not valid JSON: {e}")
        return {}
    except Exception as e:
        logger.error(f"❌ AI contact extraction failed: {e}")
        return {}


def _validate_ai_contact(contact_data: dict) -> dict:
    """Validate AI-extracted contact data to prevent hallucinations.
    
    Args:
        contact_data: Raw AI output
        
    Returns:
        Cleaned and validated contact data
    """
    import re
    
    validated = {
        'name': '',
        'email': '',
        'phone': '',
        'linkedin': '',
        'github': ''
    }
    
    # Validate name (must have at least 2 words, no placeholders)
    name = contact_data.get('name', '').strip()
    if name and len(name) >= 6:
        words = name.split()
        placeholder_words = ['name', 'your', 'candidate', 'applicant', 'person']
        if len(words) >= 2 and not any(pw in name.lower() for pw in placeholder_words):
            validated['name'] = name
    
    # Validate email (proper format)
    email = contact_data.get('email', '').strip()
    if email and '@' in email:
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            # Reject example/placeholder emails
            if 'example' not in email.lower() and 'placeholder' not in email.lower():
                validated['email'] = email
    
    # Validate phone (has digits, reasonable length)
    phone = contact_data.get('phone', '').strip()
    if phone:
        digits = re.sub(r'\D', '', phone)
        if 7 <= len(digits) <= 15:
            validated['phone'] = phone
    
    # Validate URLs
    linkedin = contact_data.get('linkedin', '').strip()
    if linkedin and 'linkedin.com' in linkedin.lower():
        validated['linkedin'] = linkedin
    
    github = contact_data.get('github', '').strip()
    if github and 'github.com' in github.lower():
        validated['github'] = github
    
    return validated
