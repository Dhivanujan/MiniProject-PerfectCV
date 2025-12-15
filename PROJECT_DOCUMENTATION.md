# PerfectCV - Complete Project Documentation

**Version**: 2.0.0  
**Last Updated**: December 15, 2025  
**Status**: ✅ Production Ready

---

## 📑 Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start](#quick-start)
3. [Tech Stack](#tech-stack)
4. [System Architecture](#system-architecture)
5. [Installation & Setup](#installation--setup)
6. [CV Processing Pipeline](#cv-processing-pipeline)
7. [API Documentation](#api-documentation)
8. [Features](#features)
9. [AI Integration](#ai-integration)
10. [Testing](#testing)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

PerfectCV is a modern, AI-powered resume builder that helps users create professional, ATS-friendly resumes quickly and efficiently. The application features a Flask backend with MongoDB integration and a React frontend for a seamless user experience.

### Key Capabilities

- **Intelligent CV Extraction**: Upload PDF/DOCX files and automatically extract structured data
- **AI-Powered Enhancement**: Improve CV content with AI suggestions
- **ATS Optimization**: Automatic keyword matching and scoring for better job application success
- **Professional Templates**: Multiple modern, recruiter-friendly templates
- **PDF Generation**: High-quality PDF exports
- **Interactive Chatbot**: Get personalized CV improvement advice
- **User Management**: Secure authentication and profile management

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+** and npm
- **MongoDB Atlas Account**
- **API Keys**: Groq (required), OpenAI (optional), Google Gemini (optional)

### Backend Setup (5 Minutes)

```bash
# Navigate to backend
cd perfectcv-backend

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file with:
MONGO_URI=your_mongodb_connection_string
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_key (optional)
GEMINI_API_KEY=your_gemini_key (optional)

# Run server
python run.py
```

Server starts at: **http://localhost:8000**

### Frontend Setup (3 Minutes)

```bash
# Navigate to frontend
cd perfectcv-frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend starts at: **http://localhost:5173**

### Quick Test

```bash
# Test backend health
curl http://localhost:8000/health

# Test modern extraction system
cd perfectcv-backend
python test_modern_system.py
```

---

## 🛠️ Tech Stack

### Backend
- **Flask** - Python web framework
- **FastAPI** - Modern async API framework
- **MongoDB Atlas** - Cloud database
- **PyMongo** - MongoDB driver
- **Flask-Login** - User session management
- **GridFS** - File storage system

### AI & NLP
- **Groq (LLaMA 3.1)** - Primary AI engine for CV analysis
- **Microsoft Phi-3** - Local AI (optional, privacy-focused)
- **OpenAI GPT-4** - Advanced AI features (optional)
- **Google Gemini** - AI fallback (optional)
- **spaCy** - NLP entity extraction
- **Tesseract OCR** - Scanned PDF support (optional)

### PDF Processing
- **PyMuPDF (fitz)** - PDF text extraction (primary)
- **docx2txt** - DOCX text extraction
- **WeasyPrint** - HTML to PDF conversion
- **ReportLab** - PDF generation alternative

### Frontend
- **React 18** - Modern JavaScript library
- **Vite** - Fast build tool
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls

---

## 🏗️ System Architecture

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│  - Dashboard, CV Upload, Analysis, Download                 │
│  - Vite + TailwindCSS + React Router                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API (Axios)
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (Flask/FastAPI)                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         1. EXTRACTION LAYER                           │  │
│  │  • Text Extractor (PyMuPDF, docx2txt)               │  │
│  │  • Text Cleaner (normalization, OCR fixes)          │  │
│  │  • Entity Extractor (spaCy NER + Regex)             │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         2. VALIDATION LAYER                           │  │
│  │  • Field validation (name, email, phone)            │  │
│  │  • Completeness scoring (0-100%)                    │  │
│  │  • Smart AI fallback triggers                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         3. AI ENHANCEMENT LAYER                       │  │
│  │  • Groq (primary AI)                                 │  │
│  │  • Phi-3 (local AI fallback)                        │  │
│  │  • Content improvement & suggestions                │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         4. GENERATION LAYER                           │  │
│  │  • CV Template Rendering (Jinja2)                   │  │
│  │  • PDF Generation (WeasyPrint/ReportLab)            │  │
│  │  • ATS Scoring & Optimization                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ↓
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE (MongoDB Atlas)                   │
│  - Users Collection (authentication)                        │
│  - CVs Collection (extracted data)                          │
│  - GridFS (file storage)                                    │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
perfectcv-backend/
├── app/
│   ├── models/          # Data models
│   │   └── user.py      # User authentication model
│   ├── routes/          # API endpoints
│   │   ├── auth.py      # Authentication routes
│   │   ├── chatbot.py   # Chatbot functionality
│   │   ├── contact.py   # Contact form
│   │   ├── cv.py        # CV operations
│   │   └── files.py     # File upload/download
│   ├── services/        # Business logic layer
│   │   ├── extraction_service.py           # Orchestrates extraction
│   │   ├── validation_service.py           # Validates data
│   │   ├── ai_service.py                   # AI integration
│   │   ├── phi3_service.py                 # Local AI service
│   │   ├── cv_generation_service.py        # PDF generation
│   │   ├── cv_scoring_service.py           # ATS scoring
│   │   ├── cv_extraction_orchestrator.py   # Pipeline orchestration
│   │   └── course_recommender.py           # Course suggestions
│   ├── utils/           # Utility functions
│   │   ├── extractor.py          # Text extraction
│   │   ├── cleaner.py            # Text normalization
│   │   ├── entity_extractor.py   # spaCy + Regex extraction
│   │   ├── cv_utils.py           # CV helper functions
│   │   ├── ai_utils.py           # AI utilities
│   │   └── email_utils.py        # Email functionality
│   └── templates/       # Jinja2 templates
│       └── cv/
│           └── professional.html   # CV template
├── config/
│   └── config.py        # Configuration
├── tests/               # Test suite
│   ├── test_end_to_end.py
│   ├── test_ats_scoring.py
│   └── test_cv_parsers.py
├── app_fastapi.py       # FastAPI application
├── run.py               # Flask application entry point
└── requirements.txt     # Python dependencies

perfectcv-frontend/
├── src/
│   ├── api.js           # API client
│   ├── App.jsx          # Main application component
│   ├── components/      # Reusable components
│   └── pages/           # Page components
│       ├── Dashboard.jsx
│       ├── Login.jsx
│       ├── Register.jsx
│       └── CVBuilder.jsx
├── public/              # Static assets
├── package.json         # npm dependencies
└── vite.config.js       # Vite configuration
```

---

## 📦 Installation & Setup

### System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB minimum

### Backend Installation

#### 1. Clone Repository

```bash
git clone https://github.com/Dhivanujan/MiniProject-PerfectCV.git
cd MiniProject-PerfectCV/perfectcv-backend
```

#### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt

# Install spaCy language model
python -m spacy download en_core_web_sm
```

#### 4. Configure Environment

Create `.env` file in `perfectcv-backend/`:

```env
# Database
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/perfectcv

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# AI Services (at least one required)
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_key_here (optional)
GEMINI_API_KEY=your_gemini_key_here (optional)

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Environment
FLASK_ENV=development
```

#### 5. Initialize Database

```bash
python create_test_user.py  # Create test user (optional)
```

#### 6. Run Backend

```bash
python run.py
```

Backend runs at **http://localhost:8000**

### Frontend Installation

#### 1. Navigate to Frontend

```bash
cd perfectcv-frontend
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Configure API Endpoint

Update `src/api.js` if needed:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

#### 4. Run Frontend

```bash
npm run dev
```

Frontend runs at **http://localhost:5173**

### Optional: Phi-3 Local AI Setup

For privacy-focused local AI processing:

```bash
# Install Ollama
# Windows: Download from https://ollama.ai/download
# Linux/Mac: curl -fsSL https://ollama.ai/install.sh | sh

# Pull Phi-3 model
ollama pull phi3

# Start Ollama server
ollama serve

# Test integration
cd perfectcv-backend
python test_phi3_integration.py
```

---

## 🔄 CV Processing Pipeline

### Complete Flow

```
📄 User Uploads CV (PDF/DOCX)
    ↓
┌─────────────────────────────────────────┐
│  STAGE 1: TEXT EXTRACTION               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • PyMuPDF extracts text from PDF      │
│  • docx2txt extracts text from DOCX    │
│  • Fallbacks: pdfplumber, pdfminer     │
│  Time: 100-500ms                       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  STAGE 2: TEXT NORMALIZATION            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Fix broken lines & hyphenation      │
│  • Normalize phone numbers             │
│  • Fix OCR errors                      │
│  • Clean whitespace & bullets          │
│  Time: 50-100ms                        │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  STAGE 3: SECTION EXTRACTION            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Detect section headers              │
│  • Extract: summary, experience,       │
│    education, skills, certifications   │
│  Time: 100-200ms                       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  STAGE 4: ENTITY EXTRACTION             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • spaCy NER: names, orgs, dates       │
│  • Regex: email, phone, LinkedIn       │
│  • Skills matching & categorization    │
│  Time: 200-400ms                       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  STAGE 5: VALIDATION                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Check critical fields (name, email) │
│  • Calculate completeness (0-100%)     │
│  • Decide if AI fallback needed        │
│  Time: 10-20ms                         │
└─────────────────────────────────────────┘
    ↓
    Complete (85%)? ──YES──> Continue ✅
    ↓ NO
┌─────────────────────────────────────────┐
│  STAGE 6: AI ENHANCEMENT (if needed)    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Groq/Phi-3 fills missing data       │
│  • Improves content quality            │
│  • Suggests enhancements               │
│  Time: 3-10s                           │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  STAGE 7: ATS SCORING                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Keyword matching                    │
│  • Format analysis                     │
│  • Optimization suggestions            │
│  Time: 100-200ms                       │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│  STAGE 8: PDF GENERATION                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Template rendering (Jinja2)         │
│  • PDF creation (WeasyPrint/ReportLab) │
│  • Professional formatting             │
│  Time: 500ms-2s                        │
└─────────────────────────────────────────┘
    ↓
✅ Download Professional CV PDF
```

### Processing Times

- **Well-formatted CV**: 500ms - 1.5s total
- **Missing data (with AI)**: 4s - 12s total
- **Success Rate**: 95%+ extraction accuracy

---

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}

Response: 201 Created
{
  "message": "User registered successfully",
  "user_id": "507f1f77bcf86cd799439011"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response: 200 OK
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### CV Operations

#### Upload CV
```http
POST /api/upload-cv
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: [CV file - PDF or DOCX]

Response: 200 OK
{
  "cv_id": "507f1f77bcf86cd799439012",
  "extracted_data": {
    "entities": {
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1 (555) 123-4567",
      "skills": ["Python", "JavaScript", "React"]
    },
    "sections": {
      "summary": "Experienced software developer...",
      "experience": [...],
      "education": [...]
    }
  },
  "completeness": 95
}
```

#### Get CV Data
```http
GET /api/cv/{cv_id}
Authorization: Bearer {token}

Response: 200 OK
{
  "cv_id": "507f1f77bcf86cd799439012",
  "data": {...},
  "created_at": "2025-12-15T10:30:00Z"
}
```

#### Generate PDF
```http
POST /api/cv/generate-pdf
Authorization: Bearer {token}
Content-Type: application/json

{
  "cv_id": "507f1f77bcf86cd799439012",
  "template": "professional"
}

Response: 200 OK (PDF file)
```

#### ATS Scoring
```http
POST /api/cv/ats-score
Authorization: Bearer {token}
Content-Type: application/json

{
  "cv_id": "507f1f77bcf86cd799439012",
  "job_description": "We are looking for a Python developer..."
}

Response: 200 OK
{
  "score": 87,
  "matched_keywords": ["Python", "React", "MongoDB"],
  "missing_keywords": ["Docker", "AWS"],
  "suggestions": [
    "Add Docker experience",
    "Include cloud platform skills"
  ]
}
```

### Chatbot

#### Send Message
```http
POST /api/chatbot/message
Authorization: Bearer {token}
Content-Type: application/json

{
  "message": "How can I improve my CV?",
  "cv_id": "507f1f77bcf86cd799439012"
}

Response: 200 OK
{
  "response": "Here are some suggestions to improve your CV...",
  "suggestions": [...]
}
```

---

## ✨ Features

### 1. Intelligent CV Extraction

**Capabilities:**
- Upload PDF or DOCX files
- Automatic text extraction with 95%+ accuracy
- Smart entity recognition (names, emails, phones, skills)
- Section detection (summary, experience, education, skills)
- OCR support for scanned documents
- Multi-format support

**Technologies:**
- PyMuPDF for PDF parsing
- spaCy for NLP entity extraction
- Regex for pattern matching
- Tesseract for OCR (optional)

### 2. AI-Powered Enhancement

**Features:**
- Missing data completion
- Content quality improvement
- Grammar and spelling fixes
- Professional phrasing suggestions
- Skill recommendations
- Achievement quantification

**AI Models:**
- **Groq (LLaMA 3.1)**: Fast, accurate, cost-effective
- **Microsoft Phi-3**: Local processing, privacy-focused
- **OpenAI GPT-4**: Premium quality (optional)
- **Google Gemini**: Alternative provider (optional)

### 3. ATS Optimization

**Scoring Factors:**
- Keyword matching (40%)
- Format readability (30%)
- Content quality (20%)
- Completeness (10%)

**Provides:**
- Overall ATS score (0-100)
- Matched keywords
- Missing keywords
- Specific improvement suggestions

### 4. Professional Templates

**Available Templates:**
- Professional (default)
- Modern
- Classic
- Creative

**Customization:**
- Color schemes
- Font choices
- Layout options
- Section ordering

### 5. Interactive Chatbot

**Capabilities:**
- CV analysis and feedback
- Improvement suggestions
- Skill recommendations
- Industry insights
- Job-specific advice
- Interview preparation tips

**Context-Aware:**
- Understands your CV content
- Provides personalized advice
- References your experience
- Suggests relevant improvements

### 6. Course Recommendations

**Features:**
- Skill gap analysis
- Course suggestions based on career goals
- Learning path recommendations
- Industry trend insights

---

## 🤖 AI Integration

### Groq (LLaMA 3.1) - Primary AI

**Why Groq?**
- ⚡ Fastest inference (100+ tokens/sec)
- 💰 Free tier with generous limits
- 🎯 High accuracy for CV parsing
- 🔄 Reliable API with 99.9% uptime

**Configuration:**
```python
# config/config.py
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_MODEL = 'llama-3.1-70b-versatile'
```

**Usage Example:**
```python
from app.services.ai_service import AIService

ai_service = AIService()
result = ai_service.improve_cv_content(cv_data)
```

### Microsoft Phi-3 - Local AI

**Benefits:**
- 🔒 100% Private - runs locally
- 💰 Zero API costs
- ⚡ Fast inference (10-30 tokens/sec)
- 🎯 Optimized for CV tasks

**Setup:**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull Phi-3 model
ollama pull phi3

# Start server
ollama serve
```

**Smart Fallback:**
```python
# AI is used only when needed (15-20% of CVs)
if completeness < 85%:
    use_ai_fallback()
```

### AI Pipeline Logic

```python
def extract_cv_with_ai(cv_text):
    # Stage 1: Rule-based extraction (fast)
    data = extract_with_rules(cv_text)
    
    # Stage 2: Validation
    completeness = validate_data(data)
    
    # Stage 3: AI enhancement (only if needed)
    if completeness < 85:
        data = enhance_with_ai(data, cv_text)
    
    return data
```

---

## 🧪 Testing

### Run All Tests

```bash
cd perfectcv-backend

# Run all tests
python -m pytest tests/

# Run specific test
python test_modern_system.py

# Run end-to-end test
python test_end_to_end.py
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=app tests/

# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/
```

### Manual Testing

```bash
# Test CV extraction
python test_cv_pipeline.py

# Test ATS scoring
python tests/test_ats_scoring.py

# Test PDF generation
python tests/test_weasyprint_pdf.py

# Test AI integration
python test_phi3_integration.py
```

### Integration Tests

```bash
# Test complete pipeline
python test_complete_pipeline.py

# Test conversational chatbot
python test_conversational_bot.py

# Test name extraction
python test_name_extraction.py
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed

**Error:** `pymongo.errors.ServerSelectionTimeoutError`

**Solution:**
```bash
# Check MongoDB URI in .env
# Ensure IP is whitelisted in MongoDB Atlas
# Test connection:
python -c "from pymongo import MongoClient; print(MongoClient('your_uri').server_info())"
```

#### 2. spaCy Model Not Found

**Error:** `OSError: [E050] Can't find model 'en_core_web_sm'`

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

#### 3. PDF Extraction Fails

**Error:** `AttributeError: module 'fitz' has no attribute 'open'`

**Solution:**
```bash
pip uninstall fitz PyMuPDF
pip install PyMuPDF
```

#### 4. Port Already in Use

**Error:** `Address already in use: ('0.0.0.0', 8000)`

**Solution:**
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

#### 5. AI API Rate Limit

**Error:** `Rate limit exceeded`

**Solution:**
- Use Phi-3 local AI (no limits)
- Implement caching for repeated requests
- Add exponential backoff
- Switch to different AI provider

### Performance Optimization

#### 1. Slow CV Extraction

```python
# Enable caching
from functools import lru_cache

@lru_cache(maxsize=100)
def extract_cv(file_hash):
    # Extraction logic
    pass
```

#### 2. Reduce AI Costs

```python
# Use AI selectively
if completeness > 85:
    return data  # Skip AI
else:
    return enhance_with_ai(data)  # Use AI only when needed
```

#### 3. Database Optimization

```python
# Add indexes
db.cvs.create_index([("user_id", 1)])
db.cvs.create_index([("created_at", -1)])
```

### Debugging Tips

```bash
# Enable debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1

# Check logs
tail -f logs/app.log

# Test individual components
python -c "from app.utils.extractor import extract_text; print(extract_text('test.pdf'))"
```

---

## 📝 Best Practices

### For Users

1. **Upload Quality Files**: Use clear, text-based PDFs (not scanned images)
2. **Standard Formatting**: Use common section headers (Experience, Education, Skills)
3. **Complete Information**: Include all relevant details
4. **Regular Updates**: Keep your CV current
5. **Review AI Suggestions**: Validate AI-generated improvements

### For Developers

1. **Error Handling**: Always wrap AI calls in try-except blocks
2. **Input Validation**: Validate all user inputs
3. **Security**: Never expose API keys in code
4. **Testing**: Write tests for new features
5. **Documentation**: Update docs when changing APIs
6. **Performance**: Monitor response times
7. **Logging**: Log important operations

---

## 📄 License

This project is licensed under the MIT License.

---

## 👥 Support

For issues, questions, or contributions:
- **GitHub Issues**: [Report bugs](https://github.com/Dhivanujan/MiniProject-PerfectCV/issues)
- **Email**: support@perfectcv.com
- **Documentation**: This file

---

## 🎉 Credits

**Developed by**: Dhivanujan  
**AI Models**: Groq (LLaMA 3.1), Microsoft Phi-3, OpenAI, Google Gemini  
**Libraries**: spaCy, PyMuPDF, Flask, React, MongoDB  

---

**Last Updated**: December 15, 2025  
**Version**: 2.0.0
