"""
Setup script for AI-enhanced CV extraction features.
Run this after installing requirements.txt to verify all dependencies.
"""

import sys
import subprocess
import os

def check_module(module_name, package_name=None):
    """Check if a Python module is installed."""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✓ {package_name} is installed")
        return True
    except ImportError:
        print(f"✗ {package_name} is NOT installed")
        return False

def check_system_command(command, name):
    """Check if a system command is available."""
    try:
        result = subprocess.run(
            [command, '--version'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0:
            print(f"✓ {name} is installed: {result.stdout.split()[0] if result.stdout else 'found'}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    
    print(f"✗ {name} is NOT installed (optional for OCR)")
    return False

def check_env_variable(var_name):
    """Check if environment variable is set."""
    value = os.getenv(var_name)
    if value and value != f"your_{var_name.lower()}_here":
        print(f"✓ {var_name} is configured")
        return True
    else:
        print(f"✗ {var_name} is NOT configured")
        return False

def main():
    print("=" * 60)
    print("PerfectCV - AI Enhancement Setup Verification")
    print("=" * 60)
    print()
    
    # Load .env file
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print("✓ .env file loaded")
        else:
            print("⚠ .env file not found")
    except ImportError:
        print("⚠ python-dotenv not installed")
    
    print()
    print("Checking Python Dependencies:")
    print("-" * 60)
    
    # Core dependencies
    core_deps = {
        'groq': 'groq',
        'openai': 'openai',
        'pytesseract': 'pytesseract',
        'PIL': 'pillow',
        'pdf2image': 'pdf2image',
        'fitz': 'PyMuPDF',
        'pdfplumber': 'pdfplumber',
        'google.generativeai': 'google-generativeai',
    }
    
    core_status = []
    for module, package in core_deps.items():
        status = check_module(module, package)
        core_status.append(status)
    
    print()
    print("Checking System Dependencies (for OCR):")
    print("-" * 60)
    
    tesseract_ok = check_system_command('tesseract', 'Tesseract OCR')
    poppler_ok = check_system_command('pdftoppm', 'Poppler (pdf2image)')
    
    print()
    print("Checking API Configuration:")
    print("-" * 60)
    
    groq_ok = check_env_variable('GROQ_API_KEY')
    openai_ok = check_env_variable('OPENAI_API_KEY')
    google_ok = check_env_variable('GOOGLE_API_KEY')
    
    print()
    print("=" * 60)
    print("Summary:")
    print("=" * 60)
    
    all_core = all(core_status)
    ocr_ready = tesseract_ok and poppler_ok
    ai_ready = groq_ok or openai_ok or google_ok
    
    if all_core:
        print("✓ All core Python dependencies are installed")
    else:
        print("✗ Some Python dependencies are missing. Run: pip install -r requirements.txt")
    
    if ocr_ready:
        print("✓ OCR support is fully configured")
    else:
        print("⚠ OCR support incomplete (optional - for scanned PDFs)")
        print("  Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
        print("  Install Poppler: https://github.com/oschwartz10612/poppler-windows/releases/")
    
    if groq_ok:
        print("✓ Groq is configured (RECOMMENDED - ultra-fast & FREE)")
    elif openai_ok:
        print("✓ OpenAI GPT-4 is configured (high quality)")
    elif google_ok:
        print("⚠ Using Google Gemini only (consider adding Groq for speed)")
        print("  Groq is FREE and 10x faster! Add GROQ_API_KEY to .env")
    else:
        print("⚠ No AI API configured - will use rule-based extraction only")
        print("  Add GROQ_API_KEY to .env (FREE & recommended)")
        print("  Or add OPENAI_API_KEY or GOOGLE_API_KEY")
    
    print()
    
    if all_core and ai_ready:
        print("🎉 Setup complete! AI-enhanced CV extraction is ready to use.")
        if groq_ok:
            print("⚡ Using Groq for ultra-fast processing!")
    elif all_core:
        print("⚠ Core features ready, but AI enhancement needs API key configuration.")
    else:
        print("❌ Setup incomplete. Please install missing dependencies.")
    
    print()
    print("Next steps:")
    if not all_core:
        print("  1. Run: pip install -r requirements.txt")
    if not groq_ok and not openai_ok and not google_ok:
        print("  2. Add GROQ_API_KEY to .env (FREE, ultra-fast, recommended!)")
        print("     Get key at: https://console.groq.com")
    if not ocr_ready:
        print("  3. (Optional) Install Tesseract and Poppler for OCR support")
    
    print()
    print("For detailed setup instructions, see: AI_CV_EXTRACTION_GUIDE.md")
    print("=" * 60)

if __name__ == "__main__":
    main()
