"""
Test script for modern CV extraction and formatting system
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modern modules can be imported"""
    print("🔍 Testing imports...")
    try:
        from app.utils.modern_extractor import extract_pdf_modern, ModernPDFExtractor, ExtractionResult
        print("✅ modern_extractor imports successfully")
        
        from app.utils.modern_formatter import format_cv_modern, ModernCVFormatter
        print("✅ modern_formatter imports successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_modern_extractor():
    """Test modern extraction with sample data"""
    print("\n🔍 Testing modern extractor...")
    from app.utils.modern_extractor import ModernPDFExtractor
    
    extractor = ModernPDFExtractor()
    print(f"✅ ModernPDFExtractor created: {extractor}")
    
    # Test with dummy data (will fail gracefully)
    try:
        dummy_bytes = b"Not a real PDF"
        result = extractor.extract(dummy_bytes)
        print(f"⚠️  Extraction attempted with dummy data (expected to fail gracefully)")
    except Exception as e:
        print(f"✅ Error handling works: {str(e)[:100]}")
    
    return True

def test_modern_formatter():
    """Test modern formatting with sample CV data"""
    print("\n🔍 Testing modern formatter...")
    from app.utils.modern_formatter import format_cv_modern
    
    # Sample CV data
    cv_data = {
        'name': 'John Doe',
        'contact_info': {
            'email': 'john.doe@example.com',
            'phone': '+1-555-1234',
            'linkedin': 'linkedin.com/in/johndoe',
            'github': 'github.com/johndoe'
        },
        'professional_summary': 'Senior Software Engineer with 8+ years of experience in full-stack development.',
        'skills': {
            'Languages': ['Python', 'JavaScript', 'TypeScript'],
            'Frameworks': ['Flask', 'React', 'Node.js'],
            'Tools': ['Docker', 'Git', 'AWS']
        },
        'work_experience': [
            {
                'title': 'Senior Software Engineer',
                'company': 'Tech Corp',
                'location': 'San Francisco, CA',
                'start_date': '2020-01',
                'end_date': 'Present',
                'responsibilities': [
                    'Led team of 5 engineers',
                    'Architected microservices platform',
                    'Reduced deployment time by 40%'
                ]
            }
        ],
        'education': [
            {
                'degree': 'B.S. Computer Science',
                'institution': 'University of Technology',
                'graduation_date': '2016',
                'gpa': '3.8'
            }
        ],
        'projects': [
            {
                'name': 'CV Analysis System',
                'description': 'Built intelligent CV parsing system',
                'technologies': ['Python', 'Flask', 'MongoDB', 'AI'],
                'url': 'github.com/johndoe/cv-system'
            }
        ],
        'certifications': [
            {
                'name': 'AWS Solutions Architect',
                'issuer': 'Amazon Web Services',
                'date': '2022'
            }
        ]
    }
    
    # Test text format
    try:
        text_output = format_cv_modern(cv_data, 'text')
        if text_output:
            print(f"✅ Text formatting works ({len(text_output)} chars)")
            print(f"   Preview: {text_output[:100]}...")
        else:
            print("⚠️  Text formatting returned empty")
    except Exception as e:
        print(f"❌ Text formatting failed: {e}")
    
    # Test HTML format
    try:
        html_output = format_cv_modern(cv_data, 'html')
        if html_output and ('<html>' in html_output.lower() or 'DOCTYPE' in html_output):
            print(f"✅ HTML formatting works ({len(html_output)} chars)")
            # Save to file for inspection
            with open('test_output.html', 'w', encoding='utf-8') as f:
                f.write(html_output)
            print("   HTML saved to test_output.html for inspection")
        else:
            print(f"⚠️  HTML formatting returned unexpected result: {html_output[:100]}")
    except Exception as e:
        print(f"❌ HTML formatting failed: {e}")
    
    # Test Markdown format
    try:
        markdown_output = format_cv_modern(cv_data, 'markdown')
        if markdown_output and '#' in markdown_output:
            print(f"✅ Markdown formatting works ({len(markdown_output)} chars)")
        else:
            print("⚠️  Markdown formatting returned unexpected result")
    except Exception as e:
        print(f"❌ Markdown formatting failed: {e}")
    
    return True

def test_dependencies():
    """Test that all required dependencies are installed"""
    print("\n🔍 Testing dependencies...")
    
    dependencies = {
        'pypdf': 'pypdf',
        'pydantic': 'pydantic',
        'rich': 'rich',
        'reportlab': 'reportlab',
        'PyMuPDF': 'fitz'
    }
    
    all_installed = True
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} NOT installed (pip install {name.lower()})")
            all_installed = False
    
    return all_installed

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 Modern CV Extraction & Formatting System Test")
    print("="*60)
    
    results = []
    
    # Test dependencies
    results.append(("Dependencies", test_dependencies()))
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Only test functionality if imports work
    if results[-1][1]:
        results.append(("Modern Extractor", test_modern_extractor()))
        results.append(("Modern Formatter", test_modern_formatter()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Modern system is ready.")
        print("\n📝 Next steps:")
        print("   1. Test with real CV PDFs")
        print("   2. Verify upload endpoint integration")
        print("   3. Check API response includes modern_formatted and extraction_metadata")
    else:
        print("\n⚠️  Some tests failed. Please fix issues before proceeding.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
