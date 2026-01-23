# Quick Reference: CV Generation with Jinja2 + xhtml2pdf

## 🚀 Quick Start

### Generate CV from Extracted Data
```python
from app.services.unified_cv_extractor import get_cv_extractor
from app.services.cv_generator import get_cv_generator

# 1. Extract CV data (pdfplumber)
extractor = get_cv_extractor()
with open('resume.pdf', 'rb') as f:
    extraction_result = extractor.extract_from_file(f.read(), 'resume.pdf')

# 2. Generate new CV (Jinja2 + xhtml2pdf)
cv_gen = get_cv_generator()
pdf_io = cv_gen.generate_cv_pdf(
    extraction_result,  # Contains {'entities': {...}}
    template_name='modern_cv.html',
    output_path='output/new_resume.pdf'
)
```

### Generate CV from Direct Data
```python
from app.services.cv_generator import get_cv_generator

cv_data = {
    'name': 'Jane Doe',
    'email': 'jane@example.com',
    'phone': '+1-555-0123',
    'location': 'New York, NY',
    'summary': 'Experienced software engineer...',
    'skills': ['Python', 'JavaScript', 'React'],
    'experience': [
        {
            'title': 'Senior Developer',
            'company': 'Tech Inc.',
            'start_date': '2020',
            'end_date': 'Present',
            'description': 'Led team of 5 engineers...'
        }
    ],
    'education': [
        {
            'degree': 'B.S. Computer Science',
            'institution': 'MIT',
            'graduation_year': '2018'
        }
    ]
}

cv_gen = get_cv_generator()
pdf_io = cv_gen.generate_cv_pdf(cv_data, template_name='modern_cv.html')

# pdf_io is BytesIO - can be used in Flask/FastAPI responses
```

## 📋 API Endpoints

### Flask: Download Optimized CV
```python
# POST /api/download-optimized-cv
{
    "structured_cv": {
        "name": "John Doe",
        "email": "john@example.com",
        "skills": ["Python", "Docker"],
        "experience": [...]
    },
    "optimized_text": "Fallback text...",
    "filename": "My_CV.pdf"
}

# Returns: PDF file download
```

### FastAPI: Generate CV from Upload
```python
# POST /api/generate-cv
# Upload: PDF/DOCX file
# Query params: improve=true/false

# 1. Extracts CV data with pdfplumber
# 2. Optionally improves with AI
# 3. Generates PDF with modern template
# Returns: PDF file download
```

### FastAPI: Generate from JSON
```python
# POST /api/generate-pdf-from-json
{
    "name": "Alice Smith",
    "email": "alice@example.com",
    "phone": "+1-555-9876",
    "skills": ["Java", "Spring Boot"],
    "experience": [...],
    "education": [...]
}

# Returns: PDF file download
```

## 🎨 Template Customization

### Template Location
```
app/templates/
  ├── modern_cv.html       # Default modern template
  └── cv_template.html     # Legacy template
```

### Template Variables
```jinja2
{{ entities.name }}           # Full name
{{ entities.email }}          # Email address
{{ entities.phone }}          # Phone number
{{ entities.location }}       # Location/address
{{ entities.summary }}        # Professional summary
{{ entities.linkedin }}       # LinkedIn URL
{{ entities.github }}         # GitHub URL

# Lists
{{ entities.skills }}         # ['Python', 'React', ...]
{{ entities.certifications }} # ['AWS Certified', ...]

# Structured Data
{{ entities.experience }}     # List of dicts
  - title                     # Job title
  - company                   # Company name
  - location                  # Job location
  - start_date                # Start date
  - end_date                  # End date
  - description               # Job description

{{ entities.education }}      # List of dicts
  - degree                    # Degree name
  - institution               # School name
  - location                  # School location
  - graduation_year           # Year
  - gpa                       # GPA (optional)

{{ entities.projects }}       # List of dicts
  - name                      # Project name
  - description               # Description
  - technologies              # Tech stack
```

### Create Custom Template
```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ entities.name }} - CV</title>
    <style>
        @page {
            size: A4;
            margin: 20mm;
        }
        body {
            font-family: Arial, sans-serif;
            font-size: 11pt;
        }
    </style>
</head>
<body>
    <h1>{{ entities.name }}</h1>
    <p>{{ entities.email }} | {{ entities.phone }}</p>
    
    <h2>Skills</h2>
    <ul>
    {% for skill in entities.skills %}
        <li>{{ skill }}</li>
    {% endfor %}
    </ul>
    
    <h2>Experience</h2>
    {% for job in entities.experience %}
    <div>
        <h3>{{ job.title }} - {{ job.company }}</h3>
        <p>{{ job.start_date }} - {{ job.end_date }}</p>
        <p>{{ job.description }}</p>
    </div>
    {% endfor %}
</body>
</html>
```

