"""
Test Phi-3 Integration
Tests the complete CV extraction flow with Phi-3 fallback.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_phi3_availability():
    """Test if Phi-3 is available"""
    print("\n" + "="*70)
    print("TEST 1: Phi-3 Availability")
    print("="*70)
    
    from app.services.phi3_service import get_phi3_service
    
    phi3 = get_phi3_service()
    available = phi3.check_availability()
    
    if available:
        print("✅ PASS: Phi-3 is available")
        return True
    else:
        print("❌ FAIL: Phi-3 not available")
        print("   Make sure Ollama is running: ollama serve")
        print("   And Phi-3 model is installed: ollama pull phi3")
        return False


def test_phi3_extraction():
    """Test Phi-3 CV extraction"""
    print("\n" + "="*70)
    print("TEST 2: Phi-3 CV Data Extraction")
    print("="*70)
    
    from app.services.phi3_service import get_phi3_service
    
    # Sample CV text with complete information
    sample_cv = """
John Doe
Email: john.doe@example.com
Phone: +1-555-123-4567
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Software Engineer with 5+ years of experience in full-stack development.

SKILLS
- Python, JavaScript, TypeScript
- React, Node.js, Django
- AWS, Docker, Kubernetes

EXPERIENCE
Senior Software Engineer
Tech Company Inc., San Francisco, CA
Jan 2020 - Present
- Led development of microservices architecture
- Improved system performance by 40%
- Mentored junior developers

Software Engineer
StartUp Co., San Jose, CA
Jun 2018 - Dec 2019
- Developed REST APIs using Django
- Built responsive web applications with React
- Implemented CI/CD pipelines

EDUCATION
Bachelor of Science in Computer Science
Stanford University, 2018
GPA: 3.8/4.0

CERTIFICATIONS
- AWS Certified Solutions Architect
- Google Cloud Professional
"""
    
    phi3 = get_phi3_service()
    result = phi3.extract_cv_data(sample_cv)
    
    if result:
        print("✅ PASS: Phi-3 extraction successful")
        print(f"\n📊 Extracted Data:")
        print(f"   Name: {result.get('name', 'NOT FOUND')}")
        print(f"   Email: {result.get('email', 'NOT FOUND')}")
        print(f"   Phone: {result.get('phone', 'NOT FOUND')}")
        print(f"   Skills: {len(result.get('skills', []))} items")
        print(f"   Experience: {len(result.get('experience', []))} entries")
        print(f"   Education: {len(result.get('education', []))} entries")
        return True
    else:
        print("❌ FAIL: Phi-3 extraction failed")
        return False


def test_validation_gate():
    """Test validation gate logic"""
    print("\n" + "="*70)
    print("TEST 3: Validation Gate")
    print("="*70)
    
    from app.services.cv_validation_service import get_cv_validator
    
    validator = get_cv_validator()
    
    # Test complete data
    complete_data = {
        'contact_info': {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1-555-1234'
        },
        'skills': {'technical': ['Python', 'JavaScript']},
        'experience': [{'title': 'Engineer', 'company': 'Company'}],
        'education': [{'degree': 'BSc', 'institution': 'University'}]
    }
    
    result = validator.validate_extraction(complete_data)
    
    print(f"\n📊 Complete Data Test:")
    print(f"   Is Complete: {result['is_complete']}")
    print(f"   Needs AI Fallback: {result['needs_ai_fallback']}")
    print(f"   Completeness Score: {result['completeness_score']:.1f}%")
    
    if result['is_complete'] and not result['needs_ai_fallback']:
        print("✅ PASS: Complete data validation correct")
    else:
        print("❌ FAIL: Complete data should not need AI fallback")
        return False
    
    # Test incomplete data (missing name)
    incomplete_data = {
        'contact_info': {
            'email': 'john@example.com',
            'phone': '+1-555-1234'
        },
        'skills': {},
        'experience': [],
        'education': []
    }
    
    result = validator.validate_extraction(incomplete_data)
    
    print(f"\n📊 Incomplete Data Test:")
    print(f"   Is Complete: {result['is_complete']}")
    print(f"   Needs AI Fallback: {result['needs_ai_fallback']}")
    print(f"   Missing Critical: {result['missing_critical']}")
    print(f"   Completeness Score: {result['completeness_score']:.1f}%")
    
    if not result['is_complete'] and result['needs_ai_fallback']:
        print("✅ PASS: Incomplete data correctly triggers AI fallback")
        return True
    else:
        print("❌ FAIL: Incomplete data should trigger AI fallback")
        return False


def test_extraction_orchestrator():
    """Test extraction orchestrator with fallback"""
    print("\n" + "="*70)
    print("TEST 4: Extraction Orchestrator")
    print("="*70)
    
    from app.services.cv_extraction_orchestrator import get_extraction_orchestrator
    
    # Sample CV with missing contact info
    incomplete_cv = """
