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

def _pdfminer_from_stream(file_stream):
    try:
        file_stream.seek(0)
        return pdfminer_extract_text(file_stream)
    except Exception as e:
        logger.exception("pdfminer extraction failed: %s", e)
        return ""

def extract_text_from_pdf(file_stream) -> str:
    """
    Extract text from PDF using the fastest available method.
    Priority: PyMuPDF (fitz) -> pdfplumber -> pdfminer
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
            logger.info(f"Extracted PDF with PyMuPDF in {time.time() - start_time:.2f}s")
            return full_text
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
            logger.info(f"Extracted PDF with pdfplumber in {time.time() - start_time:.2f}s")
            return full_text
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")

    # 3. pdfminer - Fallback, slowest
    logger.info("Falling back to pdfminer")
    return _pdfminer_from_stream(file_stream)
