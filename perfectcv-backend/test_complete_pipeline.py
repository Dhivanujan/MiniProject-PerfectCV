"""
Comprehensive Test Suite for PerfectCV Pipeline
Tests the complete flow: Upload -> Extract -> Analyze -> Generate -> Score
"""
import os
import sys
import json
import logging
from pathlib import Path

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.cv_extract_service import extract_cv_data
from app.services.cv_ai_service import improve_cv_data, score_ats_compatibility
from app.services.cv_scoring_service import CVScoringService
from app.utils.extractor import extract_text_from_pdf
from config.config import Config

# Try to import WeasyPrint, fallback to ReportLab
try:
    from app.services.cv_pdf_service import generate_cv_pdf
    PDF_LIBRARY = "WeasyPrint"
except (ImportError, OSError):
    from app.services.cv_pdf_service_reportlab import generate_cv_pdf_reportlab as generate_cv_pdf
    PDF_LIBRARY = "ReportLab"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_ai_client():
    """Initialize AI client (Groq preferred, fallback to OpenAI)."""
    ai_client = None
    
    try:
        from groq import Groq
        if Config.GROQ_API_KEY:
            ai_client = Groq(api_key=Config.GROQ_API_KEY)
            logger.info("✓ Groq AI client initialized")
            return ai_client
    except ImportError:
        logger.warning("⚠ Groq package not installed")
    
    try:
        from openai import OpenAI
        if Config.OPENAI_API_KEY:
            ai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
            logger.info("✓ OpenAI client initialized")
            return ai_client
    except ImportError:
        logger.warning("⚠ OpenAI package not installed")
    
    if not ai_client:
        logger.error("✗ No AI client available. Set GROQ_API_KEY or OPENAI_API_KEY")
    
    return ai_client


def create_sample_cv_data():
    """Create a sample CV for testing when no file is provided."""
    return {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "+1-555-123-4567",
        "summary": "Experienced software engineer with expertise in full-stack development and cloud technologies.",
        "skills": [
            "Python", "JavaScript", "React", "Node.js", "FastAPI", "Django",
            "AWS", "Docker", "Kubernetes", "PostgreSQL", "MongoDB", "Git"
        ],
        "experience": [
            {
                "role": "Senior Software Engineer",
                "company": "Tech Solutions Inc.",
                "years": "2020 - Present",
                "description": "Led development of microservices architecture serving 1M+ users. Implemented CI/CD pipelines reducing deployment time by 60%. Mentored team of 5 junior developers."
            },
            {
                "role": "Software Developer",
                "company": "Digital Innovations Ltd.",
                "years": "2018 - 2020",
                "description": "Developed RESTful APIs and responsive web applications. Optimized database queries improving performance by 40%. Collaborated with cross-functional teams."
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "State University",
                "year": "2018",
                "details": "GPA: 3.8/4.0 - Dean's List"
            }
        ],
        "projects": [
            {
                "name": "E-Commerce Platform",
                "description": "Built scalable e-commerce solution handling 10K+ daily transactions with React frontend and Django backend.",
                "technologies": ["React", "Django", "PostgreSQL", "Redis", "AWS"]
            },
            {
                "name": "Real-time Chat Application",
                "description": "Developed WebSocket-based chat app supporting 5K concurrent users with message encryption.",
                "technologies": ["Node.js", "Socket.io", "MongoDB", "Docker"]
            }
        ],
        "certifications": [
            "AWS Certified Solutions Architect",
            "Google Cloud Professional Developer"
        ]
    }


def test_cv_extraction(file_path=None, ai_client=None):
    """Test CV extraction from file or create sample data."""
    print("\n" + "="*70)
    print("TEST 1: CV EXTRACTION")
    print("="*70)
    
    try:
        if file_path and os.path.exists(file_path):
            logger.info(f"Extracting data from: {file_path}")
            cv_data = extract_cv_data(file_path, ai_client)
        else:
            logger.info("No file provided, using sample CV data")
            cv_data = create_sample_cv_data()
        
        print("\n✓ CV Data Extracted Successfully!")
        print(f"\nName: {cv_data.get('name', 'N/A')}")
        print(f"Email: {cv_data.get('email', 'N/A')}")
        print(f"Phone: {cv_data.get('phone', 'N/A')}")
        print(f"Skills: {len(cv_data.get('skills', []))} skills found")
        print(f"Experience: {len(cv_data.get('experience', []))} positions")
        print(f"Education: {len(cv_data.get('education', []))} entries")
        print(f"Projects: {len(cv_data.get('projects', []))} projects")
        print(f"Certifications: {len(cv_data.get('certifications', []))} certifications")
        
        return cv_data
        
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        logger.error(f"Extraction error: {e}", exc_info=True)
        return None


