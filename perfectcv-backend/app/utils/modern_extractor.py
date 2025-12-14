"""
Modern CV Extraction System
Uses state-of-the-art libraries and techniques for superior text extraction
"""
import io
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# Modern PDF extraction libraries
try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False
    logger.warning("pypdf not available - install with: pip install pypdf")

try:
    import fitz  # PyMuPDF - still best for complex PDFs
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    logger.warning("pydantic not available - install with: pip install pydantic")


class ExtractionMethod(Enum):
    """Available extraction methods ranked by quality"""
    PYMUPDF = "pymupdf"  # Best quality, preserves layout
    PYPDF = "pypdf"      # Modern, pure Python
    FALLBACK = "fallback"  # Basic extraction


@dataclass
class ExtractionResult:
    """Structured extraction result with metadata"""
    text: str
    method: ExtractionMethod
    page_count: int = 0
    char_count: int = 0
    word_count: int = 0
    has_images: bool = False
    has_tables: bool = False
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate statistics after initialization"""
        if self.text:
            self.char_count = len(self.text)
            self.word_count = len(self.text.split())
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'text': self.text,
            'method': self.method.value,
            'page_count': self.page_count,
            'char_count': self.char_count,
            'word_count': self.word_count,
            'has_images': self.has_images,
            'has_tables': self.has_tables,
            'confidence': self.confidence,
            'metadata': self.metadata
        }


class ModernPDFExtractor:
    """
    State-of-the-art PDF text extraction with multiple fallback strategies
    """
    
    def __init__(self):
        self.methods = []
        
        # Register available extraction methods in order of preference
        if FITZ_AVAILABLE:
            self.methods.append(ExtractionMethod.PYMUPDF)
        if PYPDF_AVAILABLE:
            self.methods.append(ExtractionMethod.PYPDF)
        
        if not self.methods:
            logger.error("No PDF extraction libraries available!")
            self.methods.append(ExtractionMethod.FALLBACK)
    
    def extract(self, file_bytes: bytes) -> ExtractionResult:
        """
        Extract text using best available method with automatic fallback
        
        Args:
            file_bytes: PDF file as bytes
            
        Returns:
            ExtractionResult with text and metadata
        """
        file_stream = io.BytesIO(file_bytes)
        
        # Try each method in order
        for method in self.methods:
            try:
                if method == ExtractionMethod.PYMUPDF:
                    return self._extract_with_pymupdf(file_stream)
                elif method == ExtractionMethod.PYPDF:
                    return self._extract_with_pypdf(file_stream)
            except Exception as e:
                logger.warning(f"Extraction with {method.value} failed: {e}")
                file_stream.seek(0)  # Reset for next attempt
                continue
        
        # Ultimate fallback
        return ExtractionResult(
            text="",
            method=ExtractionMethod.FALLBACK,
            confidence=0.0
        )
    
    def _extract_with_pymupdf(self, file_stream: io.BytesIO) -> ExtractionResult:
        """
        Extract using PyMuPDF with advanced layout preservation
        
        PyMuPDF is still the best for:
        - Layout preservation
        - Multi-column documents
        - Complex formatting
        - Table detection
        """
        import fitz
        
        file_stream.seek(0)
        doc = fitz.open(stream=file_stream.read(), filetype="pdf")
        
        # Extract with advanced options
        text_parts = []
        has_images = False
        has_tables = False
        
        for page_num, page in enumerate(doc):
            # Get text with layout preservation
            text = page.get_text(
                "text",
                sort=True,  # Sort by reading order
                flags=fitz.TEXT_PRESERVE_WHITESPACE | fitz.TEXT_PRESERVE_LIGATURES
            )
            
            if text.strip():
                text_parts.append(text)
            
            # Check for images
            if page.get_images():
                has_images = True
            
            # Check for tables (heuristic: multiple tab characters)
            if '\t' in text or text.count('|') > 5:
                has_tables = True
        
        full_text = "\n\n".join(text_parts)
        
        # Clean and normalize
        full_text = self._normalize_text(full_text)
        
        metadata = {
            'title': doc.metadata.get('title', ''),
            'author': doc.metadata.get('author', ''),
            'creator': doc.metadata.get('creator', ''),
            'producer': doc.metadata.get('producer', ''),
        }
        
        doc.close()
        
        logger.info(f"✓ PyMuPDF extraction: {len(full_text)} chars, {len(text_parts)} pages")
        
        return ExtractionResult(
            text=full_text,
            method=ExtractionMethod.PYMUPDF,
            page_count=len(text_parts),
            has_images=has_images,
            has_tables=has_tables,
            confidence=0.95 if len(full_text) > 100 else 0.5,
            metadata=metadata
        )
    
    def _extract_with_pypdf(self, file_stream: io.BytesIO) -> ExtractionResult:
        """
        Extract using pypdf (modern, pure Python)
        
        Benefits:
        - Pure Python, no system dependencies
        - Active development
        - Good for simple PDFs
        """
        from pypdf import PdfReader
        
        file_stream.seek(0)
        reader = PdfReader(file_stream)
        
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text.strip():
                text_parts.append(text)
        
        full_text = "\n\n".join(text_parts)
        full_text = self._normalize_text(full_text)
        
        metadata = {
            'title': reader.metadata.get('/Title', '') if reader.metadata else '',
            'author': reader.metadata.get('/Author', '') if reader.metadata else '',
        }
        
        logger.info(f"✓ pypdf extraction: {len(full_text)} chars, {len(text_parts)} pages")
        
        return ExtractionResult(
            text=full_text,
            method=ExtractionMethod.PYPDF,
            page_count=len(text_parts),
            confidence=0.85 if len(full_text) > 100 else 0.4,
            metadata=metadata
        )
    
    def _normalize_text(self, text: str) -> str:
        """
        Modern text normalization using advanced techniques
        """
        import re
        
        if not text:
            return ""
        
        # Fix broken phone numbers (from PDF line breaks)
        text = self._fix_phone_numbers(text)
        
        # Fix broken words with hyphens
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Normalize whitespace
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
        
        # Remove form feed and other control characters
        text = re.sub(r'[\x0c\x0b]', '\n', text)
        
        # Fix common PDF artifacts
        text = text.replace('\uf0b7', '•')  # Bullet point
        text = text.replace('\u2022', '•')
        text = text.replace('\u2013', '-')  # En dash
        text = text.replace('\u2014', '—')  # Em dash
        
        return text.strip()
    
    def _fix_phone_numbers(self, text: str) -> str:
        """Fix phone numbers broken across lines"""
        import re
        
        # Pattern: +XX followed by digits with newlines
        pattern = r'(\+?\d{1,4})[\s\n]+(\d{1,4})[\s\n]+(\d{2,4})[\s\n]+(\d{2,4})'
        
        def join_parts(match):
            parts = [p for p in match.groups() if p]
            if parts[0].startswith('+'):
                return parts[0] + ' ' + ''.join(parts[1:])
            return ''.join(parts)
        
        return re.sub(pattern, join_parts, text)


# Global extractor instance
_extractor = None

def get_extractor() -> ModernPDFExtractor:
    """Get singleton extractor instance"""
    global _extractor
    if _extractor is None:
        _extractor = ModernPDFExtractor()
    return _extractor


def extract_pdf_modern(file_bytes: bytes) -> ExtractionResult:
    """
    Modern PDF extraction with automatic method selection
    
    Usage:
        result = extract_pdf_modern(pdf_bytes)
        print(f"Extracted {result.word_count} words using {result.method.value}")
        print(f"Confidence: {result.confidence}")
        print(result.text)
    
    Args:
        file_bytes: PDF file as bytes
        
    Returns:
        ExtractionResult with text and comprehensive metadata
    """
    extractor = get_extractor()
    return extractor.extract(file_bytes)
