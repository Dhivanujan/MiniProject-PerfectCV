"""
Demo: PyMuPDF Layout Analysis Features
Shows how the CV extractor identifies components using layout information
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.unified_cv_extractor import get_cv_extractor
import fitz

def create_demo_cv():
    """Create a demo CV with various formatting."""
    doc = fitz.open()
    page = doc.new_page()
    y = 50
    
    # Name - Large font
    page.insert_text((50, y), "Jane Smith", fontsize=20)
    y += 30
    
    # Title - Medium font
    page.insert_text((50, y), "Senior Data Scientist", fontsize=13)
    y += 25
    
    # Contact - Small font
    page.insert_text((50, y), "jane.smith@email.com | +1-555-987-6543", fontsize=10)
    y += 20
    page.insert_text((50, y), "New York, NY", fontsize=10)
    y += 35
    
    # Section: SUMMARY (All caps, medium)
    page.insert_text((50, y), "PROFESSIONAL SUMMARY", fontsize=14)
    y += 20
    page.insert_text((50, y), "Data scientist with 7+ years experience in ML", fontsize=10)
    y += 15
    page.insert_text((50, y), "and statistical analysis.", fontsize=10)
    y += 30
    
    # Section: SKILLS (All caps, medium)
    page.insert_text((50, y), "TECHNICAL SKILLS", fontsize=14)
    y += 20
    page.insert_text((50, y), "Python, TensorFlow, PyTorch, Scikit-learn, R", fontsize=10)
    y += 15
    page.insert_text((50, y), "SQL, MongoDB, Docker, AWS, Azure", fontsize=10)
    y += 30
    
    # Section: EXPERIENCE
    page.insert_text((50, y), "WORK EXPERIENCE", fontsize=14)
    y += 20
    page.insert_text((50, y), "Lead Data Scientist", fontsize=11)
    y += 15
    page.insert_text((50, y), "DataCorp Inc., New York | 2020 - Present", fontsize=10)
    y += 15
    page.insert_text((50, y), "• Built ML models improving accuracy by 35%", fontsize=10)
    y += 15
    page.insert_text((50, y), "• Led team of 5 data scientists", fontsize=10)
    y += 30
    
    # Section: EDUCATION
    page.insert_text((50, y), "EDUCATION", fontsize=14)
    y += 20
    page.insert_text((50, y), "Ph.D. in Statistics", fontsize=11)
    y += 15
    page.insert_text((50, y), "Stanford University | 2015 - 2019", fontsize=10)
    
    return doc.write()

def main():
    print("=" * 80)
    print("PyMuPDF Layout Analysis Demo")
    print("=" * 80)
    
    # Create demo CV
    print("\n📄 Creating demo CV with formatted layout...")
    cv_bytes = create_demo_cv()
    print("✓ Demo CV created")
    
    # Extract with layout analysis
    print("\n🔍 Extracting CV with PyMuPDF layout analysis...")
    extractor = get_cv_extractor()
    result = extractor.extract_from_file(cv_bytes, "demo_cv.pdf")
    
    # Display layout analysis details
    print("\n" + "=" * 80)
    print("Layout Analysis Results")
    print("=" * 80)
    
    layout_meta = result.get('layout_metadata', {})
    
    print("\n📊 Document Structure:")
    print(f"  • Extraction Method: {result.get('extraction_method')}")
    print(f"  • Layout Analysis: {layout_meta.get('has_layout_analysis', False)}")
    print(f"  • Headers Detected: {layout_meta.get('headers_detected', 0)}")
    print(f"  • Contact Blocks: {layout_meta.get('contact_blocks_count', 0)}")
    print(f"  • Average Font Size: {layout_meta.get('avg_font_size', 0):.1f}pt")
    
    print("\n📑 Sections Detected:")
    sections_found = layout_meta.get('sections_detected', [])
    for section in sections_found:
        print(f"  • {section.upper()}")
    
    # Display extracted entities
    entities = result.get('entities', {})
    
    print("\n" + "=" * 80)
    print("Extracted Information")
    print("=" * 80)
    
    print("\n👤 Personal Information:")
    print(f"  Name: {entities.get('name', 'Not found')}")
    print(f"  Email: {entities.get('email', 'Not found')}")
    print(f"  Phone: {entities.get('phone', 'Not found')}")
    print(f"  Location: {entities.get('location', 'Not found')}")
    
    print("\n🎯 Skills:")
    skills = entities.get('skills', [])
    if skills:
        print(f"  Found {len(skills)} skills:")
        for skill in skills[:10]:  # Show first 10
            print(f"    • {skill}")
        if len(skills) > 10:
            print(f"    ... and {len(skills) - 10} more")
    else:
        print("  No skills detected")
    
    print("\n💼 Experience:")
    experience = entities.get('experience', [])
    if experience:
        for exp in experience:
            print(f"  • {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}")
            print(f"    Duration: {exp.get('duration', 'Not specified')}")
    else:
        print("  No experience entries detected")
    
    print("\n🎓 Education:")
    education = entities.get('education', [])
    if education:
        for edu in education:
            print(f"  • {edu.get('degree', 'Unknown')} from {edu.get('institution', 'Unknown')}")
            if edu.get('year'):
                print(f"    Year: {edu.get('year')}")
    else:
        print("  No education entries detected")
    
    print("\n" + "=" * 80)
    print("Layout Analysis Benefits")
    print("=" * 80)
    
    print("""
✨ How PyMuPDF Layout Analysis Helps:

1. Smart Name Detection
   • Identifies largest text at top of CV
   • Filters out job titles and contact info
   • Uses font size and position as primary indicators

2. Section Recognition
   • Detects headers by font size, bold style, or all-caps
   • Groups content under appropriate sections
   • Works across different CV formats

3. Contact Information
   • Prioritizes top 20% of first page
   • Uses visual positioning, not just keywords
   • More accurate than text-only approaches

4. Document Structure
   • Understands visual hierarchy
   • Preserves logical flow
   • Adapts to various layouts

5. Metadata Rich
   • Provides debugging insights
   • Enables quality scoring
   • Supports analytics
    """)
    
    print("=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