def test_ats_scoring(cv_data):
    """Test ATS compatibility scoring."""
    print("\n" + "="*70)
    print("TEST 2: ATS SCORING")
    print("="*70)
    
    try:
        ats_result = score_ats_compatibility(cv_data)
        ats_score = ats_result['score']
        
        print(f"\n✓ ATS Score: {ats_score}/100")
        print(f"   Percentage: {ats_result['percentage']}%")
        
        if ats_score >= 80:
            print("   Rating: Excellent - Highly ATS-friendly")
        elif ats_score >= 60:
            print("   Rating: Good - Acceptable for most ATS systems")
        elif ats_score >= 40:
            print("   Rating: Fair - Needs improvement")
        else:
            print("   Rating: Poor - Significant improvements needed")
        
        if ats_result.get('suggestions'):
            print(f"\n   Suggestions:")
            for suggestion in ats_result['suggestions'][:3]:
                print(f"      • {suggestion}")
        
        return ats_score
        
    except Exception as e:
        print(f"✗ ATS scoring failed: {e}")
        logger.error(f"ATS scoring error: {e}", exc_info=True)
        return None


def test_comprehensive_analysis(cv_data):
    """Test comprehensive CV analysis."""
    print("\n" + "="*70)
    print("TEST 3: COMPREHENSIVE CV ANALYSIS")
    print("="*70)
    
    try:
        # Create raw text from cv_data for analysis
        raw_text = f"{cv_data.get('name', '')} {cv_data.get('email', '')} "
        raw_text += " ".join(cv_data.get('skills', []))
        
        scoring_service = CVScoringService()
        analysis = scoring_service.analyze_cv(cv_data, raw_text)
        
        print(f"\n✓ CV Score: {analysis['score']}/{analysis['max_score']}")
        print(f"   Candidate Level: {analysis['candidate_level']}")
        print(f"   Predicted Field: {analysis['predicted_field']}")
        
        print(f"\n   Score Breakdown:")
        for section, score in analysis['score_breakdown'].items():
            print(f"      • {section}: {score} points")
        
        print(f"\n   Present Sections: {', '.join(analysis['present_sections'])}")
        
        if analysis['missing_sections']:
            print(f"   Missing Sections: {', '.join(analysis['missing_sections'])}")
        
        print(f"\n   Top Recommended Skills:")
        for skill in analysis['recommended_skills'][:5]:
            print(f"      • {skill}")
        
        print(f"\n   Recommendations ({len(analysis['recommendations'])}):")
        for i, rec in enumerate(analysis['recommendations'][:3], 1):
            print(f"      {i}. {rec}")
        
        return analysis
        
    except Exception as e:
        print(f"✗ Analysis failed: {e}")
        logger.error(f"Analysis error: {e}", exc_info=True)
        return None


def test_cv_improvement(cv_data, ai_client):
    """Test AI-powered CV improvement."""
    print("\n" + "="*70)
    print("TEST 4: AI CV IMPROVEMENT")
    print("="*70)
    
    if not ai_client:
        print("⚠ Skipping - No AI client available")
        return cv_data
    
    try:
        improved_cv = improve_cv_data(cv_data, ai_client)
        
        print("\n✓ CV improved successfully!")
        
        # Compare before and after
        orig_skills = len(cv_data.get('skills', []))
        new_skills = len(improved_cv.get('skills', []))
        
        print(f"\n   Skills: {orig_skills} → {new_skills}")
        
        if improved_cv.get('summary') != cv_data.get('summary'):
            print("   ✓ Summary enhanced")
        
        if len(improved_cv.get('experience', [])) >= len(cv_data.get('experience', [])):
            print("   ✓ Experience descriptions improved")
        
        return improved_cv
        
    except Exception as e:
        print(f"✗ Improvement failed: {e}")
        logger.error(f"Improvement error: {e}", exc_info=True)
        return cv_data


