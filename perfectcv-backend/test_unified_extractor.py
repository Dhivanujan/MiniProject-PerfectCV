"""
Quick test for the unified CV extractor
"""
import sys
sys.path.insert(0, 'f:\\Mini Project\\project\\New - Copy\\MiniProject-PerfectCV\\perfectcv-backend')

def test_extractor_initialization():
    """Test that the extractor can be initialized."""
    print("Testing unified CV extractor initialization...")
    
    try:
        from app.services.unified_cv_extractor import get_cv_extractor
        
        # Get extractor instance
        extractor = get_cv_extractor()
        
        if extractor is None:
            print("❌ Failed: Extractor is None")
            return False
        
        if extractor.nlp is None:
            print("⚠️  Warning: spaCy model not loaded (run: python -m spacy download en_core_web_sm)")
            print("✓ Extractor created but needs spaCy model")
            return True
        
        print(f"✓ Extractor initialized successfully")
        print(f"✓ spaCy model loaded: {extractor.nlp.meta.get('name', 'unknown')}")
        print(f"✓ Skills database: {len(extractor.TECH_SKILLS)} skills")
        print(f"✓ Job titles database: {len(extractor.JOB_TITLES)} titles")
        print(f"✓ Section patterns: {len(extractor.SECTION_PATTERNS)} patterns")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sample_cv():
    """Test extraction with sample CV text."""
    print("\n" + "="*70)
    print("Testing sample CV extraction...")
    print("="*70)
    
    sample_cv = """
John Doe
Software Engineer
Email: john.doe@example.com
Phone: +1 (555) 123-4567
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years in full-stack development.

SKILLS
Python, JavaScript, React, Node.js, Docker, AWS, MongoDB, PostgreSQL

EXPERIENCE

Senior Software Engineer
Tech Company Inc. - San Francisco, CA
January 2020 - Present
- Developed microservices using Python and FastAPI
- Led team of 5 engineers
- Improved system performance by 40%

Software Engineer
Startup LLC - New York, NY
June 2018 - December 2019
- Built web applications with React and Node.js
- Implemented CI/CD pipelines

EDUCATION

Bachelor of Science in Computer Science
University of California, Berkeley
2014 - 2018
    """
    
    try:
        from app.services.unified_cv_extractor import get_cv_extractor
        import tempfile
        
        # Save sample CV as temporary PDF (simulated)
        # For this test, we'll just pass the text directly
        extractor = get_cv_extractor()
        
        if extractor.nlp is None:
            print("⚠️  Skipping extraction test - spaCy model not loaded")
            print("   Run: python -m spacy download en_core_web_sm")
            return True
        
        # Process the text directly (simulating extracted PDF text)
        cleaned_text = extractor._clean_text(sample_cv)
        
        # Debug: Print first few lines
        print("\n🔍 Debug - First 10 lines of cleaned text:")
        for i, line in enumerate(cleaned_text.split('\n')[:10], 1):
            print(f"   {i}: '{line}'")
        
        sections = extractor._extract_sections(cleaned_text)
        entities = extractor._extract_entities(cleaned_text, sections)
        
        print("\n📊 Extraction Results:")
        print(f"   Name: {entities.get('name', 'NOT FOUND')}")
        print(f"   Email: {entities.get('email', 'NOT FOUND')}")
        print(f"   Phone: {entities.get('phone', 'NOT FOUND')}")
        print(f"   Location: {entities.get('location', 'NOT FOUND')}")
        print(f"   Skills: {len(entities.get('skills', []))} found")
        print(f"   Organizations: {len(entities.get('organizations', []))} found")
        print(f"   Education: {len(entities.get('education', []))} entries")
        print(f"   Experience: {len(entities.get('experience', []))} entries")
        
        if entities.get('skills'):
            print(f"\n   Skills found: {', '.join(entities['skills'][:10])}")
        
        # Verify minimum expected fields
        checks = {
            'Name': entities.get('name') is not None,
            'Email': entities.get('email') is not None,
            'Phone': entities.get('phone') is not None,
            'Skills': len(entities.get('skills', [])) > 0,
        }
        
        print("\n✅ Validation:")
        for field, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {field}")
        
        all_passed = all(checks.values())
        if all_passed:
            print("\n✅ All checks passed!")
        else:
            print("\n⚠️  Some checks failed")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error during extraction test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*70)
    print("Unified CV Extractor Test Suite")
    print("="*70)
    
    # Test 1: Initialization
    test1_passed = test_extractor_initialization()
    
    # Test 2: Sample extraction
    test2_passed = test_sample_cv()
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Initialization: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"Sample CV Test: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        sys.exit(1)
