import argparse
import io
import os
import sys
from typing import Dict, List

from app.utils import cv_utils


def _safe_get(d: Dict, *keys, default: str = "") -> str:
    cur = d or {}
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    if isinstance(cur, str):
        val = cur.strip()
        if val.lower() == "not provided":
            return default
        return val or default
    return default


def render_ats_text(structured: Dict) -> str:
    contact = structured.get("contact_information", {}) if isinstance(structured.get("contact_information"), dict) else {}
    skills = structured.get("skills", {}) if isinstance(structured.get("skills"), dict) else {}

    name = _safe_get(contact, "name")
    email = _safe_get(contact, "email")
    phone = _safe_get(contact, "phone")
    linkedin = _safe_get(contact, "linkedin", default="")
    github = _safe_get(contact, "github", default="")
    portfolio = _safe_get(contact, "website", default="")

    # Infer Job Title from first experience entry title if present
    job_title = ""
    exp = structured.get("work_experience") or []
    if exp and isinstance(exp, list) and isinstance(exp[0], dict):
        title = (exp[0].get("title") or "").strip()
        if title:
            job_title = title

    lines: List[str] = []
    # Header block (strict format)
    if name:
        lines.append(f"{name}")
    if job_title:
        lines.append(f"{job_title}")
    lines.append(f"Phone: {phone}" if phone else "Phone:")
    lines.append(f"Email: {email}" if email else "Email:")
    lines.append(f"LinkedIn: {linkedin}" if linkedin else "LinkedIn:")
    lines.append(f"GitHub: {github}" if github else "GitHub:")
    lines.append(f"Portfolio: {portfolio}" if portfolio else "Portfolio:")
    lines.append("")
    lines.append("---")
    lines.append("")

    # PROFESSIONAL SUMMARY
    lines.append("## PROFESSIONAL SUMMARY")
    summary = structured.get("professional_summary") or ""
    summary = summary.strip()
    if summary:
        lines.append(summary)
    lines.append("")

    # TECHNICAL STRENGTHS (Added to improve CV)
    lines.append("## TECHNICAL STRENGTHS (Added to improve CV)")
    strengths: list[str] = []
    tech_list = skills.get("technical") or []
    other_list = skills.get("other") or []
    soft_list = skills.get("soft") or []
    # Heuristic strengths based on skills present
    tech_lower = {s.lower() for s in tech_list}
    if any(k in tech_lower for k in ("python", "flask", "django")):
        strengths.append("Backend/API development with Python and modern frameworks")
    if any(k in tech_lower for k in ("react", "vue", "angular")):
        strengths.append("Front-end engineering and component-driven UI design")
    if any(k in tech_lower for k in ("aws", "azure", "gcp")):
        strengths.append("Cloud-native design, deployment, and environment automation")
    if any(k in tech_lower for k in ("docker", "kubernetes")):
        strengths.append("Containerization, orchestration, and scalable microservices")
    if any(k in tech_lower for k in ("sql", "nosql", "postgres", "mongodb")):
        strengths.append("Data modeling, performance tuning, and reliable persistence")
    if any(k in tech_lower for k in ("ml", "machine", "pytorch", "tensorflow", "nlp")):
        strengths.append("Applied AI/ML and NLP for real-world product features")
    # Fallback to a couple of generic strengths if empty and we have any content
    if not strengths and (tech_list or other_list or soft_list):
        strengths = [
            "Clean, testable code with strong documentation",
            "Cross-functional collaboration and stakeholder communication",
        ]
    for s in strengths:
        lines.append(f"- {s}")
    lines.append("")

    # SKILLS
    lines.append("## SKILLS")
    # Attempt to split skills into the requested buckets
    prog_langs = ", ".join([s for s in tech_list if s.lower() in {"python","java","c#","c++","go","javascript","typescript","sql"}])
    frameworks = ", ".join([s for s in tech_list if s.lower() in {"flask","django","spring","react","angular","vue","fastapi"}])
    ai_ml = ", ".join([s for s in tech_list if s.lower() in {"ml","machine learning","pytorch","tensorflow","sklearn","nlp"}])
    tools = ", ".join(sorted(set(tech_list) - set(filter(None, (prog_langs + "," + frameworks + "," + ai_ml).split(",")))))
    soft = ", ".join(soft_list)
    lines.append(f"**Programming Languages:** {prog_langs}" if prog_langs else "**Programming Languages:**")
    lines.append(f"**Tools & Technologies:** {tools}" if tools else "**Tools & Technologies:**")
    lines.append(f"**Frameworks:** {frameworks}" if frameworks else "**Frameworks:**")
    lines.append(f"**AI/ML:** {ai_ml}" if ai_ml else "**AI/ML:**")
    lines.append(f"**Soft Skills:** {soft}" if soft else "**Soft Skills:**")
    lines.append("")

    # EXPERIENCE
    lines.append("## EXPERIENCE")
    if exp:
        for job in exp:
            if not isinstance(job, dict):
                continue
            role = (job.get("title") or "Role").strip() or "Role"
            company = (job.get("company") or job.get("organization") or "Company").strip() or "Company"
            location = (job.get("location") or "").strip()
            dates = (job.get("dates") or "").strip()
            header = f"**{role} | {company} | {dates or ''} | {location or ''}**".rstrip(" | ")
            lines.append(header)
            points = [p for p in (job.get("points") or []) if isinstance(p, str) and p.strip()]
            if points:
                strengthened = cv_utils.strengthen_experience_points("\n".join(f"- {p}" for p in points))
                for bullet in strengthened.splitlines():
                    if bullet.strip():
                        lines.append(bullet)
            lines.append("")
    else:
        lines.append("")

    # PROJECTS
    lines.append("## PROJECTS")
    projects = structured.get("projects") or []
    if projects:
        for proj in projects:
            if not isinstance(proj, dict):
                continue
            name = (proj.get("name") or "Project").strip() or "Project"
            techs = ", ".join((proj.get("technologies") or []))
            lines.append(f"**{name} | Tools Used**: {techs}" if techs else f"**{name} | Tools Used**")
            desc = (proj.get("description") or proj.get("desc") or "").strip()
            if desc:
                lines.append(f"- {desc}")
            lines.append("")
    else:
        lines.append("")

    # EDUCATION
    lines.append("## EDUCATION")
    edu = structured.get("education") or []
    if edu:
        for e in edu:
            if not isinstance(e, dict):
                continue
            degree = (e.get("degree") or "Degree").strip() or "Degree"
            school = (e.get("school") or "Institution").strip() or "Institution"
            year = (e.get("year") or e.get("date") or "").strip()
            line = f"**{degree} | {school} | {year}**".rstrip(" | ")
            lines.append(line)
        lines.append("")
    else:
        lines.append("")

    # CERTIFICATIONS
    lines.append("## CERTIFICATIONS")
    certs = structured.get("certifications") or []
    if certs:
        for c in certs:
            if isinstance(c, str) and c.strip():
                lines.append(f"- {c.strip()}")
        lines.append("")
    else:
        lines.append("")

    # ACHIEVEMENTS
    lines.append("## ACHIEVEMENTS")
    ach = structured.get("achievements") or []
    if ach:
        for a in ach:
            if isinstance(a, str) and a.strip():
                lines.append(f"- {a.strip()}")
        lines.append("")
    else:
        lines.append("")

    # VOLUNTEER EXPERIENCE (Optional)
    lines.append("## VOLUNTEER EXPERIENCE (Optional)")
    vol = structured.get("volunteer_experience") or []
    if vol:
        for v in vol:
            if not isinstance(v, dict):
                continue
            role = (v.get("title") or "Volunteer").strip() or "Volunteer"
            org = (v.get("company") or v.get("organization") or "").strip()
            dates = (v.get("dates") or "").strip()
            loc = (v.get("location") or "").strip()
            header = f"**{role} | {org} | {dates or ''} | {loc or ''}**".rstrip(" | ")
            lines.append(header)
            pts = [p for p in (v.get("points") or []) if isinstance(p, str) and p.strip()]
            for p in pts:
                lines.append(f"- {p.strip()}")
        lines.append("")
    else:
        lines.append("")

    # LANGUAGES
    lines.append("## LANGUAGES")
    languages = structured.get("languages") or []
    if languages:
        lines.append("- " + ", ".join(languages))
        lines.append("")
    else:
        lines.append("")

    return "\n".join(lines).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Render an ATS-friendly resume from a CV file.")
    parser.add_argument("cv_path", help="Path to the input CV file (pdf, docx, doc, txt)")
    parser.add_argument("--domain", dest="domain", default=None, help="Optional job domain for keyword scoring")
    args = parser.parse_args()

    cv_path = os.path.abspath(args.cv_path)
    if not os.path.exists(cv_path):
        print(f"File not found: {cv_path}", file=sys.stderr)
        return 2

    with open(cv_path, "rb") as f:
        data = f.read()

    # Extract and build structured sections
    text = cv_utils.extract_text_from_any(data, os.path.basename(cv_path))
    structured = cv_utils.build_standardized_sections(text)

    # Render to ATS text per requested structure
    ats_text = render_ats_text(structured)

    print(ats_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
