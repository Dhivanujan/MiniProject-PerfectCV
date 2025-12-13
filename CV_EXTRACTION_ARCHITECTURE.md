# CV Extraction System - Clean Architecture Implementation

## Overview

This is a production-quality CV extraction and processing system built with clean architecture principles. The system extracts text from PDF/DOCX files, uses spaCy for entity recognition, validates data, and optionally uses AI to improve content and fill missing fields.

## Architecture

```
perfectcv-backend/
├── app/
│   ├── services/           # Business logic layer
│   │   ├── extraction_service.py      # Orchestrates extraction pipeline
│   │   ├── validation_service.py      # Validates extracted data
│   │   ├── ai_service.py              # AI processing (OpenAI/Gemini/Groq)
│   │   └── cv_generation_service.py   # PDF generation from templates
│   │
│   ├── utils/              # Utility functions
│   │   ├── text_extractor.py          # PDF/DOCX text extraction
│   │   ├── text_cleaner.py            # Text normalization
│   │   └── entity_extractor.py        # spaCy-based entity extraction
│   │
│   ├── routes/             # API endpoints (thin layer)
│   │   ├── files.py                   # Original routes
│   │   └── files_v2.py                # New enhanced routes
│   │
│   ├── templates/cv/       # Jinja2 templates for PDF generation
│   │   └── professional.html
│   │
│   └── models/             # Data models
│
├── config/
│   └── config.py           # Configuration
│
└── requirements.txt        # Dependencies
```

## Processing Pipeline

### Stage 1: Text Extraction
- **Input**: PDF or DOCX file
- **Methods**: 
  - PDFs: pdfplumber → PyPDF2 → pdfminer → OCR (fallback)
  - DOCX: python-docx
- **Output**: Raw text

### Stage 2: Text Cleaning
- Fix broken lines (hyphenated words across lines)
- Normalize whitespace
- Fix common OCR errors
- Normalize phone numbers
- Fix bullet points
- Remove duplicate lines

### Stage 3: Section Extraction
- Identifies major CV sections:
  - Professional Summary
  - Work Experience
  - Education
  - Skills
  - Certifications
  - Projects
  - Awards

### Stage 4: Entity Extraction (spaCy + Regex)
- **spaCy NER**: PERSON, ORG, GPE, DATE entities
- **Regex Extraction**:
  - Email addresses
  - Phone numbers (with phonenumbers library validation)
- **Keyword Matching**:
  - Technical skills
  - Education institutions
  - Job titles

### Stage 5: Validation
- Checks for critical fields: name, email, phone
- Checks for important sections: skills, experience
- Generates completeness score
- Provides warnings and suggestions

### Stage 6: AI Fallback (Optional)
- **When**: Critical fields are missing
- **Purpose**: Extract missing fields from text
- **Important**: AI only extracts existing information, does NOT hallucinate
- **Providers**: OpenAI GPT-3.5, Google Gemini, Groq

### Stage 7: AI Content Improvement (Optional)
- **What**: Improves summary and experience descriptions
- **How**: Better wording, stronger action verbs, improved clarity
- **Important**: Does NOT add new achievements or responsibilities

### Stage 8: PDF Generation
- **Template Engine**: Jinja2
- **PDF Generation**: WeasyPrint (primary) or FPDF (fallback)
- **Output**: Professional ATS-optimized CV

## API Endpoints

### POST /api/v2/upload-cv-v2
Upload and process a CV file.

**Request**:
```bash
curl -X POST http://localhost:5000/api/v2/upload-cv-v2 \
  -F "cv_file=@resume.pdf" \
  -F "job_domain=Software Engineering" \
  -F "use_ai=true" \
  -H "Authorization: Bearer <token>"
```

**Parameters**:
- `cv_file` (required): PDF or DOCX file
- `job_domain` (optional): Target job domain for AI optimization
- `use_ai` (optional): Enable AI processing (default: true)

**Response**:
```json
{
  "success": true,
  "message": "CV processed successfully",
  "file_id": "507f1f77bcf86cd799439011",
  "filename": "ATS_user123_resume.pdf",
  "extraction": {
    "method": "pdfplumber",
    "sections_found": ["summary", "experience", "education", "skills"],
    "entities_extracted": {
      "name": "John Doe",
      "email": "john.doe@example.com",
      "phone": "+1 (234) 567-8900",
      "location": "San Francisco, CA",
      "skills_count": 15,
      "organizations_count": 3
    }
  },
  "validation": {
    "is_complete": true,
    "completeness_score": 95.0,
    "missing_critical": [],
    "missing_important": []
  },
  "processing": {
    "ai_used": true,
    "job_domain": "Software Engineering",
    "improvements_applied": true
  },
  "suggestions": []
}
```

### GET /api/v2/download-cv/<file_id>
Download processed CV.

### GET /api/v2/cv-list
List all CVs for the current user.

## Configuration

Add to your `.env` file:

