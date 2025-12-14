import io
import logging
import time

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None
    logger.warning("PyMuPDF (fitz) not installed. Install it for faster PDF extraction.")

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from pdfminer.high_level import extract_text as pdfminer_extract_text

# OCR support for scanned PDFs
try:
    import pytesseract
    from PIL import Image
    import pdf2image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR libraries not available. Install with: pip install pytesseract pillow pdf2image")

def _pdfminer_from_stream(file_stream):
    try:
        file_stream.seek(0)
        return pdfminer_extract_text(file_stream)
    except Exception as e:
        logger.exception("pdfminer extraction failed: %s", e)
        return ""


def _try_ocr_extraction(file_bytes) -> str:
    """Attempt OCR extraction for scanned PDFs."""
    if not OCR_AVAILABLE:
        return ""
    
    try:
        logger.info("Attempting OCR extraction for scanned PDF")
        
        # Save to temporary file for pdf2image
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(file_bytes)
            tmp_path = tmp_file.name
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(tmp_path, dpi=300)
            
            # Extract text from each page
            text_parts = []
            for i, image in enumerate(images):
                logger.info(f"OCR processing page {i+1}/{len(images)}")
                text = pytesseract.image_to_string(image, lang='eng')
                if text.strip():
                    text_parts.append(text)
            
            full_text = "\n\n".join(text_parts)
            logger.info(f"OCR extraction successful: {len(full_text)} characters")
            return full_text
        finally:
            # Clean up temporary file
            import os
            try:
                os.unlink(tmp_path)
            except:
                pass
                
    except Exception as e:
        logger.warning(f"OCR extraction failed: {e}")
        return ""


def normalize_phone_blocks(text: str) -> str:
    """Normalize phone numbers broken across lines in PDF extraction.
    
    Example: '+94\n77\n2027\n2019' -> '+94 7720272019'
    """
    import re
    
    if not text:
        return ""
    
    # Find phone number patterns that might be broken across lines
    # Pattern: optional +, followed by digits with newlines/spaces between groups
    phone_pattern = r'(\+?\d{1,4})[\s\n]+(\d{1,4})[\s\n]+(\d{2,4})[\s\n]+(\d{2,4})'
    
    def join_phone_parts(match):
        # Join all captured groups with spaces, removing + if present
        parts = [p for p in match.groups() if p]
        if parts[0].startswith('+'):
            return parts[0] + ' ' + ''.join(parts[1:])
        return ''.join(parts)
    
    text = re.sub(phone_pattern, join_phone_parts, text)
    
    # Also handle simple newlines within phone numbers
    # Pattern: digits followed by newline and more digits (likely phone number)
    text = re.sub(r'(\d{2,4})\n(\d{2,4})', r'\1\2', text)
    
    return text

def clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted PDF text with phone number normalization."""
    import re
    
    if not text:
        return ""
    
    # CRITICAL: Normalize phone numbers FIRST before any other processing
    text = normalize_phone_blocks(text)
    
    # Remove common PDF artifacts
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    
    # Normalize line breaks - preserve paragraph structure
    text = text.replace('\\n', '\n')
    
    # Remove page numbers (standalone numbers on lines)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove header/footer patterns (repeated text)
    lines = text.split('\n')
    if len(lines) > 10:
        first_line = lines[0].strip().lower()
        if any(word in first_line for word in ['page', 'confidential', 'draft']):
            lines = lines[1:]
        last_line = lines[-1].strip().lower()
        if any(word in last_line for word in ['page', 'confidential', 'draft']):
            lines = lines[:-1]
    
    text = '\n'.join(lines)
    
    # Restore proper spacing around punctuation
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    
    # Normalize excessive whitespace but preserve single newlines
    text = re.sub(r' +', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\n{3,}', '\n\n', text)  # Multiple newlines to double
    
    # Trim whitespace
    text = text.strip()
    
    return text

def extract_text_from_pdf(file_stream) -> str:
    """
    Extract text from PDF using the fastest available method.
    Priority: PyMuPDF (fitz) -> pdfplumber -> pdfminer -> OCR (for scanned PDFs)
    """
    start_time = time.time()
    
    # Ensure stream is at start
    try:
        file_stream.seek(0)
    except Exception:
        pass
        
    # Read stream content once if needed for libraries that require bytes
    file_bytes = None
    try:
        file_bytes = file_stream.read()
        file_stream.seek(0)
    except Exception:
        pass

    # 1. PyMuPDF (fitz) - PRIMARY EXTRACTION METHOD
    if fitz and file_bytes:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_parts = []
            
            for page_num, page in enumerate(doc, 1):
                # Use "text" layout mode for better text extraction
                # This preserves reading order and handles multi-column layouts better
                page_text = page.get_text("text", sort=True)
                
                # Alternative: Use "blocks" for more structured extraction
                # blocks = page.get_text("blocks")
                # page_text = "\n".join([block[4] for block in blocks if block[6] == 0])  # text blocks only
                
                if page_text.strip():
                    text_parts.append(page_text)
                    logger.debug(f"PyMuPDF: Extracted {len(page_text)} chars from page {page_num}")
            
            doc.close()
            
            full_text = "\n\n".join(text_parts)  # Double newline between pages
            
            # Check if extraction was successful (not a scanned PDF)
            if full_text.strip() and len(full_text.strip()) > 100:
                # Clean and normalize the extracted text
                cleaned_text = clean_extracted_text(full_text)
                logger.info(f"✓ PyMuPDF extracted {len(cleaned_text)} chars in {time.time() - start_time:.2f}s")
                return cleaned_text
            else:
                logger.warning("⚠ PyMuPDF extracted minimal text, might be scanned PDF")
        except Exception as e:
            logger.warning(f"⚠ PyMuPDF extraction failed: {e}")
    elif not fitz:
        logger.warning("⚠ PyMuPDF not installed. Install: pip install PyMuPDF")

    # 2. pdfplumber - Fallback if PyMuPDF fails
    if pdfplumber:
        try:
            logger.info("Trying pdfplumber as fallback")
            file_stream.seek(0)
            with pdfplumber.open(file_stream) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            full_text = "\n".join(text_parts)
            
            if full_text.strip() and len(full_text.strip()) > 100:
                logger.info(f"✓ pdfplumber extracted {len(full_text)} chars in {time.time() - start_time:.2f}s")
                return full_text
            else:
                logger.warning("⚠ pdfplumber extracted minimal text")
        except Exception as e:
            logger.warning(f"⚠ pdfplumber extraction failed: {e}")

    # 3. pdfminer - Last fallback
    logger.info("Trying pdfminer as last fallback")
    text = _pdfminer_from_stream(file_stream)
    
    # If all text extraction methods failed or returned minimal text, try OCR
    if not text or len(text.strip()) < 100:
        logger.info("Minimal text extracted, attempting OCR for scanned PDF")
        if file_bytes:
            ocr_text = _try_ocr_extraction(file_bytes)
            if ocr_text and len(ocr_text.strip()) > len(text.strip()):
                logger.info(f"OCR extraction successful in {time.time() - start_time:.2f}s")
                text = ocr_text
    
    # Clean the extracted text
    cleaned_text = clean_extracted_text(text)
    
    logger.info(f"Final extraction: {len(cleaned_text)} characters in {time.time() - start_time:.2f}s")
    
    return cleaned_text
