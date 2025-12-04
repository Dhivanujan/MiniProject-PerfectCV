import io
import logging
try:
    import pdfplumber
except Exception:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

from pdfminer.high_level import extract_text as pdfminer_extract_text

logger = logging.getLogger(__name__)


def _pdfminer_from_stream(file_stream):
    try:
        # pdfminer accepts file-like objects
        file_stream.seek(0)
        return pdfminer_extract_text(file_stream)
    except Exception as e:
        logger.exception("pdfminer extraction failed: %s", e)
        return ""


def extract_text_from_pdf(file_stream) -> str:
    """Try multiple backends to extract text from PDF. Returns normalized plain text.

    Order:
    1. pdfplumber (if installed)
    2. PyMuPDF (fitz)
    3. pdfminer.six fallback
    """
    try:
        # Ensure we have a fresh stream start
        file_stream.seek(0)
    except Exception:
        try:
            file_stream = io.BytesIO(file_stream.read())
            file_stream.seek(0)
        except Exception:
            pass

    # 1) pdfplumber - often gives best layout-preserving text
    if pdfplumber:
        try:
            file_stream.seek(0)
            with pdfplumber.open(file_stream) as pdf:
                texts = []
                for page in pdf.pages:
                    try:
                        t = page.extract_text() or ""
                    except Exception:
                        t = page.extract_text(x_tolerance=1) or ""
                    texts.append(t)
                return "\n\n".join(p for p in texts if p)
        except Exception as e:
            logger.debug("pdfplumber failed: %s", e)

    # 2) PyMuPDF (fitz)
    if fitz:
        try:
            file_stream.seek(0)
            doc = fitz.open(stream=file_stream.read(), filetype="pdf")
            texts = []
            for page in doc:
                texts.append(page.get_text("text"))
            return "\n\n".join(p for p in texts if p)
        except Exception as e:
            logger.debug("PyMuPDF extraction failed: %s", e)

    # 3) pdfminer fallback
    try:
        file_stream.seek(0)
    except Exception:
        pass
    return _pdfminer_from_stream(file_stream)
