"""
Text extraction utilities for PDF and DOCX files.
Supports multiple extraction methods with fallback.
"""
import io
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Import available libraries
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not available")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available")

try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False
    logger.warning("pdfminer.six not available")

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logger.warning("python-docx not available")

try:
    import pytesseract
    from PIL import Image
    import pdf2image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.info("OCR not available - install pytesseract, pillow, pdf2image for scanned PDF support")


class TextExtractor:
    """Extract text from PDF and DOCX files with multiple fallback methods."""
    
    @staticmethod
    def extract_from_pdf(file_bytes: bytes, filename: str = "document.pdf") -> Tuple[str, str]:
        """
        Extract text from PDF with fallback methods.
        
        Args:
            file_bytes: PDF file content as bytes
            filename: Original filename for logging
            
        Returns:
            Tuple of (extracted_text, extraction_method)
        """
        text = ""
        method = "none"
        
        # Try pdfplumber first (best for CVs with tables)
        if PDFPLUMBER_AVAILABLE and not text:
            try:
                text = TextExtractor._extract_with_pdfplumber(file_bytes)
                if text and len(text.strip()) > 50:
                    method = "pdfplumber"
                    logger.info(f"Extracted {len(text)} chars from {filename} using pdfplumber")
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed: {e}")
        
        # Try PyPDF2 as fallback
        if PYPDF2_AVAILABLE and not text:
            try:
                text = TextExtractor._extract_with_pypdf2(file_bytes)
                if text and len(text.strip()) > 50:
                    method = "pypdf2"
                    logger.info(f"Extracted {len(text)} chars from {filename} using PyPDF2")
            except Exception as e:
                logger.warning(f"PyPDF2 extraction failed: {e}")
        
        # Try pdfminer as fallback
        if PDFMINER_AVAILABLE and not text:
            try:
                text = TextExtractor._extract_with_pdfminer(file_bytes)
                if text and len(text.strip()) > 50:
                    method = "pdfminer"
                    logger.info(f"Extracted {len(text)} chars from {filename} using pdfminer")
            except Exception as e:
                logger.warning(f"pdfminer extraction failed: {e}")
        
        # Try OCR as last resort for scanned PDFs
        if OCR_AVAILABLE and (not text or len(text.strip()) < 50):
            try:
                ocr_text = TextExtractor._extract_with_ocr(file_bytes)
                if ocr_text and len(ocr_text.strip()) > 50:
                    text = ocr_text
                    method = "ocr"
                    logger.info(f"Extracted {len(text)} chars from {filename} using OCR")
            except Exception as e:
                logger.warning(f"OCR extraction failed: {e}")
        
        if not text:
            logger.error(f"Failed to extract text from {filename}")
            raise ValueError("Could not extract text from PDF. File may be corrupted or scanned without OCR support.")
        
        return text, method
    
    @staticmethod
    def _extract_with_pdfplumber(file_bytes: bytes) -> str:
        """Extract text using pdfplumber (good for tables)."""
        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n\n".join(text_parts)
    
    @staticmethod
    def _extract_with_pypdf2(file_bytes: bytes) -> str:
        """Extract text using PyPDF2."""
        text_parts = []
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n\n".join(text_parts)
    
    @staticmethod
    def _extract_with_pdfminer(file_bytes: bytes) -> str:
        """Extract text using pdfminer.six."""
        return pdfminer_extract_text(io.BytesIO(file_bytes))
    
    @staticmethod
    def _extract_with_ocr(file_bytes: bytes) -> str:
        """Extract text using OCR (for scanned PDFs)."""
        import tempfile
        import os
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(tmp_path)
            text_parts = []
            
            for i, image in enumerate(images):
                logger.info(f"Performing OCR on page {i+1}/{len(images)}")
                page_text = pytesseract.image_to_string(image)
                if page_text:
                    text_parts.append(page_text)
            
            return "\n\n".join(text_parts)
        finally:
            # Cleanup temp file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
    
    @staticmethod
    def extract_from_docx(file_bytes: bytes, filename: str = "document.docx") -> Tuple[str, str]:
        """
        Extract text from DOCX file.
        
        Args:
            file_bytes: DOCX file content as bytes
            filename: Original filename for logging
            
        Returns:
            Tuple of (extracted_text, extraction_method)
        """
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx library not available. Install with: pip install python-docx")
        
        try:
            doc = Document(io.BytesIO(file_bytes))
            text_parts = []
            
            # Extract paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            
            # Extract tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        text_parts.append(row_text)
            
            text = "\n".join(text_parts)
            logger.info(f"Extracted {len(text)} chars from {filename} using python-docx")
            
            if not text or len(text.strip()) < 20:
                raise ValueError("Extracted text is too short or empty")
            
            return text, "python-docx"
            
        except Exception as e:
            logger.error(f"Failed to extract text from {filename}: {e}")
            raise ValueError(f"Could not extract text from DOCX: {str(e)}")
    
    @staticmethod
    def extract_text(file_bytes: bytes, filename: str) -> Tuple[str, str]:
        """
        Auto-detect file type and extract text.
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            
        Returns:
            Tuple of (extracted_text, extraction_method)
        """
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.pdf'):
            return TextExtractor.extract_from_pdf(file_bytes, filename)
        elif filename_lower.endswith(('.docx', '.doc')):
            return TextExtractor.extract_from_docx(file_bytes, filename)
        else:
            raise ValueError(f"Unsupported file type: {filename}. Supported: PDF, DOCX")
