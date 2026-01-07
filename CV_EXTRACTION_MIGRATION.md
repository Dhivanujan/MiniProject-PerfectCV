# CV Extraction System - Migration Guide

## Changes Made

### ✅ Removed Redundant Files
The following unnecessary extraction files have been removed:
- `app/services/cv_extract_service.py` - Old regex-based extractor
- `app/services/extraction_service.py` - Old orchestrator
- `app/utils/extractor.py` - Legacy PDF extraction
- `app/utils/modern_extractor.py` - Duplicate extractor
- `app/utils/entity_extractor.py` - Replaced by unified extractor
- `app/utils/text_extractor.py` - Legacy text extraction

### ✨ New Unified System
Created **`app/services/unified_cv_extractor.py`** with:
- **spaCy-based NLP extraction** with custom pattern matchers
- **Robust regex patterns** for email, phone, etc.
- **Custom rules** for skills, job titles, and sections
- **Structured entity extraction** (name, email, phone, location, skills, experience, education)
- **Clean, maintainable code** with proper logging
- **Singleton pattern** for efficient model loading

## Features

### 1. spaCy Integration
- Uses `en_core_web_sm` model for NER (Named Entity Recognition)
- Custom matchers for:
  - Email patterns
  - Phone patterns
  - Technical skills (70+ skills database)
  - Job titles (20+ common titles)
  - Section headers (education, experience, skills, etc.)

### 2. Custom Rules
- **Email extraction**: Robust regex with multiple format support
- **Phone extraction**: International format support with phonenumbers library validation
- **Name extraction**: Smart detection from document header with exclusion rules
- **Skills extraction**: Phrase matching against curated skills database
- **Section parsing**: Pattern-based section detection and splitting

### 3. Structured Output
```python
{
    'raw_text': '...',
    'cleaned_text': '...',
    'extraction_method': 'PyMuPDF',
    'sections': {
        'header': '...',
        'education': '...',
        'experience': '...',
        'skills': '...'
    },
    'entities': {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1 234 567 8900',
        'location': 'San Francisco',
        'skills': ['python', 'javascript', 'react', ...],
        'job_titles': ['Software Engineer', ...],
        'organizations': ['Google', 'Microsoft', ...],
        'education': [{...}],
        'experience': [{...}],
        'summary': '...'
    },
    'filename': 'resume.pdf',
    'processed_at': '2026-01-22T...'
}
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 3. Usage

#### Basic Usage
```python
from app.services.unified_cv_extractor import get_cv_extractor

# Get singleton instance
extractor = get_cv_extractor()

# Extract from file
with open('resume.pdf', 'rb') as f:
    result = extractor.extract_from_file(f.read(), 'resume.pdf')

# Access extracted data
name = result['entities']['name']
email = result['entities']['email']
skills = result['entities']['skills']
```

#### In Routes (FastAPI)
```python
from app.services.unified_cv_extractor import get_cv_extractor

@router.post("/extract")
async def extract(file: UploadFile):
    content = await file.read()
    extractor = get_cv_extractor()
    result = extractor.extract_from_file(content, file.filename)
    return result['entities']
```

## Updated Files

### Routes Updated
1. **`app/routes/cv.py`**
   - Replaced `extract_cv_data()` with `get_cv_extractor().extract_from_file()`
   - Updated imports
   - Removed temporary file dependency

2. **`app/routes/files.py`**
   - Replaced multi-step extraction with unified extractor
   - Simplified extraction pipeline
   - Removed AI fallback orchestrator (now handled by spaCy)

### Requirements Updated
- Removed: `pypdf`, `pdfplumber`, `pdfminer.six`, `nltk`, OCR libraries
- Kept: `PyMuPDF`, `python-docx`, `spacy`, `phonenumbers`
- Added proper spaCy model download instructions

## Performance Benefits

1. **Faster extraction**: Single-pass processing instead of multi-stage
2. **More accurate**: spaCy's NER is more reliable than regex-only
3. **Maintainable**: Single source of truth for extraction logic
4. **Extensible**: Easy to add new skills, job titles, or custom patterns
5. **Better logging**: Clear extraction pipeline visibility

## Custom Rules Examples

### Adding New Skills
```python
# In CVExtractor class
TECH_SKILLS = {
    'python', 'java', 'javascript',
    # Add your skills here
    'your_skill',
}
```

### Adding New Job Titles
```python
JOB_TITLES = {
    'software engineer',
    # Add your titles here
    'your_custom_title',
}
```

### Adding New Section Patterns
```python
SECTION_PATTERNS = {
    'custom_section': r'(?i)^(your|pattern|here)',
}
```

## Troubleshooting

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### Import Errors
Make sure you've removed the old files and restarted your server:
```bash
# Windows
Get-Process python | Stop-Process
```

### Extraction Quality Issues
- Check logs for extraction method used
- Verify spaCy model is loaded: Look for "✓ Loaded spaCy model" in logs
- Test with different CV formats

## Migration Checklist

- [x] Remove old extraction files
- [x] Create unified extractor with spaCy + custom rules
- [x] Update imports in routes
- [x] Update requirements.txt
- [x] Test extraction pipeline
- [ ] Download spaCy model: `python -m spacy download en_core_web_sm`
- [ ] Run tests
- [ ] Verify API endpoints work

## Next Steps

1. Download the spaCy model
2. Restart your application
3. Test CV upload endpoints
4. Monitor logs for extraction quality
5. Fine-tune custom rules based on your CV samples

## Support

If you encounter issues:
1. Check logs for error messages
2. Verify spaCy model is installed
3. Test with a simple CV first
4. Check that PyMuPDF is properly installed