## 🧪 Testing

### Run All Tests
```bash
# Integration tests
python test_api_integration.py

# Complete workflow demo
python demo_cv_generation.py

# Original extraction + generation test
python test_cv_generation.py
```

### Test Individual Components
```python
# Test extraction only
from app.services.unified_cv_extractor import get_cv_extractor
extractor = get_cv_extractor()
result = extractor.extract_from_file(pdf_bytes, 'test.pdf')
print(result['entities'])

# Test generation only
from app.services.cv_generator import get_cv_generator
cv_gen = get_cv_generator()
pdf = cv_gen.generate_cv_pdf({'name': 'Test', 'email': 'test@example.com'})
print(f"PDF size: {len(pdf.getvalue())} bytes")
```

## 📦 Dependencies

### Core Libraries
```txt
pdfplumber>=0.10.0       # PDF extraction
Jinja2>=3.1.0            # Templating
xhtml2pdf>=0.2.13        # PDF generation
phonenumbers>=8.13.26    # Phone validation
```

### Install
```bash
pip install -r requirements.txt
```

## 🔧 Troubleshooting

### Issue: PDF not generating
```python
# Check template exists
import os
templates_dir = 'app/templates'
print(os.listdir(templates_dir))  # Should show modern_cv.html

# Check data format
cv_data = {...}
print('entities' in cv_data)  # Should be True for extraction results
# OR pass direct data (auto-wrapped in 'entities')
```

### Issue: Missing fields in PDF
```python
# Ensure all expected fields are in data
required_fields = ['name', 'email', 'skills', 'experience']
for field in required_fields:
    if field not in cv_data:
        print(f"Missing: {field}")
```

### Issue: Template rendering error
```python
# Generate HTML preview to debug
cv_gen = get_cv_generator()
html = cv_gen.generate_cv_html(cv_data, template_name='modern_cv.html')
with open('debug.html', 'w', encoding='utf-8') as f:
    f.write(html)
# Open debug.html in browser to see rendering
```

## 🎯 Best Practices

### 1. Data Validation
```python
# Validate before generation
def validate_cv_data(cv_data):
    if 'entities' not in cv_data:
        cv_data = {'entities': cv_data}
    
    entities = cv_data['entities']
    
    # Ensure required fields
    if not entities.get('name'):
        raise ValueError("Name is required")
    
    # Provide defaults
    entities.setdefault('skills', [])
    entities.setdefault('experience', [])
    
    return cv_data
```

### 2. Error Handling
```python
try:
    cv_gen = get_cv_generator()
    pdf = cv_gen.generate_cv_pdf(cv_data, template_name='modern_cv.html')
except Exception as e:
    logger.error(f"CV generation failed: {e}")
    # Fallback to basic template or return error
```

### 3. Performance
```python
# Reuse cv_generator instance (singleton pattern)
cv_gen = get_cv_generator()  # Called once

# Generate multiple PDFs
for cv_data in cv_list:
    pdf = cv_gen.generate_cv_pdf(cv_data)
    # Process PDF...
```

## 📊 Output Files

### Location
```
perfectcv-backend/output/
  ├── demo_sarah_martinez_cv.pdf
  ├── demo_sarah_martinez_cv.html
  ├── test_api_integration.pdf
  └── test_api_integration.html
```

### File Sizes
- **Typical CV PDF**: 3-6 KB
- **Minimal CV**: 2-3 KB
- **Comprehensive CV**: 5-7 KB
- **HTML Preview**: 8-11 KB

## 🔗 Related Files

### Services
- `app/services/cv_generator.py` - CV generation service
- `app/services/unified_cv_extractor.py` - CV extraction with pdfplumber

### Routes
- `app/routes/files.py` - Flask routes (`/download-optimized-cv`)
- `app/routes/cv.py` - FastAPI routes (`/generate-cv`, `/generate-pdf-from-json`)

### Templates
- `app/templates/modern_cv.html` - Modern gradient design
- `app/templates/cv_template.html` - Legacy template

### Tests
- `test_api_integration.py` - Integration tests
- `demo_cv_generation.py` - Complete demo
- `test_cv_generation.py` - Original tests

## ✅ Summary

**What Works:**
- ✅ Extract CV data with pdfplumber (character-level layout analysis)
- ✅ Generate professional PDFs with Jinja2 templates
- ✅ Modern gradient design template
- ✅ Windows-compatible (xhtml2pdf)
- ✅ Flexible data handling (extraction or direct)
- ✅ HTML preview generation
- ✅ File output support
- ✅ API endpoints updated
- ✅ All tests passing

**Ready to Use:**
- API endpoints for frontend integration
- Template customization
- Production deployment
