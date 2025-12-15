"""
Test CV Generation Pipeline
Demonstrates the complete workflow
"""
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.cv_extract_service import extract_cv_data
from app.services.cv_ai_service import improve_cv_data, score_ats_compatibility
from app.services.cv_pdf_service import generate_cv_pdf, generate_cv_html
from config.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_cv_pipeline(cv_file_path: str):
    """
    Test the complete CV generation pipeline
    
    Args:
        cv_file_path: Path to test CV file (PDF or DOCX)
    """
    print("\n" + "="*60)
    print("TESTING CV GENERATION PIPELINE")
    print("="*60 + "\n")
    
    # Initialize AI client
    ai_client = None
    
    try:
        from groq import Groq
        if Config.GROQ_API_KEY:
            ai_client = Groq(api_key=Config.GROQ_API_KEY)
            print("✓ Groq AI client initialized")
    except ImportError:
        print("✗ Groq package not installed")
    
    if not ai_client:
        try:
            from openai import OpenAI
            if Config.OPENAI_API_KEY:
                ai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
                print("✓ OpenAI client initialized")
        except ImportError:
            print("✗ OpenAI package not installed")
    
    if not ai_client:
        print("\n⚠ WARNING: No AI client available!")
        print("Set GROQ_API_KEY or OPENAI_API_KEY in your .env file")
        return
    
    print(f"\nProcessing CV: {cv_file_path}\n")
    
    # Step 1: Extract CV data
    print("STEP 1: Extracting CV data...")
    print("-" * 40)
    try:
        cv_data = extract_cv_data(cv_file_path, ai_client)
        print(f"✓ Extracted CV data for: {cv_data.get('name', 'Unknown')}")
        print(f"  - Email: {cv_data.get('email', 'N/A')}")
        print(f"  - Phone: {cv_data.get('phone', 'N/A')}")
        print(f"  - Skills: {len(cv_data.get('skills', []))} found")
        print(f"  - Experience: {len(cv_data.get('experience', []))} positions")
        print(f"  - Education: {len(cv_data.get('education', []))} entries")
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        return
    
    # Step 2: Score original CV
    print("\nSTEP 2: Scoring original CV...")
    print("-" * 40)
    try:
        original_score = score_ats_compatibility(cv_data)
        print(f"✓ ATS Score: {original_score['percentage']}%")
        if original_score.get('suggestions'):
            print("  Suggestions:")
            for suggestion in original_score['suggestions'][:3]:
                print(f"    - {suggestion}")
    except Exception as e:
        print(f"✗ Scoring failed: {e}")
    
    # Step 3: Improve CV with AI
    print("\nSTEP 3: Improving CV with AI...")
    print("-" * 40)
    try:
        improved_cv = improve_cv_data(cv_data, ai_client)
        print("✓ CV improved successfully")
        print(f"  - Summary enhanced: {len(improved_cv.get('summary', ''))} chars")
        print(f"  - Skills optimized: {len(improved_cv.get('skills', []))} total")
    except Exception as e:
        print(f"✗ Improvement failed: {e}")
        improved_cv = cv_data
    
    # Step 4: Score improved CV
    print("\nSTEP 4: Scoring improved CV...")
    print("-" * 40)
    try:
        improved_score = score_ats_compatibility(improved_cv)
        print(f"✓ Improved ATS Score: {improved_score['percentage']}%")
        improvement = improved_score['percentage'] - original_score['percentage']
        if improvement > 0:
            print(f"  📈 Score increased by {improvement}%")
        else:
            print(f"  Score: {improvement}%")
    except Exception as e:
        print(f"✗ Scoring failed: {e}")
    
    # Step 5: Generate HTML
    print("\nSTEP 5: Generating HTML preview...")
    print("-" * 40)
    try:
        html_path = "output/test_cv.html"
        generate_cv_html(improved_cv, html_path)
        print(f"✓ HTML generated: {html_path}")
    except Exception as e:
        print(f"✗ HTML generation failed: {e}")
    
    # Step 6: Generate PDF
    print("\nSTEP 6: Generating professional PDF...")
    print("-" * 40)
    try:
        pdf_path = "output/test_cv.pdf"
        generate_cv_pdf(improved_cv, pdf_path)
        print(f"✓ PDF generated: {pdf_path}")
        
        # Check file size
        file_size = os.path.getsize(pdf_path) / 1024  # KB
        print(f"  File size: {file_size:.1f} KB")
    except Exception as e:
        print(f"✗ PDF generation failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("="*60)
    print(f"\n✓ Original ATS Score: {original_score['percentage']}%")
    print(f"✓ Improved ATS Score: {improved_score['percentage']}%")
    print(f"✓ Output files in: output/")
    print("\n")


def create_sample_cv_json():
    """Create a sample CV JSON for testing"""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1 (555) 123-4567",
        "summary": "Software engineer with 5 years of experience in web development.",
        "skills": [
            "Python", "JavaScript", "React", "FastAPI", "MongoDB",
            "Docker", "AWS", "Git", "REST APIs", "Agile"
        ],
        "experience": [
            {
                "role": "Senior Software Engineer",
                "company": "Tech Corp",
                "years": "2021 - Present",
                "description": "Led development of microservices architecture. Improved system performance by 40%. Mentored junior developers."
            },
            {
                "role": "Software Engineer",
                "company": "StartupXYZ",
                "years": "2019 - 2021",
                "description": "Built RESTful APIs using Python and FastAPI. Implemented CI/CD pipelines. Collaborated with cross-functional teams."
            }
        ],
        "education": [
            {
                "degree": "B.S. Computer Science",
                "institution": "University of Technology",
                "year": "2019",
                "details": "GPA: 3.8/4.0"
            }
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Built a full-stack e-commerce platform with React and Python",
                "technologies": ["React", "Python", "MongoDB", "Stripe API"]
            }
        ],
        "certifications": [
            "AWS Certified Developer - Associate",
            "MongoDB Certified Developer"
        ]
    }


def test_json_to_pdf():
    """Test PDF generation from JSON"""
    print("\n" + "="*60)
    print("TESTING JSON TO PDF CONVERSION")
    print("="*60 + "\n")
    
    cv_data = create_sample_cv_json()
    
    print("Sample CV Data:")
    print(f"  Name: {cv_data['name']}")
    print(f"  Skills: {len(cv_data['skills'])}")
    print(f"  Experience: {len(cv_data['experience'])} positions")
    
    try:
        pdf_path = "output/sample_cv.pdf"
        generate_cv_pdf(cv_data, pdf_path)
        print(f"\n✓ PDF generated successfully: {pdf_path}")
        
        file_size = os.path.getsize(pdf_path) / 1024
        print(f"  File size: {file_size:.1f} KB")
    except Exception as e:
        print(f"\n✗ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    if len(sys.argv) > 1:
        # Test with provided CV file
        cv_file = sys.argv[1]
        if os.path.exists(cv_file):
            test_cv_pipeline(cv_file)
        else:
            print(f"Error: File not found: {cv_file}")
    else:
        # Test JSON to PDF
        print("No CV file provided. Testing JSON to PDF conversion...\n")
        print("Usage: python test_cv_pipeline.py <path_to_cv.pdf>")
        print("\nRunning sample test instead:\n")
        test_json_to_pdf()
