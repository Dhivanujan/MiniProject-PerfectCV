# CV Processing Pipeline Implementation

## Overview
Implemented an **explicit 5-step pipeline** for CV processing following the architecture:
```
Extract CV → JSON → Improve CV → Render HTML → Convert PDF
```

## Pipeline Structure

### STEP 1: Extract CV → JSON
**File**: `app/routes/files.py` (lines 53-77)

Extracts structured data from uploaded CV (PDF/DOCX):
- **Text Extraction**: Uses PyMuPDF or docx2txt
- **Text Cleaning**: Normalizes text, fixes broken lines
- **Section Parsing**: Identifies sections (summary, experience, education, skills, etc.)
- **Entity Extraction**: Uses spaCy NLP + regex to extract:
  - Contact info (name, email, phone, location)
  - Organizations, dates, job titles
  - Skills, certifications, education institutions

**Output**: CV JSON structure
```json
{
  "entities": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-0123",
    "location": "New York, NY",
    "skills": ["Python", "JavaScript", ...],
    ...
  },
  "sections": {
    "summary": "Experienced software engineer...",
    "experience": "Senior Software Engineer\n...",
    "education": "Bachelor of Science...",
    ...
  },
  "metadata": {
    "source_filename": "resume.pdf",
    "extraction_method": "ExtractionService",
    "ai_enhanced": false
  }
}
```

### STEP 2: Validate JSON
**File**: `app/routes/files.py` (lines 78-90)

Validates extracted data quality:
- **Critical Fields**: name, email, phone
- **Important Fields**: skills, experience
- **Completeness Score**: 0-100% based on field presence
- **Status**: complete/incomplete

**Output**: Validation report added to CV JSON
```json
{
  "validation": {
    "status": "incomplete",
    "is_complete": false,
    "missing_critical": ["phone"],
    "missing_important": [],
    "completeness_score": 80
  }
}
```

### STEP 3: Improve CV (AI or Rules)
**File**: `app/routes/files.py` (lines 92-131)

Enhances CV content using AI or rules:

**AI Fallback** (if fields missing):
- Extracts missing critical fields from text using Groq/OpenAI/Gemini
- Temperature: 0.1 (strict extraction, no hallucination)

**AI Enhancement** (if content exists):
- Improves summary and experience sections
- Makes content more impactful and ATS-friendly
- Validates improved length (must be >= 50% of original to prevent data loss)

**Output**: Updated CV JSON with improved content

### STEP 4: Render HTML (Jinja2)
**File**: `app/routes/files.py` (lines 133-145)

Renders professional HTML CV from JSON:
- **Service**: CVGenerationService
- **Template**: `app/templates/cv/professional.html`
- **Template Engine**: Jinja2
- **Data Preparation**: Parses sections into structured format (experience list, education list, etc.)

**Output**: HTML string (6000+ characters)

### STEP 5: Convert to PDF (WeasyPrint)
**File**: `app/routes/files.py` (lines 147-157)

Converts HTML to professional PDF:
- **Primary**: WeasyPrint (production quality)
- **Fallback**: FPDF (if WeasyPrint unavailable)
- **Output**: PDF bytes ready for storage

### STEP 6: Save to Database
**File**: `app/routes/files.py` (lines 159-172)

Stores generated PDF in MongoDB GridFS:
- Filename format: `ATS_{user_id}_{original_name}.pdf`
- Metadata: user_id, job_domain, ATS score, original filename

## Services Used

### ExtractionService
**File**: `app/services/extraction_service.py`
- Orchestrates text extraction → cleaning → section parsing → entity extraction
- Uses TextExtractor, TextCleaner, EntityExtractor

### ValidationService
**File**: `app/services/validation_service.py`
- Validates critical and important fields
- Calculates completeness score
- Returns validation report

### AIService
**File**: `app/services/ai_service.py`
- Groq (Llama 3.3), OpenAI (GPT-4), or Gemini
- Extract missing fields with strict anti-hallucination prompts
- Improve CV content for ATS optimization

### CVGenerationService
**File**: `app/services/cv_generation_service.py`
- `_prepare_template_data()`: Structures JSON for template
- `_render_template()`: Jinja2 rendering
- `_html_to_pdf_weasyprint()`: HTML → PDF conversion

## Logging

Each step logs detailed progress with emojis:
```
🚀 CV PROCESSING PIPELINE STARTED: resume.pdf
📤 STEP 1: EXTRACT CV → JSON
  ✓ Extracted entities: ['name', 'email', 'phone', ...]
  ✓ Extracted sections: ['summary', 'experience', ...]
🔍 STEP 2: VALIDATE JSON
  ✓ Validation: 80% complete
✨ STEP 3: IMPROVE CV JSON
  → AI Enhancement: Improving summary
  ✓ Summary improved
🎨 STEP 4: RENDER HTML (Jinja2)
  ✓ HTML rendered: 6517 characters
📄 STEP 5: CONVERT TO PDF (WeasyPrint)
  ✓ PDF generated: 45231 bytes
💾 STEP 6: SAVE PDF TO DATABASE
  ✓ PDF saved: ObjectId('...')
✅ CV PROCESSING PIPELINE COMPLETED
```

## Testing

**Test File**: `test_pipeline.py`

Tests complete pipeline flow:
1. Extract CV → JSON ✓
2. Validate JSON ✓
3. Improve CV ✓
4. Render HTML ✓
5. Convert PDF ✓

All steps verified working correctly.

## Response Format

API returns comprehensive data:
```json
{
  "success": true,
  "file_id": "...",
  "cv_json": { /* complete JSON structure */ },
  "optimized_text": "...",
  "sections": {...},
  "entities": {...},
  "template_data": {...},
  "validation": {...},
  "ats_score": 85,
  "suggestions": [...],
  "file": {...}
}
```

## Benefits

1. **Clear Architecture**: Each step has a single responsibility
2. **Easy Debugging**: Detailed logging at each stage
3. **Flexible Enhancement**: AI or rule-based improvement
4. **Quality Control**: Validation ensures data completeness
5. **Professional Output**: Jinja2 + WeasyPrint for production-quality PDFs
6. **Maintainable**: Clear separation of concerns across services
7. **Testable**: Each step can be tested independently

## Future Improvements

- Add more CV templates
- Implement template selection based on industry
- Add custom CSS styling options
- Implement batch processing
- Add resume scoring/ranking
- Implement A/B testing for AI improvements
