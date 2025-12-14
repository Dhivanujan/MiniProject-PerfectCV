"""
Quick test to verify name extraction fixes
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_name_extraction():
    """Test name extraction from various CV data structures"""
    from app.utils.cv_template_mapper import normalize_cv_for_template
    
    print("="*60)
    print("Testing Name Extraction")
    print("="*60)
    
    # Test Case 1: Name in Personal Information
    test_data_1 = {
        "Personal Information": {
            "name": "John Smith",
            "email": "john@example.com",
            "phone": "+1-555-1234"
        }
    }
    result1 = normalize_cv_for_template(test_data_1)
    print(f"\nTest 1 - Personal Information:")
    print(f"  Input name: {test_data_1['Personal Information']['name']}")
    print(f"  Output name: '{result1['name']}'")
    print(f"  ✓ PASS" if result1['name'] == "John Smith" else f"  ✗ FAIL")
    
    # Test Case 2: Name at root level
    test_data_2 = {
        "name": "Jane Doe",
        "email": "jane@example.com"
    }
    result2 = normalize_cv_for_template(test_data_2)
    print(f"\nTest 2 - Root level:")
    print(f"  Input name: {test_data_2['name']}")
    print(f"  Output name: '{result2['name']}'")
    print(f"  ✓ PASS" if result2['name'] == "Jane Doe" else f"  ✗ FAIL")
    
    # Test Case 3: Full name variant
    test_data_3 = {
        "Personal Information": {
            "full_name": "Alice Johnson",
            "email": "alice@example.com"
        }
    }
    result3 = normalize_cv_for_template(test_data_3)
    print(f"\nTest 3 - Full name variant:")
    print(f"  Input name: {test_data_3['Personal Information']['full_name']}")
    print(f"  Output name: '{result3['name']}'")
    print(f"  ✓ PASS" if result3['name'] == "Alice Johnson" else f"  ✗ FAIL")
    
    # Test Case 4: Contact information variant
    test_data_4 = {
        "contact_information": {
            "name": "Bob Williams",
            "email": "bob@example.com"
        }
    }
    result4 = normalize_cv_for_template(test_data_4)
    print(f"\nTest 4 - Contact information:")
    print(f"  Input name: {test_data_4['contact_information']['name']}")
    print(f"  Output name: '{result4['name']}'")
    print(f"  ✓ PASS" if result4['name'] == "Bob Williams" else f"  ✗ FAIL")
    
    # Test Case 5: Single word name (international)
    test_data_5 = {
        "Personal Information": {
            "name": "Krishna",
            "email": "krishna@example.com"
        }
    }
    result5 = normalize_cv_for_template(test_data_5)
    print(f"\nTest 5 - Single word name:")
    print(f"  Input name: {test_data_5['Personal Information']['name']}")
    print(f"  Output name: '{result5['name']}'")
    print(f"  ✓ PASS" if result5['name'] == "Krishna" else f"  ✗ FAIL")
    
    print("\n" + "="*60)
    print("Name Extraction Tests Complete")
    print("="*60)


def test_pdf_generation():
    """Test PDF generation with name"""
    from app.utils.cv_templates import build_professional_cv_html
    
    print("\n" + "="*60)
    print("Testing PDF HTML Generation")
    print("="*60)
    
    # Test with Personal Information
    test_data = {
        "Personal Information": {
            "name": "Sarah Connor",
            "email": "sarah@example.com",
            "phone": "+1-555-9999"
        },
        "professional_summary": "Experienced professional"
    }
    
    html = build_professional_cv_html(test_data)
    
    if "Sarah Connor" in html:
        print("\n✓ PASS: Name appears in generated HTML")
        print(f"  Name found in HTML: 'Sarah Connor'")
    else:
        print("\n✗ FAIL: Name NOT found in generated HTML")
        print(f"  HTML preview: {html[:500]}")
    
    print("="*60)


if __name__ == "__main__":
    try:
        test_name_extraction()
        test_pdf_generation()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