```env
# AI Service (choose one)
AI_PROVIDER=openai  # or 'google' or 'groq'

# API Keys
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...

# MongoDB
MONGO_URI=mongodb://localhost:27017/perfectcv

# Flask
SECRET_KEY=your-secret-key
```

## Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 3. Install WeasyPrint (Optional but Recommended)

**For better PDF generation**, install WeasyPrint:

**Linux/Mac**:
```bash
pip install weasyprint
```

**Windows**: WeasyPrint requires GTK+. Two options:
1. Use WSL (recommended)
2. Install GTK+ for Windows: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer

**Fallback**: If WeasyPrint installation fails, the system will use FPDF automatically.

### 4. OCR Support (Optional)

For scanned PDFs, install Tesseract:

**Ubuntu/Debian**:
```bash
sudo apt-get install tesseract-ocr
pip install pytesseract pillow pdf2image
```

**Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki

**Mac**:
```bash
brew install tesseract
pip install pytesseract pillow pdf2image
```

## Usage Examples

### Basic Usage (Python)
```python
from app.services.extraction_service import ExtractionService
from app.services.validation_service import ValidationService

# Extract CV data
extraction_service = ExtractionService()
cv_data = extraction_service.process_cv(file_bytes, "resume.pdf")

# Validate
validation_service = ValidationService()
report = validation_service.get_validation_report(
    cv_data['entities'], 
    cv_data['sections']
)

print(f"Completeness: {report['completeness_score']:.1f}%")
print(f"Name: {cv_data['entities']['name']}")
print(f"Email: {cv_data['entities']['email']}")
print(f"Skills: {cv_data['entities']['skills']}")
```

### With AI Enhancement
```python
from app.services.ai_service import AIService

# Initialize AI service
ai_service = AIService(
    openai_api_key="sk-...",
    provider="openai"
)

# Extract missing fields
if report['missing_critical']:
    ai_extracted = ai_service.extract_missing_fields(
        cv_data['cleaned_text'],
        report['missing_critical']
    )

# Improve content
improved_sections = ai_service.improve_cv_content(
    cv_data['sections'],
    job_domain="Software Engineering"
)
```

### Generate PDF
```python
from app.services.cv_generation_service import CVGenerationService

# Generate professional PDF
generation_service = CVGenerationService()
pdf_bytes = generation_service.generate_cv_pdf(cv_data)

# Save to file
with open("output_cv.pdf", "wb") as f:
    f.write(pdf_bytes)
```

## Logging

The system provides comprehensive logging at each stage:

```
INFO - Starting CV processing for: resume.pdf
INFO - Stage 1: Extracting text from file
INFO - Extracted 2456 characters using pdfplumber
INFO - Stage 2: Cleaning and normalizing text
INFO - Stage 3: Extracting CV sections
INFO - Extracted 4 sections: ['summary', 'experience', 'education', 'skills']
INFO - Stage 4: Extracting entities using NLP
INFO - Extracted entities: name=John Doe, email=john@example.com, 15 skills
INFO - Validation: completeness=95.0%, valid=True
INFO - Stage 7: Generating ATS-optimized PDF
INFO - Generated PDF: 45632 bytes
INFO - CV processing completed for: resume.pdf
```

## Testing

### Test Extraction Only
```bash
python -m pytest tests/test_extraction.py
```

### Test Full Pipeline
```bash
python perfectcv-backend/tools/test_cv_pipeline.py path/to/resume.pdf
```

## Error Handling

The system handles various scenarios:

1. **Corrupted/Unreadable PDFs**: Falls back to OCR
2. **Missing Critical Fields**: Uses AI fallback extraction
3. **No AI Service**: Continues without AI enhancement
4. **WeasyPrint Not Available**: Falls back to FPDF
5. **spaCy Model Missing**: Logs warning, uses regex extraction only

## Performance

Typical processing times:
- Text extraction: 0.5-2 seconds
- Entity extraction: 0.3-1 seconds
- AI processing: 2-5 seconds (if enabled)
- PDF generation: 1-3 seconds

**Total**: 4-11 seconds depending on file size and AI usage

## Best Practices

1. **Always validate** extracted data before using
2. **Use AI judiciously**: It adds latency but improves accuracy
3. **Log everything**: Helps debug extraction issues
4. **Test with various CV formats**: Different templates extract differently
5. **Monitor completeness scores**: Adjust extraction logic as needed

## Limitations

1. **spaCy NER**: May miss names in non-standard formats
2. **Section Detection**: Relies on common section headers
3. **Skills Extraction**: Keyword-based, not comprehensive
4. **AI Costs**: OpenAI API calls cost money
5. **WeasyPrint**: Requires GTK+ on Windows (use WSL or FPDF fallback)

## Future Improvements

- [ ] Train custom spaCy NER model for CV-specific entities
- [ ] Add support for more CV sections (volunteer work, publications)
- [ ] Implement ATS keyword matching
- [ ] Add multi-language support
- [ ] Cache AI responses to reduce costs
- [ ] Support more file formats (RTF, TXT)

## License

MIT License - See LICENSE file for details
