"""
Unified CV Extraction Service
Uses pdfplumber for superior layout analysis and regex-based entity extraction.
"""
import re
import io
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)

# Import text extraction libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available. Install: pip install pdfplumber")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not available. Install: pip install python-docx")

try:
    import phonenumbers
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    logger.warning("phonenumbers not available. Install: pip install phonenumbers")


class CVExtractor:
    """Unified CV extraction using pdfplumber layout analysis and regex patterns."""
    
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
    
    def __init__(self):
        """Initialize CV extractor with pdfplumber."""
        self._layout_data = None  # Store PDF layout analysis
        
        if not PDFPLUMBER_AVAILABLE:
            logger.error("pdfplumber is required for CV extraction!")
            logger.error("Install: pip install pdfplumber")
        else:
            logger.info("✓ pdfplumber available for PDF extraction")
    
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
        
        # Prepare layout metadata
        layout_meta = {}
        if self._layout_data:
            layout_meta = {
                'has_layout_analysis': True,
                'headers_detected': len(self._layout_data.get('headers', [])),
                'sections_detected': list(self._layout_data.get('sections', {}).keys()),
                'contact_blocks_count': len(self._layout_data.get('contact_blocks', [])),
                'avg_font_size': sum(self._layout_data.get('font_sizes', [])) / len(self._layout_data.get('font_sizes', [1])) if self._layout_data.get('font_sizes') else 0
            }
        
        result = {
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'extraction_method': extraction_method,
            'sections': sections,
            'entities': entities,
            'layout_metadata': layout_meta,
            'filename': filename,
            'processed_at': datetime.now().isoformat()
        }
        
        logger.info(f"=" * 70)
        logger.info(f"✅ Successfully processed: {filename}")
        if layout_meta:
            logger.info(f"📊 Layout Analysis: {layout_meta['headers_detected']} headers, {len(layout_meta['sections_detected'])} sections")
        logger.info(f"=" * 70)
        
        return result
    
    def _extract_text(self, file_bytes: bytes, filename: str) -> Tuple[str, str]:
        """Extract raw text from PDF or DOCX file."""
        file_lower = filename.lower()
        
        # PDF extraction with layout analysis
        if file_lower.endswith('.pdf'):
            # Store layout analysis for later use
            self._layout_data = self._analyze_pdf_layout(file_bytes)
            return self._extract_from_pdf(file_bytes), "pdfplumber+Layout"
        
        # DOCX extraction
        elif file_lower.endswith('.docx'):
            self._layout_data = None
            return self._extract_from_docx(file_bytes), "python-docx"
        
        else:
            raise ValueError(f"Unsupported file format: {filename}")
    
    def _extract_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF using pdfplumber."""
        if not PDFPLUMBER_AVAILABLE:
            raise RuntimeError("pdfplumber not available. Install: pip install pdfplumber")
        
        try:
            text_parts = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_parts.append(page_text)
            
            return "\n\n".join(text_parts)
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise
    
    def _analyze_pdf_layout(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Analyze PDF layout using pdfplumber to identify CV components.
        
        Returns:
            Dictionary containing:
            - text_blocks: List of text objects with position, font, size
            - headers: Detected header blocks (large font, bold)
            - contact_info: Top section blocks (likely contact details)
            - sections: Detected major sections based on layout
        """
        if not PDFPLUMBER_AVAILABLE:
            raise RuntimeError("pdfplumber not available")
        
        try:
            layout_data = {
                'text_blocks': [],
                'headers': [],
                'contact_blocks': [],
                'sections': defaultdict(list),
                'font_sizes': []
            }
            
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract characters with detailed layout information
                    chars = page.chars
                    
                    if not chars:
                        continue
                    
                    # Group characters into text blocks (lines)
                    lines = self._group_chars_into_lines(chars)
                    page_height = page.height
                    
                    for line in lines:
                        block_info = self._analyze_text_line(line, page_num, page_height)
                        if block_info:
                            layout_data['text_blocks'].append(block_info)
                            
                            # Collect font sizes for statistical analysis
                            if block_info['font_size']:
                                layout_data['font_sizes'].append(block_info['font_size'])
                            
                            # Identify potential header blocks
                            # Headers are typically: larger font (12+), bold, or all caps
                            is_header = (
                                (block_info['is_bold'] and block_info['font_size'] >= 12) or
                                (block_info['font_size'] >= 14) or
                                (block_info['text'].isupper() and len(block_info['text'].split()) <= 5)
                            )
                            if is_header:
                                layout_data['headers'].append(block_info)
                            
                            # Top section blocks (likely contact info) - first 20% of page
                            if page_num == 1 and block_info['y_position'] < 0.2:
                                layout_data['contact_blocks'].append(block_info)
            
            # Identify sections based on headers
            layout_data['sections'] = self._identify_sections_from_layout(
                layout_data['headers'], 
                layout_data['text_blocks']
            )
            
            return layout_data
            
        except Exception as e:
            logger.error(f"PDF layout analysis failed: {e}")
            return {
                'text_blocks': [],
                'headers': [],
                'contact_blocks': [],
                'sections': {},
                'font_sizes': []
            }
    
    def _group_chars_into_lines(self, chars: List[Dict]) -> List[List[Dict]]:
        """
        Group character objects into lines based on vertical position.
        
        Args:
            chars: List of character dictionaries from pdfplumber
        
        Returns:
            List of lines, where each line is a list of characters
        """
        if not chars:
            return []
        
        # Sort characters by vertical position (top), then horizontal (left)
        sorted_chars = sorted(chars, key=lambda c: (round(c['top'], 1), c['x0']))
        
        lines = []
        current_line = []
        current_top = None
        tolerance = 2  # pixels
        
        for char in sorted_chars:
            char_top = round(char['top'], 1)
            
            if current_top is None or abs(char_top - current_top) <= tolerance:
                # Same line
                current_line.append(char)
                current_top = char_top
            else:
                # New line
                if current_line:
                    lines.append(current_line)
                current_line = [char]
                current_top = char_top
        
        # Add last line
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _analyze_text_line(self, line_chars: List[Dict], page_num: int, page_height: float) -> Optional[Dict[str, Any]]:
        """
        Analyze a text line from pdfplumber characters.
        
        Args:
            line_chars: List of character dictionaries in a line
            page_num: Page number
            page_height: Height of the page for normalizing positions
        
        Returns:
            Dictionary with line analysis or None if invalid
        """
        try:
            if not line_chars:
                return None
            
            # Extract text and font information
            text = ''.join(char['text'] for char in line_chars)
            text = text.strip()
            
            if not text:
                return None
            
            # Collect font information
            font_sizes = [char.get('size', 0) for char in line_chars if char.get('size')]
            font_names = [char.get('fontname', '') for char in line_chars if char.get('fontname')]
            
            # Check if bold (font name contains 'Bold')
            is_bold = any('bold' in name.lower() for name in font_names if name)
            
            # Calculate bounding box
            x0 = min(char['x0'] for char in line_chars)
            y0 = min(char['top'] for char in line_chars)
            x1 = max(char['x1'] for char in line_chars)
            y1 = max(char['bottom'] for char in line_chars)
            
            return {
                'text': text,
                'page': page_num,
                'bbox': [x0, y0, x1, y1],
                'x_position': x0,
                'y_position': y0 / page_height if page_height > 0 else 0,  # Normalized position
                'width': x1 - x0,
                'height': y1 - y0,
                'font_size': max(font_sizes) if font_sizes else 0,
                'avg_font_size': sum(font_sizes) / len(font_sizes) if font_sizes else 0,
                'fonts': list(set(font_names)),
                'is_bold': is_bold,
                'char_count': len(line_chars)
            }
            
        except Exception as e:
            logger.error(f"Line analysis failed: {e}")
            return None
    
    def _identify_sections_from_layout(self, headers: List[Dict], text_blocks: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Identify CV sections based on header blocks and text layout.
        
        Args:
            headers: List of header blocks
            text_blocks: All text blocks
        
        Returns:
            Dictionary mapping section names to their content blocks
        """
        sections = defaultdict(list)
        
        # Sort blocks by page and position
        sorted_blocks = sorted(text_blocks, key=lambda b: (b['page'], b['y_position']))
        
        # Section keywords to look for
        section_keywords = {
            'experience': ['experience', 'work history', 'employment', 'work experience', 'professional experience'],
            'education': ['education', 'academic', 'qualification', 'degree'],
            'skills': ['skills', 'technical skills', 'competencies', 'expertise'],
            'projects': ['projects', 'portfolio'],
            'certifications': ['certifications', 'certificates', 'licenses'],
            'summary': ['summary', 'profile', 'objective', 'about']
        }
        
        current_section = 'other'
        
        for block in sorted_blocks:
            text_lower = block['text'].lower()
            
            # Check if this block is a section header
            section_found = False
            for section_name, keywords in section_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    current_section = section_name
                    section_found = True
                    sections[current_section].append(block)
                    break
            
            if not section_found:
                sections[current_section].append(block)
        
        return dict(sections)
    
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
        """Extract all entities using regex patterns and layout analysis."""
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
        
        # Extract email using regex
        entities['email'] = self._extract_email(text)
        
        # Extract phone using regex
        entities['phone'] = self._extract_phone(text)
        
        # Extract name using layout analysis if available (for PDFs)
        if self._layout_data and self._layout_data.get('contact_blocks'):
            # Use layout-based name extraction for better accuracy
            entities['name'] = self._extract_name_from_layout(self._layout_data['contact_blocks'])
        
        # Fallback to text-based extraction if layout not available or name not found
        if not entities['name']:
            first_lines = '\n'.join(text.split('\n')[:10])  # First 10 lines of document
            entities['name'] = self._extract_name_regex(first_lines)
        
        # Extract location using regex
        entities['location'] = self._extract_location(text)
        
        # Extract organizations using regex
        entities['organizations'] = self._extract_organizations(text)
        
        # Extract skills using keyword matching
        entities['skills'] = self._extract_skills_regex(text)
        
        # Extract job titles using keyword matching
        entities['job_titles'] = self._extract_job_titles_regex(text)
        
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
    
    def _extract_name_from_layout(self, contact_blocks: List[Dict]) -> Optional[str]:
        """
        Extract name using PDF layout analysis.
        Looks for large, bold text at the top of the CV.
        
        Args:
            contact_blocks: Text blocks from top section of first page
        
        Returns:
            Extracted name or None
        """
        if not contact_blocks:
            return None
        
        # Sort by font size (descending) and position (top first)
        sorted_blocks = sorted(
            contact_blocks,
            key=lambda b: (-b.get('font_size', 0), b.get('y_position', 0))
        )
        
        # Look for name in largest text blocks
        for block in sorted_blocks[:5]:  # Check top 5 blocks
            text = block.get('text', '').strip()
            
            # Skip if too short or too long
            if not text or len(text) < 3 or len(text) > 50:
                continue
            
            # Skip if contains email or phone patterns
            if '@' in text or re.search(r'\d{3}[-\s]\d{3}[-\s]\d{4}', text):
                continue
            
            # Check if it looks like a name (2-3 capitalized words)
            words = text.split()
            if 2 <= len(words) <= 3 and all(w[0].isupper() for w in words if w):
                # Filter out job titles
                text_lower = text.lower()
                if not any(title.lower() in text_lower for title in self.JOB_TITLES):
                    return text
        
        return None
    
    def _extract_name_regex(self, text: str) -> Optional[str]:
        """
        Extract name using regex patterns.
        Looks for capitalized words at the beginning of the document.
        
        Args:
            text: First few lines of the CV
        
        Returns:
            Extracted name or None
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        # Look at first 5 lines
        for line in lines[:5]:
            # Skip lines with email or phone
            if '@' in line or re.search(r'\d{3}[-\s()]\d{3}[-\s()]\d{4}', line):
                continue
            
            # Name pattern: 2-3 capitalized words
            name_pattern = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})$'
            match = re.match(name_pattern, line)
            if match:
                name = match.group(1)
                # Filter out job titles
                if not any(title.lower() in name.lower() for title in self.JOB_TITLES):
                    return name
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location using regex patterns."""
        # Common location patterns
        patterns = [
            r'(?:Location|Address|Based in):\s*([A-Z][a-z]+(?:,?\s+[A-Z]{2})?)',
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State
            r'([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # City, Country
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # Look for common city names in first 500 chars
        common_cities = [
            'San Francisco', 'New York', 'Los Angeles', 'Chicago', 'Boston',
            'Seattle', 'Austin', 'Denver', 'Portland', 'Atlanta', 'Miami',
            'London', 'Paris', 'Berlin', 'Tokyo', 'Singapore', 'Sydney'
        ]
        
        first_part = text[:500]
        for city in common_cities:
            if city in first_part:
                return city
        
        return None
    
    def _extract_organizations(self, text: str) -> List[str]:
        """Extract organization names using patterns."""
        orgs = []
        
        # Look for "at Company" or "@ Company" patterns
        pattern = r'(?:at|@)\s+([A-Z][A-Za-z0-9\s&]+(?:Inc\.|Corp\.|LLC|Ltd\.|Co\.|Group)?)'
        matches = re.findall(pattern, text)
        orgs.extend([m.strip() for m in matches])
        
        # Remove duplicates and limit
        return sorted(list(set(orgs)))[:10]
    
    def _extract_skills_regex(self, text: str) -> List[str]:
        """Extract skills using keyword matching."""
        text_lower = text.lower()
        skills_found = set()
        
        for skill in self.TECH_SKILLS:
            # Use word boundaries for accurate matching
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                skills_found.add(skill.lower())
        
        return sorted(list(skills_found))
    
    def _extract_job_titles_regex(self, text: str) -> List[str]:
        """Extract job titles using keyword matching."""
        text_lower = text.lower()
        titles_found = set()
        
        for title in self.JOB_TITLES:
            if title.lower() in text_lower:
                titles_found.add(title)
        
        return list(titles_found)
    
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
    
    # Removed old _extract_name method - replaced with _extract_name_regex
    
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
            
            # Extract institution (first capitalized line or org name)
            lines = [l.strip() for l in section.split('\n') if l.strip()]
            for line in lines[1:3]:  # Check 2nd and 3rd lines
                if len(line) > 5 and line[0].isupper():
                    entry['institution'] = line
                    break
            
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
            # Extract company name from the section
            # Look for company patterns
            company_pattern = r'(?:at|@)\s+([A-Z][A-Za-z0-9\s&]+(?:Inc\.|Corp\.|LLC|Ltd\.|Co\.|Group)?)'
            match = re.search(company_pattern, section)
            if match:
                entry['company'] = match.group(1).strip()
            
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
