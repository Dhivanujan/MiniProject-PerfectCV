"""
Test PyMuPDF Layout Analysis Features
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.unified_cv_extractor import get_cv_extractor

def test_layout_analysis():
    """Test PyMuPDF layout analysis with a sample CV."""
    print("=" * 70)
    print("PyMuPDF Layout Analysis Test")
    print("=" * 70)
    
    # Sample CV content
    cv_content = """John Doe
Software Engineer
Email: john.doe@example.com
Phone: +1 (555) 123-4567
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years in full-stack development.

SKILLS
Python, JavaScript, React, Node.js, MongoDB, PostgreSQL, Docker, AWS, CI/CD, FastAPI, Microservices

WORK EXPERIENCE
Senior Software Engineer
Tech Corp, San Francisco, CA
January 2020 - Present
- Led development of microservices architecture
- Mentored junior developers
- Improved system performance by 40%

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley
2015 - 2019
"""
    
    # Create PDF from content
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    
    # Write content with different font sizes to simulate CV layout
    y_pos = 50
    
    # Name (large, bold)
    page.insert_text((50, y_pos), "John Doe", fontsize=18, fontname="helv")
    y_pos += 25
    
    # Title
    page.insert_text((50, y_pos), "Software Engineer", fontsize=12, fontname="helv")
    y_pos += 20
    
    # Contact info
    page.insert_text((50, y_pos), "Email: john.doe@example.com", fontsize=10)
    y_pos += 15
    page.insert_text((50, y_pos), "Phone: +1 (555) 123-4567", fontsize=10)
    y_pos += 15
    page.insert_text((50, y_pos), "Location: San Francisco, CA", fontsize=10)
    y_pos += 30
    
    # Section: Professional Summary
    page.insert_text((50, y_pos), "PROFESSIONAL SUMMARY", fontsize=14, fontname="helv")
    y_pos += 20
    page.insert_text((50, y_pos), "Experienced software engineer with 5+ years", fontsize=10)
    y_pos += 15
    page.insert_text((50, y_pos), "in full-stack development.", fontsize=10)
    y_pos += 30
    
    # Section: Skills
    page.insert_text((50, y_pos), "SKILLS", fontsize=14, fontname="helv")
    y_pos += 20
    page.insert_text((50, y_pos), "Python, JavaScript, React, Node.js, MongoDB,", fontsize=10)
    y_pos += 15
    page.insert_text((50, y_pos), "PostgreSQL, Docker, AWS, CI/CD, FastAPI", fontsize=10)
    y_pos += 30
    
    # Section: Work Experience
    page.insert_text((50, y_pos), "WORK EXPERIENCE", fontsize=14, fontname="helv")
    y_pos += 20
    page.insert_text((50, y_pos), "Senior Software Engineer", fontsize=11, fontname="helv")
    y_pos += 15
    page.insert_text((50, y_pos), "Tech Corp, San Francisco, CA", fontsize=10)
    y_pos += 15
    page.insert_text((50, y_pos), "January 2020 - Present", fontsize=10)
    y_pos += 15
    page.insert_text((50, y_pos), "- Led development of microservices", fontsize=10)
    y_pos += 15
    page.insert_text((50, y_pos), "- Mentored junior developers", fontsize=10)
    y_pos += 30
    
    # Section: Education
    page.insert_text((50, y_pos), "EDUCATION", fontsize=14, fontname="helv")
    y_pos += 20
    page.insert_text((50, y_pos), "Bachelor of Science in Computer Science", fontsize=11)
    y_pos += 15
    page.insert_text((50, y_pos), "University of California, Berkeley", fontsize=10)
    y_pos += 15
    page.insert_text((50, y_pos), "2015 - 2019", fontsize=10)
    
    # Save PDF to bytes
    pdf_bytes = doc.write()
    doc.close()
    
    # Initialize extractor
    print("\n✓ Created sample PDF with formatted layout")
    extractor = get_cv_extractor()
    print("✓ Initialized CV extractor")
    
    # Extract with layout analysis
    print("\n" + "=" * 70)
    print("Extracting with PyMuPDF Layout Analysis...")
    print("=" * 70)
    
    result = extractor.extract_from_file(pdf_bytes, "test_cv.pdf")
    
    # Display layout metadata
    print("\n📊 Layout Analysis Results:")
    print("-" * 70)
    
    layout_meta = result.get('layout_metadata', {})
    if layout_meta:
        print(f"✓ Layout analysis performed: {layout_meta.get('has_layout_analysis', False)}")
        print(f"✓ Headers detected: {layout_meta.get('headers_detected', 0)}")
        print(f"✓ Sections detected: {', '.join(layout_meta.get('sections_detected', []))}")
        print(f"✓ Contact blocks: {layout_meta.get('contact_blocks_count', 0)}")
        print(f"✓ Average font size: {layout_meta.get('avg_font_size', 0):.1f}pt")
    else:
        print("⚠ No layout metadata available")
    
    # Display extraction results
    entities = result.get('entities', {})
    print("\n📋 Extracted Entities:")
    print("-" * 70)
    print(f"Name: {entities.get('name', 'Not found')}")
    print(f"Email: {entities.get('email', 'Not found')}")
    print(f"Phone: {entities.get('phone', 'Not found')}")
    print(f"Location: {entities.get('location', 'Not found')}")
    print(f"Skills: {len(entities.get('skills', []))} found")
    print(f"Education: {len(entities.get('education', []))} entries")
    print(f"Experience: {len(entities.get('experience', []))} entries")
    
    # Validation
    print("\n✅ Validation:")
    print("-" * 70)
    
    checks = [
        ('Name extracted', entities.get('name') == 'John Doe'),
        ('Email extracted', entities.get('email') == 'john.doe@example.com'),
        ('Phone extracted', entities.get('phone') is not None),
        ('Layout analysis performed', layout_meta.get('has_layout_analysis', False)),
        ('Headers detected', layout_meta.get('headers_detected', 0) > 0),
        ('Contact blocks found', layout_meta.get('contact_blocks_count', 0) > 0),
    ]
    
    all_passed = True
    for check_name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 All layout analysis tests passed!")
    else:
        print("⚠ Some tests failed")
    print("=" * 70)
    
    return all_passed

if __name__ == "__main__":
    success = test_layout_analysis()
    sys.exit(0 if success else 1)
