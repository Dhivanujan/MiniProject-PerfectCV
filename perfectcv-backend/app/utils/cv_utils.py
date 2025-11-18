import io
import os
import re
import json
import logging
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
    text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
    
    # Fix email addresses that may be split
    text = re.sub(r'(\w+)\s+@\s+(\w+)', r'\1@\2', text)
    
    # Remove repeated newlines while preserving paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Clean up extra spaces in lines
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    return text.strip()

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
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                pdf.ln(5)
                continue
            if line.lower().startswith(("education", "experience", "skills", "projects", "contact", "professional summary", "key skills")):
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
    """Split text into structured sections with improved accuracy.
    
    Sections: about, education, experience, projects, achievements, skills, other
    Uses multiple regex passes to handle various formatting styles.
    """
    sections = {
        "about": "",
        "skills": "",
        "experience": "",
        "education": "",
        "projects": "",
        "achievements": "",
        "other": ""
    }
    
    # Enhanced regex with word boundaries for better section detection
    section_pattern = r"\n\s*(?:^|\s)(" \
        r"about|summary|profile|professional\s+summary|" \
        r"skills|key\s+skills|technical\s+skills|" \
        r"experience|work\s+experience|career|employment|" \
        r"education|academic|qualifications|" \
        r"projects?|" \
        r"achievements?|certifications?|volunteer|extracurricular|activities|awards|" \
        r"languages?|interests?|references?" \
        r")\s*[\n:]"
    
    parts = re.split(section_pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    
    if len(parts) <= 1:
        # No sections found - try to split first entry as name/contact
        lines = text.strip().split('\n')
        if lines:
            sections["about"] = '\n'.join(lines)
        return sections
    
    # parts: [before_heading1, heading1, content1, heading2, content2, ...]
    prefix = parts[0].strip()
    if prefix and len(prefix) > 5:  # Only treat as "about" if meaningful
        sections["about"] = prefix
    
    # Process heading-content pairs
    for i in range(1, len(parts), 2):
        if i + 1 >= len(parts):
            break
            
        heading = parts[i].lower().strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        
        if not content:
            continue
        
        # Classify heading and append to appropriate section
        if any(k in heading for k in ("about", "summary", "profile", "professional")):
            sections["about"] = (sections["about"] + "\n" + content).strip()
        elif "skill" in heading:
            sections["skills"] = (sections["skills"] + "\n" + content).strip()
        elif any(k in heading for k in ("experience", "work", "career", "employment")):
            sections["experience"] = (sections["experience"] + "\n" + content).strip()
        elif "education" in heading or "academic" in heading or "qualification" in heading:
            sections["education"] = (sections["education"] + "\n" + content).strip()
        elif "project" in heading:
            sections["projects"] = (sections["projects"] + "\n" + content).strip()
        elif any(k in heading for k in ("achiev", "certif", "volunteer", "extracurr", "activity", "award", "language", "interest", "reference")):
            sections["achievements"] = (sections["achievements"] + "\n" + content).strip()
        else:
            sections["other"] = (sections["other"] + "\n" + content).strip()
    
    # Final cleanup and whitespace normalization
    for k in sections:
        # Remove leading/trailing whitespace and collapse multiple newlines
        sections[k] = re.sub(r'\n{2,}', '\n', sections[k].strip())
    
    return sections


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


def optimize_cv_rule_based(cv_text, job_domain=None):
    """Produce a cleaned, slightly rewritten ATS-friendly CV and suggestions without AI.

    Returns dict with keys: optimized_text, sections, suggestions (list), ats_score, recommended_keywords
    """
    sections = extract_sections(cv_text)
    # normalize bullets inside experience and other, then strengthen bullets to start with action verbs
    raw_experience = normalize_bullets(sections.get("experience", ""))
    try:
        sections["experience"] = strengthen_experience_points(raw_experience)
    except Exception:
        sections["experience"] = raw_experience
    sections["skills"] = re.sub(r"[,;]+", ", ", sections.get("skills", ""))

    # Compose a structured ATS-friendly text using a template
    def format_to_ats_text(sections_dict):
        out = []
        # Header placeholder (name/contact) - left blank for user to replace
        out.append("NAME\nEmail: you@example.com | Phone: +1-555-555-5555\nLocation: City, Country\n")

        if sections_dict.get("summary"):
            out.append("PROFESSIONAL SUMMARY\n" + sections_dict["summary"].strip())

        if sections_dict.get("skills"):
            # ensure skills are comma separated
            skills = sections_dict["skills"].replace("\n", ", ")
            out.append("KEY SKILLS\n" + skills.strip())

        if sections_dict.get("experience"):
            out.append("EXPERIENCE\n" + sections_dict["experience"].strip())

        if sections_dict.get("projects"):
            out.append("PROJECTS\n" + sections_dict["projects"].strip())

        if sections_dict.get("education"):
            out.append("EDUCATION\n" + sections_dict["education"].strip())

        if sections_dict.get("other"):
            out.append("ADDITIONAL INFORMATION\n" + sections_dict["other"].strip())

        # Join with double newlines for readability
        return "\n\n".join(out)

    # Build optimized text from sections (do not invent new facts; reuse cleaned sections)
    try:
        optimized_text = format_to_ats_text(sections)
    except Exception:
        # Fallback to raw text if formatting fails
        optimized_text = cv_text or ""

    # Build extracted structured representation
    extracted = build_extracted_sections(cv_text)

    # The 'optimized_cv' should be a polished version of the optimized_text.
    # We will reuse optimized_text (template) and ensure bullets are strengthened.
    try:
        optimized_cv = optimized_text
    except Exception:
        optimized_cv = optimized_text

    # Compute ATS score and keyword suggestions based on domain
    ats_score, missing_keywords, found_keywords = compute_ats_score(optimized_text, job_domain)

    # Provide lightweight suggestions: missing keywords and formatting hints
    suggestions = []
    if missing_keywords:
        suggestions.append({"category": "keywords", "message": f"Consider adding these keywords: {', '.join(missing_keywords[:10])}"})
    # Suggest adding a skills section if none detected
    if not sections.get("skills"):
        suggestions.append({"category": "format", "message": "Add a Key Skills section to improve ATS matching."})

    # Return a consistent dict expected by callers, plus new structured outputs
    return {
        "optimized_text": optimized_text,
        "optimized_cv": optimized_cv,
        "sections": sections,
        "extracted": extracted,
        "suggestions": suggestions,
        "ats_score": ats_score,
        "recommended_keywords": missing_keywords,
        "found_keywords": found_keywords,
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
    
    # Build contact string
    contact_str = f"{contact_info['email']}"
    if contact_info['phone'] and contact_info['phone'] != '+1 (555) 000-0000':
        contact_str += f" | {contact_info['phone']}"
    if contact_info['location'] and contact_info['location'] != 'City, Country':
        contact_str += f" | {contact_info['location']}"
    
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

    # Add certifications from achievements if any
    if sections.get('achievements'):
        certs = []
        for line in sections['achievements'].split('\n'):
            line = line.strip()
            if line:
                certs.append(line.lstrip('-•* '))
        if certs:
            template_data['certifications'] = certs

    return template_data


def build_extracted_sections(cv_text):
    """Return a cleaned, structured extracted representation of the CV.

    Keys returned:
    - header (dict): personal information (name, email, phone, location)
    - professional_summary (string)
    - skills (list)
    - experience (list of jobs with title, company, dates, points)
    - projects (list)
    - education (list)
    - certifications (list)
    - achievements (list)
    - additional (dict) other sections
    """
    sections = extract_sections(cv_text or "")

    # ensure strings
    for k in ['about', 'skills', 'experience', 'projects', 'education', 'achievements', 'other']:
        sections[k] = (sections.get(k) or "").strip()

    contact = extract_contact_info(sections.get('about', ''))

    template = convert_to_template_format(sections)

    extracted = {
        'header': {
            'name': template.get('name') or contact.get('name') or 'Not Provided',
            'email': contact.get('email') or 'Not Provided',
            'phone': contact.get('phone') or 'Not Provided',
            'location': contact.get('location') or 'Not Provided'
        },
        'professional_summary': sections.get('about') or 'Not Provided',
        'skills': template.get('skills') or [],
        'experience': template.get('experience') or [],
        'projects': template.get('projects') or [],
        'education': template.get('education') or [],
        'certifications': template.get('certifications') or [],
        'achievements': [a for a in (sections.get('achievements') or '').split('\n') if a.strip()] or [],
        'additional': {}
    }

    # Populate additional with anything left in 'other'
    other = sections.get('other')
    if other:
        extracted['additional']['other'] = other
    else:
        extracted['additional']['other'] = 'Not Provided'

    # Ensure Not Provided for empty list/string sections where appropriate
    if not extracted['professional_summary']:
        extracted['professional_summary'] = 'Not Provided'
    if not extracted['skills']:
        extracted['skills'] = []
    if not extracted['experience']:
        extracted['experience'] = []
    if not extracted['projects']:
        extracted['projects'] = []
    if not extracted['education']:
        extracted['education'] = []
    if not extracted['certifications']:
        extracted['certifications'] = []
    if not extracted['achievements']:
        extracted['achievements'] = []

    return extracted


def extract_contact_info(text):
    """Extract name, email, phone, and location from text.
    
    Returns dict with keys: name, email, phone, location
    """
    contact = {
        'name': '',
        'email': '',
        'phone': '',
        'location': ''
    }
    
    lines = text.split('\n')
    
    # First 10 lines are likely to contain name and contact info
    for i, line in enumerate(lines[:min(10, len(lines))]):
        line = line.strip()
        if not line:
            continue
        
        # Extract email
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', line)
        if email_match and not contact['email']:
            contact['email'] = email_match.group(0)
        
        # Extract phone
        phone_match = re.search(r'\+?[\d\s\-()]{10,}', line)
        if phone_match and not contact['phone']:
            phone = phone_match.group(0).strip()
            if re.search(r'\d{7,}', phone):  # At least 7 digits
                contact['phone'] = phone
        
        # Extract location (usually contains city, state/country)
        if any(loc_word in line.lower() for loc_word in ['city', 'state', 'country', 'address', 'location', 'based in', '•']):
            if not (email_match or phone_match or any(keyword in line.lower() for keyword in ['email', 'phone', 'mobile'])):
                contact['location'] = line
            continue
        
        # First non-contact line is likely the name
        if not contact['name'] and not email_match and not phone_match:
            # Skip if it looks like a title or section header
            if not any(keyword in line.lower() for keyword in ['summary', 'profile', 'experience', 'education', 'skills', 'projects', 'certification']):
                # Skip very short lines or lines that look like descriptors
                if len(line) > 3 and not line.isupper():
                    contact['name'] = line
    
    return contact
    


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
    if use_ai:
        try:
            data = optimize_cv_with_gemini(cv_text, job_domain=job_domain)
            # Defensive: if the AI returned null or non-dict (e.g. JSON `null`), treat as failure
            if not isinstance(data, dict):
                logger.warning("AI returned non-dict response (null?), falling back to rule-based")
                data = {}
            # ensure ats_score and recommended keywords exist
            if "ats_score" not in data:
                ats_score, missing, found = compute_ats_score(data.get("optimized_text", cv_text), job_domain)
                data.setdefault("ats_score", ats_score)
                data.setdefault("recommended_keywords", missing)
                data.setdefault("found_keywords", found)
            # Add template-formatted data (handle case where 'sections' exists but is None)
            data['template_data'] = convert_to_template_format(data.get('sections') or {})
            # Always provide a deterministic extracted structure (rule-based) to avoid hallucination
            data['extracted'] = build_extracted_sections(cv_text)
            # Ensure 'optimized_cv' exists (may be named optimized_text or optimized_cv)
            if data.get('optimized_cv'):
                data['optimized_cv'] = data.get('optimized_cv')
            elif data.get('optimized_text'):
                data['optimized_cv'] = data.get('optimized_text')
            else:
                try:
                    fb = optimize_cv_rule_based(cv_text, job_domain)
                    data['optimized_cv'] = fb.get('optimized_cv') or fb.get('optimized_text') or cv_text
                except Exception:
                    data['optimized_cv'] = data.get('optimized_text') or cv_text
            return data
        except Exception as e:
            logger.warning("AI optimization unavailable, falling back to rule-based: %s", e)

    # Rule-based fallback
    data = optimize_cv_rule_based(cv_text, job_domain)
    # Add template-formatted data (handle None)
    data['template_data'] = convert_to_template_format(data.get('sections') or {})
    return data

