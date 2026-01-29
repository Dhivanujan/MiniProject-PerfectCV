"""
CV Generation Service using Jinja2 and xhtml2pdf
Generates professional PDFs from extracted CV data.

Refactored for:
- Better error handling and validation
- Flexible data normalization
- Template management
- Performance optimization
- Extensibility
"""
import io
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# Import templating and PDF generation
try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound
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


@dataclass
class CVGenerationConfig:
    """Configuration for CV generation."""
    default_template: str = "enhanced_cv.html"  # Enhanced template optimized for xhtml2pdf
    enable_logging: bool = True
    max_pdf_size_mb: float = 10.0
    encoding: str = 'utf-8'
    
    # Template rendering options
    strip_whitespace: bool = True
    optimize_output: bool = True
    
    # PDF generation options
    pdf_compression: bool = True


@dataclass
class CVGenerationResult:
    """Result of CV generation operation."""
    success: bool
    pdf_bytes: Optional[io.BytesIO] = None
    file_path: Optional[Path] = None
    file_size: int = 0
    template_used: str = ""
    generation_time_ms: float = 0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class CVDataNormalizer:
    """Handles normalization of different CV data formats."""
    
    @staticmethod
    def normalize(cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize CV data to consistent format for templates.
        
        Args:
            cv_data: Raw CV data in various formats
            
        Returns:
            Normalized data with 'entities' key
        """
        if not cv_data:
            return {'entities': CVDataNormalizer._get_empty_cv()}
        
        # Already normalized
        if 'entities' in cv_data and isinstance(cv_data['entities'], dict):
            return cv_data
        
        # Direct data format - wrap in entities
        return {'entities': cv_data}
    
    @staticmethod
    def _get_empty_cv() -> Dict[str, Any]:
        """Get empty CV structure."""
        return {
            'name': '',
            'email': '',
            'phone': '',
            'location': '',
            'summary': '',
            'skills': [],
            'experience': [],
            'education': [],
            'projects': [],
            'certifications': []
        }
    
    @staticmethod
    def validate(cv_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate CV data structure.
        
        Returns:
            (is_valid, list_of_warnings)
        """
        warnings = []
        entities = cv_data.get('entities', {})
        
        # Check required fields
        if not entities.get('name'):
            warnings.append("Name is missing or empty")
        
        if not entities.get('email') and not entities.get('phone'):
            warnings.append("No contact information (email or phone)")
        
        # Check list fields
        list_fields = ['skills', 'experience', 'education']
        for field in list_fields:
            value = entities.get(field)
            if value is not None and not isinstance(value, list):
                warnings.append(f"{field} should be a list, got {type(value).__name__}")
        
        return len(warnings) == 0, warnings


class TemplateManager:
    """Manages CV templates."""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self._cache = {}
    
    def get_template_path(self, template_name: str) -> Path:
        """Get full path to template file."""
        return self.templates_dir / template_name
    
    def template_exists(self, template_name: str) -> bool:
        """Check if template exists."""
        return self.get_template_path(template_name).exists()
    
    def list_templates(self) -> List[str]:
        """List all available templates."""
        if not self.templates_dir.exists():
            return []
        return sorted([f.name for f in self.templates_dir.glob("*.html")])
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a template."""
        path = self.get_template_path(template_name)
        if not path.exists():
            return {'exists': False}
        
        stat = path.stat()
        return {
            'exists': True,
            'name': template_name,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
        }


class CVGenerator:
    """Generate professional CVs from extracted data using Jinja2 and xhtml2pdf."""
    
    def __init__(
        self, 
        templates_dir: Optional[Path] = None,
        config: Optional[CVGenerationConfig] = None
    ):
        """
        Initialize CV generator.
        
        Args:
            templates_dir: Path to templates directory. If None, uses default.
            config: Generation configuration
        """
        if not JINJA2_AVAILABLE:
            raise RuntimeError("Jinja2 is required. Install: pip install Jinja2")
        
        if not XHTML2PDF_AVAILABLE:
            raise RuntimeError("xhtml2pdf is required. Install: pip install xhtml2pdf")
        
        # Configuration
        self.config = config or CVGenerationConfig()
        
        # Set templates directory
        if templates_dir is None:
            current_file = Path(__file__)
            templates_dir = current_file.parent.parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        
        if not self.templates_dir.exists():
            raise FileNotFoundError(f"Templates directory not found: {self.templates_dir}")
        
        # Initialize managers
        self.template_manager = TemplateManager(self.templates_dir)
        self.normalizer = CVDataNormalizer()
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=self.config.strip_whitespace,
            lstrip_blocks=self.config.strip_whitespace
        )
        
        # Add custom filters
        self._register_template_filters()
        
        if self.config.enable_logging:
            logger.info(f"✓ CV Generator initialized")
            logger.info(f"  Templates: {self.templates_dir}")
            logger.info(f"  Available: {len(self.template_manager.list_templates())} templates")
    
    def _register_template_filters(self):
        """Register custom Jinja2 filters for templates."""
        
        def format_date(date_str: str, format: str = '%Y-%m-%d') -> str:
            """Format date string."""
            if not date_str:
                return ''
            try:
                if isinstance(date_str, str):
                    # Try parsing common formats
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d/%m/%Y']:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            return dt.strftime(format)
                        except ValueError:
                            continue
                return str(date_str)
            except Exception:
                return str(date_str)
        
        def truncate_text(text: str, length: int = 100) -> str:
            """Truncate text to specified length."""
            if not text or len(text) <= length:
                return text
            return text[:length].rsplit(' ', 1)[0] + '...'
        
        def capitalize_words(text: str) -> str:
            """Capitalize each word."""
            if not text:
                return ''
            return ' '.join(word.capitalize() for word in text.split())
        
        # Register filters with Jinja2 environment
        self.env.filters['format_date'] = format_date
        self.env.filters['truncate_text'] = truncate_text
        self.env.filters['capitalize_words'] = capitalize_words
    
    def generate_cv_pdf(
        self, 
        cv_data: Dict[str, Any], 
        template_name: Optional[str] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> Union[io.BytesIO, CVGenerationResult]:
        """
        Generate a PDF CV from extracted data.
        
        Args:
            cv_data: CV data (extraction result or direct data)
            template_name: Template to use (default from config)
            output_path: Optional path to save PDF file
        
        Returns:
            BytesIO with PDF content (for backward compatibility)
            or CVGenerationResult (if detailed result needed)
        """
        start_time = datetime.now()
        result = CVGenerationResult(success=False)
        
        try:
            # Use default template if not specified
            template_name = template_name or self.config.default_template
            result.template_used = template_name
            
            if self.config.enable_logging:
                logger.info(f"{'=' * 70}")
                logger.info(f"🎨 Generating CV PDF")
                logger.info(f"{'=' * 70}")
                logger.info(f"Template: {template_name}")
            
            # Validate template exists
            if not self.template_manager.template_exists(template_name):
                available = self.template_manager.list_templates()
                raise FileNotFoundError(
                    f"Template '{template_name}' not found. "
                    f"Available: {', '.join(available)}"
                )
            
            # Normalize data
            normalized_data = self.normalizer.normalize(cv_data)
            
            # Validate data
            is_valid, warnings = self.normalizer.validate(normalized_data)
            result.warnings = warnings
            
            if warnings and self.config.enable_logging:
                for warning in warnings:
                    logger.warning(f"⚠ {warning}")
            
            candidate_name = normalized_data.get('entities', {}).get('name', 'Unknown')
            
            if self.config.enable_logging:
                logger.info(f"Candidate: {candidate_name}")
            
            # Render HTML
            html_content = self._render_template(template_name, normalized_data)
            
            if self.config.enable_logging:
                logger.info(f"✓ Template rendered ({len(html_content)} chars)")
            
            # Generate PDF
            pdf_output = self._generate_pdf_from_html(html_content)
            
            pdf_bytes = pdf_output.getvalue()
            result.file_size = len(pdf_bytes)
            
            # Check size limit
            size_mb = result.file_size / (1024 * 1024)
            if size_mb > self.config.max_pdf_size_mb:
                result.warnings.append(
                    f"PDF size ({size_mb:.2f}MB) exceeds recommended limit "
                    f"({self.config.max_pdf_size_mb}MB)"
                )
            
            if self.config.enable_logging:
                logger.info(f"✓ PDF generated ({result.file_size:,} bytes)")
            
            # Save to file if requested
            if output_path:
                output_path = Path(output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(pdf_bytes)
                result.file_path = output_path
                
                if self.config.enable_logging:
                    logger.info(f"✓ PDF saved to: {output_path}")
            
            # Reset BytesIO position
            pdf_output.seek(0)
            result.pdf_bytes = pdf_output
            result.success = True
            
            # Calculate generation time
            end_time = datetime.now()
            result.generation_time_ms = (end_time - start_time).total_seconds() * 1000
            
            if self.config.enable_logging:
                logger.info(f"⏱ Generation time: {result.generation_time_ms:.0f}ms")
                logger.info(f"{'=' * 70}")
                logger.info(f"✅ CV generation complete")
                logger.info(f"{'=' * 70}")
            
            # Return BytesIO for backward compatibility
            return pdf_output
            
        except TemplateNotFound as e:
            error_msg = f"Template not found: {e}"
            logger.error(f"❌ {error_msg}")
            result.error_message = error_msg
            raise FileNotFoundError(error_msg)
        
        except Exception as e:
            error_msg = f"PDF generation failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            result.error_message = error_msg
            raise
    
    def _render_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Render Jinja2 template with data."""
        try:
            template = self.env.get_template(template_name)
            return template.render(**data)
        except Exception as e:
            raise RuntimeError(f"Template rendering failed: {e}")
    
    def _generate_pdf_from_html(self, html_content: str) -> io.BytesIO:
        """Convert HTML to PDF using xhtml2pdf."""
        output = io.BytesIO()
        
        try:
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=output,
                encoding=self.config.encoding
            )
            
            if pisa_status.err:
                raise RuntimeError(
                    f"PDF generation failed with {pisa_status.err} error(s)"
                )
            
            return output
            
        except Exception as e:
            raise RuntimeError(f"PDF conversion failed: {e}")
    
    def generate_cv_html(
        self, 
        cv_data: Dict[str, Any], 
        template_name: Optional[str] = None
    ) -> str:
        """
        Generate HTML CV from extracted data (for preview).
        
        Args:
            cv_data: CV data (extraction result or direct data)
            template_name: Template to use (default from config)
        
        Returns:
            HTML string
        """
        try:
            template_name = template_name or self.config.default_template
            
            # Normalize data
            normalized_data = self.normalizer.normalize(cv_data)
            
            # Render template
            return self._render_template(template_name, normalized_data)
            
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            raise
    
    def list_available_templates(self) -> List[str]:
        """List all available CV templates."""
        return self.template_manager.list_templates()
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get information about a specific template."""
        return self.template_manager.get_template_info(template_name)
    
    def validate_cv_data(self, cv_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate CV data structure.
        
        Returns:
            (is_valid, list_of_warnings)
        """
        normalized = self.normalizer.normalize(cv_data)
        return self.normalizer.validate(normalized)


# Singleton instance
_generator_instance: Optional[CVGenerator] = None
_generator_config: Optional[CVGenerationConfig] = None


def get_cv_generator(config: Optional[CVGenerationConfig] = None) -> CVGenerator:
    """
    Get or create singleton CV generator instance.
    
    Args:
        config: Optional configuration (only used on first call)
    """
    global _generator_instance, _generator_config
    
    if _generator_instance is None:
        _generator_config = config or CVGenerationConfig()
        _generator_instance = CVGenerator(config=_generator_config)
    
    return _generator_instance


def reset_cv_generator():
    """Reset singleton instance (useful for testing)."""
    global _generator_instance, _generator_config
    _generator_instance = None
    _generator_config = None


def generate_cv_from_extraction(
    extraction_result: Dict[str, Any],
    template: str = "modern_cv.html",
    output_path: Optional[Path] = None
) -> io.BytesIO:
    """
    Convenience function to generate CV PDF from extraction result.
    
    Args:
        extraction_result: Result from unified_cv_extractor.extract_from_file()
        template: Template name to use
        output_path: Optional path to save PDF
    
    Returns:
        BytesIO with PDF content
    """
    generator = get_cv_generator()
    return generator.generate_cv_pdf(extraction_result, template, output_path)

