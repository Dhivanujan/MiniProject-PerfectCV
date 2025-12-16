# PerfectCV - Complete Project Documentation

**Project:** AI-Powered CV Optimization System  
**Version:** 1.0  
**Last Updated:** December 16, 2025

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Backend Structure](#backend-structure)
4. [Frontend Structure](#frontend-structure)
5. [Key Features](#key-features)
6. [File Descriptions](#file-descriptions)
7. [API Endpoints](#api-endpoints)
8. [Database Schema](#database-schema)
9. [Configuration](#configuration)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview

PerfectCV is an AI-powered CV optimization platform that helps users create ATS-friendly resumes. The system analyzes uploaded CVs, provides intelligent suggestions, scores them based on ATS compatibility, and generates optimized PDF versions.

### Tech Stack

**Backend:**
- Python 3.13
- Flask (Web Framework)
- MongoDB Atlas (Database)
- PyMongo (Database Driver)
- Google Gemini AI (CV Analysis)
- PyPDF2 & FPDF (PDF Processing)
- Flask-Login (Authentication)
- python-dotenv (Environment Management)

**Frontend:**
- React 18
- Vite (Build Tool)
- TailwindCSS (Styling)
- Axios (HTTP Client)
- React Router DOM (Routing)

---

## Architecture

```
PerfectCV/
├── perfectcv-backend/          # Flask Backend
│   ├── app/
│   │   ├── __init__.py         # Flask app initialization
│   │   ├── auth/               # Authentication modules
│   │   ├── models/             # Database models
│   │   ├── routes/             # API endpoints
│   │   ├── services/           # Business logic services
│   │   └── utils/              # Utility functions
│   ├── config/                 # Configuration files
│   ├── .env                    # Environment variables
│   ├── run.py                  # Application entry point
│   └── requirements.txt        # Python dependencies
│
└── perfectcv-frontend/         # React Frontend
    ├── src/
    │   ├── components/         # Reusable React components
    │   ├── pages/              # Page components
    │   ├── assets/             # Images and static files
    │   ├── api.js              # Axios configuration
    │   ├── App.jsx             # Main app component
    │   └── main.jsx            # Entry point
    ├── public/                 # Public static files
    ├── package.json            # NPM dependencies
    └── vite.config.js          # Vite configuration
```

---

## Backend Structure

### 📁 `/perfectcv-backend`

#### **Root Files**

| File | Purpose |
|------|---------|
| `run.py` | Main application entry point, starts Flask server |
| `app_fastapi.py` | FastAPI implementation (alternative) |
| `test_api_keys.py` | Tests AI API key configuration |
| `test_mongo_login.py` | Tests MongoDB connection and login |
| `requirements.txt` | Python package dependencies |
| `.env` | Environment variables (MongoDB URI, API keys, etc.) |

#### **`/app` - Core Application**

**`__init__.py`**
- Initializes Flask application
- Sets up MongoDB connection
- Configures CORS
- Registers blueprints (routes)
- Initializes Flask-Login for authentication

#### **`/app/auth` - Authentication**

| File | Purpose |
|------|---------|
| `jwt_handler.py` | JWT token generation and validation |

#### **`/app/models` - Database Models**

| File | Purpose |
|------|---------|
| `user.py` | User model with Flask-Login integration |

#### **`/app/routes` - API Endpoints**

| File | Purpose | Endpoints |
|------|---------|-----------|
| `auth.py` | User authentication | `/auth/login`, `/auth/register`, `/auth/logout` |
| `auth_fastapi.py` | FastAPI authentication routes | FastAPI version of auth |
| `files.py` | CV file upload/download | `/api/upload-cv`, `/api/download/:id` |
| `cv.py` | CV operations | `/api/cv/*` |
| `chatbot.py` | AI chatbot integration | `/api/chatbot/*` |
| `contact.py` | Contact form | `/api/contact` |

#### **`/app/services` - Business Logic**

| File | Purpose |
|------|---------|
| `ai_service.py` | Core AI service integration (Google Gemini) |
| `cv_ai_service.py` | AI-powered CV analysis and optimization |
| `cv_extract_service.py` | Extracts structured data from CVs |
| `cv_extraction_orchestrator.py` | Orchestrates multi-step extraction |
| `cv_generation_service.py` | Generates optimized CV content |
| `cv_pdf_service.py` | PDF generation using FPDF |
| `cv_pdf_service_reportlab.py` | PDF generation using ReportLab |
| `cv_scoring_service.py` | ATS scoring algorithm |
| `cv_validation_service.py` | Validates CV data |
| `extraction_service.py` | General extraction utilities |
| `validation_service.py` | Data validation utilities |
| `course_recommender.py` | Course/learning recommendations |
| `phi3_service.py` | Phi3 AI model integration |

#### **`/app/utils` - Utility Functions**

| File | Purpose |
|------|---------|
| `ai_utils.py` | AI-related utilities |
| `ai_cv_parser.py` | AI-powered CV parsing |
| `cv_utils.py` | CV processing utilities |
| `cv_template_mapper.py` | Maps CV data to template format |
| `cv_template_generator.py` | Generates CV templates |
| `cv_templates.py` | CV template definitions |
| `text_extractor.py` | Extracts text from PDFs |
| `text_cleaner.py` | Cleans and normalizes text |
| `entity_extractor.py` | Extracts entities (names, emails, etc.) |
| `extractor.py` | General extraction utilities |
| `modern_extractor.py` | Modern extraction algorithms |
| `modern_formatter.py` | Modern formatting utilities |
| `nlp_utils.py` | NLP processing utilities |
| `cleaner.py` | Data cleaning utilities |
| `email_utils.py` | Email sending utilities |

#### **`/config`**

| File | Purpose |
|------|---------|
| `config.py` | Application configuration (loads from .env) |

---

## Frontend Structure

### 📁 `/perfectcv-frontend`

#### **Root Files**

| File | Purpose |
|------|---------|
| `index.html` | HTML entry point |
| `package.json` | NPM dependencies and scripts |
| `vite.config.js` | Vite build configuration |
| `tailwind.config.js` | TailwindCSS configuration |
| `postcss.config.js` | PostCSS configuration |
| `eslint.config.js` | ESLint configuration |

#### **`/src/pages` - Page Components**

| File | Purpose | Route |
|------|---------|-------|
| `Home.jsx` | Landing page | `/` |
| `Login.jsx` | User login | `/login` |
| `Register.jsx` | User registration | `/register` |
| `ForgotPassword.jsx` | Password reset request | `/forgot-password` |
| `ResetPassword.jsx` | Password reset | `/reset-password/:token` |
| `Dashboard.jsx` | Main dashboard (CV upload/analysis) | `/dashboard` |
| `ChatbotPage.jsx` | AI chatbot interface | `/chatbot` |
| `LoadingPage.jsx` | Loading screen | N/A (component) |

#### **`/src/components` - Reusable Components**

| File | Purpose |
|------|---------|
| `Navbar.jsx` | Navigation bar |
| `Footer.jsx` | Page footer |
| `Hero.jsx` | Hero section (landing page) |
| `About.jsx` | About section |
| `HowItWorks.jsx` | How it works section |
| `CTA.jsx` | Call-to-action section |
| `FAQ.jsx` | Frequently asked questions |
| `Contact.jsx` | Contact form |
| `Testimonials.jsx` | User testimonials |
| `CVAnalysisPanel.jsx` | CV analysis results display |
| `CVAnalyzer_Example.jsx` | Example CV analyzer |
| `ResumeTemplate.jsx` | CV preview/render template |
| `ConfirmationModal.jsx` | Confirmation dialog |

#### **`/src` - Core Files**

| File | Purpose |
|------|---------|
| `main.jsx` | React entry point, sets up routing |
| `App.jsx` | Main app component with routes |
| `api.js` | Axios instance with base URL configuration |
| `index.css` | Global styles (TailwindCSS imports) |
| `App.css` | App-specific styles |

---

## Key Features

### 1. **AI-Powered CV Analysis**
- Uses Google Gemini AI to analyze CV content
- Extracts structured data (personal info, skills, experience, education)
- Provides intelligent suggestions for improvement
- Categorizes suggestions (content, formatting, keywords, etc.)

### 2. **ATS Scoring**
- Scores CVs based on ATS (Applicant Tracking System) compatibility
- Analyzes keyword density
- Checks formatting and structure
- Provides actionable recommendations

### 3. **CV Optimization**
- Rewrites CV content for better ATS performance
- Optimizes for specific job domains
- Suggests missing keywords
- Improves professional language

### 4. **PDF Generation**
- Converts optimized CVs to professional PDF format
- Multiple template options
- Clean, ATS-friendly formatting

### 5. **User Authentication**
- Secure login/registration
- Password reset functionality
- Session management with Flask-Login

### 6. **File Management**
- Upload CV files (PDF, DOCX)
- Download optimized CVs
- View upload history
- Store files in MongoDB GridFS

### 7. **AI Chatbot**
- Interactive career advice
- CV improvement tips
- Job search guidance

---

## File Descriptions

### Backend Key Files

#### **`app/__init__.py`**
```python
# Main Flask application factory
# - Initializes Flask app
# - Configures MongoDB connection
# - Sets up CORS for frontend communication
# - Registers all route blueprints
# - Initializes Flask-Login for user sessions
```

#### **`routes/files.py`**
```python
# Core CV upload and processing endpoint
# POST /api/upload-cv
# - Accepts PDF/DOCX files
# - Extracts text content
# - Calls AI service for analysis
# - Generates structured CV data
# - Calculates ATS score
# - Stores in MongoDB GridFS
# - Returns optimized CV and suggestions
```

#### **`services/cv_ai_service.py`**
```python
# AI-powered CV analysis
# - Uses Google Gemini API
# - Analyzes CV content
# - Extracts structured data
# - Generates improvement suggestions
# - Optimizes for ATS compatibility
```

#### **`services/cv_scoring_service.py`**
```python
# ATS Scoring Algorithm
# - Keyword analysis
# - Format validation
# - Section completeness check
# - Returns 0-100 score
```

#### **`utils/cv_template_mapper.py`**
```python
# Maps extracted CV data to template format
# normalize_cv_for_template()
# - Extracts contact info
# - Normalizes skills
# - Formats experience
# - Cleans education data
# - Returns structured template data
```

### Frontend Key Files

#### **`pages/Dashboard.jsx`**
```jsx
// Main dashboard component
// Features:
// - CV file upload
// - ATS score display
// - Optimized CV preview
// - Suggestions display
// - Download optimized PDF
// - File history
```

#### **`components/ResumeTemplate.jsx`**
```jsx
// CV preview/render component
// - Displays formatted CV
// - Handles multiple data sources
// - Professional styling
// - Responsive design
```

#### **`api.js`**
```javascript
// Axios configuration
// - Base URL: http://localhost:8000
// - Credentials: include
// - Response/error interceptors
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/auth/register` | Register new user | `{username, email, password}` | `{message, user_id}` |
| POST | `/auth/login` | User login | `{email, password}` | `{message, user}` |
| POST | `/auth/logout` | User logout | - | `{message}` |
| GET | `/api/current-user` | Get current user | - | `{user}` |

### CV Operations

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/api/upload-cv` | Upload and analyze CV | FormData: `file`, `jobDomain` | Full analysis result |
| GET | `/api/download/:id` | Download CV | - | PDF file |
| POST | `/api/download-optimized-cv` | Download optimized CV | `{structured_cv, optimized_text}` | PDF file |
| GET | `/api/files` | Get user's uploaded files | - | `{files: [...]}` |

### Chatbot

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/chatbot/chat` | Send message to AI chatbot | `{message, conversationHistory}` | `{reply}` |

### Contact

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/contact` | Submit contact form | `{name, email, message}` | `{message}` |

---

## Database Schema

### MongoDB Collections

#### **`users` Collection**

```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String (unique, required),
  password: String (hashed, required),
  createdAt: Date,
  lastLogin: Date
}
```

#### **`fs.files` Collection (GridFS)**

```javascript
{
  _id: ObjectId,
  filename: String,
  uploadDate: Date,
  length: Number,
  chunkSize: Number,
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
API_KEY=AIzaSy...              # Google Gemini API Key
GOOGLE_API_KEY=AIzaSy...       # Google AI API Key
GROQ_API_KEY=gsk_...           # Groq API Key (optional)

# Email Configuration
MAIL_USERNAME=your-email@gmail.com
MAIL=your-email@gmail.com
MAIL_PASSWORD=app-password

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Frontend URL
FRONTEND_URL=http://localhost:5173
```

### Frontend Configuration

**`vite.config.js`**
```javascript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

---

## Troubleshooting

### Common Issues

#### 1. **MongoDB Connection Failed**

**Error:** `DNS resolution failed` or `Connection timeout`

**Solutions:**
- Change DNS to Google DNS (8.8.8.8) or Cloudflare (1.1.1.1)
- Run: `ipconfig /flushdns` (Windows)
- Check MongoDB Atlas IP whitelist
- Verify MONGO_URI in `.env`
- Check firewall settings

**Test:**
```bash
cd perfectcv-backend
python test_mongo_login.py
```

#### 2. **API Key Not Working**

**Error:** `API key invalid` or `Quota exceeded`

**Solutions:**
- Verify API key in `.env`
- Check Google Cloud Console for quota
- Enable Gemini API in Google Cloud

**Test:**
```bash
cd perfectcv-backend
python test_api_keys.py
```

#### 3. **CORS Issues**

**Error:** `CORS policy blocked`

**Solution:**
- Check CORS configuration in `app/__init__.py`
- Ensure frontend URL matches FRONTEND_URL in `.env`

#### 4. **PDF Generation Fails**

**Error:** `PDF generation error`

**Solutions:**
- Check if FPDF is installed: `pip install fpdf`
- Verify font files are available
- Check `cv_pdf_service.py` for errors

#### 5. **Login Not Working**

**Error:** `AttributeError: 'NoneType' object has no attribute 'users'`

**Solution:**
- This means MongoDB is not connected
- Follow MongoDB Connection troubleshooting above

---

## Running the Application

### Backend

```bash
cd perfectcv-backend
pip install -r requirements.txt
python run.py
```

Server runs on: `http://localhost:8000`

### Frontend

```bash
cd perfectcv-frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:5173`

---

## Project Dependencies

### Backend (`requirements.txt`)

```
Flask>=3.0.0
flask-cors>=4.0.0
Flask-Login>=0.6.3
pymongo>=4.6.0
python-dotenv>=1.0.0
PyPDF2>=3.0.1
fpdf>=1.7.2
google-generativeai>=0.3.0
bcrypt>=4.1.2
python-jose>=3.3.0
```

### Frontend (`package.json`)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "vite": "^5.0.8"
  }
}
```

---

## Development Workflow

### 1. **Feature Development**

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes
# Test locally

# Commit
git add .
git commit -m "feat: Your feature description"

# Push
git push origin feature/your-feature-name
```

### 2. **Testing**

**Backend Tests:**
```bash
python test_api_keys.py      # Test AI API keys
python test_mongo_login.py   # Test MongoDB connection
```

**Frontend Tests:**
```bash
npm run dev                   # Start dev server
# Manual testing in browser
```

### 3. **Deployment**

**Backend (Render/Heroku):**
- Set environment variables
- Deploy from GitHub repo
- Use `run.py` as entry point

**Frontend (Vercel/Netlify):**
- Build command: `npm run build`
- Output directory: `dist`
- Set VITE_API_URL environment variable

---

## Security Best Practices

1. **Never commit `.env` files** - Add to `.gitignore`
2. **Use strong passwords** - Hashed with bcrypt
3. **Validate user input** - Prevent injection attacks
4. **Use HTTPS** in production
5. **Rotate API keys** regularly
6. **Limit file upload size** - Prevent DoS attacks
7. **Sanitize user data** - Before storing in database

---

## Future Enhancements

- [ ] Multiple CV templates
- [ ] Export to Word format
- [ ] LinkedIn integration
- [ ] Job matching algorithm
- [ ] Interview preparation tips
- [ ] Cover letter generation
- [ ] Real-time collaboration
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

---

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## License

This project is proprietary software developed for SE5014 Mini Project.

---

## Contact & Support

For issues or questions:
- Create an issue in the repository
- Contact: team@perfectcv.com

---

**Last Updated:** December 16, 2025  
**Version:** 1.0  
**Maintainers:** PerfectCV Team
