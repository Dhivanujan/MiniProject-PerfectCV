"""
NLP-based entity extraction using spaCy.
Extracts structured information from CV text.
"""
import re
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import spaCy
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available. Install with: pip install spacy")

try:
    import phonenumbers
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    logger.warning("phonenumbers not available")


class EntityExtractor:
    """Extract structured entities from CV text using spaCy and regex."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize entity extractor with spaCy model."""
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(model_name)
                logger.info(f"Loaded spaCy model: {model_name}")
            except OSError:
                logger.warning(f"spaCy model '{model_name}' not found. Download with: python -m spacy download {model_name}")
                logger.info("Attempting to use spaCy without pre-trained model (limited functionality)")
    
    def extract_entities(self, text: str) -> Dict:
        """
        Extract all entities from CV text.
        
        Args:
            text: Cleaned CV text
            
        Returns:
            Dictionary with extracted entities
        """
        entities = {
            'name': None,
            'email': None,
            'phone': None,
            'location': None,
            'organizations': [],
            'dates': [],
            'skills': [],
            'education_institutions': [],
            'job_titles': [],
        }
        
        # Extract email (regex)
        entities['email'] = self._extract_email(text)
        
        # Extract phone (regex + phonenumbers library)
        entities['phone'] = self._extract_phone(text)
        
        # Extract entities using spaCy if available
        if self.nlp:
            doc = self.nlp(text)
            
            # Extract person names (assume first PERSON entity is the CV owner)
            persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
            if persons:
                entities['name'] = persons[0]
            
            # Extract organizations
            entities['organizations'] = [
                ent.text for ent in doc.ents if ent.label_ == 'ORG'
            ][:10]  # Limit to first 10
            
            # Extract locations (GPE = Geopolitical Entity)
            locations = [ent.text for ent in doc.ents if ent.label_ in ('GPE', 'LOC')]
            if locations:
                entities['location'] = locations[0]
            
            # Extract dates
            entities['dates'] = [
                ent.text for ent in doc.ents if ent.label_ == 'DATE'
            ][:20]  # Limit to first 20
        
        # Extract skills using keyword matching
        entities['skills'] = self._extract_skills(text)
        
        # Extract education institutions
        entities['education_institutions'] = self._extract_education_institutions(text)
        
        # Extract job titles
        entities['job_titles'] = self._extract_job_titles(text)
        
        # If name not found via NER, try to extract from top of document
        if not entities['name']:
            entities['name'] = self._extract_name_fallback(text)
        
        return entities
    
    @staticmethod
    def _extract_email(text: str) -> Optional[str]:
        """Extract email address using regex."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else None
    
    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        """Extract phone number using regex and phonenumbers library."""
        # Simple regex patterns for common formats
        phone_patterns = [
            r'\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # US format
            r'\+?\d{1,3}[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}',  # International
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                phone = matches[0]
                
                # Validate using phonenumbers library if available
                if PHONENUMBERS_AVAILABLE:
                    try:
                        parsed = phonenumbers.parse(phone, "US")
                        if phonenumbers.is_valid_number(parsed):
                            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    except Exception:
                        pass
                
                # Return raw match if validation not available
                return phone.strip()
        
        return None
    
    @staticmethod
    def _extract_skills(text: str) -> List[str]:
        """
        Extract technical skills using keyword matching.
        This is a simplified approach - can be enhanced with ML models.
        """
        # Common technical skills keywords
        skills_keywords = {
            # Programming languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 'swift',
            'kotlin', 'go', 'rust', 'scala', 'r', 'matlab', 'sql',
            
            # Web technologies
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
            'spring', 'asp.net', 'jquery', 'bootstrap', 'tailwind',
            
            # Databases
            'mysql', 'postgresql', 'mongodb', 'oracle', 'sql server', 'redis', 'elasticsearch',
            'dynamodb', 'cassandra',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd', 'terraform',
            'ansible', 'git', 'github', 'gitlab',
            
            # Data Science & ML
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
            'pandas', 'numpy', 'data analysis', 'statistics', 'nlp',
            
            # Other
            'agile', 'scrum', 'rest api', 'graphql', 'microservices', 'linux', 'windows',
        }
        
        found_skills = set()
        text_lower = text.lower()
        
        for skill in skills_keywords:
            # Use word boundaries for exact matches
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found_skills.add(skill.title())
        
        return sorted(list(found_skills))
    
    @staticmethod
    def _extract_education_institutions(text: str) -> List[str]:
        """Extract education institution names."""
        # Keywords that often precede university names
        edu_keywords = [
            'university', 'college', 'institute', 'school', 'academy',
            'polytechnic', 'université'
        ]
        
        institutions = []
        
        # Look for lines containing education keywords
        for line in text.split('\n'):
            line_lower = line.lower()
            for keyword in edu_keywords:
                if keyword in line_lower:
                    # Clean up the line
                    cleaned = line.strip()
                    if cleaned and len(cleaned) > 5 and len(cleaned) < 100:
                        institutions.append(cleaned)
                    break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_institutions = []
        for inst in institutions:
            if inst not in seen:
                seen.add(inst)
                unique_institutions.append(inst)
        
        return unique_institutions[:5]  # Limit to 5
    
    @staticmethod
    def _extract_job_titles(text: str) -> List[str]:
        """Extract job titles using common patterns."""
        # Common job title keywords
        title_keywords = [
            'engineer', 'developer', 'manager', 'analyst', 'consultant', 'architect',
            'designer', 'scientist', 'specialist', 'administrator', 'coordinator',
            'director', 'lead', 'senior', 'junior', 'intern'
        ]
        
        job_titles = []
        
        # Look for title patterns in text
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check if line contains job title keywords
            for keyword in title_keywords:
                if keyword in line_lower:
                    cleaned = line.strip()
                    # Filter reasonable length
                    if 5 < len(cleaned) < 60:
                        # Avoid adding full sentences
                        if cleaned.count(' ') < 8:
                            job_titles.append(cleaned)
                            break
        
        # Remove duplicates
        seen = set()
        unique_titles = []
        for title in job_titles:
            if title not in seen:
                seen.add(title)
                unique_titles.append(title)
        
        return unique_titles[:10]  # Limit to 10
    
    @staticmethod
    def _extract_name_fallback(text: str) -> Optional[str]:
        """
        Fallback method to extract name from top of CV.
        Assumes name is in first few lines.
        """
        lines = text.strip().split('\n')[:5]  # Check first 5 lines
        
        for line in lines:
            line = line.strip()
            # Name is likely 2-4 words, all capitalized or title case
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if looks like a name (capitalized words)
                if all(word[0].isupper() for word in words if word):
                    # Avoid lines that look like headers or sections
                    if not any(keyword in line.lower() for keyword in ['resume', 'cv', 'curriculum', 'vitae']):
                        return line
        
        return None
