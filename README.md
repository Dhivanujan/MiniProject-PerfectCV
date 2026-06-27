# 📄 PerfectCV — AI-Powered CV Optimization System

PerfectCV is an intelligent platform that helps job seekers create ATS-friendly resumes by analyzing uploaded CVs, providing AI-powered recommendations, calculating ATS compatibility scores, and generating professionally optimized resumes automatically.

The project combines modern full-stack development with Large Language Models (LLMs) to streamline the resume optimization process and improve candidates' chances of passing Applicant Tracking Systems (ATS).

---

## ✨ Features

### 📑 Resume Analysis

* 📄 Automatic CV parsing and information extraction
* 🎯 ATS compatibility scoring (0–100)
* 📊 Detailed feedback on strengths and weaknesses
* 🧠 Skill, education, and experience detection

### 🤖 AI Features

* 💡 AI-powered resume improvement suggestions
* 💬 AI chatbot for CV advice and career guidance
* 📝 Professional resume rewriting using LLMs
* 🎯 Personalized career recommendations

### 📄 CV Generation

* 📥 Generate professionally formatted PDF resumes
* 🎨 Modern, ATS-friendly resume templates
* 🔄 Automatically populate templates using extracted data

### 🔐 User Management

* 👤 Secure user authentication
* 📁 Upload and manage multiple resumes
* ☁️ File storage using MongoDB GridFS

---

## 🛠️ Tech Stack

| Layer                      | Technology                            |
| -------------------------- | ------------------------------------- |
| 🌐 **Frontend**            | React.js, Vite, Tailwind CSS, Axios   |
| ⚙️ **Backend**             | FastAPI, Python                       |
| 🗄️ **Database**           | MongoDB Atlas, MongoDB GridFS         |
| 🤖 **AI Integration**      | Google Gemini AI, Groq LLaMA 3.3      |
| 📄 **Document Processing** | PyPDF2, pdfplumber, Jinja2, xhtml2pdf |
| 🔐 **Authentication**      | JWT (JSON Web Tokens)                 |

---

## 📁 Project Structure

```text
perfectcv/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   ├── models/
│   │   ├── database/
│   │   ├── utils/
│   │   └── ai/
│   ├── templates/
│   └── main.py
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       ├── context/
│       └── assets/
│
├── screenshots/
├── README.md
└── requirements.txt
```

---

## 🚀 Getting Started

### 📋 Prerequisites

* Python 3.10+
* Node.js 18+
* MongoDB Atlas
* Google Gemini API Key
* Groq API Key

---

## ⚙️ Backend Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/perfectcv.git
cd perfectcv
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the backend directory.

```env
MONGODB_URI=your_mongodb_connection_string

JWT_SECRET=your_jwt_secret

GEMINI_API_KEY=your_gemini_api_key

GROQ_API_KEY=your_groq_api_key
```

> ⚠️ Never commit API keys or secrets to version control.

### 5️⃣ Run the Backend

```bash
uvicorn main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

---

# 💻 Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Start Development Server

```bash
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

---

## 📸 Screenshots

> Add your application screenshots inside the `screenshots/` folder.

Example:

```text
screenshots/
├── home.png
├── upload.png
├── analysis.png
├── ats-score.png
├── generated-cv.png
└── chatbot.png
```

---

## 🔗 API Overview

| Resource          | Endpoint        |
| ----------------- | --------------- |
| 🔑 Authentication | `/api/auth/*`   |
| 📄 Resume Upload  | `/api/upload`   |
| 🤖 AI Analysis    | `/api/analyze`  |
| 📊 ATS Score      | `/api/score`    |
| 📥 CV Generation  | `/api/generate` |
| 💬 AI Chatbot     | `/api/chat`     |

---

## 🌍 Environment Variables

| Variable         | Description                     |
| ---------------- | ------------------------------- |
| `MONGODB_URI`    | MongoDB Atlas connection string |
| `JWT_SECRET`     | JWT signing secret              |
| `GEMINI_API_KEY` | Google Gemini API key           |
| `GROQ_API_KEY`   | Groq API key                    |

---

## 🚀 Deployment

The application can be deployed using:

* ☁️ Vercel (Frontend)
* ⚙️ Render / Railway / VPS (Backend)
* 🗄️ MongoDB Atlas (Database)

---

## 🔒 Security

* 🔐 JWT-based authentication
* 📁 Secure file storage using MongoDB GridFS
* 🚫 Environment variables for API keys and secrets
* 🛡️ Input validation and request sanitization

---

## 🎓 Project Information

This project was developed as an academic group project to demonstrate the integration of Artificial Intelligence with modern full-stack web development. It focuses on helping job seekers optimize their resumes for Applicant Tracking Systems (ATS) using Large Language Models (LLMs), automated document processing, and intelligent career assistance.
