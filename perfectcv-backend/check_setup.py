"""
Check if all required dependencies are installed.
Run this after pip install to verify your setup.
"""
import sys

def check_imports():
    """Check if all required libraries are available."""
    checks = {
        'PyPDF2': False,
        'pdfplumber': False,
        'pdfminer.six': False,
        'docx (python-docx)': False,
        'spacy': False,
        'phonenumbers': False,
        'jinja2': False,
        'flask': False,
        'pymongo': False,
    }
    
    # Check imports
    try:
        import PyPDF2
        checks['PyPDF2'] = True
    except ImportError:
        pass
    
    try:
        import pdfplumber
        checks['pdfplumber'] = True
    except ImportError:
        pass
    
    try:
        from pdfminer.high_level import extract_text
        checks['pdfminer.six'] = True
    except ImportError:
        pass
    
    try:
        from docx import Document
        checks['docx (python-docx)'] = True
    except ImportError:
        pass
    
    try:
        import spacy
        checks['spacy'] = True
        # Check if model is downloaded
        try:
            nlp = spacy.load('en_core_web_sm')
            checks['spacy'] = 'with en_core_web_sm model ✓'
        except OSError:
            checks['spacy'] = 'installed but model MISSING ⚠'
    except ImportError:
        pass
    
    try:
        import phonenumbers
        checks['phonenumbers'] = True
    except ImportError:
        pass
    
    try:
        import jinja2
        checks['jinja2'] = True
    except ImportError:
        pass
    
    try:
        import flask
        checks['flask'] = True
    except ImportError:
        pass
    
    try:
        import pymongo
        checks['pymongo'] = True
    except ImportError:
        pass
    
    # Optional libraries
    optional = {}
    
    try:
        from weasyprint import HTML
        optional['weasyprint (Better PDFs)'] = True
    except (ImportError, OSError) as e:
        # WeasyPrint requires GTK+ on Windows - handle gracefully
        optional['weasyprint (Better PDFs)'] = False
    
    try:
        from fpdf import FPDF
        optional['fpdf2 (PDF Fallback)'] = True
    except ImportError:
        optional['fpdf2 (PDF Fallback)'] = False
    
    try:
        import pytesseract
        optional['pytesseract (OCR Support)'] = True
    except ImportError:
        optional['pytesseract (OCR Support)'] = False
    
    try:
        from PIL import Image
        optional['Pillow (Image Processing)'] = True
    except ImportError:
        optional['Pillow (Image Processing)'] = False
    
    try:
        import pdf2image
        optional['pdf2image (OCR Support)'] = True
    except ImportError:
        optional['pdf2image (OCR Support)'] = False
    
    try:
        from openai import OpenAI
        optional['openai (AI Features)'] = True
    except ImportError:
        optional['openai (AI Features)'] = False
    
    try:
        import google.generativeai as genai
        optional['google-generativeai (AI)'] = True
    except ImportError:
        optional['google-generativeai (AI)'] = False
    
    try:
        from groq import Groq
        optional['groq (AI Features)'] = True
    except ImportError:
        optional['groq (AI Features)'] = False
    
    # Print results
    print("=" * 70)
    print(" " * 15 + "DEPENDENCY CHECK RESULTS")
    print("=" * 70)
    print("\n📦 REQUIRED DEPENDENCIES:")
    print("-" * 70)
    
    all_required_ok = True
    for lib, status in checks.items():
        if status and status is not True and 'MISSING' not in str(status):
            symbol = "✓"
            color = "\033[92m"  # Green
        elif status is True:
            symbol = "✓"
            color = "\033[92m"  # Green
        else:
            symbol = "✗"
            color = "\033[91m"  # Red
            all_required_ok = False
        
        reset = "\033[0m"
        status_str = status if status else "NOT INSTALLED"
        print(f"  {color}{symbol}{reset} {lib:.<40} {status_str}")
    
    print("\n🔧 OPTIONAL DEPENDENCIES:")
    print("-" * 70)
    
    for lib, status in optional.items():
        if status:
            symbol = "✓"
            color = "\033[92m"  # Green
            status_str = "Installed"
        else:
            symbol = "○"
            color = "\033[93m"  # Yellow
            status_str = "Not installed (optional)"
        
        reset = "\033[0m"
        print(f"  {color}{symbol}{reset} {lib:.<40} {status_str}")
    
    print("\n" + "=" * 70)
    
    # Summary
    if all_required_ok:
        print("\n✅ SUCCESS: All required dependencies are installed!")
        print("\nℹ️  NOTES:")
        
        if not optional['weasyprint (Better PDFs)'] and not optional['fpdf2 (PDF Fallback)']:
            print("  • No PDF generation library found")
            print("    Install: pip install weasyprint  (or fpdf2)")
        elif not optional['weasyprint (Better PDFs)']:
            print("  • Using FPDF for PDF generation (basic)")
            print("    For better PDFs: pip install weasyprint")
        
        if not any(optional.get(k, False) for k in ['openai (AI Features)', 'google-generativeai (AI)', 'groq (AI Features)']):
            print("  • No AI library installed - AI features won't work")
            print("    Install: pip install openai  (or google-generativeai, or groq)")
        
        if not optional['pytesseract (OCR Support)']:
            print("  • OCR not available - scanned PDFs won't be processed")
            print("    Install: pip install pytesseract pillow pdf2image")
            print("    Also install Tesseract: https://github.com/tesseract-ocr/tesseract")
        
        print("\n🚀 You're ready to start the server!")
        print("   Run: python run.py")
    else:
        print("\n❌ ERROR: Missing required dependencies!")
        print("\n📋 TO FIX:")
        
        missing = [lib for lib, status in checks.items() if not status]
        if missing:
            print("\n1. Install missing packages:")
            print("   pip install -r requirements.txt")
        
        # Check spaCy model specifically
        spacy_status = checks.get('spacy', False)
        if spacy_status and 'MISSING' in str(spacy_status):
            print("\n2. Download spaCy language model:")
            print("   python -m spacy download en_core_web_sm")
        
        print("\n3. Run this check again:")
        print("   python check_setup.py")
    
    print("=" * 70)
    print()
    
    return all_required_ok


if __name__ == "__main__":
    success = check_imports()
    sys.exit(0 if success else 1)
