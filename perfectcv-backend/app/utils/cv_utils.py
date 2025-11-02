import io
import os
import re
import json
import logging
from PyPDF2 import PdfReader
from fpdf import FPDF
import google.generativeai as genai
from app.utils.ai_utils import setup_gemini, get_valid_model

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
    """Clean and normalize text while preserving meaningful spacing."""
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Preserve newlines that likely indicate sections or list items
    text = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1\n\n\2', text)
    # Ensure list items and bullets start on new lines
    text = re.sub(r'\s*([•\-\*]|\d+\.)\s*', r'\n\1 ', text)
    # Fix collapsed words (missing spaces after punctuation)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
    # Remove repeated newlines while preserving paragraph breaks
    text = re.sub(r'\n{3,}', '\n\n', text)
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
    """Split text into structured sections: about, education, experience, projects, achievements, skills, other.

    Note: the key name for work experience is `experience` (consistent with other helpers).
    """
    sections = {"about": "", "skills": "", "experience": "", "education": "", "projects": "", "achievements": "", "other": ""}
    # Split by a broader set of headings
    parts = re.split(r"\n\s*(about|summary|profile|professional summary|skills|experience|work experience|education|projects|project|achievements|certifications|volunteer|extracurricular|activities)\s*\n", text, flags=re.I)
    if len(parts) <= 1:
        sections["other"] = text.strip()
        return sections
    # parts: [before, heading1, content1, heading2, content2, ...]
    # take pairs
    prefix = parts[0].strip()
    if prefix:
        sections["about"] = prefix
    for i in range(1, len(parts), 2):
        heading = parts[i].lower()
        content = parts[i+1].strip() if i+1 < len(parts) else ""
        if any(k in heading for k in ("about", "summary", "profile")):
            sections["about"] += "\n" + content
        elif "skill" in heading:
            sections["skills"] += "\n" + content
        elif "experience" in heading or "work" in heading:
            sections["experience"] += "\n" + content
        elif "education" in heading:
            sections["education"] += "\n" + content
        elif any(k in heading for k in ("project", "projects")):
            sections["projects"] += "\n" + content
        elif any(k in heading for k in ("achiev", "certif", "volunteer", "extracurr", "activities")):
            sections["achievements"] += "\n" + content
        else:
            sections["other"] += "\n" + content
    # clean
    for k in sections:
        sections[k] = sections[k].strip()
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


def optimize_cv_rule_based(cv_text, job_domain=None):
    """Produce a cleaned, slightly rewritten ATS-friendly CV and suggestions without AI.

    Returns dict with keys: optimized_text, sections, suggestions (list), ats_score, recommended_keywords
    """
    sections = extract_sections(cv_text)
    # normalize bullets inside experience and other
    sections["experience"] = normalize_bullets(sections.get("experience", ""))
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

    # Build optimized text from sections
    try:
        optimized_text = format_to_ats_text(sections)
    except Exception:
        # Fallback to raw text if formatting fails
        optimized_text = cv_text or ""

    # Compute ATS score and keyword suggestions based on domain
    ats_score, missing_keywords, found_keywords = compute_ats_score(optimized_text, job_domain)

    # Provide lightweight suggestions: missing keywords and formatting hints
    suggestions = []
    if missing_keywords:
        suggestions.append({"category": "keywords", "message": f"Consider adding these keywords: {', '.join(missing_keywords[:10])}"})
    # Suggest adding a skills section if none detected
    if not sections.get("skills"):
        suggestions.append({"category": "format", "message": "Add a Key Skills section to improve ATS matching."})

    # Return a consistent dict expected by callers
    return {
        "optimized_text": optimized_text,
        "sections": sections,
        "suggestions": suggestions,
        "ats_score": ats_score,
        "recommended_keywords": missing_keywords,
        "found_keywords": found_keywords,
    }

def parse_experience_section(text):
    """Parse experience section text into structured format for ResumeTemplate.

    Returns list of {title, company, dates, points[]}.
    """
    jobs = []
    current_job = None
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # New job entry typically starts with non-bulleted line
        if not line.startswith(('-', '•', '*')):
            # Save previous job if exists
            if current_job and current_job.get('points'):
                jobs.append(current_job)
            
            # Try to split into title and company/dates
            parts = line.split(' at ', 1)
            if len(parts) == 2:
                title, company = parts
                # Try to extract dates from company line
                company_parts = company.rsplit('(', 1)
                if len(company_parts) == 2:
                    company = company_parts[0].strip()
                    dates = company_parts[1].rstrip(')').strip()
                else:
                    dates = "Present"  # Default if no dates found
            else:
                # Fallback if can't parse cleanly
                title = line
                company = ""
                dates = "Present"
                
            current_job = {
                'title': title,
                'company': company,
                'dates': dates,
                'points': []
            }
        elif current_job:  # Bullet point
            point = line.lstrip('-•* ').strip()
            if point:
                current_job['points'].append(point)
    
    # Add last job
    if current_job and current_job.get('points'):
        jobs.append(current_job)
        
    return jobs


def parse_education_section(text):
    """Parse education section into [{degree, school, year}]."""
    education = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Try to extract components
        # Pattern: Degree - School (Year) or similar
        parts = line.split(' - ', 1)
        if len(parts) == 2:
            degree = parts[0]
            rest = parts[1]
            # Try to extract year
            rest_parts = rest.rsplit('(', 1)
            if len(rest_parts) == 2:
                school = rest_parts[0].strip()
                year = rest_parts[1].rstrip(')').strip()
            else:
                school = rest.strip()
                year = ""
        else:
            # Fallback if can't parse cleanly
            degree = line
            school = ""
            year = ""
            
        education.append({
            'degree': degree,
            'school': school,
            'year': year
        })
    
    return education


def parse_projects_section(text):
    """Parse projects section into [{name, desc}]."""
    projects = []
    current = None
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        if line.startswith(('-', '•', '*')):
            # Bullet point - treat as description
            if current:
                current['desc'] = line.lstrip('-•* ').strip()
                projects.append(current)
                current = None
        else:
            # Non-bullet - treat as project name
            current = {'name': line, 'desc': ''}
    
    # Add last project if pending
    if current:
        projects.append(current)
        
    return projects


def convert_to_template_format(sections):
    """Convert raw sections dict into format expected by ResumeTemplate.jsx."""
    # Defensive: ensure sections is a dict (AI may return a string or null for sections)
    if not isinstance(sections, dict):
        sections = {}
    # Extract name and contact from about/summary if possible
    about = sections.get('about', '').strip()
    name_line = ""
    contact_line = ""
    if about:
        lines = about.split('\n')
        if lines:
            name_line = lines[0]
            if len(lines) > 1:
                contact_line = lines[1]

    # Parse skills into list
    skills_text = sections.get('skills', '').strip()
    skills = [s.strip() for s in re.split(r'[,;]', skills_text) if s.strip()]

    template_data = {
        'name': name_line or 'Your Name',
        'contact': contact_line or 'email@example.com | phone | location',
        'summary': sections.get('about', '').strip(),
        'skills': skills,
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
            return data
        except Exception as e:
            logger.warning("AI optimization unavailable, falling back to rule-based: %s", e)

    # Rule-based fallback
    data = optimize_cv_rule_based(cv_text, job_domain)
    # Add template-formatted data (handle None)
    data['template_data'] = convert_to_template_format(data.get('sections') or {})
    return data

