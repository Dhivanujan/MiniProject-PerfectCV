"""
Comprehensive System Test
Tests all major components of the PerfectCV system
"""
import sys
import requests
import json
from colorama import init, Fore, Style

init(autoreset=True)

BACKEND_URL = "http://127.0.0.1:5000"
FRONTEND_URL = "http://localhost:5174"

def print_header(text):
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}{text:^70}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

def print_success(text):
    print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")

def print_error(text):
    print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")

def print_warning(text):
    print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")

def print_info(text):
    print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")

def test_backend_health():
    """Test backend health endpoint"""
    print_header("BACKEND HEALTH CHECK")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is running on {BACKEND_URL}")
            print_info(f"MongoDB Status: {'Connected' if data.get('mongo') else 'Disconnected'}")
            return True, data.get('mongo', False)
        else:
            print_error(f"Backend returned status {response.status_code}")
            return False, False
    except requests.exceptions.ConnectionError:
        print_error("Backend is not running! Start it with: python run.py")
        return False, False
    except Exception as e:
        print_error(f"Backend error: {str(e)}")
        return False, False

def test_auth_endpoints():
    """Test authentication endpoints"""
    print_header("AUTHENTICATION ENDPOINTS")
    
    # Test login endpoint (expect 400 for missing credentials)
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login", 
                               json={}, 
                               timeout=5)
        if response.status_code in [400, 401]:
            print_success("Login endpoint responding correctly")
        else:
            print_warning(f"Login endpoint returned unexpected status: {response.status_code}")
    except Exception as e:
        print_error(f"Login endpoint error: {str(e)}")
        return False
    
    # Test register endpoint (expect 400 for missing data)
    try:
        response = requests.post(f"{BACKEND_URL}/auth/register", 
                               json={}, 
                               timeout=5)
        if response.status_code in [400, 422]:
            print_success("Register endpoint responding correctly")
        else:
            print_warning(f"Register endpoint returned unexpected status: {response.status_code}")
    except Exception as e:
        print_error(f"Register endpoint error: {str(e)}")
        return False
    
    return True

def test_file_endpoints():
    """Test file management endpoints"""
    print_header("FILE MANAGEMENT ENDPOINTS")
    
    # Test v1 upload endpoint
    try:
        response = requests.post(f"{BACKEND_URL}/api/upload-cv", 
                               files={},
                               timeout=5)
        if response.status_code in [400, 401]:
            print_success("V1 Upload endpoint responding")
        else:
            print_warning(f"V1 Upload returned: {response.status_code}")
    except Exception as e:
        print_error(f"V1 Upload error: {str(e)}")
    
    # Test v2 upload endpoint (NEW) - requires authentication
    try:
        response = requests.post(f"{BACKEND_URL}/api/v2/upload-cv-v2", 
                               files={},
                               timeout=5)
        # 401 = authentication required (correct behavior)
        if response.status_code == 401:
            print_success("V2 Upload endpoint (Enhanced) responding [auth required]")
        elif response.status_code == 400:
            print_success("V2 Upload endpoint responding [bad request]")
        else:
            print_warning(f"V2 Upload returned: {response.status_code}")
    except Exception as e:
        print_error(f"V2 Upload error: {str(e)}")
    
    return True

def test_chatbot_endpoints():
    """Test chatbot endpoints"""
    print_header("CHATBOT ENDPOINTS")
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/chatbot/ask", 
                               json={"message": "test"},
                               timeout=5)
        if response.status_code in [400, 401, 500]:
            print_success("Chatbot endpoint responding")
        else:
            print_warning(f"Chatbot returned: {response.status_code}")
    except Exception as e:
        print_error(f"Chatbot error: {str(e)}")
    
    return True

def test_frontend():
    """Test frontend server"""
    print_header("FRONTEND CHECK")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_success(f"Frontend is running on {FRONTEND_URL}")
            return True
        else:
            print_warning(f"Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Frontend is not running! Start it with: npm run dev")
        return False
    except Exception as e:
        print_error(f"Frontend error: {str(e)}")
        return False

def test_dependencies():
    """Test critical Python dependencies"""
    print_header("PYTHON DEPENDENCIES")
    
    deps = {
        'spacy': 'spaCy NLP',
        'PyPDF2': 'PDF Extraction',
        'pdfplumber': 'Advanced PDF',
        'docx': 'DOCX Processing',
        'jinja2': 'Template Engine',
        'fpdf': 'PDF Generation',
        'openai': 'OpenAI API (optional)',
        'google.generativeai': 'Google AI (optional)',
        'groq': 'Groq AI (optional)'
    }
    
    for module, name in deps.items():
        try:
            __import__(module)
            print_success(f"{name} available")
        except ImportError:
            if module in ['openai', 'google.generativeai', 'groq']:
                print_warning(f"{name} not installed (optional)")
            else:
                print_error(f"{name} missing! Install: pip install {module}")
    
    # Check spaCy model
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print_success(f"spaCy model loaded: {nlp.meta['name']} v{nlp.meta['version']}")
    except OSError:
        print_error("spaCy model not found! Run: python -m spacy download en_core_web_sm")
    
    return True

def test_services():
    """Test service layer availability"""
    print_header("SERVICE LAYER")
    
    try:
        from app.services.extraction_service import ExtractionService
        print_success("ExtractionService available")
    except Exception as e:
        print_error(f"ExtractionService error: {str(e)}")
    
    try:
        from app.services.validation_service import ValidationService
        print_success("ValidationService available")
    except Exception as e:
        print_error(f"ValidationService error: {str(e)}")
    
    try:
        from app.services.ai_service import AIService
        print_success("AIService available")
    except Exception as e:
        print_error(f"AIService error: {str(e)}")
    
    try:
        from app.services.cv_generation_service import CVGenerationService
        print_success("CVGenerationService available")
    except Exception as e:
        print_error(f"CVGenerationService error: {str(e)}")
    
    return True

def main():
    """Run all tests"""
    print(f"\n{Fore.MAGENTA}{'#'*70}")
    print(f"{Fore.MAGENTA}#{'PERFECTCV SYSTEM TEST':^68}#")
    print(f"{Fore.MAGENTA}{'#'*70}{Style.RESET_ALL}\n")
    
    results = {}
    
    # Test dependencies first
    results['dependencies'] = test_dependencies()
    
    # Test services
    results['services'] = test_services()
    
    # Test backend
    backend_ok, mongo_ok = test_backend_health()
    results['backend'] = backend_ok
    results['mongodb'] = mongo_ok
    
    if backend_ok:
        results['auth'] = test_auth_endpoints()
        results['files'] = test_file_endpoints()
        results['chatbot'] = test_chatbot_endpoints()
    else:
        print_warning("Skipping API tests (backend not running)")
        results['auth'] = False
        results['files'] = False
        results['chatbot'] = False
    
    # Test frontend
    results['frontend'] = test_frontend()
    
    # Summary
    print_header("SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for component, status in results.items():
        symbol = "✓" if status else "✗"
        color = Fore.GREEN if status else Fore.RED
        print(f"{color}{symbol} {component.replace('_', ' ').title()}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}Tests Passed: {passed}/{total}{Style.RESET_ALL}")
    
    if not results['backend']:
        print_info("\nStart backend: cd perfectcv-backend && python run.py")
    if not results['frontend']:
        print_info("Start frontend: cd perfectcv-frontend && npm run dev")
    if not results['mongodb']:
        print_warning("\nMongoDB connection issue - check MONGO_URI in .env")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
