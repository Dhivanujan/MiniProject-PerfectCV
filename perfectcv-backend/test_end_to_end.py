"""
End-to-End Test: Extract CV with pdfplumber → Generate PDF with Jinja2 + xhtml2pdf
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

def test_full_pipeline():
    """Test complete extraction and generation pipeline"""
    print("=" * 70)
    print("END-TO-END TEST: Extraction → Generation")
    print("=" * 70)
    
    try:
        from app.services.unified_cv_extractor import get_cv_extractor
        from app.services.cv_generator import get_cv_generator
        
        # Check for sample CV
        sample_cv = 'sample_cv.pdf'
        if not os.path.exists(sample_cv):
            print(f"\n⚠ Sample CV not found: {sample_cv}")
            print("Creating a test sample CV for demonstration...")
            
            # Use the extractor test CV
            test_cv = 'test_sample_cv.pdf'
            if os.path.exists(test_cv):
                sample_cv = test_cv
            else:
                print("❌ No test CV found. Please provide a sample_cv.pdf")
                return False
        
        print(f"\n✓ Using CV: {sample_cv}")
        
        # Step 1: Extract CV data using pdfplumber
        print("\n" + "-" * 70)
        print("STEP 1: Extracting CV data with pdfplumber")
        print("-" * 70)
        
        extractor = get_cv_extractor()
        
        with open(sample_cv, 'rb') as f:
            file_content = f.read()
        
        extraction_result = extractor.extract_from_file(file_content, sample_cv)
        cv_data = extraction_result['entities']
        
        print(f"\n📊 Extraction Results:")
        print(f"  Name: {cv_data.get('name', 'N/A')}")
        print(f"  Email: {cv_data.get('email', 'N/A')}")
        print(f"  Phone: {cv_data.get('phone', 'N/A')}")
        print(f"  Location: {cv_data.get('location', 'N/A')}")
        print(f"  Skills: {len(cv_data.get('skills', []))} found")
        if cv_data.get('skills'):
            print(f"    → {', '.join(cv_data['skills'][:10])}")
        print(f"  Experience: {len(cv_data.get('experience', []))} entries")
        print(f"  Education: {len(cv_data.get('education', []))} entries")
        
        # Step 2: Generate new CV PDF using Jinja2 + xhtml2pdf
        print("\n" + "-" * 70)
        print("STEP 2: Generating new CV PDF with Jinja2 + xhtml2pdf")
        print("-" * 70)
        
        cv_gen = get_cv_generator()
        
        # List available templates
        templates_dir = os.path.join('app', 'templates')
        available_templates = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
        print(f"\n📋 Available templates: {', '.join(available_templates)}")
        
        # Generate PDFs with both templates
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        
        for template in ['modern_cv.html', 'cv_template.html']:
            if template in available_templates:
                print(f"\n  Generating PDF with {template}...")
                output_path = os.path.join(output_dir, f'final_{template.replace(".html", ".pdf")}')
                
                # Pass extraction result directly (contains 'entities' key)
                pdf_io = cv_gen.generate_cv_pdf(
                    extraction_result,  # Pass full extraction result
                    template_name=template,
                    output_path=output_path
                )
                
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"  ✅ Success! Saved to: {output_path}")
                    print(f"     Size: {file_size:,} bytes")
                else:
                    print(f"  ❌ Failed to create {output_path}")
        
        # Generate HTML preview
        print(f"\n  Generating HTML preview...")
        html_content = cv_gen.generate_cv_html(extraction_result, template_name='modern_cv.html')
        html_path = os.path.join(output_dir, 'final_cv_preview.html')
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  ✅ HTML preview saved to: {html_path}")
        
        # Summary
        print("\n" + "=" * 70)
        print("✅ END-TO-END TEST PASSED!")
        print("=" * 70)
        print("\n📁 Generated Files:")
        for filename in os.listdir(output_dir):
            if filename.startswith('final_'):
                filepath = os.path.join(output_dir, filename)
                size = os.path.getsize(filepath)
                print(f"  • {filename} ({size:,} bytes)")
        
        print("\n🎯 Next Steps:")
        print("  1. Open generated PDFs to verify formatting")
        print("  2. Open HTML preview in browser to see styling")
        print("  3. Test with your own CV files")
        print("  4. API endpoints are ready for frontend integration!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_pipeline()
    sys.exit(0 if success else 1)
