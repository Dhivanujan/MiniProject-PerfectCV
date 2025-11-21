import io
import os
import re
import json
import logging
import zipfile
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from xml.etree import ElementTree as ET
from PyPDF2 import PdfReader
from fpdf import FPDF
import google.generativeai as genai
from app.utils.ai_utils import setup_gemini, get_valid_model, improve_sentence

logger = logging.getLogger(__name__)


ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}


def allowed_file(filename):
    """Return True if filename has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


DOMAIN_KEYWORDS = {
    "software": [
        "python", "java", "c++", "c#", "javascript", "react", "node", "docker", "kubernetes",
        "aws", "azure", "gcp", "ci/cd", "rest", "graphql", "microservices", "sql", "nosql"
    ],
    "data_science": [
        "python", "r", "sql", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "machine learning",
        "nlp", "computer vision", "statistics", "data visualization"
    ],
    "product": ["roadmap", "roadmapping", "stakeholders", "a/b testing", "user research", "metrics", "okrs", "prds"],
    "design": ["ux", "ui", "figma", "prototyping", "wireframes", "user research", "visual design"],
    "marketing": ["seo", "content", "campaign", "analytics", "growth", "google ads", "facebook ads", "email marketing"]
}

STANDARD_SECTION_ORDER: List[Tuple[str, str]] = [
    ("contact_information", "Contact Information"),
    ("professional_summary", "Professional Summary"),
    ("skills", "Skills"),
    ("work_experience", "Work Experience"),
    ("projects", "Projects"),
    ("education", "Education"),
    ("certifications", "Certifications"),
    ("achievements", "Achievements / Awards"),
    ("languages", "Languages"),
    ("volunteer_experience", "Volunteer Experience"),
    ("additional_information", "Additional Information"),
]

SOFT_SKILL_KEYWORDS: Tuple[str, ...] = (
    "communication", "leadership", "collaboration", "team", "problem", "critical", "creative",
    "adaptability", "negotiation", "stakeholder", "mentoring", "mentorship", "coaching", "presentation",
    "interpersonal", "time management", "conflict", "organization", "organisational", "empathy",
)

TECH_SKILL_HINTS: Tuple[str, ...] = (
    "python", "java", "c++", "c#", "go", "javascript", "typescript", "sql", "nosql", "aws", "azure",
    "gcp", "docker", "kubernetes", "linux", "react", "angular", "vue", "node", "django", "flask",
    "spring", "ml", "machine", "data", "analytics", "cloud", "devops", "git", "spark", "hadoop",
    "tensorflow", "pytorch", "api", "rest", "graphql", "microservice", "etl", "pandas", "numpy",
    "tableau", "power bi", "excel", "jira", "confluence", "salesforce", "php", "html", "css",
)

LANGUAGE_NAMES: Tuple[str, ...] = (
    "english", "french", "spanish", "german", "hindi", "mandarin", "cantonese", "arabic", "portuguese",
    "italian", "japanese", "korean", "tamil", "telugu", "malayalam", "urdu", "bengali", "marathi",
    "russian", "polish", "dutch", "swedish", "danish", "norwegian", "turkish", "thai", "vietnamese",
    "indonesian", "malay", "finnish", "greek", "hebrew", "punjabi", "romanian", "czech", "slovak",
)

SECTION_SYNONYMS: Dict[str, Tuple[str, ...]] = {
    "about": (
        "about",
        "summary",
        "professional summary",
        "profile",
        "career summary",
        "objective",
        "career objective",
        "about me",
        "contact",
        "contact information",
        "contact details",
        "personal information",
        "highlights",
    ),
    "skills": (
        "skills",
        "technical skills",
        "key skills",
        "core skills",
        "competencies",
        "skill set",
        "areas of expertise",
        "summary of skills",
    ),
    "experience": (
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "career history",
        "employment",
        "work history",
        "relevant experience",
        "experience highlights",
    ),
    "projects": ("projects", "project experience", "project work", "portfolio", "case studies"),
    "education": (
        "education",
        "academic background",
        "qualifications",
        "education & training",
        "academic history",
        "academics",
    ),
    "achievements": (
        "achievements",
        "accomplishments",
        "awards",
        "honors",
        "recognitions",
        "events",
        "extracurricular",
        "activities",
    ),
    "certifications": (
        "certifications",
        "certification",
        "licenses",
        "licences",
        "credentials",
        "certificates",
        "training",
        "licensure",
    ),
    "volunteer": (
        "volunteer",
        "volunteer experience",
        "volunteer work",
        "community service",
        "community involvement",
        "service",
    ),
    "languages": (
        "languages",
        "language proficiency",
        "language skills",
        "spoken languages",
        "languages known",
    ),
    "other": (
        "additional information",
        "other",
        "interests",
        "activities",
        "extra",
        "hobbies",
        "additional details",
    ),
}

ALL_SECTION_KEYWORDS = tuple(sorted({kw for values in SECTION_SYNONYMS.values() for kw in values}))
ALL_SECTION_HEADINGS_PATTERN = "|".join(re.escape(keyword) for keyword in ALL_SECTION_KEYWORDS)

SECTION_KEYS: Tuple[str, ...] = (
    "about",
    "summary",
    "skills",
    "experience",
    "education",
    "projects",
    "achievements",
    "certifications",
    "volunteer",
    "languages",
    "other",
)

INLINE_HEADING_PATTERN = re.compile(r"^(?P<label>[A-Za-z][\w &+/().']{1,80})\s*[:\-–]\s*(?P<body>.+)$")
BULLET_PREFIXES: Tuple[str, ...] = ("-", "*", "•")


def _normalize_heading_label(label: str) -> str:
    cleaned = (label or "").strip().lower()
    cleaned = re.sub(r"[:\-–]+$", "", cleaned)
    cleaned = re.sub(r"[^a-z0-9&+/ ]+", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _build_section_heading_index() -> Dict[str, str]:
    index: Dict[str, str] = {}
    for key, keywords in SECTION_SYNONYMS.items():
        for keyword in keywords:
            normalized = _normalize_heading_label(keyword)
            if normalized and normalized not in index:
                index[normalized] = key
    return index


SECTION_HEADING_INDEX = _build_section_heading_index()


def _heading_lookup(label: str) -> Optional[str]:
    normalized = _normalize_heading_label(label)
    if not normalized:
        return None
    if normalized in SECTION_HEADING_INDEX:
        return SECTION_HEADING_INDEX[normalized]
    for keyword, key in SECTION_HEADING_INDEX.items():
        if normalized.startswith(keyword) and len(normalized.split()) <= len(keyword.split()) + 2:
            return key
    return None


def normalize_text(text):
    """Clean and normalize text while preserving meaningful spacing and structure."""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Preserve newlines that likely indicate sections or list items
    text = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1\n\n\2', text)
    
    # Ensure list items and bullets start on new lines
    text = re.sub(r'\s*([•\-\*]|\d+\.)\s*', r'\n\1 ', text)
    
    # Fix collapsed words (missing spaces after punctuation)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    
    # Fix email addresses that may be split
    text = re.sub(r'(\w+)\s+@\s+(\w+)', r'\1@\2', text)
    
    # Remove repeated newlines while preserving paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Clean up extra spaces in lines
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()


def _safe_decode_bytes(data: bytes, encoding: str = "utf-8") -> str:
    """Best-effort decode for binary CV uploads."""
    try:
        return data.decode(encoding, errors="ignore")
    except Exception:
        try:
            return data.decode("latin-1", errors="ignore")
        except Exception:
            return ""


def extract_text_from_docx_bytes(file_bytes: bytes) -> str:
    """Extract plain text from a DOCX file without external dependencies."""
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
            xml_content = archive.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile, RuntimeError) as exc:
        logger.warning("DOCX extraction failed: %s", exc)
        return normalize_text(_safe_decode_bytes(file_bytes))

    try:
        tree = ET.fromstring(xml_content)
    except ET.ParseError as exc:
        logger.warning("DOCX XML parsing failed: %s", exc)
        return normalize_text(_safe_decode_bytes(file_bytes))

    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: List[str] = []

    for paragraph in tree.iter(f"{namespace}p"):
        texts: List[str] = []
        for node in paragraph.iter(f"{namespace}t"):
            if node.text:
                texts.append(node.text)
        if texts:
            paragraphs.append("".join(texts))

    raw_text = "\n".join(paragraphs)
    return normalize_text(raw_text)


def extract_text_from_doc_bytes(file_bytes: bytes) -> str:
    """Fallback extraction for legacy DOC files using best-effort decoding."""
    # Binary .doc format is proprietary; without external tools we attempt best-effort decoding.
    decoded = _safe_decode_bytes(file_bytes)
    return normalize_text(decoded)


def _dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    """Return a list with duplicates removed while preserving original ordering."""
    seen = set()
    ordered: List[str] = []
    for item in items:
        if not item:
            continue
        normalized = item.strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(normalized)
    return ordered


def _split_section_lines(section_text: str) -> List[str]:
    """Convert multiline/bulleted section text into normalized line items."""
    if not section_text:
        return []
    entries: List[str] = []
    for raw_line in section_text.split("\n"):
        cleaned = raw_line.strip().lstrip("-•* ").strip()
        if cleaned:
            entries.append(cleaned)
    return entries

def _extract_section_by_keywords(text: str, keywords: Sequence[str]) -> str:
    """Best-effort extraction of a section block given keyword variants."""
    if not keywords:
        return ""
    heading_group = "|".join(re.escape(keyword) for keyword in keywords if keyword)
    if not heading_group:
        return ""

    inline_pattern = rf"(?:^|\n)\s*(?:{heading_group})\b[^\n]*[:\-]\s*(?P<inline>[^\n\r]+)"
    match = re.search(inline_pattern, text, flags=re.IGNORECASE)
    if match:
        return match.group("inline").strip()

    stop_pattern = rf"(?=\n\s*(?:{ALL_SECTION_HEADINGS_PATTERN})\b|$)" if ALL_SECTION_HEADINGS_PATTERN else r"(?=$)"
    block_pattern = rf"(?:^|\n)\s*(?:{heading_group})\b[^\n]*\n(?P<body>.*?){stop_pattern}"
    match = re.search(block_pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group("body").strip()
    return ""


def _augment_sections_from_keywords(text: str, sections: Dict[str, str]) -> None:
    """Populate missing sections using keyword heuristics."""
    for key, keywords in SECTION_SYNONYMS.items():
        if not keywords or sections.get(key):
            continue
        snippet = _extract_section_by_keywords(text, keywords)
        if snippet:
            sections[key] = (sections.get(key, "") + "\n" + snippet).strip()


def _infer_skills_from_text(text: str) -> List[str]:
    """Collect technical keywords within free-form text as fallback skills."""
    found: List[str] = []
    seen = set()
    text_lower = text.lower()
    for keyword in TECH_SKILL_HINTS:
        if keyword and keyword.lower() in text_lower:
            cleaned = keyword.strip()
            normalized = cleaned if cleaned.isupper() else cleaned.title()
            if normalized.lower() in seen:
                continue
            seen.add(normalized.lower())
            found.append(normalized)
    return found


def _categorize_skills(skills: Sequence[str]) -> Dict[str, List[str]]:
    """Split skills into technical, soft, and other buckets using heuristics."""
    technical: List[str] = []
    soft: List[str] = []
    other: List[str] = []

    for raw_skill in _dedupe_preserve_order(skills):
        lowered = raw_skill.lower()
        if any(keyword in lowered for keyword in TECH_SKILL_HINTS) or re.search(r"[0-9+/]|\bapi\b", lowered):
            technical.append(raw_skill)
            continue
        if any(keyword in lowered for keyword in SOFT_SKILL_KEYWORDS):
            soft.append(raw_skill)
            continue
        # Heuristic: short uppercase abbreviations (e.g., PMP, PRINCE2) are likely certifications/technical
        if len(raw_skill) <= 5 and raw_skill.isupper():
            technical.append(raw_skill)
        else:
            other.append(raw_skill)

    return {
        "technical": technical,
        "soft": soft,
        "other": other,
    }


def _format_skills_section(skills: Dict[str, List[str]]) -> str:
    """Format categorized skills into a readable string."""
    parts: List[str] = []
    if skills.get("technical"):
        parts.append("Technical: " + ", ".join(skills["technical"]))
    if skills.get("soft"):
        parts.append("Soft: " + ", ".join(skills["soft"]))
    if skills.get("other"):
        parts.append("Additional: " + ", ".join(skills["other"]))
    return "\n".join(parts)


def _format_contact_section(contact: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
    """Return formatted contact block string and sanitized contact dict."""
    sanitized = {
        "name": (contact.get("name") or "" ).strip() or "Not Provided",
        "email": (contact.get("email") or "" ).strip() or "Not Provided",
        "phone": (contact.get("phone") or "" ).strip() or "Not Provided",
        "location": (contact.get("location") or "" ).strip() or "Not Provided",
        "linkedin": (contact.get("linkedin") or "" ).strip(),
        "github": (contact.get("github") or "" ).strip(),
        "website": (contact.get("website") or "" ).strip(),
    }
    lines = [
        f"Name: {sanitized['name']}",
        f"Email: {sanitized['email']}",
    ]
    if sanitized["phone"] != "Not Provided":
        lines.append(f"Phone: {sanitized['phone']}")
    if sanitized["location"] != "Not Provided":
        lines.append(f"Location: {sanitized['location']}")
    for field in ("linkedin", "github", "website"):
        value = sanitized.get(field)
        if value:
            lines.append(f"{field.title()}: {value}")
    return "\n".join(lines), sanitized


def _format_experience_section(experience: Sequence[Dict[str, str]]) -> str:
    """Format structured experience entries into ATS-friendly bullet lists."""
    entries: List[str] = []
    for job in experience:
        if not isinstance(job, dict):
            continue
        title = (job.get("title") or "Role").strip() or "Role"
        company = (job.get("company") or "Company").strip() or "Company"
        dates = (job.get("dates") or "").strip()
        location = (job.get("location") or "").strip()
        header_parts = [title, "|", company]
        header = " ".join(part for part in header_parts if part)
        if location:
            header = f"{header} ({location})"
        if dates:
            header = f"{header} — {dates}"

        raw_points = [p.strip() for p in job.get("points", []) if isinstance(p, str) and p.strip()]
        if raw_points:
            prepped = "\n".join(f"- {point}" for point in raw_points)
            strengthened = strengthen_experience_points(prepped)
            bullet_lines = [line for line in strengthened.splitlines() if line.strip()]
        else:
            bullet_lines = []

        section_lines = [header]
        section_lines.extend(bullet_lines)
        entries.append("\n".join(section_lines))

    return "\n\n".join(entries)


def _format_projects_section(projects: Sequence[Dict[str, str]]) -> str:
    blocks: List[str] = []
    for project in projects:
        if not isinstance(project, dict):
            continue
        name = (project.get("name") or "Project").strip()
        if not name:
            continue
        desc = (project.get("desc") or project.get("description") or "").strip()
        technologies = project.get("technologies") or project.get("tech") or []
        lines = [name]
        if desc:
            lines.append(f"- {desc}")
        if technologies:
            tech = ", ".join(_dedupe_preserve_order(str(t) for t in technologies))
            if tech:
                lines.append(f"- Tech: {tech}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _format_education_section(education: Sequence[Dict[str, str]]) -> str:
    entries: List[str] = []
    for edu in education:
        if not isinstance(edu, dict):
            continue
        degree = (edu.get("degree") or "Qualification").strip()
        school = (edu.get("school") or edu.get("institution") or "Institution").strip()
        year = (edu.get("year") or edu.get("date") or "").strip()
        line = degree
        if school:
            line = f"{line} — {school}"
        if year:
            line = f"{line} ({year})"
        entries.append(line)
    return "\n".join(entries)


def _format_list_section(items: Sequence[str], prefix: str = "- ") -> str:
    cleaned = _dedupe_preserve_order(str(item) for item in items)
    if not cleaned:
        return ""
    return "\n".join(f"{prefix}{item}" for item in cleaned)


def _extract_languages(sections: Dict[str, str]) -> List[str]:
    """Identify languages from any section content using simple heuristics."""
    candidates: List[str] = []
    search_space = "\n".join(str(v) for v in sections.values() if v)
    for match in re.finditer(r"languages?\s*[:\-]\s*([^\n]+)", search_space, flags=re.IGNORECASE):
        fragment = match.group(1)
        parts = re.split(r"[,;/]", fragment)
        candidates.extend(p.strip() for p in parts if p.strip())
    for name in LANGUAGE_NAMES:
        pattern = rf"\b{name}\b"
        if re.search(pattern, search_space, flags=re.IGNORECASE):
            candidates.append(name.title())
    return _dedupe_preserve_order(candidates)

def extract_text_from_pdf(file_stream):
    """Extract text from PDF while preserving structure and formatting."""
    try:
        reader = PdfReader(file_stream)
        sections = []
        
        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if not page_text:
                    continue
                    
                # Try to extract font information for better section detection
                sections_in_page = []
                current_section = []
                
                for line in page_text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Likely section header if all caps or ends with colon
                    if line.isupper() or line.endswith(':'):
                        if current_section:
                            sections_in_page.append('\n'.join(current_section))
                            current_section = []
                        current_section.append(line)
                    else:
                        current_section.append(line)
                
                if current_section:
                    sections_in_page.append('\n'.join(current_section))
                
                # Join sections with double newline for clear separation
                sections.extend(sections_in_page)
                
            except Exception as page_error:
                logger.warning(f"Error extracting text from page: {page_error}")
                # Continue to next page on error
                continue
        
        # Join all sections and normalize the text
        text = '\n\n'.join(sections)
        return normalize_text(text)
        
    except Exception as e:
        logger.exception("Failed to extract text from PDF: %s", e)
        # Attempt to rewind the stream
        try:
            file_stream.seek(0)
        except Exception:
            pass
        return ""


def extract_text_from_any(file_bytes: bytes, filename: Optional[str]) -> str:
    """Extract text from supported CV formats (PDF, DOC, DOCX, raw text)."""
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(io.BytesIO(file_bytes))
    if name.endswith(".docx"):
        return extract_text_from_docx_bytes(file_bytes)
    if name.endswith(".doc"):
        return extract_text_from_doc_bytes(file_bytes)

    decoded = _safe_decode_bytes(file_bytes)
    return normalize_text(decoded)


def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    font_path = os.path.join(os.path.dirname(__file__), "DejaVuSans.ttf")
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)
    else:
        pdf.set_font("Helvetica", size=12)
        text = text.encode("latin-1", "replace").decode("latin-1")
    pdf.set_auto_page_break(auto=True, margin=15)

    def get_width(indent=0):
        return pdf.w - pdf.l_margin - pdf.r_margin - indent

    # If caller passed a dict, treat it as structured sections and render template
    if isinstance(text, dict):
        sections = text
        # Header placeholder
        header = sections.get("header") or "NAME\nEmail: you@example.com | Phone: +1-555-555-5555\nLocation: City, Country"
        for hline in header.split("\n"):
            pdf.set_font(pdf.font_family, "B", 14)
            pdf.cell(0, 8, hline, ln=True)
        pdf.ln(4)

        def render_section(title, content):
            if not content:
                return
            pdf.set_font(pdf.font_family, "B", 12)
            pdf.cell(0, 8, title, ln=True)
            pdf.set_font(pdf.font_family, size=11)
            # render bullets specially
            for line in str(content).split("\n"):
                line = line.strip()
                if not line:
                    pdf.ln(2)
                    continue
                if line.startswith("-"):
                    bullet = "•" if pdf.font_family == "DejaVu" else "-"
                    pdf.cell(6)
                    pdf.multi_cell(get_width(6), 6, f"{bullet} {line.lstrip('- ').strip()}")
                else:
                    pdf.multi_cell(get_width(), 6, line)
            pdf.ln(2)

        # Render in sensible order
        render_section("PROFESSIONAL SUMMARY", sections.get("about") or sections.get("summary"))
        render_section("KEY SKILLS", sections.get("skills"))
        render_section("WORK EXPERIENCE", sections.get("work_experience") or sections.get("experience"))
        render_section("PROJECTS", sections.get("projects"))
        render_section("ACHIEVEMENTS & EXTRACURRICULAR", sections.get("achievements") or sections.get("other"))
        render_section("EDUCATION", sections.get("education"))
    else:
        heading_prefixes = (
            "education",
            "experience",
            "skills",
            "projects",
            "contact",
            "professional summary",
            "key skills",
            "work experience",
            "certifications",
            "achievements",
            "languages",
            "additional information",
        )
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                pdf.ln(5)
                continue
            if line.lower().startswith(heading_prefixes):
                pdf.set_font(pdf.font_family, "B", 14)
                pdf.cell(0, 10, line, ln=True)
                pdf.set_font(pdf.font_family, size=12)
            elif line.startswith(("-", "*")) or (line and line[0:2].isdigit()):
                indent = 10
                pdf.cell(indent)
                bullet = "•" if pdf.font_family == "DejaVu" else "-"
                safe_text = line.lstrip("-*0123456789. ")
                pdf.multi_cell(get_width(indent), 8, f"{bullet} {safe_text}")
            else:
                pdf.multi_cell(get_width(), 8, line)
    # Use 'S' to get PDF as string and encode to bytes (avoid passing BytesIO to FPDF.output)
    pdf_str = pdf.output(dest='S')
    pdf_data = pdf_str.encode('latin-1')
    pdf_bytes = io.BytesIO(pdf_data)
    pdf_bytes.seek(0)
    return pdf_bytes


def _score_by_keywords(text, domain):
    """Return (score_fraction, missing_keywords, found_keywords) based on domain keywords."""
    if not domain:
        return 0.0, [], []
    domain = domain.lower().replace(" ", "_")
    keywords = DOMAIN_KEYWORDS.get(domain, [])
    text_lower = text.lower()
    found = [k for k in keywords if k.lower() in text_lower]
    missing = [k for k in keywords if k.lower() not in text_lower]
    score = 0.0
    if keywords:
        score = min(1.0, len(found) / len(keywords))
    return score, missing, found


def compute_ats_score(text, domain=None):
    """Compute a heuristic ATS score (0-100).

    Factors:
    - presence of contact info
    - keyword match for domain
    - presence of skills section
    - reasonable length
    """
    score = 0
    text_lower = text.lower()
    # contact info
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text_lower):
        score += 20
    if re.search(r"\+?\d[\d \-()]{7,}\d", text_lower):
        score += 10

    # keyword match
    kw_score, missing, found = _score_by_keywords(text, domain)
    score += int(30 * kw_score)

    # skills section
    if re.search(r"\bskills\b", text_lower):
        score += 15

    # reasonable length
    words = len(re.findall(r"\w+", text))
    if 200 <= words <= 1200:
        score += 15
    elif words < 200:
        score += 5

    return min(100, score), missing, found


def extract_sections(text):
    """Split text into structured sections using heading-aware heuristics."""
    sections: Dict[str, str] = {key: "" for key in SECTION_KEYS}

    if not text:
        return sections

    lines = text.split('\n')
    current_key = "about"
    buffer: List[str] = []

    def _commit_buffer():
        if not buffer:
            return
        block = "\n".join(buffer).strip()
        if not block:
            buffer.clear()
            return
        existing = sections.get(current_key, "")
        sections[current_key] = (existing + "\n" + block).strip() if existing else block
        buffer.clear()

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if buffer and buffer[-1] != "":
                buffer.append("")
            continue

        candidate = line
        candidate_is_bullet = False
        if candidate[0] in BULLET_PREFIXES:
            candidate = candidate.lstrip(''.join(BULLET_PREFIXES) + ' ')
            candidate = candidate.strip()
            candidate_is_bullet = True

        heading_key: Optional[str] = None
        inline_body: Optional[str] = None
        inline_match = INLINE_HEADING_PATTERN.match(candidate)
        if inline_match:
            heading_key = _heading_lookup(inline_match.group("label"))
            inline_body = inline_match.group("body").strip()
        if not heading_key:
            heading_key = _heading_lookup(candidate)

        if heading_key and (not candidate_is_bullet or len(candidate.split()) <= 5):
            _commit_buffer()
            current_key = heading_key
            if inline_body:
                buffer.append(inline_body)
            continue

        buffer.append(line)

    _commit_buffer()

    _augment_sections_from_keywords(text, sections)

    for key in sections:
        sections[key] = re.sub(r'\n{2,}', '\n\n', sections[key].strip())

    sections["summary"] = sections.get("about", sections.get("summary", ""))

    return sections


def build_standardized_sections(cv_text: str) -> Dict[str, object]:
    """Return structured sections aligned with the standardized preview spec."""
    normalized_text = normalize_text(cv_text or "")
    raw_sections = extract_sections(normalized_text)

    about_text = raw_sections.get("about", "")
    contact_info = extract_contact_info(about_text)
    contact_block, sanitized_contact = _format_contact_section(contact_info)

    # Remove lines that contain contact details from summary
    summary_lines: List[str] = []
    for line in about_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", stripped):
            continue
        if re.search(r"\+?[\d\s\-()]{7,}", stripped):
            continue
        if any(keyword in stripped.lower() for keyword in ("email", "phone", "mobile", "linkedin", "github")):
            continue
        summary_lines.append(stripped)
    summary_text = " ".join(summary_lines).strip()

    skills_candidates: List[str] = []
    raw_skills = raw_sections.get("skills", "")
    if raw_skills:
        skills_candidates = [s.strip() for s in re.split(r"[,;\n]", raw_skills) if s.strip()]
    if not skills_candidates:
        skills_candidates = _infer_skills_from_text(normalized_text)
    categorized_skills = _categorize_skills(skills_candidates)
    skills_formatted = _format_skills_section(categorized_skills)

    experience_structured = parse_experience_section(raw_sections.get("experience", ""))
    experience_formatted = _format_experience_section(experience_structured)

    projects_structured = parse_projects_section(raw_sections.get("projects", ""))
    projects_formatted = _format_projects_section(projects_structured)

    education_structured = parse_education_section(raw_sections.get("education", ""))
    education_formatted = _format_education_section(education_structured)

    volunteer_structured = parse_experience_section(raw_sections.get("volunteer", ""))

    certifications_list: List[str] = []
    achievements_list: List[str] = []

    for line in _split_section_lines(raw_sections.get("certifications", "")):
        certifications_list.append(line)

    for source in (raw_sections.get("achievements", ""), raw_sections.get("other", "")):
        if not source:
            continue
        for line in _split_section_lines(source):
            lowered = line.lower()
            if any(keyword in lowered for keyword in ("cert", "license", "licence", "credential", "honor", "award")):
                certifications_list.append(line)
            else:
                achievements_list.append(line)

    languages: List[str] = []
    if raw_sections.get("languages"):
        for chunk in re.split(r"[,/;\n]", raw_sections["languages"]):
            cleaned = chunk.strip()
            if not cleaned:
                continue
            languages.append(cleaned.title() if cleaned.islower() else cleaned)
    languages.extend(_extract_languages(raw_sections))
    languages = _dedupe_preserve_order(languages)

    additional_text = raw_sections.get("other", "") or ""
    additional_text = additional_text.strip()

    structured = {
        "contact_information": {**sanitized_contact, "block": contact_block},
        "professional_summary": summary_text,
        "skills": {**categorized_skills, "formatted": skills_formatted},
        "work_experience": experience_structured,
        "projects": projects_structured,
        "education": education_structured,
        "certifications": _dedupe_preserve_order(certifications_list),
        "achievements": _dedupe_preserve_order(achievements_list),
        "languages": languages,
        "volunteer_experience": volunteer_structured,
        "additional_information": additional_text,
    }

    return structured


def _structured_to_preview(structured: Dict[str, object]) -> Tuple[List[Dict[str, str]], Dict[str, str], str]:
    """Convert structured sections into ordered preview sections and optimized text."""
    ordered_sections: List[Dict[str, str]] = []
    sections_map: Dict[str, str] = {}

    for key, label in STANDARD_SECTION_ORDER:
        content = ""
        if key == "contact_information":
            block = structured.get(key, {}).get("block") if isinstance(structured.get(key), dict) else ""
            content = block or "Not Provided"
        elif key == "professional_summary":
            summary = structured.get(key) or ""
            content = summary if summary else "Not Provided"
        elif key == "skills":
            skills_block = ""
            if isinstance(structured.get(key), dict):
                skills_block = structured[key].get("formatted") or ""
            content = skills_block or "Not Provided"
        elif key == "work_experience":
            content = _format_experience_section(structured.get(key, [])) if structured.get(key) else "Not Provided"
        elif key == "projects":
            content = _format_projects_section(structured.get(key, [])) if structured.get(key) else "Not Provided"
        elif key == "education":
            content = _format_education_section(structured.get(key, [])) if structured.get(key) else "Not Provided"
        elif key in ("certifications", "achievements", "languages"):
            items = structured.get(key) or []
            content = _format_list_section(items) if items else "Not Provided"
        elif key == "volunteer_experience":
            content = _format_experience_section(structured.get(key, [])) if structured.get(key) else "Not Provided"
        elif key == "additional_information":
            addl = structured.get(key) or ""
            content = addl if addl else "Not Provided"

        clean_content = content.strip()
        if not clean_content:
            clean_content = "Not Provided"

        sections_map[key] = clean_content
        ordered_sections.append({
            "key": key,
            "label": label,
            "content": clean_content,
        })

    optimized_lines: List[str] = []
    for section in ordered_sections:
        optimized_lines.append(section["label"].upper())
        optimized_lines.append(section["content"])
        optimized_lines.append("")

    optimized_text = "\n".join(optimized_lines).strip()
    return ordered_sections, sections_map, optimized_text


def _structured_to_legacy_sections(structured: Dict[str, object]) -> Dict[str, str]:
    """Create a legacy sections dict compatible with existing template utilities."""
    contact = structured.get("contact_information", {}) if isinstance(structured.get("contact_information"), dict) else {}
    summary = structured.get("professional_summary") or ""
    summary_block = "\n".join(line for line in (contact.get("block"), summary) if line)

    skills_section = structured.get("skills", {}) if isinstance(structured.get("skills"), dict) else {}
    all_skills: List[str] = []
    for bucket in ("technical", "soft", "other"):
        all_skills.extend(skills_section.get(bucket) or [])
    skills_text = ", ".join(_dedupe_preserve_order(all_skills))

    experience_text = _format_experience_section(structured.get("work_experience", []))
    projects_text = _format_projects_section(structured.get("projects", []))
    education_text = _format_education_section(structured.get("education", []))

    achievements_combo = _dedupe_preserve_order(
        list(structured.get("certifications", []) or []) + list(structured.get("achievements", []) or [])
    )
    if structured.get("languages"):
        achievements_combo.extend([f"Language: {lang}" for lang in structured.get("languages", [])])
    for volunteer in structured.get("volunteer_experience", []) or []:
        if isinstance(volunteer, dict):
            title = (volunteer.get("title") or "Volunteer").strip()
            organization = (volunteer.get("company") or volunteer.get("organization") or "Organization").strip()
            dates = (volunteer.get("dates") or "").strip()
            entry = f"Volunteer: {title} at {organization}"
            if dates:
                entry = f"{entry} ({dates})"
            achievements_combo.append(entry)

    achievements_text = "\n".join(_dedupe_preserve_order(achievements_combo))

    return {
        "about": summary_block,
        "skills": skills_text,
        "experience": experience_text,
        "projects": projects_text,
        "education": education_text,
        "achievements": achievements_text,
        "other": structured.get("additional_information") or "",
    }


ACTION_VERBS = [
    "led", "built", "designed", "developed", "implemented", "improved", "optimized", "created",
    "reduced", "increased", "managed", "launched", "orchestrated", "analyzed", "automated", "mentored"
]


def normalize_bullets(text):
    """Ensure bullets are on separate lines, start with action verbs where possible."""
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            lines.append("")
            continue
        # turn commas in long sentences into bullets if looks like list
        if "," in line and len(line.split()) > 12 and not line.startswith("-"):
            parts = [p.strip() for p in line.split(",") if p.strip()]
            for p in parts:
                lines.append(f"- {p}")
            continue
        # ensure bullet prefix
        if line[0] in "-*•" or re.match(r"^\d+\.", line):
            # ensure starts with action verb
            content = re.sub(r"^[\-*•\s\d.]+", "", line).strip()
            first_word = content.split()[0].lower() if content else ""
            if first_word not in ACTION_VERBS and content:
                content = ACTION_VERBS[0] + " " + content
            lines.append(f"- {content}")
        else:
            lines.append(line)
    return "\n".join(lines)


def strengthen_experience_points(text):
    """Ensure experience bullets start with action verbs and are concise.

    This is a lightweight, rule-based improvement applied when AI is unavailable.
    """
    if not text:
        return text
    out_lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            out_lines.append("")
            continue
        # if it's a bullet, ensure it begins with an action verb
        is_bullet = line.startswith("-") or line.startswith("*") or line.startswith("•")
        content = line.lstrip('-*• ').strip()
        words = content.split()
        if words:
            first = words[0].lower()
            if first not in ACTION_VERBS:
                # Prepend a sensible action verb
                content = ACTION_VERBS[0].capitalize() + ' ' + content
            else:
                # capitalize first word
                content = words[0].capitalize() + ' ' + ' '.join(words[1:])

        if is_bullet:
            out_lines.append(f"- {content}")
        else:
            out_lines.append(content)

    return '\n'.join(out_lines)


def optimize_cv_rule_based(cv_text: str, job_domain: Optional[str] = None) -> Dict[str, object]:
    """Produce a cleaned, ATS-friendly CV structure without relying on AI."""
    structured = build_standardized_sections(cv_text or "")
    ordered_sections, sections_map, optimized_text = _structured_to_preview(structured)
    structured_payload = build_structured_cv_payload(structured)

    # Compute ATS score and keyword coverage
    ats_score, missing_keywords, found_keywords = compute_ats_score(optimized_text, job_domain)

    suggestions = _generate_suggestions(structured, missing_keywords)

    legacy_sections = _structured_to_legacy_sections(structured)
    template_data = convert_to_template_format(legacy_sections)
    extracted = build_extracted_sections(cv_text, structured_sections=structured)

    return {
        "optimized_text": optimized_text,
        "optimized_cv": optimized_text,
        "optimized_ats_cv": optimized_text,
        "sections": sections_map,
        "ordered_sections": ordered_sections,
        "structured_sections": structured,
        "structured_cv": structured_payload,
        "extracted": extracted,
        "extracted_text": cv_text,
        "suggestions": suggestions,
        "ats_score": ats_score,
        "recommended_keywords": missing_keywords,
        "found_keywords": found_keywords,
        "template_data": template_data,
    }

def parse_experience_section(text):
    """Parse experience section text into structured format.
    
    Handles multiple formats:
    - Job Title at Company (Date Range)
    - Company | Job Title | Dates
    - Date Range: Job Title at Company
    
    Returns list of {title, company, dates, points[]}.
    """
    if not text or not text.strip():
        return []
    
    jobs = []
    current_job = None
    lines = text.split('\n')
    
    # Regex patterns for date ranges
    date_pattern = r'\(([^)]*(?:20|19)\d{2}[^)]*)\)|\[([^\]]*(?:20|19)\d{2}[^\]]*)\]|(\w+\s+\d{4}\s*[-–]\s*(?:\w+\s+)?\d{4}|Present|Current)'
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_job and current_job.get('points'):
                jobs.append(current_job)
                current_job = None
            continue
        
        # Check if this is a new job entry (non-bulleted, contains company/title info)
        if not line.startswith(('-', '•', '*')) and any(sep in line for sep in [' at ', ' | ', ' - ', '–']):
            # Save previous job
            if current_job and (current_job.get('points') or current_job.get('title')):
                jobs.append(current_job)
            
            # Parse new job
            title = ""
            company = ""
            dates = ""
            
            # Extract dates first
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            if date_match:
                dates = date_match.group(1) or date_match.group(2) or date_match.group(3)
                line_without_dates = re.sub(date_pattern, '', line).strip()
            else:
                line_without_dates = line
            
            # Parse title and company
            if ' at ' in line_without_dates:
                title, company = [x.strip() for x in line_without_dates.split(' at ', 1)]
            elif ' | ' in line_without_dates:
                parts = [x.strip() for x in line_without_dates.split('|')]
                if len(parts) == 2:
                    company, title = parts
                elif len(parts) == 3:
                    company, title, dates_alt = parts
                    if not dates:
                        dates = dates_alt
            elif ' - ' in line_without_dates or '–' in line_without_dates:
                sep = ' – ' if '–' in line_without_dates else ' - '
                parts = [x.strip() for x in line_without_dates.split(sep, 1)]
                if len(parts) == 2 and any(year in parts[1] for year in ['20', '19', 'Present']):
                    title = parts[0]
                    dates = parts[1]
                else:
                    title = line_without_dates
            else:
                title = line_without_dates
            
            current_job = {
                'title': title or 'Position',
                'company': company or 'Company',
                'dates': dates or 'Present',
                'points': []
            }
        elif current_job and (line.startswith(('-', '•', '*')) or (current_job and current_job.get('points'))):
            # Bullet point or continuation
            point = line.lstrip('-•* ').strip()
            if point:
                current_job['points'].append(point)
        elif not current_job and line and any(sep in line for sep in [' at ', ' | ', ' - ', '–']):
            # Start new job entry
            title = ""
            company = ""
            dates = ""
            
            date_match = re.search(date_pattern, line, re.IGNORECASE)
            if date_match:
                dates = date_match.group(1) or date_match.group(2) or date_match.group(3)
                line_without_dates = re.sub(date_pattern, '', line).strip()
            else:
                line_without_dates = line
            
            if ' at ' in line_without_dates:
                title, company = [x.strip() for x in line_without_dates.split(' at ', 1)]
            elif ' | ' in line_without_dates:
                parts = [x.strip() for x in line_without_dates.split('|')]
                if len(parts) >= 2:
                    company = parts[0]
                    title = parts[1]
            
            current_job = {
                'title': title or 'Position',
                'company': company or 'Company',
                'dates': dates or 'Present',
                'points': [line] if line.startswith(('-', '•', '*')) else []
            }
    
    # Add last job if it has content
    if current_job and (current_job.get('points') or current_job.get('title')):
        jobs.append(current_job)
    
    # Filter out empty jobs and return
    return [j for j in jobs if j.get('title') and j.get('company')]


def parse_education_section(text):
    """Parse education section into structured format.
    
    Handles formats:
    - Degree - University (Year)
    - University | Degree | Year
    - Degree (Year)
    - Bachelor of Science in Computer Science - MIT (2020)
    
    Returns list of {degree, school, year}.
    """
    if not text or not text.strip():
        return []
    
    education = []
    year_pattern = r'\(([^)]*(?:20|19)\d{2}[^)]*)\)|\[([^\]]*)\]|(?:^|\s)(\d{4})(?:\s|$)|(?:graduating|graduated|expected)\s+(\d{4}|present)'
    
    for line in text.split('\n'):
        line = line.strip()
        if not line or line.startswith(('-', '•', '*')):
            # Skip bullets - they might be details
            if line and line.startswith(('-', '•', '*')):
                point = line.lstrip('-•* ').strip()
                # Only process if looks like an achievement detail
                continue
            continue
        
        degree = ""
        school = ""
        year = ""
        
        # Extract year/date
        year_match = re.search(year_pattern, line, re.IGNORECASE)
        if year_match:
            year = year_match.group(1) or year_match.group(2) or year_match.group(3) or year_match.group(4)
            line_without_year = re.sub(year_pattern, '', line, flags=re.IGNORECASE).strip()
        else:
            line_without_year = line
        
        # Split by common separators
        if ' - ' in line_without_year or '–' in line_without_year:
            sep = ' – ' if '–' in line_without_year else ' - '
            parts = [x.strip() for x in line_without_year.split(sep, 1)]
            if len(parts) == 2:
                # Could be "Degree - School" or "School - Degree"
                # Try to detect which is which
                if any(deg_term in parts[0].lower() for deg_term in ['bachelor', 'master', 'phd', 'diploma', 'certificate', 'associate', 'degree', 'b.', 'm.']):
                    degree = parts[0]
                    school = parts[1]
                elif any(deg_term in parts[1].lower() for deg_term in ['bachelor', 'master', 'phd', 'diploma', 'certificate', 'associate', 'degree', 'b.', 'm.']):
                    school = parts[0]
                    degree = parts[1]
                else:
                    # Assume first is degree, second is school
                    degree = parts[0]
                    school = parts[1]
        elif ' | ' in line_without_year:
            parts = [x.strip() for x in line_without_year.split('|')]
            if len(parts) == 2:
                school = parts[0]
                degree = parts[1]
            elif len(parts) >= 3:
                school = parts[0]
                degree = parts[1]
        else:
            # Can't parse cleanly, treat whole line as degree
            degree = line_without_year
        
        # Only add if we have at least degree or school
        if degree or school:
            education.append({
                'degree': degree or 'Qualification',
                'school': school or 'Institution',
                'year': year or 'Present'
            })
    
    return education


def parse_projects_section(text):
    """Parse projects section into structured format.
    
    Handles formats:
    - Project Name
      - Description
    - Project Name - Description
    - Project Name | Description
    
    Returns list of {name, desc, technologies[]}.
    """
    if not text or not text.strip():
        return []
    
    projects = []
    current_project = None
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            if current_project and current_project.get('name'):
                projects.append(current_project)
                current_project = None
            continue
        
        if line.startswith(('-', '•', '*')):
            # Bullet point - treat as description or tech
            content = line.lstrip('-•* ').strip()
            if current_project:
                if not current_project.get('desc'):
                    current_project['desc'] = content
                elif 'technologies' not in current_project:
                    current_project['technologies'] = [content]
                else:
                    current_project['technologies'].append(content)
            continue
        
        # Non-bullet line - could be project name or name-desc combination
        if ' - ' in line or '–' in line or ' | ' in line:
            sep = ' – ' if '–' in line else (' | ' if ' | ' in line else ' - ')
            parts = [x.strip() for x in line.split(sep, 1)]
            
            if current_project and current_project.get('name'):
                projects.append(current_project)
            
            current_project = {
                'name': parts[0],
                'desc': parts[1] if len(parts) > 1 else '',
                'technologies': []
            }
        else:
            # Simple project name
            if current_project and current_project.get('name'):
                projects.append(current_project)
            
            current_project = {
                'name': line,
                'desc': '',
                'technologies': []
            }
    
    # Add last project
    if current_project and current_project.get('name'):
        projects.append(current_project)
    
    # Clean up empty entries
    return [p for p in projects if p.get('name')]


def _generate_suggestions(structured: Dict[str, object], missing_keywords: Sequence[str]) -> List[Dict[str, str]]:
    """Create actionable suggestions based on structured content gaps."""
    suggestions: List[Dict[str, str]] = []

    summary = structured.get("professional_summary") or ""
    if len(summary.split()) < 25:
        suggestions.append({
            "category": "summary",
            "message": "Expand the professional summary to highlight 2-3 quantifiable achievements and core strengths.",
        })

    skills = structured.get("skills", {}) if isinstance(structured.get("skills"), dict) else {}
    if not skills.get("technical"):
        suggestions.append({
            "category": "skills",
            "message": "Add a dedicated technical skills line with relevant tools, frameworks, and platforms.",
        })
    if not skills.get("soft"):
        suggestions.append({
            "category": "skills",
            "message": "Include soft skills such as leadership, stakeholder communication, or team collaboration.",
        })

    experience = structured.get("work_experience", []) or []
    if not experience:
        suggestions.append({
            "category": "experience",
            "message": "Add recent work experience with job titles, companies, dates, and impact-driven bullet points.",
        })
    else:
        for job in experience:
            points = job.get("points") or []
            if len(points) < 2:
                suggestions.append({
                    "category": "experience",
                    "message": f"Add at least two bullet points quantifying impact for {job.get('title') or 'your roles'}.",
                })
                break

    if structured.get("projects") and all(not (proj.get("desc") or proj.get("technologies")) for proj in structured.get("projects", [])):
        suggestions.append({
            "category": "projects",
            "message": "Provide concise descriptions for projects, emphasizing scope, tech stack, and outcomes.",
        })

    if structured.get("education"):
        missing_dates = any(not edu.get("year") for edu in structured.get("education"))
        if missing_dates:
            suggestions.append({
                "category": "education",
                "message": "Add graduation years or expected completion dates for each education entry.",
            })
    else:
        suggestions.append({
            "category": "education",
            "message": "List your highest qualifications with institution names and completion years.",
        })

    if missing_keywords:
        suggestions.append({
            "category": "keywords",
            "message": f"Incorporate role-specific keywords such as: {', '.join(missing_keywords[:10])}.",
        })

    if not structured.get("languages"):
        suggestions.append({
            "category": "languages",
            "message": "Add a languages section if you are proficient in multiple languages relevant to the role.",
        })

    additional = structured.get("additional_information") or ""
    if additional and len(additional.split()) > 120:
        suggestions.append({
            "category": "format",
            "message": "Condense additional information into short bullet points to maintain readability.",
        })

    return suggestions


def convert_to_template_format(sections):
    """Convert raw sections dict into format expected by ResumeTemplate.jsx.
    
    Improved extraction of contact info and structured parsing of all sections.
    """
    # Defensive: ensure sections is a dict (AI may return a string or null for sections)
    if not isinstance(sections, dict):
        sections = {}
    
    # Extract contact info from about/summary section
    about = sections.get('about', '').strip()
    
    # Initialize contact info
    contact_info = {
        'name': 'Your Name',
        'email': 'email@example.com',
        'phone': '+1 (555) 000-0000',
        'location': 'City, Country'
    }
    
    # Try to extract contact details from first lines
    if about:
        lines = about.split('\n')
        extracted = extract_contact_info(about)
        contact_info['name'] = extracted['name'] or contact_info['name']
        contact_info['email'] = extracted['email'] or contact_info['email']
        contact_info['phone'] = extracted['phone'] or contact_info['phone']
        contact_info['location'] = extracted['location'] or contact_info['location']
        
        # Remove contact info from summary text (keep only the actual summary)
        summary_lines = []
        for line in lines:
            # Skip email, phone, location lines
            if not any(re.search(pattern, line) for pattern in [
                r'[\w.+-]+@[\w-]+\.[\w.-]+',
                r'\+?[\d\s\-()]{10,}',
                r'^(location|city|address|based in):', 
                r'^(phone|mobile|email|website):'
            ]):
                summary_lines.append(line)
        
        about = '\n'.join(summary_lines).strip()
    
    # Build labeled contact string for readability
    contact_parts = []
    if contact_info.get('email'):
        contact_parts.append(f"email: {contact_info['email']}")
    if contact_info.get('phone') and contact_info['phone'] != '+1 (555) 000-0000':
        contact_parts.append(f"phone: {contact_info['phone']}")
    if contact_info.get('location') and contact_info['location'] != 'City, Country':
        contact_parts.append(f"location: {contact_info['location']}")
    contact_str = " | ".join(contact_parts) if contact_parts else 'Not Provided'
    
    # Parse skills into list
    skills_text = sections.get('skills', '').strip()
    skills = [s.strip() for s in re.split(r'[,;]|\n', skills_text) if s.strip()]
    
    # Parse structured sections
    template_data = {
        'name': contact_info['name'] or 'Not Provided',
        'contact': contact_str or 'Not Provided',
        'summary': about or 'Not Provided',
        'skills': skills or [],
        'experience': parse_experience_section(sections.get('experience', '')),
        'projects': parse_projects_section(sections.get('projects', '')),
        'education': parse_education_section(sections.get('education', '')),
        'certifications': []  # Optional section
    }

    # Add certifications from dedicated or achievements sections
    cert_sources = (
        sections.get('certifications', ''),
        sections.get('achievements', ''),
    )
    certs: List[str] = []
    for source in cert_sources:
        if not source:
            continue
        for line in source.split('\n'):
            entry = line.strip().lstrip('-•* ')
            if entry:
                certs.append(entry)
    if certs:
        template_data['certifications'] = _dedupe_preserve_order(certs)

    return template_data


def build_extracted_sections(cv_text: str, structured_sections: Optional[Dict[str, object]] = None) -> Dict[str, object]:
    """Return a cleaned, structured extracted representation of the CV."""
    structured = structured_sections or build_standardized_sections(cv_text or "")

    contact_info = structured.get("contact_information", {}) if isinstance(structured.get("contact_information"), dict) else {}
    skills_dict = structured.get("skills", {}) if isinstance(structured.get("skills"), dict) else {}

    extracted = {
        "header": {
            "name": contact_info.get("name") or "Not Provided",
            "email": contact_info.get("email") or "Not Provided",
            "phone": contact_info.get("phone") or "Not Provided",
            "location": contact_info.get("location") or "Not Provided",
            "linkedin": contact_info.get("linkedin") or "Not Provided",
            "github": contact_info.get("github") or "Not Provided",
            "website": contact_info.get("website") or "Not Provided",
        },
        "professional_summary": structured.get("professional_summary") or "Not Provided",
        "skills": _dedupe_preserve_order(
            (skills_dict.get("technical") or []) + (skills_dict.get("soft") or []) + (skills_dict.get("other") or [])
        ),
        "experience": structured.get("work_experience") or [],
        "projects": structured.get("projects") or [],
        "education": structured.get("education") or [],
        "certifications": structured.get("certifications") or [],
        "achievements": structured.get("achievements") or [],
        "languages": structured.get("languages") or [],
        "volunteer": structured.get("volunteer_experience") or [],
        "additional": {
            "other": structured.get("additional_information") or "Not Provided",
        },
    }

    return extracted


def extract_contact_info(text):
    """Extract contact information including links using keyword-aware heuristics."""
    contact = {
        'name': '',
        'email': '',
        'phone': '',
        'location': '',
        'linkedin': '',
        'github': '',
        'website': ''
    }

    lines = [line.strip() for line in (text or '').split('\n')]
    nonempty_lines = [line for line in lines if line]

    email_pattern = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
    phone_pattern = re.compile(r'\+?[\d\s\-()]{7,}\d')
    linkedin_pattern = re.compile(r'(?:https?://|www\.)?linkedin\.com/[\w\-/]+', re.IGNORECASE)
    github_pattern = re.compile(r'(?:https?://|www\.)?github\.com/[\w\-/]+', re.IGNORECASE)
    url_pattern = re.compile(r'(?:https?://|www\.)[\w./-]+', re.IGNORECASE)

    location_keywords = ('city', 'state', 'country', 'address', 'location', 'based in', 'remote', '•')

    def _looks_like_name(line: str) -> bool:
        if not line or len(line) > 80:
            return False
        if email_pattern.search(line) or phone_pattern.search(line):
            return False
        if _heading_lookup(line):
            return False
        tokens = [token for token in re.split(r'\s+', line) if token]
        if not tokens or len(tokens) > 6:
            return False
        if any(any(char.isdigit() for char in token) for token in tokens):
            return False
        capitalized = sum(1 for token in tokens if token[0].isupper())
        return capitalized >= max(1, len(tokens) - 1)

    for line in nonempty_lines:
        lower = line.lower()
        if not contact['email']:
            email_match = email_pattern.search(line)
            if email_match:
                contact['email'] = email_match.group(0)
        if not contact['phone']:
            phone_match = phone_pattern.search(line)
            if phone_match:
                contact['phone'] = phone_match.group(0).strip()
        if not contact['linkedin']:
            match = linkedin_pattern.search(line)
            if match:
                contact['linkedin'] = _normalize_url(match.group(0))
        if not contact['github']:
            match = github_pattern.search(line)
            if match:
                contact['github'] = _normalize_url(match.group(0))
        if not contact['website']:
            match = url_pattern.search(line)
            if match:
                url = match.group(0)
                if 'linkedin.com' not in url.lower() and 'github.com' not in url.lower():
                    contact['website'] = _normalize_url(url)
        if not contact['location'] and any(keyword in lower for keyword in location_keywords):
            if 'email' not in lower and 'phone' not in lower and 'mobile' not in lower:
                contact['location'] = line
        if not contact['name']:
            name_label = re.match(r'^(?:name|full name)\s*[:\-–]\s*(.+)', line, re.IGNORECASE)
            if name_label:
                contact['name'] = name_label.group(1).strip()
                continue
            if email_pattern.search(line):
                before_email = line.split(email_pattern.search(line).group(0))[0].strip(' ,|-')
                if _looks_like_name(before_email):
                    contact['name'] = before_email
                    continue
            phone_in_line = phone_pattern.search(line)
            if phone_in_line:
                before_phone = line.split(phone_in_line.group(0))[0].strip(' ,|-')
                if _looks_like_name(before_phone):
                    contact['name'] = before_phone
                    continue
            if _looks_like_name(line):
                contact['name'] = line

    if not contact['email']:
        match = email_pattern.search(text)
        if match:
            contact['email'] = match.group(0)
    if not contact['phone']:
        match = phone_pattern.search(text)
        if match:
            contact['phone'] = match.group(0).strip()
    if not contact['location']:
        for line in nonempty_lines:
            lower = line.lower()
            if any(keyword in lower for keyword in location_keywords) and 'email' not in lower and 'phone' not in lower:
                contact['location'] = line
                break

    if not contact['website']:
        match = url_pattern.search(text)
        if match:
            url = match.group(0)
            if 'linkedin.com' not in url.lower() and 'github.com' not in url.lower():
                contact['website'] = _normalize_url(url)

    if not contact['name'] and nonempty_lines:
        candidate = nonempty_lines[0]
        if _looks_like_name(candidate):
            contact['name'] = candidate

    return contact
    

def _clean_text(value: Optional[str]) -> str:
    if not value:
        return ""
    stripped = value.strip()
    return "" if stripped.lower() == "not provided" else stripped


def _clean_list(values: Optional[Sequence[str]]) -> List[str]:
    cleaned: List[str] = []
    if not values:
        return cleaned
    for value in values:
        if value is None:
            continue
        text = _clean_text(str(value))
        if text:
            cleaned.append(text)
    return cleaned


def _normalize_url(url: Optional[str]) -> str:
    if not url:
        return ""
    cleaned = url.strip().strip('.,);')
    if cleaned and not cleaned.lower().startswith(("http://", "https://")):
        cleaned = "https://" + cleaned.lstrip('/')
    return cleaned


def _clean_experience_entries(entries: Optional[Sequence[Dict[str, object]]]) -> List[Dict[str, object]]:
    cleaned_entries: List[Dict[str, object]] = []
    if not entries:
        return cleaned_entries
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        cleaned_entry = {
            "title": _clean_text(entry.get("title") if isinstance(entry.get("title"), str) else str(entry.get("title") or "")),
            "company": _clean_text(entry.get("company") if isinstance(entry.get("company"), str) else str(entry.get("company") or "")),
            "dates": _clean_text(entry.get("dates") if isinstance(entry.get("dates"), str) else str(entry.get("dates") or "")),
            "location": _clean_text(entry.get("location") if isinstance(entry.get("location"), str) else str(entry.get("location") or "")),
            "points": _clean_list(entry.get("points")),
        }
        # Preserve organization field if available
        if entry.get("organization"):
            cleaned_entry["organization"] = _clean_text(
                entry.get("organization") if isinstance(entry.get("organization"), str) else str(entry.get("organization") or "")
            )
        if any(cleaned_entry.values()) or cleaned_entry.get("points"):
            cleaned_entries.append(cleaned_entry)
    return cleaned_entries


def _clean_project_entries(entries: Optional[Sequence[Dict[str, object]]]) -> List[Dict[str, object]]:
    cleaned_projects: List[Dict[str, object]] = []
    if not entries:
        return cleaned_projects
    for project in entries:
        if not isinstance(project, dict):
            continue
        cleaned_project = {
            "name": _clean_text(project.get("name") if isinstance(project.get("name"), str) else str(project.get("name") or "")),
            "description": _clean_text(
                project.get("desc") if isinstance(project.get("desc"), str) else project.get("description") if isinstance(project.get("description"), str) else str(project.get("desc") or project.get("description") or "")
            ),
            "technologies": _clean_list(project.get("technologies") or project.get("tech")),
        }
        if any((cleaned_project["name"], cleaned_project["description"], cleaned_project["technologies"])):
            cleaned_projects.append(cleaned_project)
    return cleaned_projects


def _clean_education_entries(entries: Optional[Sequence[Dict[str, object]]]) -> List[Dict[str, object]]:
    cleaned_education: List[Dict[str, object]] = []
    if not entries:
        return cleaned_education
    for edu in entries:
        if not isinstance(edu, dict):
            continue
        cleaned_entry = {
            "degree": _clean_text(edu.get("degree") if isinstance(edu.get("degree"), str) else str(edu.get("degree") or "")),
            "school": _clean_text(
                edu.get("school") if isinstance(edu.get("school"), str) else edu.get("institution") if isinstance(edu.get("institution"), str) else str(edu.get("school") or edu.get("institution") or "")
            ),
            "year": _clean_text(edu.get("year") if isinstance(edu.get("year"), str) else edu.get("date") if isinstance(edu.get("date"), str) else str(edu.get("year") or edu.get("date") or "")),
        }
        if any(cleaned_entry.values()):
            cleaned_education.append(cleaned_entry)
    return cleaned_education


def build_structured_cv_payload(structured: Dict[str, object]) -> Dict[str, object]:
    """Build the JSON-ready structured CV output aligned with mandatory sections."""
    structured = structured or {}

    contact = structured.get("contact_information") if isinstance(structured.get("contact_information"), dict) else {}
    contact_payload = {
        "name": _clean_text(contact.get("name")),
        "email": _clean_text(contact.get("email")),
        "phone": _clean_text(contact.get("phone")),
        "location": _clean_text(contact.get("location")),
        "linkedin": _clean_text(contact.get("linkedin")),
        "github": _clean_text(contact.get("github")),
        "website": _clean_text(contact.get("website")),
    }

    skills_section = structured.get("skills") if isinstance(structured.get("skills"), dict) else {}
    technical_skills = _clean_list(skills_section.get("technical"))
    soft_skills = _clean_list(skills_section.get("soft"))
    other_skills = _clean_list(skills_section.get("other"))
    formatted_skills = _clean_text(skills_section.get("formatted"))
    all_skills = _dedupe_preserve_order(technical_skills + soft_skills + other_skills)

    structured_skills = {
        "technical": technical_skills,
        "soft": soft_skills,
        "other": other_skills,
        "formatted": formatted_skills,
        "all": all_skills,
    }

    structured_payload = {
        "Contact Information": contact_payload,
        "Summary / Objective": _clean_text(structured.get("professional_summary")),
        "Skills": structured_skills,
        "Work Experience / Employment History": _clean_experience_entries(structured.get("work_experience")),
        "Projects": _clean_project_entries(structured.get("projects")),
        "Education": _clean_education_entries(structured.get("education")),
        "Certifications": _clean_list(structured.get("certifications")),
        "Achievements / Awards": _clean_list(structured.get("achievements")),
        "Languages": _clean_list(structured.get("languages")),
        "Volunteer Experience": _clean_experience_entries(structured.get("volunteer_experience")),
        "Additional Information": _clean_text(structured.get("additional_information")),
    }

    # Ensure placeholders are present if sections empty
    for key, value in structured_payload.items():
        if isinstance(value, str) and not value:
            structured_payload[key] = ""
        elif isinstance(value, list) and not value:
            structured_payload[key] = []
        elif isinstance(value, dict) and not any(v for v in value.values() if v):
            structured_payload[key] = {k: v for k, v in value.items()}

    return structured_payload
def optimize_cv_with_gemini(cv_text, job_domain=None):
    """Attempt to use Gemini to generate a structured JSON output for the optimized CV.

    If AI is not available or JSON parsing fails, raise an exception so callers can fallback.
    """
    configured = setup_gemini()
    model_name = get_valid_model() if configured else None
    if not model_name:
        raise RuntimeError("AI not configured")

    prompt = f"""
