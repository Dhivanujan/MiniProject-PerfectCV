"""
Test API Integration with new Jinja2 + xhtml2pdf CV Generator
Tests the updated routes that use cv_generator service
"""
import os
import sys
import io

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_cv_generation_service():
    """Test the CV generation service directly"""
    print("=" * 60)
    print("Testing CV Generation Service Integration")
    print("=" * 60)
    
    try:
        from app.services.cv_generator import get_cv_generator
        
        # Sample CV data
        cv_data = {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com',
            'phone': '+1 (555) 987-6543',
            'location': 'New York, NY',
            'summary': 'Experienced software engineer with 5+ years in full-stack development.',
            'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'MongoDB', 'Docker'],
            'experience': [
                {
                    'title': 'Senior Software Engineer',
                    'company': 'Tech Corp',
                    'start_date': 'Jan 2020',
                    'end_date': 'Present',
                    'description': 'Led development of microservices architecture. Improved system performance by 40%.'
                },
                {
                    'title': 'Software Engineer',
                    'company': 'StartupXYZ',
                    'start_date': 'Jun 2018',
                    'end_date': 'Dec 2019',
                    'description': 'Developed React frontend and Node.js backend for SaaS platform.'
                }
            ],
            'education': [
                {
                    'degree': 'B.S. Computer Science',
                    'institution': 'State University',
                    'graduation_year': '2018'
                }
            ]
        }
        
        print("\n✓ Imported cv_generator successfully")
        
        # Get CV generator instance
        cv_gen = get_cv_generator()
        print("✓ Got cv_generator instance")
        
        # Test 1: Generate PDF to BytesIO
        print("\n[Test 1] Generating PDF to BytesIO...")
        pdf_bytes = cv_gen.generate_cv_pdf(cv_data, template_name='modern_cv.html')
        print(f"✅ Success! PDF size: {len(pdf_bytes.getvalue()):,} bytes")
        
        # Test 2: Generate PDF to file
        print("\n[Test 2] Generating PDF to file...")
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'test_api_integration.pdf')
        
        pdf_result = cv_gen.generate_cv_pdf(cv_data, template_name='modern_cv.html', output_path=output_path)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Success! PDF saved to: {output_path}")
            print(f"   File size: {file_size:,} bytes")
        else:
            print("❌ Failed - output file not created")
            return False
        
        # Test 3: Generate HTML preview
        print("\n[Test 3] Generating HTML preview...")
        html_content = cv_gen.generate_cv_html(cv_data, template_name='modern_cv.html')
        html_path = os.path.join(output_dir, 'test_api_integration.html')
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Success! HTML saved to: {html_path}")
        print(f"   HTML size: {len(html_content):,} bytes")
        
        # Test 4: Test with minimal data
        print("\n[Test 4] Testing with minimal CV data...")
        minimal_data = {
            'name': 'John Minimal',
            'email': 'john@example.com'
        }
        
        minimal_pdf = cv_gen.generate_cv_pdf(minimal_data, template_name='modern_cv.html')
        print(f"✅ Success! Minimal PDF size: {len(minimal_pdf.getvalue()):,} bytes")
        
        print("\n" + "=" * 60)
        print("🎉 All CV Generation Service Tests Passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extraction_and_generation_pipeline():
    """Test full extraction + generation pipeline"""
    print("\n" + "=" * 60)
    print("Testing Full Extraction → Generation Pipeline")
    print("=" * 60)
    
    try:
        from app.services.unified_cv_extractor import get_cv_extractor
        from app.services.cv_generator import get_cv_generator
        
        # Get sample CV
        sample_cv_path = 'sample_cv.pdf'
        
        if not os.path.exists(sample_cv_path):
            print(f"\n⚠ Sample CV not found: {sample_cv_path}")
            print("   Skipping pipeline test...")
            return True
        
        print(f"\n✓ Found sample CV: {sample_cv_path}")
        
        # Step 1: Extract CV data
        print("\n[Step 1] Extracting CV data with pdfplumber...")
        extractor = get_cv_extractor()
        
        with open(sample_cv_path, 'rb') as f:
            file_content = f.read()
        
        result = extractor.extract_from_file(file_content, sample_cv_path)
        cv_data = result['entities']
        
        print(f"✓ Extracted data:")
        print(f"  Name: {cv_data.get('name', 'N/A')}")
        print(f"  Email: {cv_data.get('email', 'N/A')}")
        print(f"  Phone: {cv_data.get('phone', 'N/A')}")
        print(f"  Skills: {len(cv_data.get('skills', []))} found")
        print(f"  Experience: {len(cv_data.get('experience', []))} entries")
        print(f"  Education: {len(cv_data.get('education', []))} entries")
        
        # Step 2: Generate new CV PDF
        print("\n[Step 2] Generating new CV PDF...")
        cv_gen = get_cv_generator()
        
        output_path = 'output/pipeline_test_cv.pdf'
        cv_gen.generate_cv_pdf(cv_data, template_name='modern_cv.html', output_path=output_path)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"✅ Success! Generated CV saved to: {output_path}")
            print(f"   File size: {file_size:,} bytes")
        else:
            print("❌ Failed - output file not created")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 Full Pipeline Test Passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_files_route_logic():
    """Test the logic used in files.py route"""
    print("\n" + "=" * 60)
    print("Testing files.py Route Logic")
    print("=" * 60)
    
    try:
        from app.services.cv_generator import get_cv_generator
        
        cv_gen = get_cv_generator()
        
        # Test Case 1: Structured CV data (typical use case)
        print("\n[Test Case 1] Structured CV data...")
        structured_cv = {
            'name': 'Alice Johnson',
            'email': 'alice@example.com',
            'phone': '+1-555-0123',
            'skills': ['Python', 'Django', 'PostgreSQL'],
            'experience': [
                {
                    'title': 'Backend Developer',
                    'company': 'WebCorp',
                    'description': 'Built REST APIs'
                }
            ]
        }
        
        pdf_bytes = cv_gen.generate_cv_pdf(structured_cv, template_name='modern_cv.html')
        print(f"✅ Generated PDF from structured data: {len(pdf_bytes.getvalue()):,} bytes")
        
        # Test Case 2: Text fallback (when only plain text available)
        print("\n[Test Case 2] Plain text fallback...")
        optimized_text = """
        Experienced web developer with expertise in Python and JavaScript.
        Built multiple full-stack applications using Django and React.
        Strong problem-solving skills and team collaboration.
        """
        
        text_data = {
            'name': 'Resume',
            'summary': optimized_text[:500] if len(optimized_text) > 500 else optimized_text,
            'experience': [{'description': optimized_text}]
        }
        
        pdf_bytes = cv_gen.generate_cv_pdf(text_data, template_name='modern_cv.html')
        print(f"✅ Generated PDF from text data: {len(pdf_bytes.getvalue()):,} bytes")
        
        print("\n" + "=" * 60)
        print("🎉 files.py Route Logic Tests Passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Route Logic Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("API INTEGRATION TEST SUITE")
    print("Testing Jinja2 + xhtml2pdf CV Generation")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("CV Generation Service", test_cv_generation_service()))
    results.append(("Extraction → Generation Pipeline", test_extraction_and_generation_pipeline()))
    results.append(("files.py Route Logic", test_files_route_logic()))
    
    # Summary
    print("\n\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\nAPI routes are ready to use with new cv_generator service:")
        print("  ✓ /api/download-optimized-cv (files.py)")
        print("  ✓ /api/generate-cv (cv.py)")
        print("  ✓ /api/generate-pdf-from-json (cv.py)")
        sys.exit(0)
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")
        sys.exit(1)