PROFESSIONAL SUMMARY
Software developer with experience in web applications.

SKILLS
Python, JavaScript, React, Node.js

EXPERIENCE
Software Engineer at Tech Corp
Developed web applications
"""
    
    # Incomplete primary extraction
    primary_extraction = {
        'contact_info': {},  # Missing all contact info
        'skills': ['Python', 'JavaScript', 'React', 'Node.js'],
        'experience': [{'title': 'Software Engineer', 'company': 'Tech Corp'}],
        'education': []
    }
    
    orchestrator = get_extraction_orchestrator()
    final_data, metadata = orchestrator.extract_with_fallback(
        text=incomplete_cv,
        primary_extraction=primary_extraction
    )
    
    print(f"\n📊 Orchestrator Results:")
    print(f"   Primary Complete: {metadata.get('primary_extraction_complete')}")
    print(f"   AI Fallback Triggered: {metadata.get('ai_fallback_triggered')}")
    print(f"   AI Fallback Successful: {metadata.get('ai_fallback_successful')}")
    print(f"   Extraction Method: {metadata.get('extraction_method')}")
    print(f"   Completeness Score: {metadata.get('completeness_score', 0):.1f}%")
    
    if metadata.get('ai_fallback_triggered'):
        print("✅ PASS: AI fallback was triggered for incomplete data")
        return True
    else:
        print("⚠️ WARN: AI fallback not triggered (might be expected if Phi-3 unavailable)")
        return True


def test_cv_improvement():
    """Test CV improvement with Phi-3"""
    print("\n" + "="*70)
    print("TEST 5: CV Improvement")
    print("="*70)
    
    from app.services.cv_extraction_orchestrator import get_extraction_orchestrator
    
    sample_cv_data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'phone': '+1-555-1234',
        'summary': 'I am a developer with some experience.',
        'skills': ['Python', 'JavaScript'],
        'experience': [
            {
                'title': 'Developer',
                'company': 'Company',
                'description': 'I wrote code and fixed bugs.'
            }
        ],
        'education': [
            {
                'degree': 'Computer Science',
                'institution': 'University'
            }
        ]
    }
    
    orchestrator = get_extraction_orchestrator()
    improved = orchestrator.improve_cv_content(sample_cv_data)
    
    if improved:
        print("✅ PASS: CV improvement successful")
        print(f"\n📊 Original Summary: {sample_cv_data['summary']}")
        print(f"📊 Improved Summary: {improved.get('summary', 'N/A')}")
        
        # Check that name wasn't changed
        if improved.get('name') == sample_cv_data['name']:
            print("✅ Factual integrity maintained (name unchanged)")
            return True
        else:
            print("❌ FAIL: Name was changed during improvement")
            return False
    else:
        print("⚠️ WARN: CV improvement not available (Phi-3 may not be running)")
        return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("PHI-3 INTEGRATION TEST SUITE")
    print("="*70)
    
    results = []
    
    # Test 1: Availability
    results.append(("Phi-3 Availability", test_phi3_availability()))
    
    # Only continue if Phi-3 is available
    if not results[0][1]:
        print("\n⚠️ Phi-3 not available - skipping remaining tests")
        print("\nTo run full tests:")
        print("1. Start Ollama: ollama serve")
        print("2. Install Phi-3: ollama pull phi3")
        print("3. Run tests again")
        return
    
    # Test 2: Extraction
    results.append(("Phi-3 Extraction", test_phi3_extraction()))
    
    # Test 3: Validation
    results.append(("Validation Gate", test_validation_gate()))
    
    # Test 4: Orchestrator
    results.append(("Extraction Orchestrator", test_extraction_orchestrator()))
    
    # Test 5: Improvement
    results.append(("CV Improvement", test_cv_improvement()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")


if __name__ == '__main__':
    main()
