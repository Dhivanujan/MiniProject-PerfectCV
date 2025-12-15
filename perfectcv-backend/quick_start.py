"""
Quick Start Script for CV Generation Pipeline
Run this to verify setup and test the system
"""
import os
import sys
from pathlib import Path

def check_environment():
    """Check if environment is properly configured"""
    print("\n" + "="*60)
    print("CV GENERATION PIPELINE - SETUP VERIFICATION")
    print("="*60 + "\n")
    
    issues = []
    
    # Check Python version
    print("1. Checking Python version...")
    if sys.version_info >= (3, 9):
        print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    else:
        print(f"   ✗ Python {sys.version_info.major}.{sys.version_info.minor} (3.9+ required)")
        issues.append("Python version")
    
    # Check required packages
    print("\n2. Checking required packages...")
    required_packages = [
        'fastapi',
        'uvicorn',
        'groq',
        'jinja2',
        'weasyprint',
        'pdfminer',
        'docx',
        'pymupdf'
    ]
    
    for package in required_packages:
        try:
            if package == 'pymupdf':
                __import__('fitz')
            elif package == 'docx':
                __import__('docx')
            elif package == 'pdfminer':
                __import__('pdfminer.high_level')
            else:
                __import__(package)
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} (not installed)")
            issues.append(package)
    
    # Check environment variables
    print("\n3. Checking environment variables...")
    from config.config import Config
    
    if Config.GROQ_API_KEY:
        print("   ✓ GROQ_API_KEY set")
    elif Config.OPENAI_API_KEY:
        print("   ✓ OPENAI_API_KEY set")
    else:
        print("   ✗ No AI API key found")
        issues.append("AI API key")
    
    # Check directory structure
    print("\n4. Checking directory structure...")
    required_dirs = [
        'app/services',
        'app/routes',
        'app/utils',
        'app/templates',
        'output'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✓ {dir_path}/")
        else:
            print(f"   ✗ {dir_path}/ (missing)")
            os.makedirs(dir_path, exist_ok=True)
            print(f"      Created {dir_path}/")
    
    # Check template file
    print("\n5. Checking template files...")
    if os.path.exists('app/templates/cv_template.html'):
        print("   ✓ cv_template.html")
    else:
        print("   ✗ cv_template.html (missing)")
        issues.append("cv_template.html")
    
    # Summary
    print("\n" + "="*60)
    if not issues:
        print("✓ ALL CHECKS PASSED - READY TO USE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Run FastAPI server:")
        print("   python app_fastapi.py")
        print("\n2. Test with sample CV:")
        print("   python test_cv_pipeline.py sample.pdf")
        print("\n3. Access API docs:")
        print("   http://localhost:8000/docs")
        return True
    else:
        print("✗ SETUP INCOMPLETE")
        print("="*60)
        print("\nIssues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease fix the issues above and run this script again.")
        return False


def install_missing_packages():
    """Offer to install missing packages"""
    print("\nWould you like to install missing packages? (y/n): ", end='')
    response = input().strip().lower()
    
    if response == 'y':
        print("\nInstalling packages...")
        os.system('pip install -r requirements.txt')
        print("\n✓ Installation complete. Please run this script again.")
    else:
        print("\nTo install manually, run: pip install -r requirements.txt")


def main():
    """Main entry point"""
    success = check_environment()
    
    if not success:
        install_missing_packages()


if __name__ == "__main__":
    main()
