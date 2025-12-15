"""
Professional CV HTML/CSS templates for WeasyPrint PDF generation.
"""

# ATS-Optimized Professional CV Template
# Based on cv_template.html structure for maximum compatibility
PROFESSIONAL_CV_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm 2.5cm;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', 'Helvetica', 'Calibri', 'DejaVu Sans', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
            background: #fff;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}
        
        .header h1 {{
            font-size: 28pt;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-transform: uppercase;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .contact-info {{
            font-size: 10pt;
            color: #f0f0f0;
            margin-top: 10px;
            font-weight: 500;
        }}
        
        .contact-info span {{
            display: inline-block;
            margin: 0 12px;
            padding: 4px 8px;
            background: rgba(255,255,255,0.2);
            border-radius: 4px;
        }}
        
        .contact-info a {{
            color: #ffffff;
            text-decoration: none;
            font-weight: 600;
        }}
        
        .section {{
            margin-top: 22px;
            page-break-inside: avoid;
            padding: 12px;
            background: #fafafa;
            border-radius: 6px;
            border-left: 4px solid #667eea;
        }}
        
        .section-title {{
            font-size: 15pt;
            font-weight: 700;
            color: #667eea;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 12px;
            padding: 8px 12px;
            background: linear-gradient(to right, #667eea15, transparent);
            border-radius: 4px;
            position: relative;
        }}
        
        .section-title::before {{
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            width: 4px;
            background: #667eea;
            border-radius: 2px;
        }}
        
        .skill-category {{
            margin-bottom: 10px;
            padding: 10px;
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            transition: all 0.3s ease;
        }}
        
        .skill-category:hover {{
            border-color: #667eea;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.15);
        }}
        
        .skill-category strong {{
            color: #667eea;
            font-weight: 700;
            font-size: 11pt;
            display: block;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .skill-category span {{
            color: #555;
            font-size: 10.5pt;
            display: inline-block;
            margin: 3px 6px 3px 0;
            padding: 4px 10px;
            background: #f8f9fa;
            border-left: 3px solid #667eea;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
            page-break-inside: avoid;
            padding: 15px;
            background: #ffffff;
            border: 1px solid #e8e8e8;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .job-header {{
            margin-bottom: 10px;
            padding-bottom: 8px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .job-title {{
            font-size: 12.5pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 4px;
        }}
        
        .company {{
            font-size: 11.5pt;
            color: #667eea;
            font-weight: 600;
            display: inline-block;
        }}
        
        .job-meta {{
            font-size: 10pt;
            color: #888;
            font-style: italic;
            margin-top: 5px;
            font-weight: 500;
        }}
        
        .achievements {{
            margin-top: 10px;
            margin-left: 0;
            list-style-position: outside;
            padding-left: 20px;
        }}
        
        .achievements li {{
            margin-bottom: 7px;
            padding-left: 8px;
            line-height: 1.7;
            color: #2c3e50;
        }}
        
        .achievements li::marker {{
            color: #667eea;
            font-weight: bold;
            font-size: 14pt;
        }}
        
        .achievements li strong {{
            color: #667eea;
            font-weight: 600;
        }}
        
        .achievements {{
            margin-top: 8px;
            margin-left: 0;
            list-style-position: outside;
        }}
        
        .achievements li {{
            margin-bottom: 5px;
            padding-left: 5px;
            line-height: 1.5;
        }}
        
        .achievements li::marker {{
            color: #3498db;
            font-weight: bold;
        }}
        
        .project-item {{
            margin-bottom: 18px;
            page-break-inside: avoid;
            padding: 12px;
            background: #ffffff;
            border: 1px solid #e8e8e8;
            border-left: 4px solid #764ba2;
            border-radius: 6px;
        }}
        
        .project-name {{
            font-size: 11.5pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 4px;
        }}
        
        .project-tech {{
            font-size: 10pt;
            color: #764ba2;
            font-style: italic;
            margin-top: 3px;
            font-weight: 500;
            display: inline-block;
            padding: 3px 8px;
            background: #764ba215;
            border-radius: 4px;
        }}
        
        .project-description {{
            margin-top: 8px;
            margin-left: 0;
            list-style-position: outside;
            padding-left: 18px;
        }}
        
        .project-description li {{
            margin-bottom: 5px;
            font-size: 10pt;
            line-height: 1.6;
            color: #2c3e50;
        }}
        
        .education-item {{
            margin-bottom: 15px;
            page-break-inside: avoid;
            padding: 12px;
            background: #ffffff;
            border: 1px solid #e8e8e8;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .degree {{
            font-size: 11.5pt;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 3px;
        }}
        
        .institution {{
            font-size: 10.5pt;
            color: #667eea;
            font-weight: 600;
            margin-top: 2px;
        }}
        
        .edu-meta {{
            font-size: 9.5pt;
            color: #888;
            margin-top: 4px;
            font-style: italic;
            font-style: italic;
            margin-top: 2px;
        }}
        
        .certification-item {{
            margin-bottom: 8px;
        }}
        
        .cert-name {{
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .cert-issuer {{
            font-size: 10pt;
            color: #555;
        }}
        
        .simple-list {{
            margin-left: 0;
            list-style-position: outside;
        }}
        
        .simple-list li {{
            margin-bottom: 5px;
        }}
        
        .two-column {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}
        
        @media print {{
            .section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

# Minimal clean template for simple CVs
MINIMAL_CV_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        body {{
            font-family: 'DejaVu Sans', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }}
        
        h1 {{
            font-size: 24pt;
            margin-bottom: 10px;
            color: #000;
        }}
        
        h2 {{
            font-size: 14pt;
            margin-top: 20px;
            margin-bottom: 10px;
            color: #000;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }}
        
        h3 {{
            font-size: 12pt;
            margin-top: 15px;
            margin-bottom: 5px;
        }}
        
        p {{
            margin-bottom: 10px;
        }}
        
        ul {{
            margin-left: 20px;
            margin-bottom: 10px;
        }}
        
        li {{
            margin-bottom: 5px;
        }}
        
        .contact {{
            font-size: 10pt;
            color: #666;
            margin-bottom: 15px;
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""


def build_professional_cv_html(data):
    """Build professional CV HTML from structured data.
    
    Args:
        data: Dict with CV sections or plain text string
        
    Returns:
        Complete HTML string
    """
    if isinstance(data, str):
        # Plain text - convert to minimal HTML
        import re
        html_content = data.replace('\n', '<br>\n')
        # Detect headings (all caps or title case followed by colon/newline)
        html_content = re.sub(
            r'(?m)^([A-Z][A-Z\s&]+)$',
            r'<h2>\1</h2>',
            html_content
        )
        # Detect bullet points
        html_content = re.sub(
            r'(?m)^[\-\•\*]\s*(.+)$',
            r'<li>\1</li>',
            html_content
        )
        # Wrap consecutive <li> in <ul>
        html_content = re.sub(
            r'(<li>.*?</li>\n?)+',
            lambda m: f'<ul>\n{m.group(0)}</ul>\n',
            html_content,
            flags=re.DOTALL
        )
        return MINIMAL_CV_TEMPLATE.format(content=html_content)
    
    # Structured data - build professional template
    sections = []
    
    # Header - Try multiple sources for contact info
    contact = {}
    contact_sources = [
        data.get('contact_information'),
        data.get('Personal Information'),
        data.get('personal_information'),
        data.get('Contact Information'),
        data  # Fallback to root level
    ]
    
    for source in contact_sources:
        if isinstance(source, dict) and (source.get('name') or source.get('email')):
            contact = source
            break
    
    # Try multiple sources for name
    name = (contact.get('name') or 
            contact.get('full_name') or
            contact.get('fullName') or
            data.get('name') or
            data.get('full_name') or
            'Your Name')
    
    contact_parts = []
    if contact.get('email'):
        contact_parts.append(f'<span>✉ {contact["email"]}</span>')
    if contact.get('phone'):
        contact_parts.append(f'<span>📱 {contact["phone"]}</span>')
    if contact.get('location'):
        contact_parts.append(f'<span>📍 {contact["location"]}</span>')
    if contact.get('linkedin'):
        contact_parts.append(f'<span><a href="{contact["linkedin"]}">LinkedIn</a></span>')
    if contact.get('github'):
        contact_parts.append(f'<span><a href="{contact["github"]}">GitHub</a></span>')
    
    header_html = f'''
    <div class="header">
        <h1>{name}</h1>
        <div class="contact-info">
            {' | '.join(contact_parts) if contact_parts else ''}
        </div>
    </div>
    '''
    sections.append(header_html)
    
    # Professional Summary
    summary = data.get('professional_summary', '') or data.get('Summary / Objective', '')
    if summary:
        sections.append(f'''
        <div class="section">
            <div class="section-title">Professional Summary</div>
            <div class="section-content">
                <p class="summary">{summary}</p>
            </div>
        </div>
        ''')
    
    # Skills
    skills = data.get('skills', {}) or data.get('Skills', {})
    if skills:
        skills_html = '<div class="section"><div class="section-title">Technical Skills</div><div class="section-content"><div class="skills-grid">'
        
        if isinstance(skills, dict):
            if skills.get('technical'):
                skills_html += f'<div class="skill-category"><strong>Programming:</strong> <span>{", ".join(skills["technical"])}</span></div>'
            if skills.get('frameworks_libraries'):
                skills_html += f'<div class="skill-category"><strong>Frameworks:</strong> <span>{", ".join(skills["frameworks_libraries"])}</span></div>'
            if skills.get('tools'):
                skills_html += f'<div class="skill-category"><strong>Tools:</strong> <span>{", ".join(skills["tools"])}</span></div>'
            if skills.get('databases'):
                skills_html += f'<div class="skill-category"><strong>Databases:</strong> <span>{", ".join(skills["databases"])}</span></div>'
            if skills.get('cloud_devops'):
                skills_html += f'<div class="skill-category"><strong>Cloud/DevOps:</strong> <span>{", ".join(skills["cloud_devops"])}</span></div>'
            if skills.get('soft'):
                skills_html += f'<div class="skill-category"><strong>Soft Skills:</strong> <span>{", ".join(skills["soft"])}</span></div>'
            if skills.get('all') and not any([skills.get('technical'), skills.get('frameworks_libraries')]):
                # Fallback to 'all' if no categorization
                skills_html += f'<div class="skill-category" style="grid-column: 1 / -1;"><span>{", ".join(skills["all"])}</span></div>'
        elif isinstance(skills, (list, tuple)):
            skills_html += f'<div class="skill-category" style="grid-column: 1 / -1;"><span>{", ".join(skills)}</span></div>'
        elif isinstance(skills, str):
            skills_html += f'<div class="skill-category" style="grid-column: 1 / -1;"><span>{skills}</span></div>'
        
        skills_html += '</div></div></div>'
        sections.append(skills_html)
    
    # Work Experience
    experience = data.get('work_experience', []) or data.get('Work Experience / Employment History', [])
    if experience and isinstance(experience, list):
        exp_html = '<div class="section"><div class="section-title">Professional Experience</div><div class="section-content">'
        
        for job in experience:
            if isinstance(job, dict):
                title = job.get('title', 'Position')
                company = job.get('company', 'Company')
                dates = job.get('dates', job.get('duration', ''))
                location = job.get('location', '')
                
                exp_html += f'''
                <div class="experience-item">
                    <div class="job-header">
                        <div class="job-title">{title}</div>
                        <div class="company">{company}</div>
                        <div class="job-meta">{dates}{" • " + location if location else ""}</div>
                    </div>
                '''
                
                achievements = job.get('achievements', []) or job.get('points', [])
                if achievements:
                    exp_html += '<ul class="achievements">'
                    for achievement in achievements:
                        exp_html += f'<li>{achievement}</li>'
                    exp_html += '</ul>'
                
                exp_html += '</div>'
        
        exp_html += '</div></div>'
        sections.append(exp_html)
    
    # Projects
    projects = data.get('projects', []) or data.get('Projects', [])
    if projects and isinstance(projects, list):
        proj_html = '<div class="section"><div class="section-title">Key Projects</div><div class="section-content">'
        
        for project in projects:
            if isinstance(project, dict):
                name = project.get('name', 'Project')
                tech = project.get('technologies', [])
                tech_str = ', '.join(tech) if isinstance(tech, list) else str(tech)
                description = project.get('description', '')
                highlights = project.get('highlights', [])
                
                proj_html += f'''
                <div class="project-item">
                    <div class="project-name">{name}</div>
                    {f'<div class="project-tech">{tech_str}</div>' if tech_str else ''}
                    {f'<p>{description}</p>' if description else ''}
                '''
                
                if highlights:
                    proj_html += '<ul class="project-description">'
                    for highlight in highlights:
                        proj_html += f'<li>{highlight}</li>'
                    proj_html += '</ul>'
                
                proj_html += '</div>'
        
        proj_html += '</div></div>'
        sections.append(proj_html)
    
    # Education
    education = data.get('education', []) or data.get('Education', [])
    if education and isinstance(education, list):
        edu_html = '<div class="section"><div class="section-title">Education</div><div class="section-content">'
        
        for edu in education:
            if isinstance(edu, dict):
                degree = edu.get('degree', 'Degree')
                institution = edu.get('institution', edu.get('school', 'Institution'))
                year = edu.get('graduation_date', edu.get('year', ''))
                gpa = edu.get('gpa', '')
                field = edu.get('field', '')
                
                edu_html += f'''
                <div class="education-item">
                    <div class="degree">{degree}{" in " + field if field else ""}</div>
                    <div class="institution">{institution}</div>
                    <div class="edu-meta">{year}{" • GPA: " + gpa if gpa else ""}</div>
                </div>
                '''
        
        edu_html += '</div></div>'
        sections.append(edu_html)
    
    # Certifications
    certifications = data.get('certifications', []) or data.get('Certifications', [])
    if certifications:
        cert_html = '<div class="section"><div class="section-title">Certifications</div><div class="section-content">'
        
        if isinstance(certifications, list):
            for cert in certifications:
                if isinstance(cert, dict):
                    name = cert.get('name', 'Certification')
                    issuer = cert.get('issuer', '')
                    date = cert.get('date', '')
                    cert_html += f'<div class="certification-item"><span class="cert-name">{name}</span> — <span class="cert-issuer">{issuer}{", " + date if date else ""}</span></div>'
                else:
                    cert_html += f'<div class="certification-item"><span class="cert-name">{cert}</span></div>'
        elif isinstance(certifications, str):
            cert_html += f'<p>{certifications}</p>'
        
        cert_html += '</div></div>'
        sections.append(cert_html)
    
    # Achievements
    achievements = data.get('achievements', []) or data.get('Achievements / Awards', [])
    if achievements and achievements != []:
        ach_html = '<div class="section"><div class="section-title">Achievements & Awards</div><div class="section-content"><ul class="simple-list">'
        
        if isinstance(achievements, list):
            for achievement in achievements:
                ach_html += f'<li>{achievement}</li>'
        elif isinstance(achievements, str):
            ach_html += f'<li>{achievements}</li>'
        
        ach_html += '</ul></div></div>'
        sections.append(ach_html)
    
    # Languages
    languages = data.get('languages', []) or data.get('Languages', [])
    if languages and languages != []:
        lang_html = '<div class="section"><div class="section-title">Languages</div><div class="section-content">'
        
        if isinstance(languages, list):
            lang_items = []
            for lang in languages:
                if isinstance(lang, dict):
                    lang_items.append(f"{lang.get('language', 'Language')} ({lang.get('proficiency', 'Proficient')})")
                else:
                    lang_items.append(str(lang))
            lang_html += '<p>' + ' • '.join(lang_items) + '</p>'
        elif isinstance(languages, str):
            lang_html += f'<p>{languages}</p>'
        
        lang_html += '</div></div>'
        sections.append(lang_html)
    
    full_content = '\n'.join(sections)
    return PROFESSIONAL_CV_TEMPLATE.format(content=full_content)
