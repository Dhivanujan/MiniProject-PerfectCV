"""
CV PDF Generation Service
Generates professional ATS-friendly PDF resumes using Jinja2 + WeasyPrint.
"""
import os
import logging
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


def generate_cv_pdf(cv_json: Dict[str, Any], output_path: str = "output/cv.pdf") -> str:
    """
    Generate a professional PDF resume from structured CV data.
    
    Args:
        cv_json: Structured CV data dictionary
        output_path: Path where PDF should be saved
        
    Returns:
        Path to generated PDF file
    """
    try:
        logger.info(f"Generating PDF resume at {output_path}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Get template directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(os.path.dirname(current_dir), 'templates')
        
        # Setup Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Load template
        template = env.get_template('cv_template.html')
        
        # Render HTML with CV data
        html_content = template.render(
            name=cv_json.get('name', ''),
            email=cv_json.get('email', ''),
            phone=cv_json.get('phone', ''),
            summary=cv_json.get('summary', ''),
            skills=cv_json.get('skills', []),
            experience=cv_json.get('experience', []),
            education=cv_json.get('education', []),
            projects=cv_json.get('projects', []),
            certifications=cv_json.get('certifications', [])
        )
        
        # Configure fonts for WeasyPrint
        font_config = FontConfiguration()
        
        # Custom CSS for better PDF rendering
        custom_css = CSS(string='''
            @page {
                size: A4;
                margin: 1.5cm;
            }
            
            body {
                font-family: Arial, Helvetica, sans-serif;
                line-height: 1.6;
                color: #333;
            }
            
            /* Prevent page breaks inside sections */
            .experience-item, .education-item, .project-item {
                page-break-inside: avoid;
            }
        ''', font_config=font_config)
        
        # Generate PDF
        html = HTML(string=html_content)
        html.write_pdf(
            output_path,
            stylesheets=[custom_css],
            font_config=font_config
        )
        
        logger.info(f"Successfully generated PDF: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to generate PDF: {e}", exc_info=True)
        raise


def generate_cv_html(cv_json: Dict[str, Any], output_path: str = "output/cv.html") -> str:
    """
    Generate HTML resume (useful for previewing before PDF generation).
    
    Args:
        cv_json: Structured CV data dictionary
        output_path: Path where HTML should be saved
        
    Returns:
        Path to generated HTML file
    """
    try:
        logger.info(f"Generating HTML resume at {output_path}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Get template directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(os.path.dirname(current_dir), 'templates')
        
        # Setup Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Load template
        template = env.get_template('cv_template.html')
        
        # Render HTML with CV data
        html_content = template.render(
            name=cv_json.get('name', ''),
            email=cv_json.get('email', ''),
            phone=cv_json.get('phone', ''),
            summary=cv_json.get('summary', ''),
            skills=cv_json.get('skills', []),
            experience=cv_json.get('experience', []),
            education=cv_json.get('education', []),
            projects=cv_json.get('projects', []),
            certifications=cv_json.get('certifications', [])
        )
        
        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Successfully generated HTML: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to generate HTML: {e}", exc_info=True)
        raise
