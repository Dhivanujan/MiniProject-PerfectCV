"""
CV Template Mapper
Maps extracted CV data to the template format expected by the frontend ResumeTemplate component.
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def normalize_cv_for_template(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize extracted CV data into the exact structure expected by ResumeTemplate.
    
    Args:
        cv_data: Raw CV data from various sources (AI extraction, manual parsing, etc.)
        
    Returns:
        Dictionary with normalized structure for ResumeTemplate component
    """
    try:
        logger.info(f"Normalizing CV data. Input keys: {list(cv_data.keys()) if isinstance(cv_data, dict) else 'Not a dict'}")
        
        # Check Personal Information structure
        personal_info_data = cv_data.get("Personal Information", {})
        if personal_info_data:
            logger.info(f"📋 Personal Information keys: {list(personal_info_data.keys()) if isinstance(personal_info_data, dict) else type(personal_info_data)}")
            if isinstance(personal_info_data, dict):
                logger.info(f"📋 Personal Information values: name={personal_info_data.get('name')}, email={personal_info_data.get('email')}")
        else:
            logger.warning("⚠️ Personal Information is empty or missing!")
        
        # Extract contact information from various possible locations
        contact_info = _extract_contact_info(cv_data)
        logger.info(f"Extracted contact: name={contact_info.get('name', 'MISSING')}, email={bool(contact_info.get('email'))}, contact_keys={list(contact_info.keys())}")
        
        # Normalize each section
        template_data = {
            # Contact & Personal Info
            "name": contact_info.get("name", ""),
            "email": contact_info.get("email", ""),
            "phone": contact_info.get("phone", ""),
            "location": contact_info.get("location", ""),
            "linkedin": contact_info.get("linkedin", ""),
            "github": contact_info.get("github", ""),
            
            # Summary
            "summary": _extract_summary(cv_data),
            
            # Skills
            "skills": _extract_skills(cv_data),
            
            # Experience
            "experience": _extract_experience(cv_data),
            
            # Projects
            "projects": _extract_projects(cv_data),
            
            # Education
            "education": _extract_education(cv_data),
            
            # Certifications
            "certifications": _extract_certifications(cv_data),
        }
        
        logger.info(f"Normalized CV - Name: '{template_data['name']}', Email: {bool(template_data['email'])}, "
                   f"Skills: {len(template_data['skills'])}, Experience: {len(template_data['experience'])}, "
                   f"Education: {len(template_data['education'])}, Projects: {len(template_data['projects'])}")
        
        # If critical fields are missing, log detailed warning
        if not template_data['name']:
            logger.warning(f"⚠️ No name extracted! Contact data keys: {list(contact_info.keys())}, "
                          f"CV data top-level keys: {list(cv_data.keys())[:10]}")
        if not template_data['skills']:
            skills_data = cv_data.get('Skills') or cv_data.get('skills')
            logger.warning(f"⚠️ No skills extracted! Skills data type: {type(skills_data)}, "
                          f"Skills keys: {list(skills_data.keys()) if isinstance(skills_data, dict) else 'N/A'}")
        if not template_data['experience']:
            logger.warning(f"⚠️ No experience extracted! Has work_experience key: {bool(cv_data.get('work_experience'))}")
        
        # Log success metrics
        total_fields = sum([
            bool(template_data['name']),
            bool(template_data['email']),
            bool(template_data['summary']),
            len(template_data['skills']) > 0,
            len(template_data['experience']) > 0,
            len(template_data['education']) > 0
        ])
        logger.info(f"✓ Extraction completeness: {total_fields}/6 critical fields populated")
        
        return template_data
        
    except Exception as e:
        logger.error(f"Error normalizing CV data: {e}", exc_info=True)
        return _get_empty_template()


