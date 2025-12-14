"""
Alternative CV PDF Service using ReportLab
For systems where WeasyPrint dependencies are not available.
"""
import os
import re
import logging
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors

logger = logging.getLogger(__name__)


def clean_text_for_pdf(text: str) -> str:
    """
    Clean text to remove Markdown syntax and special characters for PDF generation.
    
    Args:
        text: Raw text that may contain Markdown
        
    Returns:
        Cleaned text safe for ReportLab
    """
    if not text:
        return ""
    
    # Remove Markdown headers (##, ###, etc.)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove Markdown bold/italic (**text**, *text*, __text__, _text_)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    
    # Remove Markdown links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove Markdown code blocks ```
    text = re.sub(r'```[a-z]*\n?', '', text)
    
    # Remove inline code `text`
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Convert bullet points to simple dashes
    text = re.sub(r'^[\*\-\+]\s+', '• ', text, flags=re.MULTILINE)
    
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Escape special XML/HTML characters for ReportLab
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    return text.strip()


def generate_cv_pdf_reportlab(cv_json: Dict[str, Any], output_path: str = "output/cv.pdf") -> str:
    """
    Generate a professional PDF resume using ReportLab.
    Alternative to WeasyPrint for systems without system dependencies.
    
    Args:
        cv_json: Structured CV data dictionary
        output_path: Path where PDF should be saved
        
    Returns:
        Path to generated PDF file
    """
    try:
        logger.info(f"Generating PDF resume with ReportLab at {output_path}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles - Modern and Attractive
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=32,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            spaceBefore=0,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=38
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#4a5568'),
            alignment=TA_CENTER,
            spaceAfter=20,
            fontName='Helvetica'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=13,
            textColor=colors.white,
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#3b82f6'),  # Modern blue
            borderRadius=4,
            leftIndent=8,
            rightIndent=8,
            leading=20
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            alignment=TA_LEFT,
            spaceAfter=8,
            leading=14
        )
        
        bullet_style = ParagraphStyle(
            'BulletStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
            leftIndent=15,
            bulletIndent=0,
            spaceAfter=6,
            leading=14
        )
        
        # Header - Name and Contact with modern styling
        # Try multiple sources for name
        name = (cv_json.get('name') or 
                cv_json.get('full_name') or
                cv_json.get('candidate_name') or
                (cv_json.get('Personal Information', {}).get('name') if isinstance(cv_json.get('Personal Information'), dict) else None) or
                'Your Name')
        
        name = clean_text_for_pdf(name)
        if name.lower() in ['your name', 'name', '']:
            logger.warning(f"⚠️ No valid name found in CV data. Keys available: {list(cv_json.keys())[:10]}")
            name = 'Your Name'
        
        elements.append(Spacer(1, 0.1 * inch))
        elements.append(Paragraph(name.upper(), title_style))
        
        contact_parts = []
        if cv_json.get('email'):
            contact_parts.append(f"✉ {clean_text_for_pdf(cv_json['email'])}")
        if cv_json.get('phone'):
            contact_parts.append(f"☎ {clean_text_for_pdf(cv_json['phone'])}")
        if cv_json.get('linkedin'):
            linkedin = clean_text_for_pdf(cv_json['linkedin'])
            if 'linkedin.com' in linkedin:
                linkedin = linkedin.split('linkedin.com/')[-1].strip('/')
            contact_parts.append(f"🔗 {linkedin}")
        
        if contact_parts:
            contact_text = '  •  '.join(contact_parts)
            elements.append(Paragraph(contact_text, subtitle_style))
        else:
            elements.append(Spacer(1, 0.15 * inch))
        
        # Add a subtle divider line
        from reportlab.platypus import HRFlowable
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#e5e7eb'),
            spaceAfter=20
        ))
        
        # Professional Summary with enhanced styling
        if cv_json.get('summary'):
            elements.append(Paragraph("💼 PROFESSIONAL SUMMARY", heading_style))
            elements.append(Spacer(1, 0.05 * inch))
            summary_text = clean_text_for_pdf(cv_json['summary'])
            summary_style = ParagraphStyle(
                'SummaryStyle',
                parent=normal_style,
                alignment=TA_JUSTIFY,
                fontSize=10.5,
                leading=15,
                textColor=colors.HexColor('#1f2937')
            )
            elements.append(Paragraph(summary_text, summary_style))
            elements.append(Spacer(1, 0.15 * inch))
        
        # Skills with modern pill-style layout
        if cv_json.get('skills'):
            elements.append(Paragraph("🔧 TECHNICAL SKILLS", heading_style))
            elements.append(Spacer(1, 0.05 * inch))
            
            # Create skill tags with styling
            cleaned_skills = [clean_text_for_pdf(str(skill)) for skill in cv_json['skills']]
            
            # Create a table for better skill layout
            skills_data = []
            row = []
            for i, skill in enumerate(cleaned_skills):
                row.append(skill)
                if (i + 1) % 3 == 0 or i == len(cleaned_skills) - 1:
                    while len(row) < 3:
                        row.append('')
                    skills_data.append(row)
                    row = []
            
            if skills_data:
                skill_table = Table(skills_data, colWidths=[2.3*inch, 2.3*inch, 2.3*inch])
                skill_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bfdbfe')),
                    ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#eff6ff'), colors.HexColor('#dbeafe')]),
                ]))
                elements.append(skill_table)
            
            elements.append(Spacer(1, 0.15 * inch))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Skills
        if cv_json.get('skills'):
            elements.append(Paragraph("SKILLS", heading_style))
            cleaned_skills = [clean_text_for_pdf(str(skill)) for skill in cv_json['skills']]
            skills_text = ' • '.join(cleaned_skills)
            elements.append(Paragraph(skills_text, normal_style))
            elements.append(Spacer(1, 0.2 * inch))
        
        # Experience with modern timeline styling
        if cv_json.get('experience'):
            elements.append(Paragraph("💼 WORK EXPERIENCE", heading_style))
            elements.append(Spacer(1, 0.1 * inch))
            
            for idx, exp in enumerate(cv_json['experience']):
                # Job title and company with enhanced styling
                job_title = clean_text_for_pdf(exp.get('role', 'Position'))
                company = clean_text_for_pdf(exp.get('company', 'Company'))
                years = clean_text_for_pdf(exp.get('years', ''))
                
                job_style = ParagraphStyle(
                    'JobTitle',
                    parent=styles['Normal'],
                    fontSize=11.5,
                    textColor=colors.HexColor('#1f2937'),
                    fontName='Helvetica-Bold',
                    spaceAfter=3,
                    leading=14
                )
                
                company_style = ParagraphStyle(
                    'Company',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.HexColor('#6b7280'),
                    fontName='Helvetica-Oblique',
                    spaceAfter=6
                )
                
                # Add visual timeline indicator
                job_header = f"<b>{job_title}</b>"
                elements.append(Paragraph(job_header, job_style))
                elements.append(Paragraph(f"<i>{company}</i>  •  {years}", company_style))
                
                # Description with better formatting
                description = clean_text_for_pdf(exp.get('description', ''))
                
                if '•' in description:
                    desc_parts = [p.strip() for p in description.split('•') if p.strip()]
                    for part in desc_parts:
                        elements.append(Paragraph(f"▪ {part}", bullet_style))
                elif description:
                    # Split long descriptions into bullet points
                    sentences = [s.strip() + '.' for s in description.split('.') if s.strip()]
                    for sentence in sentences:
                        if len(sentence) > 10:
                            elements.append(Paragraph(f"▪ {sentence}", bullet_style))
                
                if idx < len(cv_json['experience']) - 1:
                    elements.append(Spacer(1, 0.12 * inch))
            
            elements.append(Spacer(1, 0.15 * inch))
        
        # Education with academic styling
        if cv_json.get('education'):
            elements.append(Paragraph("🎓 EDUCATION", heading_style))
            elements.append(Spacer(1, 0.08 * inch))
            
            for edu in cv_json['education']:
                degree = clean_text_for_pdf(edu.get('degree', ''))
                institution = clean_text_for_pdf(edu.get('institution', ''))
                year = clean_text_for_pdf(str(edu.get('year', '')))
                details = clean_text_for_pdf(edu.get('details', ''))
                
                edu_degree_style = ParagraphStyle(
                    'EducationDegree',
                    parent=styles['Normal'],
                    fontSize=11,
                    fontName='Helvetica-Bold',
                    textColor=colors.HexColor('#1f2937'),
                    spaceAfter=3
                )
                
                edu_inst_style = ParagraphStyle(
                    'EducationInst',
                    parent=styles['Normal'],
                    fontSize=10,
                    fontName='Helvetica-Oblique',
                    textColor=colors.HexColor('#6b7280'),
                    spaceAfter=6
                )
                
                elements.append(Paragraph(f"<b>{degree}</b>", edu_degree_style))
                elements.append(Paragraph(f"{institution}  •  {year}", edu_inst_style))
                
                if details:
                    detail_style = ParagraphStyle(
                        'EducationDetail',
                        parent=normal_style,
                        fontSize=9.5,
                        textColor=colors.HexColor('#4b5563'),
                        leftIndent=10
                    )
                    elements.append(Paragraph(details, detail_style))
                
                elements.append(Spacer(1, 0.08 * inch))
        
        # Projects with tech stack highlighting
        if cv_json.get('projects'):
            elements.append(Paragraph("🚀 KEY PROJECTS", heading_style))
            elements.append(Spacer(1, 0.08 * inch))
            
            for proj in cv_json['projects']:
                proj_name = clean_text_for_pdf(proj.get('name', ''))
                proj_desc = clean_text_for_pdf(proj.get('description', ''))
                proj_tech = proj.get('technologies', [])
                
                proj_name_style = ParagraphStyle(
                    'ProjectName',
                    parent=styles['Normal'],
                    fontSize=11,
                    fontName='Helvetica-Bold',
                    textColor=colors.HexColor('#1f2937'),
                    spaceAfter=4
                )
                
                elements.append(Paragraph(f"<b>{proj_name}</b>", proj_name_style))
                elements.append(Paragraph(proj_desc, normal_style))
                
                if proj_tech:
                    cleaned_tech = [clean_text_for_pdf(str(tech)) for tech in proj_tech]
                    tech_style = ParagraphStyle(
                        'TechStack',
                        parent=normal_style,
                        fontSize=9,
                        textColor=colors.HexColor('#3b82f6'),
                        fontName='Helvetica-Bold',
                        leftIndent=10,
                        spaceAfter=2
                    )
                    tech_text = f"<b>Tech Stack:</b> {' | '.join(cleaned_tech)}"
                    elements.append(Paragraph(tech_text, tech_style))
                
                elements.append(Spacer(1, 0.1 * inch))
        
        # Certifications with badge styling
        if cv_json.get('certifications'):
            elements.append(Paragraph("📜 CERTIFICATIONS & LICENSES", heading_style))
            elements.append(Spacer(1, 0.05 * inch))
            
            cert_style = ParagraphStyle(
                'CertBullet',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#374151'),
                leftIndent=15,
                bulletIndent=0,
                spaceAfter=5
            )
            
            for cert in cv_json['certifications']:
                cert_text = clean_text_for_pdf(str(cert))
                elements.append(Paragraph(f"✓ {cert_text}", cert_style))
            
            elements.append(Spacer(1, 0.1 * inch))
        
        # Build PDF
        doc.build(elements)
        
        logger.info(f"Successfully generated PDF with ReportLab: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to generate PDF with ReportLab: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Test PDF generation
    test_cv = {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "+1-555-123-4567",
        "summary": "Experienced software engineer with expertise in full-stack development.",
        "skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
        "experience": [
            {
                "role": "Senior Software Engineer",
                "company": "Tech Corp",
                "years": "2020 - Present",
                "description": "Led development of microservices architecture. Improved system performance by 50%."
            }
        ],
        "education": [
            {
                "degree": "B.S. Computer Science",
                "institution": "University",
                "year": "2020",
                "details": "GPA: 3.8/4.0"
            }
        ],
        "projects": [],
        "certifications": ["AWS Certified Developer"]
    }
    
    generate_cv_pdf_reportlab(test_cv, "test_output.pdf")
    print("Test PDF generated successfully!")
