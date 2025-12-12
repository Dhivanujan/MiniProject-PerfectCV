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

    # 1. PyMuPDF (fitz) - Fastest
    if fitz and file_bytes:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_parts = []
            for page in doc:
                # Get text blocks to avoid headers/footers if needed, but simple text is fastest
                text_parts.append(page.get_text())
            
            full_text = "\n".join(text_parts)
            
            # Check if extraction was successful (not a scanned PDF)
            if full_text.strip() and len(full_text.strip()) > 100:
                logger.info(f"Extracted PDF with PyMuPDF in {time.time() - start_time:.2f}s")
                return full_text
            else:
                logger.warning("PyMuPDF extracted minimal text, might be scanned PDF")
        except Exception as e:
            logger.warning(f"PyMuPDF extraction failed: {e}")

    # 2. pdfplumber - Good accuracy, slower
    if pdfplumber:
        try:
            file_stream.seek(0)
            with pdfplumber.open(file_stream) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            
            full_text = "\n".join(text_parts)
            
            if full_text.strip() and len(full_text.strip()) > 100:
                logger.info(f"Extracted PDF with pdfplumber in {time.time() - start_time:.2f}s")
                return full_text
            else:
                logger.warning("pdfplumber extracted minimal text, might be scanned PDF")
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")

    # 3. pdfminer - Fallback, slowest
    logger.info("Trying pdfminer extraction")
    text = _pdfminer_from_stream(file_stream)
    
    # If all text extraction methods failed or returned minimal text, try OCR
    if not text or len(text.strip()) < 100:
        logger.info("Minimal text extracted, attempting OCR for scanned PDF")
        if file_bytes:
            ocr_text = _try_ocr_extraction(file_bytes)
            if ocr_text and len(ocr_text.strip()) > len(text.strip()):
                logger.info(f"OCR extraction successful in {time.time() - start_time:.2f}s")
                return ocr_text
    
    return text