def _extract_with_regex(cv_text: str) -> Dict[str, str]:
    """Extract contact info using regex patterns as fallback."""
    import re
    
    extracted = {}
    
    # Extract email
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, cv_text)
    if email_match:
        extracted['email'] = email_match.group(0)
    
    # Extract phone (various formats)
    phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    phone_matches = re.findall(phone_pattern, cv_text)
    if phone_matches:
        # Take the longest match (likely most complete)
        extracted['phone'] = max(phone_matches, key=len).strip()
    
    # Extract LinkedIn
    linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+/?'
    linkedin_match = re.search(linkedin_pattern, cv_text, re.IGNORECASE)
    if linkedin_match:
        extracted['linkedin'] = linkedin_match.group(0)
    
    # Extract GitHub
    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9-]+/?'
    github_match = re.search(github_pattern, cv_text, re.IGNORECASE)
    if github_match:
        extracted['github'] = github_match.group(0)
    
    # Extract name (first line heuristic)
    lines = cv_text.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        # Name is usually 2-4 words, capitalized, without @ or numbers
        if line and 2 <= len(line.split()) <= 4 and '@' not in line and not any(c.isdigit() for c in line[:10]):
            if line[0].isupper():
                extracted['name'] = line
                break
    
    return extracted

def _extract_contact_info(cv_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract contact information from various data structures with improved accuracy."""
    
    # DIRECT EXTRACTION: Try standard format from build_structured_cv_payload first
    personal_info = cv_data.get("Personal Information")
    if personal_info and isinstance(personal_info, dict):
        # This is the standard format - extract directly
        extracted = {}
        for key in ["name", "email", "phone", "location", "linkedin", "github", "website", "address"]:
            value = personal_info.get(key)
            if value and isinstance(value, str) and value.strip():
                extracted[key] = value.strip()
        
        if extracted and extracted.get('name'):  # Must have at least name
            logger.info(f"✓ Extracted from 'Personal Information': {list(extracted.keys())}")
            return extracted
    
    # Fallback: Try AI-parsed contact_information
    ai_contact = cv_data.get("contact_information", {})
    if ai_contact and isinstance(ai_contact, dict) and ai_contact.get("name"):
        logger.info(f"✓ Using AI-extracted contact_information")
        return {k: v for k, v in ai_contact.items() if v and isinstance(v, str)}
    
    # Regex fallback: Try extracting from raw text if available
    raw_text = cv_data.get("extracted_text") or cv_data.get("raw_text") or ""
    if raw_text and isinstance(raw_text, str) and len(raw_text) > 100:
        logger.info("Attempting regex extraction from raw text")
        regex_extracted = _extract_with_regex(raw_text)
        if regex_extracted and regex_extracted.get('name'):
            logger.info(f"✓ Regex extraction successful: {list(regex_extracted.keys())}")
            return regex_extracted
    
    # Last resort: Try other possible locations
    contact_sources = [
        cv_data.get("Personal Information", {}),  # Capital case
        cv_data.get("personal_information", {}),
        cv_data.get("contact", {}),
        cv_data.get("Contact Information", {}),
        cv_data.get("Contact", {}),
        cv_data.get("personal_info", {}),
        cv_data.get("extracted", {}).get("contact_information", {}) if isinstance(cv_data.get("extracted"), dict) else {},
        cv_data  # Fallback to root level
    ]
    
    contact = {}
    
    for idx, source in enumerate(contact_sources):
        if not isinstance(source, dict) or not source:
            continue
        
        temp_contact = {}
            
        # Extract name from multiple fields
        name = (source.get("name") or 
                source.get("full_name") or 
                source.get("fullName") or 
                source.get("candidate_name") or 
                source.get("Name") or 
                source.get("Full Name") or 
                "")
        
        # Skip if it's placeholder text or too short
        placeholder_names = ["your name", "name", "full name", "candidate name", "applicant", "[name]", "n/a", "resume"]
        
        if name and isinstance(name, str):
            name = name.strip()
            
            # Log the name we're validating
            logger.debug(f"Validating name from source {idx}: '{name}'")
            
            # Skip empty or too short
            if len(name) < 2:
                logger.debug(f"Name too short: '{name}'")
                continue
            
            # Skip placeholders
            if name.lower() in placeholder_names:
                logger.debug(f"Name is placeholder: '{name}'")
                continue
            
            # Skip if all digits
            if name.replace(' ', '').replace('.', '').isdigit():
                logger.debug(f"Name is all digits: '{name}'")
                continue
            
            # Valid name found!
            temp_contact["name"] = name
            logger.info(f"✓ Valid name found from source {idx}: '{name}'")
        
        # Extract email - validate format
        email = source.get("email") or source.get("Email") or ""
        if email and isinstance(email, str) and "@" in email and "." in email:
            temp_contact["email"] = email.strip()
        
        # Extract phone - validate it looks like a phone number
        phone = source.get("phone") or source.get("phone_number") or source.get("Phone") or ""
        # Basic validation - contains digits
        if phone and isinstance(phone, str) and any(c.isdigit() for c in phone):
            temp_contact["phone"] = phone.strip()
        
        # Extract location
        location = source.get("location") or source.get("address") or source.get("city") or source.get("Location") or ""
        # Skip generic placeholders
        if location and isinstance(location, str) and location.lower() not in ["location", "city, country", "city"]:
            temp_contact["location"] = location.strip()
        
        # Extract LinkedIn - validate URL format
        linkedin = source.get("linkedin") or source.get("linkedin_url") or source.get("LinkedIn") or ""
        if linkedin and isinstance(linkedin, str) and ("linkedin.com" in linkedin.lower() or linkedin.startswith("http")):
            temp_contact["linkedin"] = linkedin.strip()
        
        # Extract GitHub - validate URL format
        github = source.get("github") or source.get("github_url") or source.get("GitHub") or ""
        if github and isinstance(github, str) and ("github.com" in github.lower() or github.startswith("http")):
            temp_contact["github"] = github.strip()
        
        # If we found a name in this source, use all data from this source (prioritize consistency)
        if temp_contact.get("name"):
            contact.update(temp_contact)
            break
        # Otherwise, accumulate fields from multiple sources
        elif temp_contact:
            for key, value in temp_contact.items():
                if not contact.get(key):
                    contact[key] = value
    
    # Clean up any remaining empty values
    return {k: v for k, v in contact.items() if v and isinstance(v, str) and v.strip()}


def _extract_summary(cv_data: Dict[str, Any]) -> str:
    """Extract professional summary from various data structures."""
    summary_fields = [
        "professional_summary",
        "Summary / Objective",
        "summary",
        "objective",
        "about",
        "profile",
        "about_me"
    ]
    
    for field in summary_fields:
        summary = cv_data.get(field)
        if summary and isinstance(summary, str) and len(summary.strip()) > 10:
            return summary.strip()
    
    return ""


def _extract_skills_from_text(text: str) -> List[str]:
    """Extract skills using pattern matching from raw text."""
    import re
    
    skills = []
    
    # Common skill section headers
    skill_section_patterns = [
        r'(?:SKILLS?|TECHNICAL SKILLS?|CORE COMPETENCIES|EXPERTISE)\s*:?\s*\n([^\n]+(?:\n[^\n]+){0,10})',
        r'(?:Technologies?|Tools?|Languages?)\s*:?\s*([^\n]+)',
    ]
    
    for pattern in skill_section_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            # Split by common delimiters
            skill_items = re.split(r'[,;\|\n•◦-]', match)
            for item in skill_items:
                item = item.strip()
                if item and 2 < len(item) < 50 and not item.endswith(':'):
                    skills.append(item)
    
    # Known technical skills patterns
    tech_patterns = [
        r'\b(?:Python|Java|JavaScript|C\+\+|C#|Ruby|PHP|Swift|Kotlin|Go|Rust|TypeScript|SQL|HTML|CSS)\b',
        r'\b(?:React|Angular|Vue|Node\.js|Django|Flask|Spring|Laravel|Express)\b',
        r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|CI/CD)\b',
        r'\b(?:MongoDB|PostgreSQL|MySQL|Redis|Elasticsearch)\b',
        r'\b(?:TensorFlow|PyTorch|Scikit-learn|Pandas|NumPy)\b',
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        skills.extend(matches)
    
    return list(set(skills))  # Remove duplicates

def _extract_skills(cv_data: Dict[str, Any]) -> List[str]:
    """Extract and flatten skills from various data structures with improved parsing."""
    skills = []
    
    # Try to get skills from various locations in priority order
    skills_data = (
        cv_data.get("skills") or 
        cv_data.get("Skills") or
        cv_data.get("technical_skills") or 
        cv_data.get("Technical Skills") or
        cv_data.get("core_competencies") or
        cv_data.get("competencies") or
        cv_data.get("expertise") or
        cv_data.get("extracted", {}).get("skills") or
        {}
    )
    
    if isinstance(skills_data, list):
        # Skills is already a list
        for skill in skills_data:
            if skill:
                skill_str = str(skill).strip()
                # Comprehensive placeholder and invalid skill filtering
                invalid_skills = ["skill", "skills", "course", "courses", "technology", "technologies", 
                                 "tool", "tools", "expertise", "competency", "[skill]", "n/a", "-", "•", "*"]
                if (skill_str.lower() not in invalid_skills and 
                    len(skill_str) > 1 and 
                    len(skill_str) < 50 and  # Skills shouldn't be sentences
                    not skill_str.endswith(':') and  # Skip section headers
                    not all(c in '.,;:!?' for c in skill_str)):  # Skip punctuation-only
                    skills.append(skill_str)
    elif isinstance(skills_data, dict):
        # Skills is an object with categories
        for category in ["all", "technical", "soft", "other", "tools", "frameworks", "frameworks_libraries", "languages", "programming", "languages_programming", "formatted"]:
            category_skills = skills_data.get(category, [])
            if isinstance(category_skills, list):
                for s in category_skills:
                    if s:
                        s_str = str(s).strip()
                        # Use comprehensive validation
                        invalid_skills = ["skill", "skills", "course", "courses", "technology", "technologies", 
                                         "tool", "tools", "expertise", "competency", "[skill]", "n/a", "-", "•", "*"]
                        if (s_str.lower() not in invalid_skills and 
                            len(s_str) > 1 and 
                            len(s_str) < 50 and
                            not s_str.endswith(':') and
                            not all(c in '.,;:!?' for c in s_str)):
                            skills.append(s_str)
            elif isinstance(category_skills, str) and category_skills.strip():
                # Split comma-separated skills
                for s in category_skills.split(','):
                    s = s.strip()
                    if s and s.lower() not in ["skill", "course"] and len(s) > 1:
                        skills.append(s)
    elif isinstance(skills_data, str):
        # Skills is a string, split by common delimiters
        skills_str = skills_data.replace('\n', ',').replace(';', ',')
        for s in skills_str.split(','):
            s = s.strip()
            if s and s.lower() not in ["skill", "skills", "course", "courses"] and len(s) > 1:
                skills.append(s)
    
    # Fallback: Try pattern-based extraction from raw text
    if not skills:
        raw_text = cv_data.get("extracted_text") or cv_data.get("raw_text") or ""
        if raw_text and isinstance(raw_text, str):
            logger.info("Using pattern-based skill extraction from raw text")
            skills = _extract_skills_from_text(raw_text)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in skills:
        if not skill or not isinstance(skill, str):
            continue
        skill_lower = skill.lower()
        if skill_lower not in seen and len(skill) > 1:
            seen.add(skill_lower)
            unique_skills.append(skill)
    
    logger.info(f"Extracted {len(unique_skills)} unique skills")
    return unique_skills[:30]  # Limit to 30 skills for clean display


def _extract_experience(cv_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract work experience in normalized format."""
    experience_list = []
    
    # Try to get experience from various locations
    exp_data = (
        cv_data.get("Work Experience / Employment History") or
        cv_data.get("work_experience") or
        cv_data.get("experience") or
        cv_data.get("employment") or
        []
    )
    
    if not isinstance(exp_data, list):
        return []
    
    for exp in exp_data:
        if not isinstance(exp, dict):
            continue
        
        # Extract fields
        title = exp.get("title") or exp.get("role") or exp.get("position") or ""
        company = exp.get("company") or exp.get("employer") or exp.get("organization") or ""
        dates = exp.get("dates") or exp.get("years") or exp.get("duration") or exp.get("period") or ""
        description = exp.get("description") or ""
        
        # Enhanced validation - skip if data looks malformed or contains placeholders
        placeholders_title = ["company", "position", "role", "title", "job title", "[position]", 
                              "work experience", "employment", "n/a", "tbd", "your position"]
        placeholders_company = ["company", "employer", "organization", "company name", "[company]", 
                                "your company", "n/a", "tbd"]
        
        # Validate title
        if not title or title.lower() in placeholders_title or len(title) < 2:
            title = ""
        
        # Validate company
        if not company or company.lower() in placeholders_company or len(company) < 2:
            company = ""
        
        # Skip if both title and company are empty/invalid
        if (not title and not company) or (title == "—" and not company):
            continue
        
        # Additional validation: skip if it looks like the title and company were swapped
        # (e.g., company name appears in title field)
        if title and company and title.lower() == company.lower():
            continue
        
        # Clean up and normalize dates
        if dates:
            dates = dates.strip()
            # Handle malformed dates like "2019 – Present Present"
            dates = dates.replace("Present Present", "Present")
            dates = dates.replace("  ", " ")
            # Normalize date separators
            dates = dates.replace(' - ', ' – ').replace(' to ', ' – ')
            # Remove year ranges that look wrong (e.g., years > 2030)
            import re
            dates = re.sub(r'20[3-9]\d', 'Present', dates)
        
        # Normalize experience entry
        normalized_exp = {
            "title": title.strip() if title else "",
            "company": company.strip() if company else "",
            "dates": dates.strip() if dates else "",
            "description": description.strip() if description else "",
            "points": _extract_experience_points(exp)
        }
        
        # Only add if has meaningful data (at least title OR company)
        if normalized_exp["title"] or normalized_exp["company"]:
            experience_list.append(normalized_exp)
    
    return experience_list


def _extract_experience_points(exp: Dict[str, Any]) -> List[str]:
    """Extract bullet points/achievements from experience entry."""
    points = []
    
    # Try various field names for achievements/responsibilities
    points_data = (
        exp.get("points") or
        exp.get("responsibilities") or
        exp.get("achievements") or
        exp.get("bullets") or
        exp.get("duties") or
        []
    )
    
    if isinstance(points_data, list):
        points = [str(p).strip() for p in points_data if p]
    elif isinstance(points_data, str) and len(points_data) > 10:
        # Split by newlines or bullet markers
        points = [
            p.strip().lstrip('•-*→∙◦ \t')
            for p in points_data.split('\n')
            if p.strip() and len(p.strip()) > 5
        ]
    
    return points[:8]  # Limit to 8 points per role


def _extract_projects(cv_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract projects in normalized format."""
    projects_list = []
    
    projects_data = cv_data.get("Projects") or cv_data.get("projects") or []
    
    if not isinstance(projects_data, list):
        return []
    
    for project in projects_data:
        if not isinstance(project, dict):
            continue
        
        # Extract technologies
        tech = project.get("technologies") or project.get("tech") or project.get("tech_stack") or []
        if isinstance(tech, str):
            tech = [t.strip() for t in tech.split(',') if t.strip()]
        
        normalized_project = {
            "name": project.get("name") or project.get("title") or "",
            "description": project.get("description") or project.get("desc") or "",
            "technologies": tech if isinstance(tech, list) else []
        }
        
        # Only add if has meaningful data
        if normalized_project["name"] or normalized_project["description"]:
            projects_list.append(normalized_project)
    
    return projects_list[:6]  # Limit to 6 projects


def _extract_education(cv_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract education in normalized format."""
    education_list = []
    
    edu_data = cv_data.get("Education") or cv_data.get("education") or []
    
    if not isinstance(edu_data, list):
        return []
    
    for edu in edu_data:
        if not isinstance(edu, dict):
            continue
        
        degree = edu.get("degree") or edu.get("qualification") or edu.get("program") or ""
        school = edu.get("school") or edu.get("institution") or edu.get("university") or edu.get("college") or ""
        year = edu.get("year") or edu.get("graduation") or edu.get("graduation_date") or edu.get("date") or ""
        field = edu.get("field") or edu.get("major") or edu.get("specialization") or ""
        details = edu.get("details") or edu.get("gpa") or edu.get("honors") or ""
        
        # Comprehensive placeholder detection
        placeholder_degrees = ["degree", "degree name", "qualification", "[degree]", "n/a", "tbd"]
        placeholder_institutions = ["institution", "university", "school", "college", "institution name", 
                                   "university name", "[institution]", "n/a", "tbd"]
        
        # Validation - detect if degree and school are swapped or contain placeholder text
        if degree.lower().strip() in placeholder_institutions:
            # Degree contains institution name, likely swapped
            degree, school = school, degree
        
        # Clean placeholders
        if degree.lower().strip() in placeholder_degrees or len(degree) < 2:
            degree = ""
        
        if school.lower().strip() in placeholder_institutions or len(school) < 2:
            school = ""
        
        # Append field to degree if both exist
        if degree and field and field.lower() not in placeholder_degrees:
            degree = f"{degree} in {field}"
        
        # Clean up year - remove "Present" if it's just that
        if year:
            year = year.strip()
            if year.lower() == "present":
                year = "Present"
            # Remove "Institution (Present)" artifacts
            year = year.replace("Institution", "").replace("(", "").replace(")", "").strip()
        
        normalized_edu = {
            "degree": degree.strip() if degree else "",
            "school": school.strip() if school else "",
            "year": year.strip() if year else "",
            "details": details.strip() if details else ""
        }
        
        # Only add if has meaningful data (not just placeholders)
        if (normalized_edu["degree"] and normalized_edu["degree"] != "—") or \
           (normalized_edu["school"] and normalized_edu["school"] != "—" and "Institution (Present)" not in normalized_edu["school"]):
            education_list.append(normalized_edu)
    
    return education_list


def _extract_certifications(cv_data: Dict[str, Any]) -> List[str]:
    """Extract certifications/awards as a list of strings."""
    certifications = []
    
    certs_data = (
        cv_data.get("Certifications") or
        cv_data.get("certifications") or
        cv_data.get("Achievements / Awards") or
        cv_data.get("awards") or
        []
    )
    
    if isinstance(certs_data, list):
        for cert in certs_data:
            if not cert:
                continue
            cert_str = str(cert).strip()
            # Skip if it's just a company name or generic text
            if cert_str.lower() in ["company", "certification", "award", ""]:
                continue
            # Skip if it looks like just a year
            if cert_str.isdigit() and len(cert_str) == 4:
                continue
            certifications.append(cert_str)
    elif isinstance(certs_data, str):
        for c in certs_data.split('\n'):
            c = c.strip()
            if c and c.lower() not in ["company", "certification", "award"] and len(c) > 3:
                certifications.append(c)
    
    return certifications[:10]  # Limit to 10 certifications


def _get_empty_template() -> Dict[str, Any]:
    """Return empty template structure."""
    return {
        "name": "",
        "email": "",
        "phone": "",
        "location": "",
        "linkedin": "",
        "github": "",
        "summary": "",
        "skills": [],
        "experience": [],
        "projects": [],
        "education": [],
        "certifications": [],
    }
