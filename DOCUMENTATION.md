# PerfectCV - Complete Documentation

**Version**: 2.0.0 (Modern Stack)  
**Last Updated**: December 13, 2024  
**Status**: ✅ Production Ready

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Modern Extraction & Formatting System](#modern-extraction--formatting-system)
4. [Setup & Installation](#setup--installation)
5. [API Documentation](#api-documentation)
6. [ATS Scoring System](#ats-scoring-system)
7. [Chatbot Features](#chatbot-features)
8. [CV Analysis & Generation](#cv-analysis--generation)
9. [Testing Guide](#testing-guide)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- MongoDB Atlas account
- API keys: Groq, OpenAI (optional), Google Gemini (optional)

### Backend Setup (Flask)

```bash
# Navigate to backend
cd perfectcv-backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and MongoDB URI

# Run server
python run.py
```

Server will start at: **http://localhost:8000**

### Frontend Setup (React)

```bash
# Navigate to frontend
cd perfectcv-frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will start at: **http://localhost:5173**

### Quick Test

```bash
# Test backend health
curl http://localhost:8000/health

# Test modern extraction system
cd perfectcv-backend
python test_modern_system.py

# Upload a CV
curl -X POST http://localhost:8000/api/upload-cv \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@sample_cv.pdf"
```

---

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  - Dashboard, CV Upload, Analysis, Download                 │
│  - Vite + TailwindCSS                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (Flask/FastAPI)                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         1. EXTRACTION LAYER                           │  │
│  │  - modern_extractor.py                               │  │
│  │  - pypdf (modern PDF extraction)                     │  │
│  │  - PyMuPDF (complex layouts)                         │  │
│  │  - Confidence scoring + metadata                     │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         2. PROCESSING LAYER                           │  │
│  │  - cv_utils.py (extraction utilities)                │  │
│  │  - cv_ai_service.py (AI processing)                  │  │
│  │  - cv_scoring_service.py (ATS scoring)               │  │
│  │  - Contact extraction, validation                    │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     ↓                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         3. PRESENTATION LAYER                         │  │
│  │  - modern_formatter.py (Rich formatting)             │  │
│  │  - cv_pdf_service_reportlab.py (PDF gen)             │  │
│  │  - Outputs: text, HTML, markdown, PDF                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────┬───────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                │
│  - MongoDB Atlas (cloud database)                           │
│  - Collections: users, cvs, files, sessions                 │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    AI SERVICES                               │
│  - Groq (llama-3.3-70b-versatile) - Primary                │
│  - OpenAI (GPT-4) - Alternative                             │
│  - Google Gemini - Alternative                              │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- Flask 3.1.2 / FastAPI 0.104.0
- PyMongo 4.14.1
- pypdf 6.4.1 (modern PDF extraction)
- PyMuPDF 1.26.6 (complex layouts)
- Rich 14.2.0 (beautiful formatting)
- Pydantic 2.11.9 (data validation)
- ReportLab 4.4.6 (PDF generation)
- spaCy 3.7.2 (NLP)
- Groq AI (primary LLM)

**Frontend:**
- React 18
- Vite
- TailwindCSS
- Axios

**Database:**
- MongoDB Atlas (cloud)

---

## Modern Extraction & Formatting System

### Overview

The system uses **state-of-the-art PDF extraction** and **rich formatting** capabilities, replacing legacy systems with modern, actively-maintained libraries.

### Key Improvements

1. **Modern PDF Extraction**
   - Primary: `pypdf` (pure Python, actively developed)
   - Secondary: `PyMuPDF` for complex layouts
   - Confidence scoring (0.0-1.0)
   - Automatic fallback strategies
   - Metadata extraction
   - Table and image detection

2. **Rich Formatting**
   - Rich library for beautiful output
   - Three formats: text (ANSI), HTML, Markdown
   - Color-coded sections
   - Professional styling

3. **Modernized PDF Generation**
   - ReportLab with modern design
   - Blue color palette
   - Icons and visual elements
   - Professional layout

### New Dependencies

```bash
pip install pypdf pydantic rich reportlab
```

### Extraction Pipeline

#### 1. Modern Extractor (`app/utils/modern_extractor.py`)

```python
from app.utils.modern_extractor import extract_pdf_modern

# Extract PDF
result = extract_pdf_modern(file_bytes)

# Access results
print(f"Method: {result.method.value}")  # pymupdf, pypdf, or fallback
print(f"Confidence: {result.confidence}")  # 0.0 to 1.0
print(f"Words: {result.word_count}")
print(f"Pages: {result.page_count}")
print(f"Has tables: {result.has_tables}")
print(f"Text: {result.text}")
```

**ExtractionResult Structure:**
```python
@dataclass
class ExtractionResult:
    text: str
    method: ExtractionMethod  # PYMUPDF, PYPDF, FALLBACK
    page_count: int
    word_count: int
    char_count: int
    has_images: bool
    has_tables: bool
    confidence: float  # 0.0 to 1.0
    metadata: dict  # title, author, creator
```

**Confidence Calculation:**
- Base: 0.7
- +0.1 if word_count > 100
- +0.1 if word_count > 300
- -0.2 if word_count < 50
- +0.05 if has_tables or has_images
- +0.05 if method is PyMuPDF

**Quality Thresholds:**
- **Excellent**: ≥0.9
- **Good**: 0.7-0.89
- **Fair**: 0.5-0.69
- **Poor**: <0.5

#### 2. Modern Formatter (`app/utils/modern_formatter.py`)

```python
from app.utils.modern_formatter import format_cv_modern

cv_data = {
    'name': 'John Doe',
    'contact_info': {...},
    'skills': {...},
    'work_experience': [...],
    # ...
}

# Get different formats
text = format_cv_modern(cv_data, 'text')      # Rich ANSI styled
html = format_cv_modern(cv_data, 'html')      # HTML with CSS
markdown = format_cv_modern(cv_data, 'markdown')  # Clean Markdown
```

**Output Formats:**

1. **Text (Rich ANSI)**:
   - Colored terminal output
   - Box borders and panels
   - Table layouts
   - Icons and emojis

2. **HTML**:
   - Modern web styling
   - Responsive design
   - Blue color scheme
   - Professional appearance

3. **Markdown**:
   - Clean structure
   - GitHub-compatible
   - Easy to read

### Enhanced API Response

```json
{
  "success": true,
  "file_id": "abc123",
  
  "modern_formatted": {
    "text": "Rich ANSI-styled text with colors",
    "html": "HTML with embedded CSS",
    "markdown": "Clean Markdown format"
  },
  
  "extraction_metadata": {
    "method": "pymupdf",
    "confidence": 0.95,
    "word_count": 450,
    "page_count": 2,
    "char_count": 2850,
    "has_images": false,
    "has_tables": true,
    "metadata": {
      "title": "Resume - John Doe",
      "author": "John Doe"
    }
  },
  
  "raw_text": "...",
  "formatted_text": "...",
  "contact_info": {...},
  "ats_score": {...}
}
```

---

## Setup & Installation

### Environment Variables

Create `.env` file in `perfectcv-backend/`:

```bash
# MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/perfectcv?retryWrites=true&w=majority

# AI Services
GROQ_API_KEY=your_groq_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional
GOOGLE_API_KEY=your_google_key_here  # Optional

# Application
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
DEBUG=True

# Server
PORT=8000
HOST=0.0.0.0
```

### Install Python Dependencies

```bash
cd perfectcv-backend
pip install -r requirements.txt
```

**Key Dependencies:**
- Flask 3.1.2
- pypdf 6.4.1
- PyMuPDF 1.26.6
- rich 14.2.0
- pydantic 2.11.9
- reportlab 4.4.6
- groq 0.4.0
- spacy 3.7.2

### Install Node Dependencies

```bash
cd perfectcv-frontend
npm install
```

### Database Setup

1. Create MongoDB Atlas account
2. Create a cluster
3. Create database: `perfectcv`
4. Create collections: `users`, `cvs`, `files`
5. Add connection string to `.env`

### Optional: Install spaCy Model

```bash
python -m spacy download en_core_web_sm
```

---

## API Documentation

### Authentication Endpoints

#### Register User
```
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}

Response:
{
  "success": true,
  "user_id": "abc123",
  "message": "User registered successfully"
}
```

#### Login
```
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response:
{
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": "abc123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### CV Upload & Processing

#### Upload CV
```
POST /api/upload-cv
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <cv.pdf>

Response:
{
  "success": true,
  "file_id": "file123",
  "raw_text": "Extracted text...",
  "formatted_text": "Formatted text with sections...",
  "modern_formatted": {
    "text": "Rich ANSI styled text",
    "html": "HTML output",
    "markdown": "Markdown output"
  },
  "extraction_metadata": {
    "method": "pymupdf",
    "confidence": 0.95,
    "word_count": 450,
    "page_count": 2
  },
  "contact_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-1234"
  },
  "ats_score": {
    "total_score": 85,
    "category_scores": {...}
  }
}
```

#### Get CV Analysis
```
GET /api/cv-analysis/<file_id>
Authorization: Bearer <token>

Response:
{
  "success": true,
  "analysis": {
    "skills": [...],
    "experience": [...],
    "education": [...],
    "recommendations": [...]
  }
}
```

#### Download CV as PDF
```
GET /api/download-cv/<file_id>
Authorization: Bearer <token>

Response: PDF file download
```

### Chatbot Endpoints

#### Send Message
```
POST /api/chatbot/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "message": "How can I improve my CV?",
  "cv_context": "..."  # Optional
}

Response:
{
  "success": true,
  "response": "AI-generated response...",
  "suggestions": [...]
}
```

---

## ATS Scoring System

### Overview

The ATS (Applicant Tracking System) scoring evaluates CVs across multiple categories to provide a comprehensive score.

### Scoring Categories

1. **Contact Information (10 points)**
   - Name: 2 points
   - Email: 3 points
   - Phone: 3 points
   - LinkedIn/GitHub: 2 points

2. **Professional Summary (15 points)**
   - Presence: 5 points
   - Quality (length, keywords): 10 points

3. **Skills (25 points)**
   - Technical skills: 15 points
   - Soft skills: 10 points
   - Skill diversity: bonus points

4. **Work Experience (30 points)**
   - Number of positions: 10 points
   - Descriptions quality: 10 points
   - Quantifiable achievements: 10 points

5. **Education (10 points)**
   - Degree information: 5 points
   - Institution: 3 points
   - GPA/honors: 2 points

6. **Projects (5 points)**
   - Presence and descriptions

7. **Certifications (5 points)**
   - Relevant certifications

### Score Interpretation

- **90-100**: Excellent - Highly competitive CV
- **80-89**: Very Good - Strong CV with minor improvements needed
- **70-79**: Good - Solid CV with room for enhancement
- **60-69**: Fair - Needs significant improvements
- **Below 60**: Poor - Major restructuring required

### Usage

```python
from app.services.cv_scoring_service import calculate_ats_score

score_result = calculate_ats_score(cv_data)
print(f"Total Score: {score_result['total_score']}")
print(f"Category Scores: {score_result['category_scores']}")
print(f"Recommendations: {score_result['recommendations']}")
```

---

## Chatbot Features

### Capabilities

1. **CV Analysis**
   - Identify strengths and weaknesses
   - Suggest improvements
   - Keyword optimization

2. **Career Guidance**
   - Job search strategies
   - Interview preparation
   - Skill development recommendations

3. **Interactive Improvements**
   - Section-by-section review
   - Real-time suggestions
   - Format recommendations

4. **Course Recommendations**
   - Based on skills gaps
   - Career path alignment
   - Learning resources

### Conversational Features

- Context-aware responses
- Multi-turn conversations
- Personalized recommendations
- Professional tone
- Actionable advice

### AI Models

- **Primary**: Groq (llama-3.3-70b-versatile)
- **Fallback**: OpenAI GPT-4
- **Alternative**: Google Gemini

---

## CV Analysis & Generation

### CV Data Extraction

The system extracts structured data from CVs:

```python
{
  "contact_info": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1-555-1234",
    "linkedin": "linkedin.com/in/johndoe",
    "github": "github.com/johndoe"
  },
  "professional_summary": "Senior Software Engineer...",
  "skills": {
    "Languages": ["Python", "JavaScript"],
    "Frameworks": ["Flask", "React"],
    "Tools": ["Docker", "Git"]
  },
  "work_experience": [
    {
      "title": "Senior Software Engineer",
      "company": "Tech Corp",
      "location": "San Francisco, CA",
      "start_date": "2020-01",
      "end_date": "Present",
      "responsibilities": [...]
    }
  ],
  "education": [...],
  "projects": [...],
  "certifications": [...]
}
```

### PDF Generation

Generate professional PDFs using ReportLab:

```python
from app.services.cv_pdf_service_reportlab import generate_cv_pdf

pdf_bytes = generate_cv_pdf(cv_data)

# Save to file
with open('cv_output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

**PDF Features:**
- Modern blue color scheme
- Professional layout
- Icons and visual elements
- 3-column skill grid
- Experience timeline
- Tech stack highlighting

---

## Testing Guide

### Backend Tests

#### 1. Test Modern System
```bash
cd perfectcv-backend
python test_modern_system.py
```

**Tests:**
- Dependency checks
- Module imports
- Modern extractor functionality
- Modern formatter (text/HTML/markdown)

#### 2. Test CV Pipeline
```bash
python test_cv_pipeline.py
```

**Tests:**
- PDF extraction
- Contact extraction
- ATS scoring
- PDF generation

#### 3. Test Groq Integration
```bash
python test_groq.py
```

**Tests:**
- API connection
- Model inference
- Error handling

#### 4. Test Upload Endpoint
```bash
python test_upload_endpoint.py
```

**Tests:**
- File upload
- Processing pipeline
- API response structure

### Frontend Tests

```bash
cd perfectcv-frontend
npm run test
```

### Manual Testing

1. **Upload CV**:
   - Go to http://localhost:5173
   - Login/Register
   - Upload a PDF CV
   - Verify extraction and scoring

2. **Check Modern Formatting**:
   - Inspect API response
   - Verify `modern_formatted` has text/html/markdown
   - Check `extraction_metadata` has confidence score

3. **Download PDF**:
   - Click download button
   - Verify PDF has modern styling
   - Check all sections are present

4. **Chatbot**:
   - Ask for CV improvements
   - Verify contextual responses
   - Test multi-turn conversation

---

## Troubleshooting

### Common Issues

#### 1. MongoDB Connection Timeout

**Symptom**: Server takes 5-10 seconds to start, "DNS timeout" error

**Solution**:
```python
# In config/config.py, increase timeout:
client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
```

Or use lazy connection:
```python
# Connect on first request instead of startup
```

#### 2. Rich Formatting Not Working

**Symptom**: Plain text instead of colored output

**Solution**:
```bash
pip install rich
```

Verify:
```python
python -c "import rich; print('Rich installed')"
```

#### 3. pypdf Import Error

**Symptom**: `ModuleNotFoundError: No module named 'pypdf'`

**Solution**:
```bash
pip install pypdf
```

#### 4. Low Extraction Confidence

**Symptom**: `extraction_metadata.confidence < 0.7`

**Causes**:
- Scanned PDF (not digital text)
- Password-protected PDF
- Corrupted file
- Non-standard format

**Solutions**:
- Use OCR for scanned PDFs
- Decrypt password-protected files
- Re-save PDF in standard format

#### 5. HTML Output Not Rendering

**Symptom**: HTML shows as plain text

**Solution**:
- Ensure HTML is properly escaped
- Check for CSS conflicts
- Verify HTML structure is valid

#### 6. spaCy Model Missing

**Symptom**: "spaCy not installed" warning

**Solution**:
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

#### 7. Server Not Starting

**Check**:
1. MongoDB connection string valid
2. Port 8000 not in use
3. All dependencies installed
4. .env file configured

**Debug**:
```bash
python run.py --debug
```

#### 8. CORS Errors

**Symptom**: Frontend can't connect to backend

**Solution**:
```python
# In app.py, ensure CORS is configured:
from flask_cors import CORS
CORS(app, origins=['http://localhost:5173'])
```

#### 9. WinError 10038 on Windows

**Symptom**: `OSError: [WinError 10038] An operation was attempted on something that is not a socket`

**Cause**: Flask's auto-reloader on Windows has socket handling issues during file change detection

**Solution**:
This has been fixed in `run.py` to use stat-based reloader on Windows. If you still see this:

1. **Ignore it**: Error appears during auto-reload but doesn't affect functionality
2. **Disable reloader**: Add `use_reloader=False` to `app.run()`
3. **Manual restart**: Stop server (Ctrl+C) and restart after making changes
4. **Use production server**: Run with `gunicorn` or `waitress` (no reloader issues)

```bash
# Alternative: Use waitress for Windows
pip install waitress
waitress-serve --port=8000 app:app
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] MongoDB indexes created
- [ ] API keys secured
- [ ] Error logging configured
- [ ] Rate limiting enabled
- [ ] HTTPS configured
- [ ] CORS properly restricted

### Backend Deployment

```bash
# Use production WSGI server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Frontend Deployment

```bash
cd perfectcv-frontend
npm run build

# Deploy dist/ folder to hosting service
```

### Environment Variables (Production)

```bash
FLASK_ENV=production
DEBUG=False
MONGODB_URI=<production_mongodb_uri>
SECRET_KEY=<strong_random_key>
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## Performance Optimization

### Backend

1. **Database Indexing**:
```python
db.cvs.create_index([("user_id", 1)])
db.files.create_index([("file_id", 1)])
```

2. **Caching**:
- Use Redis for session storage
- Cache frequently accessed data
- Implement request caching

3. **Async Processing**:
- Queue PDF processing with Celery
- Background ATS scoring
- Async AI requests

### Frontend

1. **Code Splitting**:
```javascript
const Dashboard = lazy(() => import('./pages/Dashboard'));
```

2. **Image Optimization**:
- Use WebP format
- Lazy loading
- Responsive images

3. **Bundle Optimization**:
```bash
npm run build -- --mode production
```

---

## Security Best Practices

### Authentication
- Use JWT tokens
- Implement refresh tokens
- Session timeout (1 hour)
- Password hashing (bcrypt)

### Data Protection
- Validate all inputs
- Sanitize file uploads
- Encrypt sensitive data
- HTTPS only in production

### API Security
- Rate limiting (100 req/min)
- CORS restrictions
- API key rotation
- Request size limits

---

## Maintenance

### Regular Tasks

**Weekly**:
- Check error logs
- Monitor API usage
- Review security alerts

**Monthly**:
- Update dependencies
- Database backup
- Performance review

**Quarterly**:
- Security audit
- Load testing
- User feedback review

### Monitoring

```bash
# Check server health
curl http://localhost:8000/health

# View logs
tail -f logs/app.log

# Monitor resources
top -p $(pgrep -f "python run.py")
```

---

## API Rate Limits

- **Authentication**: 10 requests/minute
- **CV Upload**: 5 requests/minute
- **Analysis**: 20 requests/minute
- **Chatbot**: 30 requests/minute
- **Download**: 10 requests/minute

---

## Contributing

### Code Style

**Python**:
- PEP 8 compliance
- Type hints preferred
- Docstrings for functions
- Maximum line length: 100

**JavaScript**:
- ESLint configuration
- Prettier formatting
- Functional components preferred

### Git Workflow

1. Create feature branch
2. Make changes
3. Write tests
4. Submit pull request
5. Code review
6. Merge to main

---

## License

MIT License - See LICENSE file for details

---

## Support

- **Documentation**: This file
- **Issues**: GitHub Issues
- **Email**: support@perfectcv.com

---

## Changelog

### Version 2.0.0 (Current)
- ✅ Modern PDF extraction (pypdf + PyMuPDF)
- ✅ Rich formatting system (text/HTML/markdown)
- ✅ Confidence scoring for extractions
- ✅ Modernized PDF generation (ReportLab)
- ✅ Enhanced API response structure
- ✅ Automatic fallback strategies

### Version 1.5.0
- ATS scoring system
- Chatbot integration
- MongoDB Atlas migration
- Groq AI integration

### Version 1.0.0
- Initial release
- Basic CV upload and analysis
- PDF generation
- Contact extraction

---

**End of Documentation**
