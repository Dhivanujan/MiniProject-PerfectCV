"""
Test script to verify name extraction fixes.
Tests that technology names like "Spring Boot" and "React" are not identified as person names.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.cv_utils import extract_name_with_spacy, extract_contact_info
from app.utils.nlp_utils import extract_entities


def test_tech_term_filtering():
    """Test that tech terms are filtered from name extraction"""
    
    print("\n" + "="*80)
    print("Testing Name Extraction - Tech Term Filtering")
    print("="*80)
    
    # Test case 1: CV with name "Binoj Maduranga" but also mentions "Spring Boot"
    test_cv_1 = """
    Binoj Maduranga
    Email: binojmadhuranga@gmail.com
    Phone: +94 76 354 6936
    Location: Colombo, Sri Lanka
    
    Professional Summary:
    Experienced software developer with expertise in Spring Boot, React, and Angular.
    
    Skills:
    - Spring Boot
    - React
    - Java
    - Python
    """
    
    print("\n📄 Test Case 1: Real name with tech terms in skills")
    print("-" * 80)
    name = extract_name_with_spacy(test_cv_1)
    print(f"Extracted Name: '{name}'")
    
    if name.lower() == "binoj maduranga":
        print("✅ PASS: Correctly identified 'Binoj Maduranga' as the name")
    else:
        print(f"❌ FAIL: Expected 'Binoj Maduranga', got '{name}'")
    
    # Test case 2: CV where tech term appears first
    test_cv_2 = """
    Spring Boot Developer
    
    John Doe
    Email: john.doe@example.com
    Phone: +1 555 123 4567
    
    I am a Spring Boot expert with 5 years experience.
    """
    
    print("\n📄 Test Case 2: Tech term as job title, real name follows")
    print("-" * 80)
    name = extract_name_with_spacy(test_cv_2)
    print(f"Extracted Name: '{name}'")
    
    if name.lower() == "john doe":
        print("✅ PASS: Correctly identified 'John Doe' as the name")
    elif name.lower() == "spring boot":
        print(f"❌ FAIL: Incorrectly identified 'Spring Boot' as name instead of 'John Doe'")
    else:
        print(f"⚠️  WARNING: Got '{name}' instead of 'John Doe'")
    
    # Test case 3: Multiple candidates
    test_cv_3 = """
    React Developer
    
    Sarah Johnson
    sarah.johnson@email.com | +44 20 1234 5678
    London, UK
    
    Professional Experience:
    Senior React Developer at Tech Corp
    """
    
    print("\n📄 Test Case 3: Multiple PERSON entities")
    print("-" * 80)
    name = extract_name_with_spacy(test_cv_3)
    print(f"Extracted Name: '{name}'")
    
    if name.lower() == "sarah johnson":
        print("✅ PASS: Correctly identified 'Sarah Johnson' as the name")
    elif name.lower() == "react":
        print(f"❌ FAIL: Incorrectly identified 'React' as name")
    else:
        print(f"⚠️  Got '{name}'")


def test_location_filtering():
    """Test that tech terms are filtered from location extraction"""
    
    print("\n" + "="*80)
    print("Testing Location Extraction - Tech Term Filtering")
    print("="*80)
    
    test_cv = """
    Binoj Maduranga
    Email: binojmadhuranga@gmail.com
    Phone: +94 76 354 6936
    Location: Colombo, Sri Lanka
    
    Skills:
    - React
    - Spring Boot
    - Node.js
    """
    
    print("\n📄 Test: Location extraction with tech terms present")
    print("-" * 80)
    entities = extract_entities(test_cv[:500])
    
    print(f"Extracted GPE entities: {entities.get('GPE', [])}")
    
    if entities.get('GPE'):
        location = entities['GPE'][0] if entities['GPE'] else None
        if location and location.lower() not in ['react', 'spring boot', 'node']:
            print(f"✅ PASS: Extracted valid location '{location}'")
        else:
            print(f"❌ FAIL: Incorrectly identified tech term '{location}' as location")
    else:
        print("⚠️  No GPE entities extracted")


def test_full_contact_extraction():
    """Test full contact info extraction"""
    
    print("\n" + "="*80)
    print("Testing Full Contact Extraction")
    print("="*80)
    
    test_cv = """
    Binoj Maduranga
    Email: binojmadhuranga@gmail.com
    Phone: +94 76 354 6936
    Address: Colombo, Sri Lanka
    
    PROFESSIONAL SUMMARY
    Experienced Full Stack Developer with expertise in Spring Boot, React, 
    Angular, and Node.js. Passionate about building scalable applications.
    
    TECHNICAL SKILLS
    - Backend: Spring Boot, Django, Flask
    - Frontend: React, Angular, Vue.js
    - Database: MongoDB, MySQL, PostgreSQL
    """
    
    print("\n📄 Test: Complete contact info extraction")
    print("-" * 80)
    
    contact = extract_contact_info(test_cv)
    
    print(f"Name: '{contact.get('name', '')}'")
    print(f"Email: '{contact.get('email', '')}'")
    print(f"Phone: '{contact.get('phone', '')}'")
    print(f"Location: '{contact.get('location', '')}'")
    
    issues = []
    
    if contact.get('name', '').lower() == 'binoj maduranga':
        print("✅ Name is correct")
    elif contact.get('name', '').lower() in ['spring boot', 'react', 'angular', 'vue', 'node', 'django']:
        print(f"❌ FAIL: Name incorrectly identified as tech term: '{contact.get('name')}'")
        issues.append('name')
    else:
        print(f"⚠️  Name is '{contact.get('name', '')}' (expected 'Binoj Maduranga')")
    
    if contact.get('email') == 'binojmadhuranga@gmail.com':
        print("✅ Email is correct")
    else:
        print(f"⚠️  Email issue: '{contact.get('email', '')}'")
    
    if contact.get('phone'):
        print(f"✅ Phone extracted: '{contact.get('phone')}'")
    else:
        print("⚠️  Phone not extracted")
    
    if contact.get('location') and contact.get('location').lower() not in ['react', 'spring boot', 'node', 'angular']:
        print(f"✅ Location is valid: '{contact.get('location')}'")
    elif contact.get('location', '').lower() in ['react', 'spring boot', 'node', 'angular']:
        print(f"❌ FAIL: Location incorrectly identified as tech term: '{contact.get('location')}'")
        issues.append('location')
    
    if not issues:
        print("\n✅ ALL TESTS PASSED!")
    else:
        print(f"\n❌ FAILED: Issues with {', '.join(issues)}")


if __name__ == "__main__":
    try:
        print("\n🔧 Name Extraction Fix Verification Test")
        print("="*80)
        
        test_tech_term_filtering()
        test_location_filtering()
        test_full_contact_extraction()
        
        print("\n" + "="*80)
        print("✅ Test Suite Complete!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