You are an assistant that converts a raw CV into a professional, ATS-friendly resume tailored to a target job domain.
Return a JSON object with the following top-level keys: "optimized_text" (string), "sections" (object with summary, skills, experience, education),
"suggestions" (array of objects with category and message), "ats_score" (number 0-100), "recommended_keywords" (array), "found_keywords" (array).

Input CV:
{cv_text}

Target domain: {job_domain or 'general'}

Return ONLY the JSON object and ensure it is parseable.
"""

    model = genai.GenerativeModel(model_name)
    response = model.generate_content([prompt])
    content = response.text.strip() if hasattr(response, "text") and response.text else ""
    # attempt to find JSON in the response
    try:
        # naive find first '{' and last '}' to extract JSON substring
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1 and end > start:
            json_str = content[start:end+1]
            data = json.loads(json_str)
            return data
    except Exception:
        logger.exception("Failed to parse AI response as JSON")
    # if parsing failed, raise so caller falls back
    raise RuntimeError("AI returned unparsable content")


def optimize_cv(cv_text, job_domain=None, use_ai=True):
    """Unified optimizer: try AI (if requested) and fall back to rule-based optimizer.

    Returns dict with keys: optimized_text, sections, template_data, suggestions,
    ats_score, recommended_keywords, found_keywords
    """
    ai_data: Dict[str, object] = {}
    if use_ai:
        try:
            ai_data = optimize_cv_with_gemini(cv_text, job_domain=job_domain) or {}
            if not isinstance(ai_data, dict):
                logger.warning("AI returned non-dict response (null?), ignoring AI output")
                ai_data = {}
        except Exception as exc:
            logger.warning("AI optimization unavailable, falling back to deterministic pipeline: %s", exc)
            ai_data = {}

    rule_based = optimize_cv_rule_based(cv_text, job_domain)

    # Merge AI insights (if any) without overwriting deterministic preview content
    merged = {**rule_based}
    if ai_data:
        for key in ("ats_score", "recommended_keywords", "found_keywords"):
            if key in ai_data and not merged.get(key):
                merged[key] = ai_data[key]
        if ai_data.get("suggestions"):
            current = [s for s in merged.get("suggestions", []) if isinstance(s, dict)]
            ai_suggestions: List[Dict[str, str]] = []
            for suggestion in ai_data.get("suggestions", []):
                if isinstance(suggestion, dict) and suggestion.get("message"):
                    ai_suggestions.append(suggestion)
                elif isinstance(suggestion, str):
                    ai_suggestions.append({"category": "ai", "message": suggestion})

            encoded = _dedupe_preserve_order(
                [json.dumps(s, sort_keys=True) for s in current] +
                [json.dumps(s, sort_keys=True) for s in ai_suggestions]
            )
            merged["suggestions"] = [json.loads(item) for item in encoded]

    return merged

