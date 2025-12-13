"""
CV Generation Service - Generate professional CVs using templates.
Uses Jinja2 for templating and WeasyPrint for PDF generation.
"""
import logging
import os
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Try importing required libraries
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    logger.warning("Jinja2 not available")

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint not available - will use fallback PDF generation")

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    logger.warning("FPDF not available")


class CVGenerationService:
    """Service for generating professional CV PDFs from templates."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize CV generation service.
        
        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(__file__), '..', 'templates', 'cv'
        )
        
        # Create templates directory if it doesn't exist
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Initialize Jinja2 environment
        if JINJA2_AVAILABLE:
            self.jinja_env = Environment(
                loader=FileSystemLoader(self.templates_dir),
                autoescape=select_autoescape(['html', 'xml'])
            )
            logger.info(f"Jinja2 environment initialized with templates from: {self.templates_dir}")
        else:
            self.jinja_env = None
    
    def generate_cv_pdf(self, 
                       cv_data: Dict, 
                       template_name: str = "professional.html") -> bytes:
        """
        Generate CV PDF from data and template.
        
        Args:
            cv_data: Dictionary with CV data (entities, sections, etc.)
            template_name: Name of template file to use
            
        Returns:
            PDF bytes
        """
        logger.info(f"Generating CV PDF using template: {template_name}")
        
        # Prepare data for template
        template_data = self._prepare_template_data(cv_data)
        
        # Generate HTML from template
        html_content = self._render_template(template_name, template_data)
        
        # Convert HTML to PDF
        if WEASYPRINT_AVAILABLE:
            pdf_bytes = self._html_to_pdf_weasyprint(html_content)
        elif FPDF_AVAILABLE:
            logger.warning("WeasyPrint not available, using FPDF fallback")
            pdf_bytes = self._generate_pdf_fpdf(template_data)
        else:
            raise RuntimeError("No PDF generation library available. Install WeasyPrint or FPDF.")
        
        logger.info(f"Generated PDF: {len(pdf_bytes)} bytes")
        return pdf_bytes
    
    def _prepare_template_data(self, cv_data: Dict) -> Dict:
        """
        Prepare and structure data for template rendering.
        
        Args:
            cv_data: Raw CV data
            
        Returns:
            Structured data for template
        """
        entities = cv_data.get('entities', {})
        sections = cv_data.get('sections', {})
        
        template_data = {
            # Personal information
            'name': entities.get('name', 'Unknown Name'),
            'email': entities.get('email', ''),
            'phone': entities.get('phone', ''),
            'location': entities.get('location', ''),
            
            # Sections
            'summary': sections.get('summary', ''),
            'experience': self._parse_experience(sections.get('experience', '')),
            'education': self._parse_education(sections.get('education', ''), entities.get('education_institutions', [])),
            'skills': entities.get('skills', []) or self._parse_skills(sections.get('skills', '')),
            'certifications': self._parse_list_section(sections.get('certifications', '')),
            'projects': self._parse_projects(sections.get('projects', '')),
            'awards': self._parse_list_section(sections.get('awards', '')),
            
            # Metadata
            'generated_date': datetime.now().strftime('%B %Y'),
        }
        
        return template_data
    
    @staticmethod
    def _parse_experience(experience_text: str) -> list:
        """Parse experience section into structured list."""
        if not experience_text:
            return []
        
        experiences = []
        
        # Split by common job separators
        # Look for patterns like company names followed by role/dates
        lines = experience_text.split('\n')
        
        current_exp = None
        for line in lines:
            line = line.strip()
            if not line:
                if current_exp:
                    experiences.append(current_exp)
                    current_exp = None
                continue
            
            # Start new experience entry if line looks like a title/company
            if current_exp is None:
                current_exp = {
                    'title': line,
                    'company': '',
                    'period': '',
                    'description': []
                }
            else:
                # Add to description
                current_exp['description'].append(line)
        
        if current_exp:
            experiences.append(current_exp)
        
        return experiences
    
    @staticmethod
    def _parse_education(education_text: str, institutions: list) -> list:
        """Parse education section into structured list."""
        if not education_text and not institutions:
            return []
        
        education = []
        
        if institutions:
            for inst in institutions:
                education.append({
                    'institution': inst,
                    'degree': '',
                    'period': '',
                    'details': ''
                })
        
        return education
    
    @staticmethod
    def _parse_skills(skills_text: str) -> list:
        """Parse skills section into list."""
        if not skills_text:
            return []
        
        # Split by common separators
        skills = []
        for separator in [',', ';', '\n', '•', '|']:
            if separator in skills_text:
                skills = [s.strip() for s in skills_text.split(separator) if s.strip()]
                break
        
        return skills if skills else [skills_text.strip()]
    
    @staticmethod
    def _parse_list_section(section_text: str) -> list:
        """Parse a list-based section."""
        if not section_text:
            return []
        
        items = []
        for line in section_text.split('\n'):
            line = line.strip()
            if line and line not in items:
                # Remove bullet points
                line = line.lstrip('•◦▪▫–—*●○ ')
                if line:
                    items.append(line)
        
        return items
    
    @staticmethod
    def _parse_projects(projects_text: str) -> list:
        """Parse projects section."""
        if not projects_text:
            return []
        
        projects = []
        lines = projects_text.split('\n')
        
        current_project = None
        for line in lines:
            line = line.strip()
            if not line:
                if current_project:
                    projects.append(current_project)
                    current_project = None
                continue
            
            if current_project is None:
                current_project = {
                    'name': line,
                    'description': []
                }
            else:
                current_project['description'].append(line)
        
        if current_project:
            projects.append(current_project)
        
        return projects
    
    def _render_template(self, template_name: str, data: Dict) -> str:
        """
        Render Jinja2 template with data.
        
        Args:
            template_name: Template filename
            data: Data dictionary
            
        Returns:
            Rendered HTML
        """
        if not JINJA2_AVAILABLE or not self.jinja_env:
            # Fallback to simple HTML generation
            return self._generate_simple_html(data)
        
        try:
            template = self.jinja_env.get_template(template_name)
            html = template.render(**data)
            logger.info(f"Template {template_name} rendered successfully")
            return html
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {e}")
            logger.info("Using fallback HTML generation")
            return self._generate_simple_html(data)
    
    @staticmethod
    def _generate_simple_html(data: Dict) -> str:
        """Generate simple HTML when template is not available."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{data.get('name', 'CV')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 25px; border-bottom: 1px solid #bdc3c7; }}
        .contact-info {{ margin-bottom: 20px; color: #7f8c8d; }}
        .section {{ margin-bottom: 20px; }}
        ul {{ list-style-type: disc; margin-left: 20px; }}
    </style>
</head>
<body>
    <h1>{data.get('name', 'Unknown Name')}</h1>
    <div class="contact-info">
        {f"Email: {data['email']}<br>" if data.get('email') else ""}
        {f"Phone: {data['phone']}<br>" if data.get('phone') else ""}
        {f"Location: {data['location']}" if data.get('location') else ""}
    </div>
    
    {f"<h2>Professional Summary</h2><div class='section'>{data['summary']}</div>" if data.get('summary') else ""}
    
    {f"<h2>Skills</h2><div class='section'><ul>{''.join(f'<li>{skill}</li>' for skill in data['skills'])}</ul></div>" if data.get('skills') else ""}
    
    {f"<h2>Work Experience</h2><div class='section'>{data['experience']}</div>" if data.get('experience') else ""}
    
    {f"<h2>Education</h2><div class='section'>{data['education']}</div>" if data.get('education') else ""}
</body>
</html>
        """
        return html
    
    @staticmethod
    def _html_to_pdf_weasyprint(html_content: str) -> bytes:
        """Convert HTML to PDF using WeasyPrint."""
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()
        return pdf_bytes
    
    @staticmethod
    def _generate_pdf_fpdf(data: Dict) -> bytes:
        """Fallback PDF generation using FPDF."""
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, data.get('name', 'CV'), ln=True, align='C')
        
        # Contact info
        pdf.set_font('Arial', '', 10)
        if data.get('email'):
            pdf.cell(0, 5, f"Email: {data['email']}", ln=True)
        if data.get('phone'):
            pdf.cell(0, 5, f"Phone: {data['phone']}", ln=True)
        if data.get('location'):
            pdf.cell(0, 5, f"Location: {data['location']}", ln=True)
        
        pdf.ln(5)
        
        # Summary
        if data.get('summary'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Professional Summary', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, data['summary'])
            pdf.ln(3)
        
        # Skills
        if data.get('skills'):
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Skills', ln=True)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, ', '.join(data['skills']))
            pdf.ln(3)
        
        return bytes(pdf.output())
