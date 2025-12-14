@echo off
REM Setup script for CV Generation Pipeline (Windows)
echo ============================================================
echo CV GENERATION PIPELINE - SETUP SCRIPT
echo ============================================================
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python 3.9+ first.
    pause
    exit /b 1
)
python --version
echo.

REM Create output directory
echo [2/5] Creating output directory...
if not exist "output" mkdir output
echo Created: output/
echo.

REM Install dependencies
echo [3/5] Installing Python dependencies...
echo This may take a few minutes...
echo.
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

REM Check for .env file
echo [4/5] Checking environment configuration...
if not exist ".env" (
    echo WARNING: .env file not found
    echo Creating template .env file...
    (
        echo # CV Generation Pipeline Configuration
        echo.
        echo # Required: Add your Groq API key here
        echo GROQ_API_KEY=your_groq_api_key_here
        echo.
        echo # Optional: OpenAI as fallback
        echo # OPENAI_API_KEY=your_openai_key_here
        echo.
        echo # Database
        echo MONGO_URI=mongodb://localhost:27017/perfectcv
        echo.
        echo # Security
        echo SECRET_KEY=your-secret-key-change-this-in-production
        echo.
        echo # Frontend
        echo FRONTEND_URL=http://127.0.0.1:5173
    ) > .env
    echo Created .env template file
    echo IMPORTANT: Edit .env and add your GROQ_API_KEY
    echo.
) else (
    echo .env file found
    echo.
)

REM Run verification
echo [5/5] Running setup verification...
echo.
python quick_start.py
echo.

echo ============================================================
echo SETUP COMPLETE!
echo ============================================================
echo.
echo Next steps:
echo 1. Edit .env file and add your GROQ_API_KEY
echo 2. Run: python app_fastapi.py
echo 3. Visit: http://localhost:8000/docs
echo.
echo For testing:
echo   python test_cv_pipeline.py your_resume.pdf
echo.

pause
