# Quick Setup Guide for CV Extraction System

## Prerequisites
- Python 3.8+
- MongoDB running locally or connection string
- (Optional) OpenAI/Google/Groq API key for AI features

## Installation Steps

### 1. Install Core Dependencies
```bash
cd perfectcv-backend
pip install -r requirements.txt
```

### 2. Download spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

### 3. Configure Environment Variables

Create a `.env` file in `perfectcv-backend/`:

```env
# MongoDB
MONGO_URI=mongodb://localhost:27017/perfectcv

# Flask
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=development

# Email (Optional - for contact form)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# AI Service (Optional - for AI enhancement)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
# Or use Google Gemini:
# AI_PROVIDER=google
# GOOGLE_API_KEY=your-key-here
# Or use Groq:
# AI_PROVIDER=groq
# GROQ_API_KEY=your-key-here
```

### 4. Optional: Install WeasyPrint (for better PDFs)

**Linux/Mac:**
```bash
pip install weasyprint
```

**Windows (Option 1 - WSL Recommended):**
```bash
# In WSL
pip install weasyprint
```

**Windows (Option 2 - GTK+ Installation):**
1. Download GTK+ installer from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Install GTK+
3. Add to PATH: `C:\Program Files\GTK3-Runtime Win64\bin`
4. `pip install weasyprint`

**If WeasyPrint fails:** The system will automatically fall back to FPDF (simpler PDFs).

### 5. Optional: Install OCR Support (for scanned PDFs)

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
pip install pytesseract pillow pdf2image poppler-utils
```

**Mac:**
```bash
brew install tesseract poppler
pip install pytesseract pillow pdf2image
```

**Windows:**
1. Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH
3. Download Poppler: https://github.com/oschwartz10612/poppler-windows/releases
4. Extract and add bin folder to PATH
5. `pip install pytesseract pillow pdf2image`

### 6. Start the Server

```bash
cd perfectcv-backend
python run.py
```

Server will start on `http://localhost:5000`

## Testing the System

### Test with a Sample CV

```bash
cd perfectcv-backend
python tools/test_cv_pipeline.py path/to/your/cv.pdf
```

This will:
1. Extract text from the CV
2. Parse entities and sections
3. Validate completeness
4. (If configured) Test AI enhancement
5. Generate a new PDF
6. Save outputs to `test_output/` directory

### Test API Endpoints

**Using curl:**
```bash
# Health check
curl http://localhost:5000/health

# Upload CV (after logging in and getting token)
curl -X POST http://localhost:5000/api/v2/upload-cv-v2 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "cv_file=@resume.pdf" \
  -F "job_domain=Software Engineering" \
  -F "use_ai=true"
```

**Using Postman:**
1. Import the API collection (if available)
2. Set authorization token
3. Test `/api/v2/upload-cv-v2` endpoint

## Verify Installation

Run this Python script to check all dependencies:

