"""
Test CV Generation with Jinja2 and WeasyPrint
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_cv_generation():
    """Test CV generation from extracted data."""
    print("=" * 70)
    print("CV Generation Test - Jinja2 + WeasyPrint")
    print("=" * 70)
    
    try:
        # Import services
        from app.services.unified_cv_extractor import get_cv_extractor
        from app.services.cv_generator import get_cv_generator, generate_cv_from_extraction
        
        # Sample CV data (simulating extraction result)
        sample_cv_text = """
John Doe
Software Engineer
Email: john.doe@example.com
Phone: +1 (555) 123-4567
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years in full-stack development.
Specialized in building scalable web applications and microservices architecture.

SKILLS
Python, JavaScript, React, Node.js, MongoDB, PostgreSQL, Docker, AWS, CI/CD, 
FastAPI, Microservices, Git, Linux, Agile, REST API

WORK EXPERIENCE

Senior Software Engineer
Tech Corp, San Francisco, CA
January 2020 - Present
- Led development of microservices architecture serving 1M+ users
- Mentored team of 5 junior developers
- Improved system performance by 40% through optimization
- Built web applications with React and Node.js
- Implemented CI/CD pipelines with GitHub Actions

Software Engineer
StartupXYZ, San Francisco, CA
June 2018 - December 2019
- Developed RESTful APIs using Python and FastAPI
- Built responsive frontend applications with React
- Managed MongoDB and PostgreSQL databases
- Collaborated with cross-functional teams

EDUCATION

Bachelor of Science in Computer Science
University of California, Berkeley
2014 - 2018
GPA: 3.8/4.0

CERTIFICATIONS
AWS Certified Solutions Architect
Certified Kubernetes Administrator (CKA)
        """
        
        print("\n✓ Imported services successfully")
        
        # Extract CV data
        print("\n📄 Extracting CV data...")
        extractor = get_cv_extractor()
        
        # Simulate PDF extraction by creating a temporary text file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_cv_text)
            temp_path = f.name
        
        # For testing, we'll manually create the extraction result
        # In production, this comes from extractor.extract_from_file()
        cleaned_text = extractor._clean_text(sample_cv_text)
        sections = extractor._extract_sections(cleaned_text)
        entities = extractor._extract_entities(cleaned_text, sections)
        
        extraction_result = {
            'entities': entities,
            'sections': sections,
            'cleaned_text': cleaned_text,
            'extraction_method': 'pdfplumber+Layout',
            'filename': 'sample_cv.pdf',
            'processed_at': '2026-01-22T23:45:00'
        }
        
        print(f"✓ Extracted data:")
        print(f"  - Name: {entities.get('name')}")
        print(f"  - Email: {entities.get('email')}")
        print(f"  - Phone: {entities.get('phone')}")
        print(f"  - Skills: {len(entities.get('skills', []))} found")
        print(f"  - Experience: {len(entities.get('experience', []))} entries")
        print(f"  - Education: {len(entities.get('education', []))} entries")
        
        # Generate CV
        print("\n🎨 Generating PDF CV...")
        generator = get_cv_generator()
        
        # List available templates
        templates = generator.list_available_templates()
        print(f"✓ Available templates: {', '.join(templates)}")
        
        # Generate PDF
        output_path = Path(__file__).parent / "output" / "generated_cv.pdf"
        pdf_bytes = generate_cv_from_extraction(
            extraction_result,
            template="modern_cv.html",
            output_path=output_path
        )
        
        print(f"\n✅ Success!")
        print(f"  - PDF size: {len(pdf_bytes):,} bytes")
        print(f"  - Saved to: {output_path}")
        print(f"  - Template: modern_cv.html")
        
        # Generate HTML preview
        print("\n📄 Generating HTML preview...")
        html_content = generator.generate_cv_html(extraction_result, "modern_cv.html")
        html_path = Path(__file__).parent / "output" / "generated_cv.html"
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html_content, encoding='utf-8')
        print(f"✓ HTML preview saved to: {html_path}")
        
        print("\n" + "=" * 70)
        print("🎉 CV Generation Test Passed!")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cv_generation()
    sys.exit(0 if success else 1)
