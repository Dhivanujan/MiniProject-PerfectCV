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
        
        # Extract location from contact line or text
        entities['location'] = self._extract_location(text)
        
        # Extract name FIRST before spaCy (which might pick up wrong entities)
        entities['name'] = self._extract_name_from_top(text)
        
        # Extract entities using spaCy if available
        if self.nlp:
            doc = self.nlp(text)
            
            # Only use spaCy for name if we didn't find it already
            if not entities['name']:
                persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
                if persons:
                    entities['name'] = persons[0]
            
            # Extract organizations
            entities['organizations'] = [
                ent.text for ent in doc.ents if ent.label_ == 'ORG'
            ][:10]  # Limit to first 10
            
            # Extract locations from spaCy if not found yet
            if not entities['location']:
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
        
        logger.info(f"Extracted entities: name={entities.get('name')}, email={entities.get('email')}, "
                   f"phone={entities.get('phone')}, location={entities.get('location')}")
        
        return entities
    
    @staticmethod
    def _extract_email(text: str) -> Optional[str]:
        """Extract email address using robust regex."""
        # Standard email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        if matches:
            # Return the first match, cleaned
            return matches[0].strip()
        return None
    
    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        """Extract phone number using regex and phonenumbers library."""
        # More comprehensive phone patterns including international formats
        phone_patterns = [
            r'(?:\+|00)\d{1,3}[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}',  # International with country code
            r'\+?1?\s*\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # US/North America
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Simple 10 digit
            r'\b\d{4,5}[\s.-]?\d{6,7}\b', # Some intl formats
        ]
        
        candidates = []
        for pattern in phone_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                candidates.append(match.group().strip())
        
        # Prioritize candidates using phonenumbers validation
        if PHONENUMBERS_AVAILABLE and candidates:
            for candidate in candidates:
                try:
                    # Attempt to parse as US first then generic
                    parsed = phonenumbers.parse(candidate, "US") 
                    if not phonenumbers.is_valid_number(parsed):
                         # Try parsing with + prefix if missing
                         if not candidate.startswith('+'):
                             parsed = phonenumbers.parse("+" + candidate, None)
                    
                    if phonenumbers.is_valid_number(parsed):
                        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                except Exception:
                    continue
        
        # Fallback: return the longest candidate that looks like a phone number
        if candidates:
            # simple filter for length
            valid_candidates = [c for c in candidates if sum(c.isdigit() for c in c) >= 10]
            if valid_candidates:
                return valid_candidates[0]
            return candidates[0]
        
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
    def _extract_name_from_top(text: str) -> Optional[str]:
        """
        Extract name from the top of CV.
        Assumes name is in the first few non-empty lines before contact info.
        """
        lines = text.strip().split('\n')
        
        # Look for name in first 15 lines, but before any section headers
        for i, line in enumerate(lines[:15]):
            line = line.strip()
            
            # Skip markdown headers
            if line.startswith('#'):
                # Remove markdown markers
                clean_line = re.sub(r'^#+\s*', '', line).strip()
                # Check if this is a potential name (not a section)
                if clean_line and not EntityExtractor._is_section_header(clean_line):
                    words = clean_line.split()
                    if 1 <= len(words) <= 4 and sum(c.isalpha() or c.isspace() for c in clean_line) / max(len(clean_line), 1) > 0.7:
                        return clean_line
                continue
            
            # Skip empty lines
            if not line or len(line) < 2:
                continue
            
            # Skip lines with contact info (email, phone, "Email:", "Phone:", "Location:")
            if any(marker in line for marker in ['@', 'Email:', 'Phone:', 'Location:', '|']):
                continue
            
            # Skip lines that are clearly phone numbers
            if re.search(r'[\d\(\)\+\-\s]{10,}', line) and sum(c.isdigit() for c in line) > 5:
                continue
            
            # Check if this looks like a name
            words = line.split()
            if 1 <= len(words) <= 4:
                # Name should be mostly alphabetic
                alpha_ratio = sum(c.isalpha() or c.isspace() for c in line) / max(len(line), 1)
                if alpha_ratio > 0.7:
                    # Check if all words are capitalized or it's a single capitalized word
                    cap_words = [w for w in words if w and w[0].isupper()]
                    if len(cap_words) >= len(words) * 0.7:  # At least 70% capitalized
                        # Exclude section headers
                        if not EntityExtractor._is_section_header(line):
                            logger.info(f"Found name from top: {line}")
                            return line
        
        return None
    
    @staticmethod
    def _is_section_header(text: str) -> bool:
        """Check if text looks like a section header."""
        text_lower = text.lower()
        section_keywords = [
            'resume', 'cv', 'curriculum', 'vitae', 'experience', 'education',
            'skills', 'summary', 'profile', 'objective', 'employment', 'work history',
            'professional experience', 'qualifications', 'certifications', 'projects',
            'awards', 'honors', 'achievements', 'languages', 'references',
            'honours', 'degree', 'bachelor', 'master', 'university', 'college'
        ]
        return any(keyword in text_lower for keyword in section_keywords)
    
    @staticmethod
    def _extract_location(text: str) -> Optional[str]:
        """Extract location from CV, prioritizing contact info line."""
        # Look for "Location: City" pattern in first 20 lines
        lines = text.split('\n')[:20]
        for line in lines:
            if 'Location:' in line or 'location:' in line:
                # Extract the location part
                match = re.search(r'[Ll]ocation:\s*([^|\n]+)', line)
                if match:
                    location = match.group(1).strip()
                    if location:
                        logger.info(f"Found location from header: {location}")
                        return location
        
        # Fallback: look for city/country patterns
        # Common patterns: "City, State" or "City, Country"
        city_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z]{2,}|[A-Z][a-z]+)\b'
        matches = re.findall(city_pattern, text[:1000])  # Check first 1000 chars
        if matches:
            return f"{matches[0][0]}, {matches[0][1]}"
        
        return None
