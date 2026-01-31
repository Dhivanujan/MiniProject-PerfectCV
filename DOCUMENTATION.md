# PerfectCV - Complete Project Documentation

**Project:** AI-Powered CV Optimization System  
**Version:** 2.0  
**Last Updated:** January 31, 2026

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Backend Structure](#backend-structure)
5. [Frontend Structure](#frontend-structure)
6. [CV Extraction System](#cv-extraction-system)
7. [CV Generation System](#cv-generation-system)
8. [API Endpoints](#api-endpoints)
9. [Database Schema](#database-schema)
10. [Configuration](#configuration)
11. [Quick Reference](#quick-reference)
12. [Troubleshooting](#troubleshooting)

---

## Project Overview

PerfectCV is an AI-powered CV optimization platform that helps users create ATS-friendly resumes. The system analyzes uploaded CVs, provides intelligent suggestions, scores them based on ATS compatibility, and generates optimized PDF versions.

### Key Features

| Feature | Description |
|---------|-------------|
| **AI-Powered Analysis** | Uses Google Gemini AI & Groq LLaMA for CV analysis |
| **ATS Scoring** | Scores CVs 0-100 based on ATS compatibility |
| **CV Extraction** | pdfplumber-based extraction with layout analysis |
| **PDF Generation** | Jinja2 + xhtml2pdf for professional CV generation |
| **AI Chatbot** | Groq-powered chatbot for CV advice |
| **User Authentication** | JWT-based secure authentication |
| **File Management** | MongoDB GridFS for file storage |

---

## Architecture

```
PerfectCV/
├── perfectcv-backend/          # FastAPI Backend
│   ├── app/
│   │   ├── auth/               # JWT Authentication
│   │   ├── models/             # Database models
│   │   ├── routes/             # API endpoints
│   │   ├── services/           # Business logic
│   │   ├── templates/          # Jinja2 CV templates
│   │   └── utils/              # Utility functions
│   ├── config/                 # Configuration
│   ├── output/                 # Generated CVs
│   ├── .env                    # Environment variables
│   └── app_fastapi.py          # Main entry point
│
└── perfectcv-frontend/         # React Frontend
    ├── src/
    │   ├── components/         # Reusable components
    │   ├── pages/              # Page components
    │   ├── api.js              # Axios configuration
    │   └── App.jsx             # Main app component
    └── package.json            # NPM dependencies
```

---

## Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| Python 3.13 | Core language |
| FastAPI | Web framework |
| MongoDB Atlas | Database |
| pdfplumber | PDF text extraction |
| Jinja2 | HTML templating |
| xhtml2pdf | PDF generation |
| Google Gemini AI | CV analysis |
| Groq LLaMA 3.3 | Chatbot AI |
| JWT | Authentication |

### Frontend
| Technology | Purpose |
|------------|---------|
| React 18 | UI framework |
| Vite | Build tool |
| TailwindCSS | Styling |
| Axios | HTTP client |
| React Router | Navigation |

---

## Backend Structure

### Services (Framework-Agnostic)

| Service | Purpose |
|---------|---------|
| `unified_cv_extractor.py` | Main CV extraction with pdfplumber + custom rules |
| `cv_generator.py` | Jinja2 + xhtml2pdf PDF generation |
| `cv_scoring_service.py` | ATS scoring algorithm (8 categories, 100 points) |
| `ai_service.py` | Google Gemini AI integration |
| `cv_ai_service.py` | AI-powered CV analysis |
| `course_recommender.py` | Learning recommendations |
| `cv_validation_service.py` | Data validation |

### Routes

| Route File | Endpoints |
|------------|-----------|
| `auth_fastapi.py` | `/auth/login`, `/auth/register`, `/auth/logout` |
| `files_fastapi.py` | `/api/upload-cv`, `/api/download/:id` |
| `cv.py` | `/api/cv/*` (analyze, generate, score) |
| `chatbot_fastapi.py` | `/api/chatbot/upload`, `/api/chatbot/ask` |

---

## Frontend Structure

### Pages

| Page | Route | Purpose |
|------|-------|---------|
| `Home.jsx` | `/` | Landing page |
| `Login.jsx` | `/login` | User login |
| `Register.jsx` | `/register` | User registration |
| `Dashboard.jsx` | `/dashboard` | CV upload/analysis |
| `ChatbotPage.jsx` | `/chatbot` | AI chatbot |

### Components

| Component | Purpose |
|-----------|---------|
| `Navbar.jsx` | Navigation bar |
| `CVAnalysisPanel.jsx` | Analysis results display |
| `ResumeTemplate.jsx` | CV preview |

---

## CV Extraction System

### Unified Extractor (`unified_cv_extractor.py`)

A single, comprehensive CV extraction service featuring:

#### Features
- **pdfplumber** for character-level PDF layout analysis
- **Custom regex patterns** for entity extraction
- **200+ technical skills** database
- **Robust section detection** (18 section types)
- **International phone number support** via phonenumbers library

#### Extraction Output
```python
{
    'raw_text': str,
    'cleaned_text': str,
    'extraction_method': 'pdfplumber+Layout',
    'sections': {
        'header': '...',
        'education': '...',
        'experience': '...',
        'skills': '...',
        'projects': '...',
        # ... up to 18 section types
    },
    'entities': {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1 234 567 8900',
        'location': 'San Francisco',
        'skills': ['python', 'javascript', ...],  # 200+ skills detected
        'job_titles': ['Software Engineer', ...],
        'education': [{...}],
        'experience': [{...}],
        'summary': '...'
    },
    'layout_metadata': {
        'headers_detected': int,
        'sections_detected': [...],
        'avg_font_size': float
    }
}
```

#### Usage
```python
from app.services.unified_cv_extractor import get_cv_extractor

extractor = get_cv_extractor()
with open('resume.pdf', 'rb') as f:
    result = extractor.extract_from_file(f.read(), 'resume.pdf')

name = result['entities']['name']
skills = result['entities']['skills']
```

---

## CV Generation System

### CV Generator (`cv_generator.py`)

Professional PDF generation using Jinja2 templates + xhtml2pdf.

#### Available Templates

| Template | Description |
|----------|-------------|
| `professional_cv.html` | Best quality, modern two-column design ⭐ |
| `enhanced_cv.html` | Enhanced professional template |
| `modern_cv.html` | Gradient sidebar design |
| `cv_template.html` | Classic format |

#### Template Features
- ✅ A4 page size optimization
- ✅ Professional typography (Helvetica Neue)
- ✅ Purple gradient sidebar
- ✅ Skill badges with rounded corners
- ✅ Timeline experience design
- ✅ Print-optimized CSS
- ✅ ATS-friendly structure

#### Usage
```python
from app.services.cv_generator import get_cv_generator

cv_gen = get_cv_generator()

# Generate PDF from extracted data
pdf_io = cv_gen.generate_cv_pdf(
    extraction_result,  # Contains {'entities': {...}}
    template_name='enhanced_cv.html',
    output_path='output/new_cv.pdf'
)

# Generate HTML preview
html = cv_gen.generate_cv_html(cv_data, template_name='enhanced_cv.html')
```

#### Supported Data Fields
```python
{
    'name': str,
    'email': str,
    'phone': str,
    'location': str,
    'linkedin': str,
    'github': str,
    'summary': str,
    'skills': List[str],
    'experience': [{'title', 'company', 'duration', 'description'}],
    'education': [{'degree', 'institution', 'year'}],
    'projects': [{'name', 'description', 'technologies'}],
    'certifications': [{'name', 'issuer', 'date'}]
}
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login, returns JWT |
| POST | `/auth/logout` | User logout |
| GET | `/api/current-user` | Get current user info |

### CV Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload-cv` | Upload and analyze CV |
| POST | `/api/cv/analyze-cv` | Analyze CV data |
| POST | `/api/cv/generate-cv` | Generate optimized CV |
| POST | `/api/cv/score` | Score CV for ATS |
| GET | `/api/download/:id` | Download CV file |
| DELETE | `/api/files/:id` | Delete CV file |

### Chatbot

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chatbot/upload` | Upload CV for chatbot |
| POST | `/api/chatbot/ask` | Ask question about CV |
| GET | `/api/chatbot/cv-info` | Get CV summary |

---

## Database Schema

### MongoDB Collections

#### `users`
```javascript
{
  _id: ObjectId,
  username: String,
  email: String (unique),
  password: String (hashed),
  createdAt: Date
}
```

#### `fs.files` (GridFS)
```javascript
{
  _id: ObjectId,
  filename: String,
  uploadDate: Date,
  contentType: String,
  metadata: {
    user_id: String,
    original_filename: String,
    job_domain: String,
    ats_score: Number
  }
}
```

---

## Configuration

### Environment Variables (`.env`)

```env
# Database
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# AI API Keys
API_KEY=AIzaSy...              # Google Gemini API
GOOGLE_API_KEY=AIzaSy...       # Google AI API
GROQ_API_KEY=gsk_...           # Groq LLaMA API

# Email
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=app-password

# Security
SECRET_KEY=your-secret-key
```

---

## Quick Reference

### Start Backend
```bash
cd perfectcv-backend
pip install -r requirements.txt
python app_fastapi.py
# Server runs on http://localhost:8000
```

### Start Frontend
```bash
cd perfectcv-frontend
npm install
npm run dev
# Frontend runs on http://localhost:5173
```

### Complete CV Workflow
```python
from app.services.unified_cv_extractor import get_cv_extractor
from app.services.cv_generator import get_cv_generator

# 1. Extract CV data
extractor = get_cv_extractor()
result = extractor.extract_from_file(pdf_bytes, 'resume.pdf')

# 2. Generate new CV
cv_gen = get_cv_generator()
pdf_io = cv_gen.generate_cv_pdf(result, template_name='enhanced_cv.html')
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| MongoDB Connection Failed | Check MONGO_URI, flush DNS, whitelist IP |
| API Key Invalid | Verify keys in `.env`, check quota |
| CORS Errors | Check frontend URL matches config |
| PDF Generation Fails | Ensure xhtml2pdf installed |
| Chatbot Not Recognizing CV | CV stored in in-memory session, re-upload after server restart |

### Testing Commands
```bash
# Test MongoDB
python test_mongo_login.py

# Test API Keys
python test_api_keys.py

# Test CV Extraction
python test_unified_extractor.py
```

---

## Dependencies

### Backend (`requirements.txt`)
```
fastapi>=0.109.0
uvicorn>=0.27.0
pymongo>=4.6.0
pdfplumber>=0.10.0
Jinja2>=3.1.0
xhtml2pdf>=0.2.13
phonenumbers>=8.13.26
google-generativeai>=0.3.0
groq>=0.4.0
python-jose>=3.3.0
bcrypt>=4.1.2
python-dotenv>=1.0.0
python-multipart>=0.0.6
```

### Frontend (`package.json`)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "vite": "^5.0.8",
    "tailwindcss": "^3.3.6"
  }
}
```

---

## Migration Notes

### Removed Dependencies
- ~~PyMuPDF~~ → Replaced with pdfplumber
- ~~spaCy~~ → Replaced with regex patterns
- ~~WeasyPrint~~ → Replaced with xhtml2pdf (Windows compatible)
- ~~Flask~~ → Migrated to FastAPI

### Files Removed (Legacy)
- `cv_extract_service.py`
- `extraction_service.py`
- `extractor.py`
- `modern_extractor.py`
- `entity_extractor.py`
- `text_extractor.py`

---

## Contact & Support

For issues or questions, create an issue in the repository.

---

**Maintainers:** PerfectCV Team  
**License:** Proprietary (SE5014 Mini Project)
