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
    
    # Technical skills database - expanded
    TECH_SKILLS = {
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c', 'go', 'rust',
        'ruby', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell',
        'bash', 'powershell', 'lua', 'groovy', 'dart', 'elixir', 'clojure', 'haskell',
        'objective-c', 'assembly', 'fortran', 'cobol', 'vba', 'visual basic',
        
        # Web Frameworks & Libraries
        'react', 'react.js', 'reactjs', 'angular', 'angularjs', 'vue', 'vue.js', 'vuejs',
        'svelte', 'next.js', 'nextjs', 'nuxt', 'nuxt.js', 'gatsby', 'remix',
        'node.js', 'nodejs', 'express', 'express.js', 'fastapi', 'django', 'flask',
        'spring boot', 'spring', 'spring mvc', 'hibernate', 'struts',
        'asp.net', '.net', '.net core', 'blazor', 'laravel', 'symfony', 'codeigniter',
        'rails', 'ruby on rails', 'sinatra', 'phoenix', 'gin', 'echo', 'fiber',
        
        # Frontend Technologies
        'html', 'html5', 'css', 'css3', 'sass', 'scss', 'less', 'tailwind', 'tailwindcss',
        'bootstrap', 'material ui', 'chakra ui', 'ant design', 'styled-components',
        'webpack', 'vite', 'babel', 'rollup', 'parcel', 'gulp', 'grunt',
        'jquery', 'ajax', 'json', 'xml', 'graphql', 'rest', 'restful', 'soap',
        
        # Mobile Development
        'android', 'ios', 'react native', 'flutter', 'xamarin', 'ionic', 'cordova',
        'swiftui', 'uikit', 'jetpack compose', 'android studio', 'xcode',
        
        # Databases
        'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'redis', 'cassandra', 'dynamodb',
        'oracle', 'sql server', 'mssql', 'sqlite', 'elasticsearch', 'neo4j', 'couchdb',
        'firebase', 'firestore', 'supabase', 'mariadb', 'snowflake', 'redshift',
        'memcached', 'influxdb', 'timescaledb', 'cockroachdb', 'arangodb',
        
        # Cloud & DevOps
        'aws', 'amazon web services', 'azure', 'microsoft azure', 'gcp', 'google cloud',
        'google cloud platform', 'docker', 'kubernetes', 'k8s', 'openshift',
        'terraform', 'ansible', 'puppet', 'chef', 'vagrant', 'packer',
        'jenkins', 'ci/cd', 'gitlab ci', 'github actions', 'circleci', 'travis ci',
        'bamboo', 'teamcity', 'azure devops', 'bitbucket pipelines',
        'nginx', 'apache', 'tomcat', 'iis', 'haproxy', 'consul', 'vault',
        'prometheus', 'grafana', 'datadog', 'splunk', 'elk', 'logstash', 'kibana',
        'cloudformation', 'pulumi', 'serverless', 'lambda', 'cloud functions',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'nlp', 'natural language processing',
        'computer vision', 'neural networks', 'artificial intelligence', 'ai', 'ml',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'sklearn', 'xgboost',
        'lightgbm', 'catboost', 'opencv', 'spacy', 'nltk', 'huggingface',
        'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly', 'bokeh',
        'jupyter', 'jupyter notebook', 'anaconda', 'conda', 'dask', 'spark', 'pyspark',
        'hadoop', 'hive', 'kafka', 'airflow', 'mlflow', 'kubeflow', 'sagemaker',
        'databricks', 'tableau', 'power bi', 'looker', 'metabase', 'superset',
        
        # Testing
        'testing', 'unit testing', 'integration testing', 'e2e testing',
        'jest', 'mocha', 'chai', 'cypress', 'selenium', 'playwright', 'puppeteer',
        'pytest', 'unittest', 'junit', 'testng', 'rspec', 'minitest',
        'tdd', 'bdd', 'cucumber', 'postman', 'insomnia', 'soapui',
        
        # Version Control & Collaboration
        'git', 'github', 'gitlab', 'bitbucket', 'svn', 'mercurial',
        'jira', 'confluence', 'trello', 'asana', 'monday', 'notion', 'slack',
        
        # Operating Systems & Tools
        'linux', 'unix', 'ubuntu', 'centos', 'debian', 'redhat', 'fedora',
        'windows', 'macos', 'wsl', 'vim', 'emacs', 'vscode', 'intellij',
        
        # Methodologies & Concepts
        'agile', 'scrum', 'kanban', 'lean', 'waterfall', 'devops', 'devsecops',
        'microservices', 'monolith', 'soa', 'event-driven', 'cqrs', 'ddd',
        'oop', 'functional programming', 'design patterns', 'solid', 'dry',
        'api design', 'system design', 'architecture', 'scalability',
        
        # Security
        'security', 'cybersecurity', 'penetration testing', 'ethical hacking',
        'owasp', 'ssl', 'tls', 'oauth', 'jwt', 'saml', 'sso', 'ldap',
        'encryption', 'cryptography', 'firewalls', 'vpn', 'iam',
        
        # Other Technologies
        'blockchain', 'ethereum', 'solidity', 'web3', 'smart contracts',
        'iot', 'embedded systems', 'arduino', 'raspberry pi',
        'unity', 'unreal engine', 'game development', '3d modeling',
        'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator',
    }
    
    # Soft skills to detect
    SOFT_SKILLS = {
        'leadership', 'communication', 'teamwork', 'problem solving', 'problem-solving',
        'critical thinking', 'time management', 'project management', 'collaboration',
        'analytical', 'creative', 'creativity', 'adaptability', 'flexibility',
        'attention to detail', 'detail-oriented', 'organization', 'organizational',
        'presentation', 'public speaking', 'negotiation', 'decision making',
        'conflict resolution', 'mentoring', 'coaching', 'strategic thinking',
        'customer service', 'client relations', 'stakeholder management',
        'multitasking', 'self-motivated', 'proactive', 'initiative',
    }
    
    # Common job titles for pattern matching - expanded
    JOB_TITLES = {
        # Engineering
        'software engineer', 'senior software engineer', 'junior software engineer',
        'staff software engineer', 'principal software engineer', 'lead software engineer',
        'full stack developer', 'frontend developer', 'backend developer',
        'full-stack developer', 'front-end developer', 'back-end developer',
        'web developer', 'mobile developer', 'ios developer', 'android developer',
        'software developer', 'application developer', 'systems developer',
        'devops engineer', 'sre', 'site reliability engineer', 'platform engineer',
        'infrastructure engineer', 'cloud engineer', 'solutions engineer',
        'qa engineer', 'quality assurance engineer', 'test engineer', 'sdet',
        'security engineer', 'network engineer', 'systems engineer',
        'embedded engineer', 'firmware engineer', 'hardware engineer',
        
        # Data & ML
        'data scientist', 'senior data scientist', 'data analyst', 'business analyst',
        'machine learning engineer', 'ml engineer', 'ai engineer', 'data engineer',
        'analytics engineer', 'bi developer', 'research scientist', 'research engineer',
        
        # Leadership
        'tech lead', 'technical lead', 'team lead', 'engineering manager',
        'director of engineering', 'vp of engineering', 'cto', 'cio',
        'software architect', 'solutions architect', 'enterprise architect',
        'principal engineer', 'distinguished engineer', 'fellow',
        
        # Product & Design
        'product manager', 'senior product manager', 'product owner', 'scrum master',
        'project manager', 'program manager', 'technical program manager',
        'ui/ux designer', 'ux designer', 'ui designer', 'product designer',
        'graphic designer', 'visual designer', 'interaction designer',
        
        # Other
        'consultant', 'technical consultant', 'it consultant',
        'system administrator', 'database administrator', 'dba',
        'technical writer', 'documentation engineer',
        'intern', 'software intern', 'engineering intern', 'trainee',
    }
    
    # Comprehensive section headers - all CV section types
    SECTION_PATTERNS = {
        # Contact / Header (usually at top, detected differently)
        'contact': r'(?i)^(?:contact|contact\s+information|contact\s+details|personal\s+information|personal\s+details)',
        
        # Professional Summary
        'summary': r'(?i)^(?:summary|profile|about|about\s+me|objective|career\s+objective|professional\s+summary|executive\s+summary|personal\s+statement|overview|professional\s+profile|career\s+summary)',
        
        # Skills sections
        'skills': r'(?i)^(?:skills|core\s+skills|key\s+skills|competencies|expertise|proficiencies|areas\s+of\s+expertise)',
        'technical_skills': r'(?i)^(?:technical\s+skills|tech\s+skills|it\s+skills|programming\s+skills|computer\s+skills|technical\s+proficiencies|technical\s+competencies)',
        'soft_skills': r'(?i)^(?:soft\s+skills|interpersonal\s+skills|personal\s+skills|transferable\s+skills|people\s+skills)',
        'tools': r'(?i)^(?:tools|tools\s+&?\s*technologies|technologies|tech\s+stack|software|applications|platforms|frameworks)',
        
        # Experience sections
        'experience': r'(?i)^(?:experience|work\s+experience|employment|professional\s+experience|work\s+history|career\s+history|employment\s+history|professional\s+background|career\s+experience)',
        'internship': r'(?i)^(?:internship|internships?|internship\s+experience|training|industrial\s+training|practical\s+training)',
        
        # Projects
        'projects': r'(?i)^(?:projects|personal\s+projects|academic\s+projects|portfolio|side\s+projects|notable\s+projects|key\s+projects|project\s+experience|major\s+projects)',
        
        # Education
        'education': r'(?i)^(?:education|academic|qualifications?|academic\s+background|educational\s+background|academic\s+qualifications?|degrees?|academic\s+credentials)',
        
        # Certifications
        'certifications': r'(?i)^(?:certifications?|certificates?|licenses?|credentials|professional\s+certifications?|accreditations?|professional\s+development|training\s+&?\s*certifications?)',
        
        # Achievements
        'achievements': r'(?i)^(?:achievements?|accomplishments?|awards?|honors?|recognition|notable\s+achievements?|key\s+achievements?|accolades)',
        
        # Volunteering / Leadership
        'volunteer': r'(?i)^(?:volunteer|volunteering|volunteer\s+experience|community\s+service|social\s+work|community\s+involvement)',
        'leadership': r'(?i)^(?:leadership|leadership\s+experience|leadership\s+roles?|positions?\s+of\s+responsibility|extracurricular\s+activities|activities)',
        
        # Publications / Research
        'publications': r'(?i)^(?:publications?|papers?|research\s+papers?|articles?|research|research\s+experience|academic\s+publications?|scholarly\s+work)',
        
        # Languages
        'languages': r'(?i)^(?:languages?|language\s+skills|linguistic\s+skills|language\s+proficiency|spoken\s+languages?)',
        
        # Links / Portfolio
        'links': r'(?i)^(?:links?|portfolio|online\s+presence|web\s+links?|social\s+profiles?|github|websites?)',
        
        # Interests
        'interests': r'(?i)^(?:interests?|hobbies|hobbies\s+&?\s*interests|personal\s+interests|extracurricular|passions?)',
        
        # References
        'references': r'(?i)^(?:references?|referees?|professional\s+references?)',
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
            # Contact / Header Information
            'name': None,
            'email': None,
            'phone': None,
            'location': None,
            'linkedin': None,
            'github': None,
            'website': None,
            'portfolio': None,
            
            # Professional Summary
            'summary': None,
            
            # Skills (categorized)
            'skills': [],           # Core/Key skills
            'technical_skills': [], # Technical/IT skills
            'soft_skills': [],      # Interpersonal skills
            'tools': [],            # Tools & Technologies
            
            # Experience
            'experience': [],       # Work experience
            'internship': [],       # Internship experience
            
            # Projects
            'projects': [],
            
            # Education
            'education': [],
            
            # Certifications
            'certifications': [],
            
            # Achievements
            'achievements': [],
            
            # Volunteering / Leadership
            'volunteer': [],
            'leadership': [],
            
            # Publications / Research
            'publications': [],
            
            # Languages
            'languages': [],
            
            # Interests
            'interests': [],
            
            # References
            'references': None,
            
            # Legacy fields for compatibility
            'job_titles': [],
            'organizations': [],
        }
        
        # Extract email using regex
        entities['email'] = self._extract_email(text)
        
        # Extract phone using regex
        entities['phone'] = self._extract_phone(text)
        
        # Extract social links
        entities['linkedin'] = self._extract_linkedin(text)
        entities['github'] = self._extract_github(text)
        entities['website'] = self._extract_website(text)
        
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
        
        # Extract technical skills using keyword matching
        entities['skills'] = self._extract_skills_regex(text)
        
        # Extract technical skills from dedicated section
        if 'technical_skills' in sections:
            entities['technical_skills'] = self._parse_skills_list(sections['technical_skills'])
        elif 'tools' in sections:
            entities['technical_skills'] = self._parse_skills_list(sections['tools'])
        else:
            # Use the main skills as technical skills if no separate section
            entities['technical_skills'] = entities['skills']
        
        # Extract soft skills
        entities['soft_skills'] = self._extract_soft_skills(text)
        
        # Extract tools & technologies
        if 'tools' in sections:
            entities['tools'] = self._parse_skills_list(sections['tools'])
        
        # Extract job titles using keyword matching
        entities['job_titles'] = self._extract_job_titles_regex(text)
        
        # Extract structured education
        if 'education' in sections:
            entities['education'] = self._parse_education(sections['education'])
        else:
            # Try to find education in full text
            entities['education'] = self._parse_education_from_text(text)
        
        # Extract structured experience
        if 'experience' in sections:
            entities['experience'] = self._parse_experience(sections['experience'])
        else:
            # Try to find experience in full text
            entities['experience'] = self._parse_experience_from_text(text)
        
        # Extract internship experience
        if 'internship' in sections:
            entities['internship'] = self._parse_experience(sections['internship'])
        
        # Extract projects
        if 'projects' in sections:
            entities['projects'] = self._parse_projects(sections['projects'])
        
        # Extract certifications
        if 'certifications' in sections:
            entities['certifications'] = self._parse_certifications(sections['certifications'])
        
        # Extract achievements
        if 'achievements' in sections:
            entities['achievements'] = self._parse_achievements(sections['achievements'])
        
        # Extract volunteering experience
        if 'volunteer' in sections:
            entities['volunteer'] = self._parse_experience(sections['volunteer'])
        
        # Extract leadership experience
        if 'leadership' in sections:
            entities['leadership'] = self._parse_experience(sections['leadership'])
        
        # Extract publications
        if 'publications' in sections:
            entities['publications'] = self._parse_publications(sections['publications'])
        
        # Extract languages
        if 'languages' in sections:
            entities['languages'] = self._parse_languages(sections['languages'])
        else:
            entities['languages'] = self._extract_languages_from_text(text)
        
        # Extract interests
        if 'interests' in sections:
            entities['interests'] = self._parse_list_section(sections['interests'])
        
        # Extract references
        if 'references' in sections:
            entities['references'] = sections['references'].strip()
        
        # Extract summary
        if 'summary' in sections:
            entities['summary'] = sections['summary'][:500]  # Limit to 500 chars
        else:
            # Try to extract summary from first paragraph
            entities['summary'] = self._extract_summary_from_text(text)
        
        return entities
    
    def _extract_linkedin(self, text: str) -> Optional[str]:
        """Extract LinkedIn URL."""
        patterns = [
            r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)',
            r'linkedin\.com/in/([a-zA-Z0-9_-]+)',
            r'linkedin:\s*([a-zA-Z0-9_-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                username = match.group(1)
                return f"linkedin.com/in/{username}"
        return None
    
    def _extract_github(self, text: str) -> Optional[str]:
        """Extract GitHub URL."""
        patterns = [
            r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)',
            r'github\.com/([a-zA-Z0-9_-]+)',
            r'github:\s*([a-zA-Z0-9_-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                username = match.group(1)
                if username.lower() not in ['login', 'signup', 'settings']:
                    return f"github.com/{username}"
        return None
    
    def _extract_website(self, text: str) -> Optional[str]:
        """Extract personal website."""
        # Look for portfolio/personal sites
        pattern = r'(?:portfolio|website|site):\s*(https?://[^\s]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Look for generic URLs that aren't social media
        url_pattern = r'https?://(?!(?:www\.)?(?:linkedin|github|twitter|facebook|instagram)\.com)[a-zA-Z0-9.-]+\.[a-z]{2,}'
        match = re.search(url_pattern, text)
        if match:
            return match.group(0)
        return None
    
    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills using keyword matching."""
        text_lower = text.lower()
        skills_found = set()
        
        for skill in self.SOFT_SKILLS:
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                skills_found.add(skill.lower())
        
        return sorted(list(skills_found))
    
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
        
        # Common words to skip
        skip_words = {'resume', 'cv', 'curriculum', 'vitae', 'profile', 'contact', 'address', 'email', 'phone', 'mobile', 'linkedin', 'github'}
        
        # Look at first 7 lines
        for line in lines[:7]:
            # Skip lines with email, phone, or URLs
            if '@' in line or re.search(r'\d{3}[-\s()]\d{3}[-\s()]\d{4}', line) or 'http' in line.lower():
                continue
            
            # Skip if contains skip words
            if any(word in line.lower() for word in skip_words):
                continue
            
            # Skip if line is too long (likely not a name)
            if len(line) > 40:
                continue
            
            # Name patterns: 2-4 capitalized words (handles middle names)
            # Pattern 1: Standard names - "John Smith" or "John Michael Smith"
            name_pattern1 = r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})$'
            match = re.match(name_pattern1, line)
            if match:
                name = match.group(1)
                # Filter out job titles
                if not any(title.lower() in name.lower() for title in self.JOB_TITLES):
                    return name
            
            # Pattern 2: Names with all caps - "JOHN SMITH"
            name_pattern2 = r'^([A-Z]+(?:\s+[A-Z]+){1,3})$'
            match = re.match(name_pattern2, line)
            if match and len(line) < 30:
                name = match.group(1)
                # Convert to title case
                name = name.title()
                if not any(title.lower() in name.lower() for title in self.JOB_TITLES):
                    return name
            
            # Pattern 3: Names with initials - "J. Michael Smith" or "John M. Smith"
            name_pattern3 = r'^([A-Z]\.?\s+)?([A-Z][a-z]+)(\s+[A-Z]\.?\s+)?([A-Z][a-z]+)$'
            match = re.match(name_pattern3, line)
            if match:
                return line
            
            # Pattern 4: Indian/Asian names with first name last - "Surname, FirstName"
            name_pattern4 = r'^([A-Z][a-z]+),\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)$'
            match = re.match(name_pattern4, line)
            if match:
                return f"{match.group(2)} {match.group(1)}"
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location using regex patterns."""
        # Common location patterns
        patterns = [
            r'(?:Location|Address|Based in|City|Living in):\s*([A-Z][a-z]+(?:[\s,]+[A-Z][a-z]+)*(?:,?\s*[A-Z]{2})?)',
            r'📍\s*([A-Z][a-z]+(?:[\s,]+[A-Z][a-z]+)*)',  # Location emoji
            r'\|?\s*([A-Z][a-z]+,\s*[A-Z]{2})\s*\|?',  # City, State (US format)
            r'\|?\s*([A-Z][a-z]+,\s*[A-Z][a-z]+)\s*\|?',  # City, Country
            r'([A-Z][a-z]+,\s*[A-Z][a-z]+,\s*[A-Z]{2})',  # City, State, Country
        ]
        
        # Check first 500 chars (contact section)
        first_part = text[:500]
        
        for pattern in patterns:
            match = re.search(pattern, first_part)
            if match:
                location = match.group(1).strip()
                # Validate it's not a name or common word
                if len(location) >= 3 and not any(title.lower() in location.lower() for title in ['resume', 'cv', 'profile']):
                    return location
        
        # Look for common city names in first 500 chars
        common_cities = [
            # US Cities
            'San Francisco', 'New York', 'Los Angeles', 'Chicago', 'Boston',
            'Seattle', 'Austin', 'Denver', 'Portland', 'Atlanta', 'Miami',
            'San Diego', 'San Jose', 'Philadelphia', 'Phoenix', 'Houston',
            'Dallas', 'Washington DC', 'Washington D.C.', 'Baltimore', 'Detroit',
            'Minneapolis', 'Charlotte', 'Nashville', 'Las Vegas', 'Salt Lake City',
            # International
            'London', 'Paris', 'Berlin', 'Tokyo', 'Singapore', 'Sydney',
            'Toronto', 'Vancouver', 'Montreal', 'Dubai', 'Mumbai', 'Bangalore',
            'Bengaluru', 'Hyderabad', 'Chennai', 'Delhi', 'New Delhi', 'Pune',
            'Hong Kong', 'Shanghai', 'Beijing', 'Seoul', 'Amsterdam', 'Dublin',
            'Zurich', 'Stockholm', 'Copenhagen', 'Melbourne', 'Auckland',
            # UK Cities
            'Manchester', 'Birmingham', 'Edinburgh', 'Glasgow', 'Liverpool',
            'Leeds', 'Bristol', 'Cambridge', 'Oxford',
        ]
        
        for city in common_cities:
            if city.lower() in first_part.lower():
                # Try to get state/country after city
                pattern = rf'{re.escape(city)}(?:,?\s*([A-Z]{{2}}|[A-Z][a-z]+))?'
                match = re.search(pattern, first_part, re.IGNORECASE)
                if match and match.group(1):
                    return f"{city}, {match.group(1)}"
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
            if not section.strip() or len(section.strip()) < 10:
                continue
            
            entry = {
                'degree': None,
                'field': None,
                'institution': None,
                'location': None,
                'year': None,
                'gpa': None,
                'details': section.strip()
            }
            
            lines = [l.strip() for l in section.split('\n') if l.strip()]
            if not lines:
                continue
            
            # Extract degree (Bachelor, Master, PhD, etc.)
            degree_patterns = [
                r'(Bachelor[\'s]*|B\.S\.|B\.A\.|B\.Tech|B\.E\.|B\.Sc\.?|B\.Com\.?)\s*(?:of|in|degree in)?\s*([A-Za-z\s,]+?)(?:\s+from|\s+at|\s*,|\s*\n|$)',
                r'(Master[\'s]*|M\.S\.|M\.A\.|M\.Tech|M\.E\.|M\.Sc\.?|M\.Com\.?|MBA)\s*(?:of|in|degree in)?\s*([A-Za-z\s,]+?)(?:\s+from|\s+at|\s*,|\s*\n|$)',
                r'(Ph\.?D\.?|Doctorate|Doctor of Philosophy)\s*(?:in)?\s*([A-Za-z\s,]+?)(?:\s+from|\s+at|\s*,|\s*\n|$)',
                r'(Associate[\'s]*|Diploma|Certificate)\s*(?:in|of)?\s*([A-Za-z\s,]+?)(?:\s+from|\s+at|\s*,|\s*\n|$)',
            ]
            
            for pattern in degree_patterns:
                degree_match = re.search(pattern, section, re.IGNORECASE)
                if degree_match:
                    entry['degree'] = degree_match.group(1).strip()
                    if degree_match.group(2):
                        field = degree_match.group(2).strip()
                        # Clean up field
                        field = re.sub(r'\s*(from|at|,).*$', '', field, flags=re.IGNORECASE)
                        entry['field'] = field if len(field) > 2 else None
                    break
            
            # Extract year(s)
            year_pattern = r'\b(19|20)\d{2}\b'
            years = re.findall(year_pattern, section)
            if years:
                all_years = re.findall(r'\b((?:19|20)\d{2})\b', section)
                if len(all_years) >= 2:
                    entry['year'] = f"{all_years[0]} - {all_years[-1]}"
                else:
                    entry['year'] = all_years[-1] if all_years else None
            
            # Extract GPA
            gpa_patterns = [
                r'(?:GPA|CGPA|Grade)[\s:]*(\d+\.?\d*)\s*/?\s*(\d+\.?\d*)?',
                r'(\d+\.\d+)\s*/\s*(\d+\.?\d*)\s*(?:GPA|CGPA)?',
            ]
            for pattern in gpa_patterns:
                gpa_match = re.search(pattern, section, re.IGNORECASE)
                if gpa_match:
                    gpa = gpa_match.group(1)
                    scale = gpa_match.group(2) if gpa_match.lastindex >= 2 else None
                    entry['gpa'] = f"{gpa}/{scale}" if scale else gpa
                    break
            
            # Extract institution - look for university/college names
            institution_patterns = [
                r'(?:University|College|Institute|School|Academy)\s+(?:of\s+)?[A-Za-z\s,]+',
                r'[A-Z][a-z]+\s+(?:University|College|Institute|School)',
                r'(?:IIT|NIT|MIT|Stanford|Harvard|Oxford|Cambridge|Berkeley|UCLA|USC|NYU|Columbia)[A-Za-z\s]*',
            ]
            
            for pattern in institution_patterns:
                inst_match = re.search(pattern, section, re.IGNORECASE)
                if inst_match:
                    entry['institution'] = inst_match.group(0).strip()
                    break
            
            # Fallback: Use first or second line if institution not found
            if not entry['institution']:
                for line in lines[:3]:
                    # Skip if line is the degree
                    if entry['degree'] and entry['degree'].lower() in line.lower():
                        continue
                    if len(line) > 5 and line[0].isupper():
                        entry['institution'] = line
                        break
            
            # Extract location
            loc_match = re.search(r'([A-Z][a-z]+,\s*[A-Z]{2})|([A-Z][a-z]+,\s*[A-Z][a-z]+)', section)
            if loc_match:
                entry['location'] = loc_match.group(0)
            
            entries.append(entry)
        
        return entries[:10]  # Limit to 10 education entries
    
    def _parse_education_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract education from full text when no section header found."""
        entries = []
        
        # Common degree patterns
        degree_patterns = [
            r'(Bachelor[\'s]*|Master[\'s]*|PhD|Ph\.D\.|MBA|B\.S\.|M\.S\.|B\.A\.|M\.A\.|B\.Tech|M\.Tech|B\.E\.|M\.E\.|B\.Sc\.|M\.Sc\.|Associate[\'s]*|Diploma)\s+(?:of|in|degree)?\s*([A-Za-z\s,]+?)(?:\s+from|\s+at|\s*,|\s*\n)',
        ]
        
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entry = {
                    'degree': match.group(0).strip(),
                    'institution': None,
                    'year': None,
                    'details': None
                }
                
                # Look for year near the degree mention
                context = text[max(0, match.start()-50):min(len(text), match.end()+100)]
                year_match = re.search(r'\b(19|20)\d{2}\b', context)
                if year_match:
                    entry['year'] = year_match.group(0)
                
                entries.append(entry)
        
        return entries[:5]  # Limit to 5 entries
    
    def _parse_experience_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract experience from full text when no section header found."""
        entries = []
        
        # Look for job title patterns followed by company/date info
        for title in self.JOB_TITLES:
            pattern = rf'\b({re.escape(title)})\b[^\n]*'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entry = {
                    'title': match.group(1),
                    'company': None,
                    'duration': None,
                    'description': None
                }
                
                # Look for company and dates in surrounding context
                context = text[match.start():min(len(text), match.end()+200)]
                
                # Extract company
                company_match = re.search(r'(?:at|@|,)\s+([A-Z][A-Za-z0-9\s&]+)', context)
                if company_match:
                    entry['company'] = company_match.group(1).strip()
                
                # Extract dates
                date_match = re.search(r'(\w+\s+\d{4}|\d{4})\s*[-–—to]+\s*(\w+\s+\d{4}|\d{4}|Present|Current)', context, re.IGNORECASE)
                if date_match:
                    entry['duration'] = date_match.group(0)
                
                entries.append(entry)
        
        return entries[:10]  # Limit to 10 entries
    
    def _parse_projects(self, projects_text: str) -> List[Dict[str, Any]]:
        """Parse projects section into structured entries."""
        entries = []
        
        # Split by double newlines or bullet points
        sections = re.split(r'\n\n+|(?=^\s*[•\-\*])', projects_text, flags=re.MULTILINE)
        
        for section in sections:
            if not section.strip() or len(section.strip()) < 10:
                continue
            
            entry = {
                'name': None,
                'description': None,
                'technologies': [],
                'url': None
            }
            
            lines = [l.strip() for l in section.split('\n') if l.strip()]
            if not lines:
                continue
            
            # First line is usually project name
            entry['name'] = lines[0].lstrip('•-* ')
            
            # Rest is description
            if len(lines) > 1:
                entry['description'] = ' '.join(lines[1:])
            
            # Extract technologies mentioned
            tech_found = []
            section_lower = section.lower()
            for tech in list(self.TECH_SKILLS)[:100]:  # Check top 100 skills
                if tech.lower() in section_lower:
                    tech_found.append(tech)
            entry['technologies'] = tech_found[:10]
            
            # Extract URL if present
            url_match = re.search(r'https?://[^\s]+', section)
            if url_match:
                entry['url'] = url_match.group(0)
            
            entries.append(entry)
        
        return entries[:10]
    
    def _parse_certifications(self, cert_text: str) -> List[Dict[str, Any]]:
        """Parse certifications section."""
        entries = []
        
        lines = [l.strip() for l in cert_text.split('\n') if l.strip()]
        
        for line in lines:
            if len(line) < 5:
                continue
            
            entry = {
                'name': line.lstrip('•-* '),
                'issuer': None,
                'date': None,
                'credential_id': None
            }
            
            # Extract issuer (common patterns)
            issuer_patterns = [
                r'(?:by|from|issued by)\s+([A-Z][A-Za-z\s]+)',
                r'-\s*([A-Z][A-Za-z\s]+)$',
            ]
            for pattern in issuer_patterns:
                match = re.search(pattern, line)
                if match:
                    entry['issuer'] = match.group(1).strip()
                    break
            
            # Extract date
            date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|\b\d{4}\b', line)
            if date_match:
                entry['date'] = date_match.group(0)
            
            entries.append(entry)
        
        return entries[:20]
    
    def _parse_languages(self, lang_text: str) -> List[Dict[str, str]]:
        """Parse languages section."""
        entries = []
        
        # Common proficiency levels
        proficiency_levels = ['native', 'fluent', 'proficient', 'intermediate', 'basic', 'beginner', 'advanced', 'professional', 'conversational', 'elementary']
        
        lines = [l.strip() for l in lang_text.split('\n') if l.strip()]
        
        for line in lines:
            if len(line) < 2:
                continue
            
            entry = {
                'language': line.lstrip('•-* '),
                'proficiency': None
            }
            
            # Extract proficiency level
            line_lower = line.lower()
            for level in proficiency_levels:
                if level in line_lower:
                    entry['proficiency'] = level.capitalize()
                    # Clean the language name
                    entry['language'] = re.sub(rf'\s*[-–:]\s*{level}.*', '', entry['language'], flags=re.IGNORECASE).strip()
                    break
            
            entries.append(entry)
        
        return entries[:10]
    
    def _extract_languages_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract languages from full text."""
        common_languages = [
            'English', 'Spanish', 'French', 'German', 'Chinese', 'Mandarin',
            'Japanese', 'Korean', 'Portuguese', 'Italian', 'Russian', 'Arabic',
            'Hindi', 'Tamil', 'Telugu', 'Bengali', 'Urdu', 'Dutch', 'Swedish',
            'Norwegian', 'Danish', 'Finnish', 'Polish', 'Greek', 'Turkish',
            'Hebrew', 'Thai', 'Vietnamese', 'Indonesian', 'Malay', 'Tagalog'
        ]
        
        found = []
        for lang in common_languages:
            if re.search(rf'\b{lang}\b', text, re.IGNORECASE):
                found.append({'language': lang, 'proficiency': None})
        
        return found[:10]
    
    def _extract_summary_from_text(self, text: str) -> Optional[str]:
        """Extract summary/objective from first paragraphs."""
        lines = text.split('\n')
        
        # Skip first few lines (usually name/contact info)
        content_lines = []
        started = False
        
        for i, line in enumerate(lines[2:12]):  # Check lines 3-12
            line = line.strip()
            if not line:
                if started and content_lines:
                    break  # End of paragraph
                continue
            
            # Skip lines that look like contact info
            if '@' in line or re.search(r'\d{3}[-\s]\d{3}[-\s]\d{4}', line):
                continue
            
            # Skip section headers
            is_header = False
            for pattern in self.SECTION_PATTERNS.values():
                if re.match(pattern, line):
                    is_header = True
                    break
            
            if is_header:
                break
            
            # Add to content
            if len(line) > 20:  # Meaningful content
                content_lines.append(line)
                started = True
        
        if content_lines:
            summary = ' '.join(content_lines)
            return summary[:500] if len(summary) > 500 else summary
        
        return None
    
    def _parse_experience(self, experience_text: str) -> List[Dict[str, Any]]:
        """Parse experience section into structured entries."""
        entries = []
        
        # Split by double newlines or date patterns that typically start new entries
        # Also split when we see a job title pattern
        sections = re.split(r'\n\n+', experience_text)
        
        current_entry = None
        
        for section in sections:
            if not section.strip():
                continue
            
            entry = {
                'title': None,
                'company': None,
                'location': None,
                'duration': None,
                'description': [],
                'raw_text': section.strip()
            }
            
            lines = [l.strip() for l in section.split('\n') if l.strip()]
            if not lines:
                continue
            
            # First line is usually job title or company
            first_line = lines[0]
            
            # Check if first line is a job title
            title_found = False
            for title in self.JOB_TITLES:
                if title.lower() in first_line.lower():
                    entry['title'] = first_line
                    title_found = True
                    break
            
            if not title_found:
                # First line might be company name
                entry['company'] = first_line
                if len(lines) > 1:
                    entry['title'] = lines[1]
            
            # Extract dates/duration from any line
            date_pattern = r'(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+\d{4}|\b\d{4})\s*[-–—to]+\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+\d{4}|\b\d{4}|Present|Current|Now)'
            for line in lines:
                date_match = re.search(date_pattern, line, re.IGNORECASE)
                if date_match:
                    entry['duration'] = date_match.group(0)
                    break
            
            # Extract company using various patterns
            if not entry['company']:
                company_patterns = [
                    r'(?:at|@|,)\s+([A-Z][A-Za-z0-9\s&.]+(?:Inc\.|Corp\.|LLC|Ltd\.|Co\.|Group|Technologies|Solutions|Systems|Software)?)',
                    r'\|\s*([A-Z][A-Za-z0-9\s&.]+)',
                    r'Company:\s*([A-Za-z0-9\s&.]+)',
                ]
                for pattern in company_patterns:
                    for line in lines[:3]:
                        match = re.search(pattern, line)
                        if match:
                            entry['company'] = match.group(1).strip()
                            break
                    if entry['company']:
                        break
            
            # Extract location
            for line in lines[:3]:
                loc_match = re.search(r'([A-Z][a-z]+,\s*[A-Z]{2})|([A-Z][a-z]+,\s*[A-Z][a-z]+)', line)
                if loc_match:
                    entry['location'] = loc_match.group(0)
                    break
            
            # Rest of lines are description (bullet points)
            description_lines = []
            for line in lines[1:]:
                # Skip lines that are dates, locations, or company info
                if entry['duration'] and entry['duration'] in line:
                    continue
                if entry['location'] and entry['location'] in line:
                    continue
                if line.startswith(('•', '-', '*', '○', '◦', '▪', '–')):
                    description_lines.append(line.lstrip('•-*○◦▪– '))
                elif len(line) > 30:  # Likely a description line
                    description_lines.append(line)
            
            entry['description'] = description_lines[:10]  # Limit to 10 bullet points
            
            entries.append(entry)
        
        return entries[:15]  # Limit to 15 experience entries

    def _parse_skills_list(self, skills_text: str) -> List[str]:
        """Parse a skills section into a list of skills."""
        skills = []
        
        # Split by common delimiters
        lines = skills_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove bullet points
            line = line.lstrip('•-*○◦▪– ')
            
            # Split by commas, pipes, or semicolons
            for skill in re.split(r'[,|;]', line):
                skill = skill.strip()
                if skill and len(skill) > 1 and len(skill) < 50:
                    skills.append(skill)
        
        return list(set(skills))[:50]  # Deduplicate and limit

    def _parse_achievements(self, achievements_text: str) -> List[Dict[str, Any]]:
        """Parse achievements/awards section."""
        entries = []
        
        lines = [l.strip() for l in achievements_text.split('\n') if l.strip()]
        
        for line in lines:
            if len(line) < 5:
                continue
            
            entry = {
                'title': line.lstrip('•-*○◦▪– '),
                'date': None,
                'issuer': None,
                'description': None
            }
            
            # Extract date
            date_match = re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|\b\d{4}\b', line)
            if date_match:
                entry['date'] = date_match.group(0)
            
            # Extract issuer (common patterns)
            issuer_patterns = [
                r'(?:by|from|at|awarded by)\s+([A-Z][A-Za-z\s&]+)',
            ]
            for pattern in issuer_patterns:
                match = re.search(pattern, line)
                if match:
                    entry['issuer'] = match.group(1).strip()
                    break
            
            entries.append(entry)
        
        return entries[:20]

    def _parse_publications(self, pub_text: str) -> List[Dict[str, Any]]:
        """Parse publications/research section."""
        entries = []
        
        lines = [l.strip() for l in pub_text.split('\n') if l.strip()]
        
        current_entry = None
        for line in lines:
            if len(line) < 5:
                continue
            
            # Check if it's a new publication (usually starts with title or author)
            if line[0].isupper() or line.startswith(('•', '-', '*')):
                if current_entry:
                    entries.append(current_entry)
                
                current_entry = {
                    'title': line.lstrip('•-*○◦▪– '),
                    'authors': None,
                    'venue': None,
                    'date': None,
                    'url': None
                }
                
                # Extract date
                date_match = re.search(r'\b(19|20)\d{2}\b', line)
                if date_match:
                    current_entry['date'] = date_match.group(0)
                
                # Extract URL
                url_match = re.search(r'https?://\S+', line)
                if url_match:
                    current_entry['url'] = url_match.group(0)
        
        if current_entry:
            entries.append(current_entry)
        
        return entries[:20]

    def _parse_list_section(self, section_text: str) -> List[str]:
        """Parse a simple list section (interests, hobbies, etc.)."""
        items = []
        
        # Split by common delimiters
        lines = section_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove bullet points
            line = line.lstrip('•-*○◦▪– ')
            
            # Split by commas, pipes, or semicolons
            for item in re.split(r'[,|;]', line):
                item = item.strip()
                if item and len(item) > 1 and len(item) < 100:
                    items.append(item)
        
        return list(set(items))[:20]  # Deduplicate and limit


# Singleton instance
_extractor_instance = None

def get_cv_extractor() -> CVExtractor:
    """Get or create singleton CV extractor instance."""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = CVExtractor()
    return _extractor_instance
