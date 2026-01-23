"""
CV Generation Service using Jinja2 and xhtml2pdf
Generates professional PDFs from extracted CV data.
"""
import io
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Import templating and PDF generation
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    logger.warning("Jinja2 not available. Install: pip install Jinja2")

try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
except ImportError:
    XHTML2PDF_AVAILABLE = False
    logger.warning("xhtml2pdf not available. Install: pip install xhtml2pdf")


class CVGenerator:
    """Generate professional CVs from extracted data using Jinja2 and xhtml2pdf."""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """
        Initialize CV generator.
        
        Args:
            templates_dir: Path to templates directory. If None, uses default.
        """
        if not JINJA2_AVAILABLE:
            raise RuntimeError("Jinja2 is required. Install: pip install Jinja2")
        
        if not XHTML2PDF_AVAILABLE:
            raise RuntimeError("xhtml2pdf is required. Install: pip install xhtml2pdf")
        
        # Set templates directory
        if templates_dir is None:
            # Default to app/templates
            current_file = Path(__file__)
            templates_dir = current_file.parent.parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        
        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        logger.info(f"✓ CV Generator initialized with templates from: {self.templates_dir}")
    
    def generate_cv_pdf(
        self, 
        cv_data: Dict[str, Any], 
        template_name: str = "modern_cv.html",
        output_path: Optional[Path] = None
    ) -> bytes:
        """
        Generate a PDF CV from extracted data.
        
        Args:
            cv_data: CV data - can be:
                     1) Extraction result: {'entities': {...}, 'raw_text': '...'}
                     2) Direct data: {'name': '...', 'email': '...', ...}
            template_name: Name of the Jinja2 template to use
            output_path: Optional path to save PDF file
        
        Returns:
            PDF bytes (as BytesIO)
        """
        try:
            logger.info(f"=" * 70)
            logger.info(f"🎨 Generating CV PDF")
            logger.info(f"=" * 70)
            logger.info(f"Template: {template_name}")
            
            # Normalize data structure - handle both extraction results and direct data
            if 'entities' in cv_data:
                # Already in extraction format
                template_data = cv_data
                candidate_name = cv_data.get('entities', {}).get('name', 'Unknown')
            else:
                # Direct data format - wrap in 'entities' key for template
                template_data = {'entities': cv_data}
                candidate_name = cv_data.get('name', 'Unknown')
            
            logger.info(f"Candidate: {candidate_name}")
            
            # Load template
            template = self.env.get_template(template_name)
            
            # Render HTML with CV data
            html_content = template.render(**template_data)
            
            logger.info(f"✓ Template rendered successfully")
            
            # Convert HTML to PDF using xhtml2pdf
            output = io.BytesIO()
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=output,
                encoding='utf-8'
            )
            
            if pisa_status.err:
                raise RuntimeError(f"PDF generation failed with error code: {pisa_status.err}")
            
            # Get bytes for file saving if needed
            pdf_bytes = output.getvalue()
            
            logger.info(f"✓ PDF generated ({len(pdf_bytes)} bytes)")
            
            # Save to file if path provided
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(pdf_bytes)
                logger.info(f"✓ PDF saved to: {output_path}")
            
            # Reset BytesIO position for reading
            output.seek(0)
            
            logger.info(f"=" * 70)
            logger.info(f"✅ CV generation complete")
            logger.info(f"=" * 70)
            
            return output
            
        except Exception as e:
            logger.error(f"❌ PDF generation failed: {e}")
            raise
    
    def generate_cv_html(
        self, 
        cv_data: Dict[str, Any], 
        template_name: str = "modern_cv.html"
    ) -> str:
        """
        Generate HTML CV from extracted data (for preview).
        
        Args:
            cv_data: CV data - can be extraction result or direct data
            template_name: Name of the Jinja2 template to use
        
        Returns:
            HTML string
        """
        try:
            # Normalize data structure - handle both formats
            if 'entities' in cv_data:
                template_data = cv_data
            else:
                template_data = {'entities': cv_data}
            
            template = self.env.get_template(template_name)
            html_content = template.render(**template_data)
            return html_content
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            raise
    
    def list_available_templates(self) -> list[str]:
        """
        List all available CV templates.
        
        Returns:
            List of template filenames
        """
        templates = []
        for file in self.templates_dir.glob("*.html"):
            templates.append(file.name)
        return sorted(templates)


# Singleton instance
_generator_instance = None

def get_cv_generator() -> CVGenerator:
    """Get or create singleton CV generator instance."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = CVGenerator()
    return _generator_instance


def generate_cv_from_extraction(
    extraction_result: Dict[str, Any],
    template: str = "modern_cv.html",
    output_path: Optional[Path] = None
) -> bytes:
    """
    Convenience function to generate CV PDF from extraction result.
    
    Args:
        extraction_result: Result from unified_cv_extractor.extract_from_file()
        template: Template name to use
        output_path: Optional path to save PDF
    
    Returns:
        PDF bytes
    """
    generator = get_cv_generator()
    return generator.generate_cv_pdf(extraction_result, template, output_path)