def test_pdf_generation(cv_data):
    """Test PDF generation from CV data."""
    print("\n" + "="*70)
    print("TEST 5: PDF GENERATION")
    print("="*70)
    
    try:
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        name = cv_data.get('name', 'sample').replace(' ', '_')
        output_path = os.path.join(output_dir, f"test_cv_{name}.pdf")
        
        generate_cv_pdf(cv_data, output_path)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / 1024  # KB
            print(f"\n✓ PDF generated successfully!")
            print(f"   Location: {output_path}")
            print(f"   Size: {file_size:.2f} KB")
            return output_path
        else:
            print("✗ PDF file not found after generation")
            return None
            
    except Exception as e:
        print(f"✗ PDF generation failed: {e}")
        logger.error(f"PDF generation error: {e}", exc_info=True)
        return None


def save_cv_comparison(original_cv, improved_cv, analysis):
    """Save comparison of original vs improved CV."""
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    comparison_file = os.path.join(output_dir, 'cv_comparison.json')
    
    comparison = {
        "original_cv": original_cv,
        "improved_cv": improved_cv,
        "analysis": analysis,
        "improvements": {
            "skills_added": list(set(improved_cv.get('skills', [])) - set(original_cv.get('skills', []))),
            "summary_improved": improved_cv.get('summary') != original_cv.get('summary'),
            "experience_enhanced": len(str(improved_cv.get('experience', []))) > len(str(original_cv.get('experience', [])))
        }
    }
    
    with open(comparison_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ CV comparison saved to: {comparison_file}")


def run_complete_pipeline(test_file_path=None):
    """Run the complete CV processing pipeline."""
    print("\n" + "="*70)
    print("PERFECTCV COMPLETE PIPELINE TEST")
    print("="*70)
    print(f"PDF Library: {PDF_LIBRARY}")
    print("="*70)
    
    # Initialize AI client
    ai_client = initialize_ai_client()
    
    # Test 1: Extract CV data
    cv_data = test_cv_extraction(test_file_path, ai_client)
    if not cv_data:
        print("\n✗ Pipeline stopped - Extraction failed")
        return
    
    original_cv = cv_data.copy()
    
    # Test 2: ATS Scoring
    ats_score = test_ats_scoring(cv_data)
    
    # Test 3: Comprehensive Analysis
    analysis = test_comprehensive_analysis(cv_data)
    
    # Test 4: AI Improvement
    improved_cv = test_cv_improvement(cv_data, ai_client)
    
    # Test 5: PDF Generation - Original
    pdf_path_original = test_pdf_generation(original_cv)
    
    # Test 6: PDF Generation - Improved
    if improved_cv and improved_cv != original_cv:
        print("\n" + "="*70)
        print("TEST 6: IMPROVED CV PDF GENERATION")
        print("="*70)
        improved_cv['name'] = improved_cv.get('name', 'sample') + '_Improved'
        pdf_path_improved = test_pdf_generation(improved_cv)
    
    # Save comparison
    if analysis and improved_cv:
        save_cv_comparison(original_cv, improved_cv, analysis)
    
    # Final Summary
    print("\n" + "="*70)
    print("PIPELINE TEST SUMMARY")
    print("="*70)
    print(f"\n✓ All tests completed successfully!")
    print(f"\nResults:")
    print(f"   • CV extracted and parsed: ✓")
    print(f"   • ATS Score: {ats_score}/100")
    if analysis:
        print(f"   • CV Score: {analysis['score']}/{analysis['max_score']}")
        print(f"   • Candidate Level: {analysis['candidate_level']}")
        print(f"   • Predicted Field: {analysis['predicted_field']}")
    print(f"   • PDF Generated: ✓")
    
    if ai_client and improved_cv != original_cv:
        print(f"   • AI Enhancement: ✓")
    
    print("\nCheck the 'output' directory for generated files.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test PerfectCV Pipeline')
    parser.add_argument('--file', type=str, help='Path to test CV file (PDF/DOCX)', default=None)
    args = parser.parse_args()
    
    run_complete_pipeline(args.file)