```python
import sys

def check_imports():
    """Check if all required libraries are available."""
    checks = {
        'PyPDF2': False,
        'pdfplumber': False,
        'pdfminer.six': False,
        'docx (python-docx)': False,
        'spacy': False,
        'phonenumbers': False,
        'jinja2': False,
        'flask': False,
        'pymongo': False,
    }
    
    # Check imports
    try:
        import PyPDF2
        checks['PyPDF2'] = True
    except: pass
    
    try:
        import pdfplumber
        checks['pdfplumber'] = True
    except: pass
    
    try:
        from pdfminer.high_level import extract_text
        checks['pdfminer.six'] = True
    except: pass
    
    try:
        from docx import Document
        checks['docx (python-docx)'] = True
    except: pass
    
    try:
        import spacy
        checks['spacy'] = True
        # Check if model is downloaded
        try:
            nlp = spacy.load('en_core_web_sm')
            checks['spacy'] = 'with en_core_web_sm model'
        except:
            checks['spacy'] = 'installed but model missing'
    except: pass
    
    try:
        import phonenumbers
        checks['phonenumbers'] = True
    except: pass
    
    try:
        import jinja2
        checks['jinja2'] = True
    except: pass
    
    try:
        import flask
        checks['flask'] = True
    except: pass
    
    try:
        import pymongo
        checks['pymongo'] = True
    except: pass
    
    # Optional libraries
    optional = {}
    
    try:
        from weasyprint import HTML
        optional['weasyprint'] = True
    except:
        optional['weasyprint'] = False
    
    try:
        from fpdf import FPDF
        optional['fpdf2'] = True
    except:
        optional['fpdf2'] = False
    
    try:
        import pytesseract
        optional['pytesseract (OCR)'] = True
    except:
        optional['pytesseract (OCR)'] = False
    
    # Print results
    print("=" * 60)
    print("DEPENDENCY CHECK")
    print("=" * 60)
    print("\nRequired Dependencies:")
    for lib, status in checks.items():
        symbol = "✓" if status else "✗"
        print(f"  {symbol} {lib}: {status}")
    
    print("\nOptional Dependencies:")
    for lib, status in optional.items():
        symbol = "✓" if status else "✗"
        note = ""
        if lib == 'weasyprint' and not status and optional['fpdf2']:
            note = " (will use fpdf2 fallback)"
        print(f"  {symbol} {lib}: {status}{note}")
    
    print("\n" + "=" * 60)
    
    # Check if critical dependencies are missing
    critical_missing = [lib for lib, status in checks.items() if not status]
    if critical_missing:
        print("⚠ WARNING: Missing required dependencies:")
        for lib in critical_missing:
            print(f"  - {lib}")
        print("\nRun: pip install -r requirements.txt")
        if 'spacy' in [lib.split()[0] for lib in critical_missing]:
            print("Then: python -m spacy download en_core_web_sm")
    else:
        print("✓ All required dependencies installed!")
        
        if not optional['weasyprint'] and not optional['fpdf2']:
            print("\n⚠ NOTE: No PDF generation library found.")
            print("  Install: pip install weasyprint  (or fpdf2 as fallback)")
    
    print("=" * 60)

if __name__ == "__main__":
    check_imports()
```

Save this as `check_setup.py` and run:
```bash
python check_setup.py
```

## Common Issues

### Issue 1: spaCy model not found
```
OSError: [E050] Can't find model 'en_core_web_sm'
```
**Solution:**
```bash
python -m spacy download en_core_web_sm
```

### Issue 2: WeasyPrint installation fails on Windows
```
OSError: cannot load library 'gobject-2.0-0'
```
**Solution:** Use WSL or install GTK+ for Windows, OR just use FPDF fallback (automatically handled).

### Issue 3: MongoDB connection error
```
ServerSelectionTimeoutError: localhost:27017
```
**Solution:** 
- Make sure MongoDB is running: `mongod` or `sudo systemctl start mongod`
- Check MONGO_URI in `.env`

### Issue 4: Import errors
```
ModuleNotFoundError: No module named 'xyz'
```
**Solution:**
```bash
pip install -r requirements.txt
```

## Next Steps

1. **Test with your CV**: Run the test script with your actual CV file
2. **Configure AI**: Add API keys to `.env` for AI features
3. **Customize templates**: Edit `app/templates/cv/professional.html`
4. **Integrate with frontend**: Use the new `/api/v2/upload-cv-v2` endpoint

## API Documentation

See [CV_EXTRACTION_ARCHITECTURE.md](../CV_EXTRACTION_ARCHITECTURE.md) for:
- Detailed architecture overview
- API endpoint documentation
- Usage examples
- Performance metrics
- Best practices

## Support

For issues or questions:
1. Check logs: `tail -f perfectcv-backend/logs/app.log`
2. Review architecture docs
3. Run test script to isolate issues
4. Check environment variables

## Production Deployment

For production:
1. Set `FLASK_ENV=production` in `.env`
2. Use a production-grade WSGI server (gunicorn/uwsgi)
3. Enable HTTPS
4. Set strong `SECRET_KEY`
5. Configure proper MongoDB authentication
6. Set up error tracking (Sentry, etc.)
7. Enable rate limiting
8. Configure CORS properly
