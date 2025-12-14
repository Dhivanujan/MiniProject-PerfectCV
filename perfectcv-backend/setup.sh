#!/bin/bash
# Setup script for CV Generation Pipeline (Linux/Mac)

echo "============================================================"
echo "CV GENERATION PIPELINE - SETUP SCRIPT"
echo "============================================================"
echo ""

# Check Python
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.9+ first."
    exit 1
fi
python3 --version
echo ""

# Create output directory
echo "[2/5] Creating output directory..."
mkdir -p output
echo "Created: output/"
echo ""

# Install dependencies
echo "[3/5] Installing Python dependencies..."
echo "This may take a few minutes..."
echo ""
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo ""

# Install WeasyPrint system dependencies
echo "[3.5/5] Checking WeasyPrint system dependencies..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux. Installing WeasyPrint dependencies..."
    sudo apt-get update
    sudo apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 libgdk-pixbuf2.0-0
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS. Installing WeasyPrint dependencies..."
    brew install pango
fi
echo ""

# Check for .env file
echo "[4/5] Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found"
    echo "Creating template .env file..."
    cat > .env << EOF
# CV Generation Pipeline Configuration

# Required: Add your Groq API key here
GROQ_API_KEY=your_groq_api_key_here

# Optional: OpenAI as fallback
# OPENAI_API_KEY=your_openai_key_here

# Database
MONGO_URI=mongodb://localhost:27017/perfectcv

# Security
SECRET_KEY=your-secret-key-change-this-in-production

# Frontend
FRONTEND_URL=http://127.0.0.1:5173
EOF
    echo "Created .env template file"
    echo "IMPORTANT: Edit .env and add your GROQ_API_KEY"
    echo ""
else
    echo ".env file found"
    echo ""
fi

# Run verification
echo "[5/5] Running setup verification..."
echo ""
python3 quick_start.py
echo ""

echo "============================================================"
echo "SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your GROQ_API_KEY"
echo "2. Run: python3 app_fastapi.py"
echo "3. Visit: http://localhost:8000/docs"
echo ""
echo "For testing:"
echo "  python3 test_cv_pipeline.py your_resume.pdf"
echo ""
