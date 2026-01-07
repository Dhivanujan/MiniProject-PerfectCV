"""
Unified CV Extraction Service
Uses spaCy with custom rules for robust CV data extraction.
"""
import re
import io
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Import text extraction libraries
try:
    import fitz  # PyMuPDF - best for PDFs
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    logger.warning("PyMuPDF not available. Install: pip install pymupdf")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not available. Install: pip install python-docx")

# Import NLP libraries
try:
    import spacy
    from spacy.matcher import Matcher, PhraseMatcher
    from spacy.tokens import Doc, Span
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.error("spaCy not available! Install: pip install spacy && python -m spacy download en_core_web_sm")

try:
    import phonenumbers
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    logger.warning("phonenumbers not available. Install: pip install phonenumbers")


class CVExtractor:
    """Unified CV extraction using spaCy with custom rules."""
    
    # Technical skills database
    TECH_SKILLS = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'rust',
        'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell',
        
        # Web Frameworks
        'react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt', 'gatsby',
        'node.js', 'express', 'fastapi', 'django', 'flask', 'spring boot', 'spring',
        'asp.net', '.net', 'laravel', 'rails', 'ruby on rails',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'dynamodb',
        'oracle', 'sql server', 'sqlite', 'elasticsearch', 'neo4j',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s',
        'terraform', 'ansible', 'jenkins', 'ci/cd', 'gitlab', 'github actions',
        'circleci', 'travis ci',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow',
        'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn',
        
        # Other Tools & Technologies
        'git', 'linux', 'unix', 'agile', 'scrum', 'jira', 'rest api', 'graphql',
        'microservices', 'testing', 'tdd', 'bdd', 'html', 'css', 'sass', 'tailwind',
        'bootstrap', 'webpack', 'vite', 'babel',
    }
    
    # Common job titles for pattern matching
    JOB_TITLES = {
        'software engineer', 'senior software engineer', 'junior software engineer',
        'full stack developer', 'frontend developer', 'backend developer',
        'data scientist', 'data analyst', 'machine learning engineer',
        'devops engineer', 'system administrator', 'network engineer',
        'project manager', 'product manager', 'scrum master',
        'ui/ux designer', 'web developer', 'mobile developer',
        'tech lead', 'engineering manager', 'cto', 'architect',
    }
    
    # Common section headers
    SECTION_PATTERNS = {
        'education': r'(?i)^(education|academic|qualifications|academic background)',
        'experience': r'(?i)^(experience|work experience|employment|professional experience|work history)',
        'skills': r'(?i)^(skills|technical skills|competencies|expertise)',
        'projects': r'(?i)^(projects|personal projects|academic projects)',
        'certifications': r'(?i)^(certifications|certificates|licenses)',
        'summary': r'(?i)^(summary|profile|about|objective|career objective)',
    }
    
    def __init__(self, spacy_model: str = "en_core_web_sm"):
        """Initialize CV extractor with spaCy model and custom rules."""
        self.nlp = None
        self.matcher = None
        self.phrase_matcher = None
        
        if not SPACY_AVAILABLE:
            logger.error("spaCy is required for CV extraction!")
            return
        
        try:
            # Load spaCy model
            self.nlp = spacy.load(spacy_model)
            logger.info(f"✓ Loaded spaCy model: {spacy_model}")
            
            # Initialize matchers for custom rules
            self._setup_custom_matchers()
            
        except OSError:
            logger.error(f"spaCy model '{spacy_model}' not found!")
            logger.error(f"Download with: python -m spacy download {spacy_model}")
    
    def _setup_custom_matchers(self):
        """Setup custom pattern matchers for CV entities."""
        if not self.nlp:
            return
        
        # Token-based pattern matcher
        self.matcher = Matcher(self.nlp.vocab)
        
        # Email pattern: word @ word.word
        email_pattern = [
            {"LIKE_EMAIL": True}
        ]
        self.matcher.add("EMAIL", [email_pattern])
        
        # Phone pattern variations
        phone_patterns = [
            # +1 (123) 456-7890
            [{"TEXT": {"REGEX": r"^\+?\d{1,3}$"}}, {"TEXT": {"REGEX": r"^\(?\d{3}\)?$"}}, 
             {"TEXT": {"REGEX": r"^\d{3}$"}}, {"TEXT": {"REGEX": r"^\d{4}$"}}],
            # 123-456-7890
            [{"TEXT": {"REGEX": r"^\d{3}$"}}, {"TEXT": "-"}, {"TEXT": {"REGEX": r"^\d{3}$"}}, 
             {"TEXT": "-"}, {"TEXT": {"REGEX": r"^\d{4}$"}}],
        ]
        self.matcher.add("PHONE", phone_patterns)
        
        # Phrase matcher for skills and job titles
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        
        # Add technical skills
        skill_patterns = [self.nlp.make_doc(skill) for skill in self.TECH_SKILLS]
        self.phrase_matcher.add("SKILL", skill_patterns)
        
        # Add job titles
        job_patterns = [self.nlp.make_doc(title) for title in self.JOB_TITLES]
        self.phrase_matcher.add("JOB_TITLE", job_patterns)
    
    def extract_from_file(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract structured CV data from file bytes.
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with all extracted CV data
        """
        logger.info(f"=" * 70)
        logger.info(f"📄 Processing CV: {filename}")
        logger.info(f"=" * 70)
        
        # Step 1: Extract raw text
        raw_text, extraction_method = self._extract_text(file_bytes, filename)
        logger.info(f"✓ Extracted {len(raw_text)} characters using {extraction_method}")
        
        # Step 2: Clean and normalize text
        cleaned_text = self._clean_text(raw_text)
        logger.info(f"✓ Cleaned text: {len(cleaned_text)} characters")
        
        # Step 3: Extract sections
        sections = self._extract_sections(cleaned_text)
        logger.info(f"✓ Found {len(sections)} sections: {list(sections.keys())}")
        
        # Step 4: Extract entities using spaCy + custom rules
        entities = self._extract_entities(cleaned_text, sections)
        logger.info(f"✓ Extracted entities:")
        logger.info(f"   - Name: {entities.get('name', 'Not found')}")
        logger.info(f"   - Email: {entities.get('email', 'Not found')}")
        logger.info(f"   - Phone: {entities.get('phone', 'Not found')}")
        logger.info(f"   - Location: {entities.get('location', 'Not found')}")
        logger.info(f"   - Skills: {len(entities.get('skills', []))} found")
        logger.info(f"   - Education: {len(entities.get('education', []))} entries")
        logger.info(f"   - Experience: {len(entities.get('experience', []))} entries")
        
        result = {
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'extraction_method': extraction_method,
            'sections': sections,
            'entities': entities,
            'filename': filename,
            'processed_at': datetime.now().isoformat()
        }
        
        logger.info(f"=" * 70)
        logger.info(f"✅ Successfully processed: {filename}")
        logger.info(f"=" * 70)
        
        return result
    
    def _extract_text(self, file_bytes: bytes, filename: str) -> Tuple[str, str]:
        """Extract raw text from PDF or DOCX file."""
        file_lower = filename.lower()
        
        # PDF extraction
        if file_lower.endswith('.pdf'):
            return self._extract_from_pdf(file_bytes), "PyMuPDF"
        
        # DOCX extraction
        elif file_lower.endswith('.docx'):
            return self._extract_from_docx(file_bytes), "python-docx"
        
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    def _extract_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF using PyMuPDF."""
        if not FITZ_AVAILABLE:
            raise RuntimeError("PyMuPDF not available. Install: pip install pymupdf")
        
        try:
            text_parts = []
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                for page_num, page in enumerate(doc, 1):
                    page_text = page.get_text("text")
                    if page_text.strip():
                        text_parts.append(page_text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise
    
    def _extract_from_docx(self, file_bytes: bytes) -> str:
        """Extract text from DOCX file."""
        if not DOCX_AVAILABLE:
            raise RuntimeError("python-docx not available. Install: pip install python-docx")
        
        try:
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            return "\n\n".join(paragraphs)
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove special characters but keep punctuation and newlines
        text = re.sub(r'[^\w\s@.+\-():,;/\n]', '', text)
        
        # Normalize horizontal whitespace (but preserve newlines)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Normalize line breaks - remove excessive ones but keep structure
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract CV sections based on header patterns."""
        sections = {}
        lines = text.split('\n')
        
        current_section = 'header'
        current_content = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Check if line matches any section pattern
            section_found = False
            for section_name, pattern in self.SECTION_PATTERNS.items():
                if re.match(pattern, line_stripped):
                    # Save previous section
                    if current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_entities(self, text: str, sections: Dict[str, str]) -> Dict[str, Any]:
        """Extract all entities using spaCy + custom rules."""
        entities = {
            'name': None,
            'email': None,
            'phone': None,
            'location': None,
            'skills': [],
            'job_titles': [],
            'organizations': [],
            'education': [],
            'experience': [],
            'summary': None,
        }
        
        if not self.nlp:
            logger.warning("spaCy not available - limited extraction")
            return entities
        
        # Extract email using regex (more reliable than spaCy)
        entities['email'] = self._extract_email(text)
        
        # Extract phone using regex
        entities['phone'] = self._extract_phone(text)
        
        # Extract name from ENTIRE text first few lines (not just header section)
        # This handles cases where section parsing might split the name
        first_lines = '\n'.join(text.split('\n')[:10])  # First 10 lines of document
        entities['name'] = self._extract_name(first_lines)
        
        # Process full document with spaCy
        doc = self.nlp(text[:10000])  # Limit to first 10k chars for performance
        
        # Extract location (GPE = Geo-Political Entity)
        locations = [ent.text for ent in doc.ents if ent.label_ in ('GPE', 'LOC')]
        if locations:
            entities['location'] = locations[0]
        
        # Extract organizations
        entities['organizations'] = [ent.text for ent in doc.ents if ent.label_ == 'ORG'][:10]
        
        # Extract skills using phrase matcher
        matches = self.phrase_matcher(doc)
        skills_found = set()
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            if label == "SKILL":
                skill = doc[start:end].text.lower()
                skills_found.add(skill)
        
        entities['skills'] = sorted(list(skills_found))
        
        # Extract job titles using phrase matcher
        job_titles_found = set()
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            if label == "JOB_TITLE":
                title = doc[start:end].text
                job_titles_found.add(title)
        
        entities['job_titles'] = list(job_titles_found)
        
        # Extract structured education
        if 'education' in sections:
            entities['education'] = self._parse_education(sections['education'])
        
        # Extract structured experience
        if 'experience' in sections:
            entities['experience'] = self._parse_experience(sections['experience'])
        
        # Extract summary
        if 'summary' in sections:
            entities['summary'] = sections['summary'][:500]  # Limit to 500 chars
        
        return entities
    
    @staticmethod
    def _extract_email(text: str) -> Optional[str]:
        """Extract email using robust regex."""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        """Extract phone number using regex and phonenumbers library."""
        # Common phone patterns
        patterns = [
            r'\+?\d{1,3}[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}',  # International
            r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}',  # US format
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                phone = matches[0].strip()
                
                # Validate with phonenumbers library if available
                if PHONENUMBERS_AVAILABLE:
                    try:
                        parsed = phonenumbers.parse(phone, None)
                        if phonenumbers.is_valid_number(parsed):
                            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    except:
                        pass
                
                return phone
        
        return None
    
    def _extract_name(self, header_text: str) -> Optional[str]:
        """Extract person name from document header."""
        if not header_text:
            return None
        
        # Process only first few lines
        lines = header_text.split('\n')[:8]
        
        for line in lines:
            line_clean = line.strip()
            if not line_clean or len(line_clean) < 3:
                continue
            
            # Skip lines with email, phone, or URLs
            if '@' in line_clean or 'http' in line_clean.lower():
                continue
            if re.search(r'\d{3,}', line_clean):  # Has 3+ consecutive digits
                continue
            
            # Skip common header keywords
            skip_keywords = {'resume', 'cv', 'curriculum vitae', 'email', 'phone', 'address', 'location'}
            if line_clean.lower() in skip_keywords:
                continue
            
            # Fallback: If line looks like a name (2-4 words, properly capitalized)
            words = line_clean.split()
            if 2 <= len(words) <= 4:
                # Check if words start with capital letters
                properly_capped = all(w and len(w) > 1 and w[0].isupper() for w in words)
                no_numbers = not any(any(c.isdigit() for c in w) for w in words)
                not_all_caps = not line_clean.isupper()
                
                # Skip job titles
                job_words = {'engineer', 'developer', 'manager', 'analyst', 'scientist', 
                           'designer', 'architect', 'consultant', 'specialist', 'director',
                           'lead', 'senior', 'junior', 'staff', 'principal'}
                has_job_word = any(word.lower() in job_words for word in words)
                
                if properly_capped and no_numbers and not_all_caps and not has_job_word:
                    return line_clean
            
            # Use spaCy to find PERSON entities if available
            if self.nlp:
                doc = self.nlp(line_clean)
                persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
                
                # Filter out job titles
                job_indicators = ['engineer', 'developer', 'manager']
                persons = [p for p in persons if not any(ind in p.lower() for ind in job_indicators)]
                
                if persons:
                    return persons[0]
        
        return None
    
    def _parse_education(self, education_text: str) -> List[Dict[str, Any]]:
        """Parse education section into structured entries."""
        entries = []
        
        # Split by double newlines or common degree patterns
        sections = re.split(r'\n\n+', education_text)
        
        for section in sections:
            if not section.strip():
                continue
            
            entry = {
                'degree': None,
                'institution': None,
                'year': None,
                'details': section.strip()
            }
            
            # Extract degree (Bachelor, Master, PhD, etc.)
            degree_pattern = r'(Bachelor|Master|PhD|Ph\.D\.|MBA|B\.S\.|M\.S\.|B\.A\.|M\.A\.|B\.Tech|M\.Tech).*(?:in|of)\s+([^\n,]+)'
            degree_match = re.search(degree_pattern, section, re.IGNORECASE)
            if degree_match:
                entry['degree'] = degree_match.group(0).strip()
            
            # Extract year
            year_pattern = r'\b(19|20)\d{2}\b'
            years = re.findall(year_pattern, section)
            if years:
                entry['year'] = years[-1]  # Most recent year
            
            # Extract institution using spaCy
            if self.nlp:
                doc = self.nlp(section[:200])
                orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
                if orgs:
                    entry['institution'] = orgs[0]
            
            entries.append(entry)
        
        return entries
    
    def _parse_experience(self, experience_text: str) -> List[Dict[str, Any]]:
        """Parse experience section into structured entries."""
        entries = []
        
        # Split by double newlines
        sections = re.split(r'\n\n+', experience_text)
        
        for section in sections:
            if not section.strip():
                continue
            
            entry = {
                'title': None,
                'company': None,
                'duration': None,
                'description': section.strip()
            }
            
            # Extract dates/duration
            date_pattern = r'(\w+\s+\d{4}|\d{4})\s*[-–—to]+\s*(\w+\s+\d{4}|\d{4}|Present|Current)'
            date_match = re.search(date_pattern, section, re.IGNORECASE)
            if date_match:
                entry['duration'] = date_match.group(0)
            
            # Extract company using spaCy
            if self.nlp:
                doc = self.nlp(section[:300])
                orgs = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
                if orgs:
                    entry['company'] = orgs[0]
            
            # Extract job title (usually first line)
            first_line = section.split('\n')[0].strip()
            if first_line:
                entry['title'] = first_line
            
            entries.append(entry)
        
        return entries


# Singleton instance
_extractor_instance = None

def get_cv_extractor() -> CVExtractor:
    """Get or create singleton CV extractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = CVExtractor()
    return _extractor_instance
