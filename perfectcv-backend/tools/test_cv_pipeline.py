"""
Test script for CV extraction pipeline.
Tests the complete extraction, validation, and generation flow.
"""
import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.extraction_service import ExtractionService
from app.services.validation_service import ValidationService
from app.services.ai_service import AIService
from app.services.cv_generation_service import CVGenerationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_extraction_pipeline(file_path: str, output_dir: str = "test_output"):
    """
    Test the complete CV extraction pipeline.
    
    Args:
        file_path: Path to CV file (PDF or DOCX)
        output_dir: Directory to save output files
    """
    logger.info("=" * 70)
    logger.info("TESTING CV EXTRACTION PIPELINE")
    logger.info("=" * 70)
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Read file
    logger.info(f"Reading file: {file_path}")
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    
    filename = Path(file_path).name
    
    # ========================================
    # TEST 1: EXTRACTION SERVICE
    # ========================================
    logger.info("\n" + "=" * 70)
    logger.info("TEST 1: EXTRACTION SERVICE")
    logger.info("=" * 70)
    
    extraction_service = ExtractionService()
    cv_data = extraction_service.process_cv(file_bytes, filename)
    
    logger.info(f"✓ Extraction method: {cv_data['extraction_method']}")
    logger.info(f"✓ Raw text length: {len(cv_data['raw_text'])} characters")
    logger.info(f"✓ Cleaned text length: {len(cv_data['cleaned_text'])} characters")
    logger.info(f"✓ Sections found: {list(cv_data['sections'].keys())}")
    
    entities = cv_data['entities']
    logger.info(f"✓ Entities extracted:")
    logger.info(f"  - Name: {entities.get('name')}")
    logger.info(f"  - Email: {entities.get('email')}")
    logger.info(f"  - Phone: {entities.get('phone')}")
    logger.info(f"  - Location: {entities.get('location')}")
    logger.info(f"  - Skills: {len(entities.get('skills', []))} found")
    logger.info(f"  - Organizations: {len(entities.get('organizations', []))} found")
    
    # Save extracted text
    text_output = output_path / f"{Path(filename).stem}_extracted.txt"
    with open(text_output, 'w', encoding='utf-8') as f:
        f.write("=== RAW TEXT ===\n\n")
        f.write(cv_data['raw_text'])
        f.write("\n\n=== CLEANED TEXT ===\n\n")
        f.write(cv_data['cleaned_text'])
        f.write("\n\n=== SECTIONS ===\n\n")
        for section, content in cv_data['sections'].items():
            f.write(f"\n--- {section.upper()} ---\n")
            f.write(content[:500] + "..." if len(content) > 500 else content)
    
    logger.info(f"✓ Saved extracted text to: {text_output}")
    
    # ========================================
    # TEST 2: VALIDATION SERVICE
    # ========================================
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: VALIDATION SERVICE")
    logger.info("=" * 70)
    
    validation_service = ValidationService()
    validation_report = validation_service.get_validation_report(
        cv_data['entities'],
        cv_data['sections']
    )
    
    logger.info(f"✓ Completeness score: {validation_report['completeness_score']:.1f}%")
    logger.info(f"✓ Is complete: {validation_report['is_valid']}")
    
    if validation_report['missing_critical']:
        logger.warning(f"⚠ Missing critical fields: {validation_report['missing_critical']}")
    else:
        logger.info("✓ All critical fields present")
    
    if validation_report['missing_important']:
        logger.warning(f"⚠ Missing important fields: {validation_report['missing_important']}")
    
    if validation_report['warnings']:
        logger.warning(f"⚠ Warnings: {validation_report['warnings']}")
    
    if validation_report['suggestions']:
        logger.info("Suggestions:")
        for suggestion in validation_report['suggestions']:
            logger.info(f"  - {suggestion}")
    
    # ========================================
    # TEST 3: AI SERVICE (if configured)
    # ========================================
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: AI SERVICE")
    logger.info("=" * 70)
    
    ai_service = AIService(
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        google_api_key=os.getenv('GOOGLE_API_KEY'),
        groq_api_key=os.getenv('GROQ_API_KEY'),
        provider=os.getenv('AI_PROVIDER', 'openai')
    )
    
    if ai_service.is_available():
        logger.info("✓ AI service available")
        
        # Test fallback extraction if needed
        if validation_report['missing_critical']:
            logger.info(f"Testing AI fallback for: {validation_report['missing_critical']}")
            ai_extracted = ai_service.extract_missing_fields(
                cv_data['cleaned_text'],
                validation_report['missing_critical']
            )
            logger.info(f"✓ AI extracted: {ai_extracted}")
        
        # Test content improvement
        if cv_data['sections'].get('summary'):
            logger.info("Testing AI content improvement...")
            improved_sections = ai_service.improve_cv_content(
                cv_data['sections'],
                job_domain="Software Engineering"
            )
            
            if improved_sections['summary'] != cv_data['sections']['summary']:
                logger.info("✓ Summary improved by AI")
                logger.info(f"Original length: {len(cv_data['sections']['summary'])}")
                logger.info(f"Improved length: {len(improved_sections['summary'])}")
            else:
                logger.info("✓ Summary unchanged (already good)")
    else:
        logger.warning("⚠ AI service not available (no API keys configured)")
    
    # ========================================
    # TEST 4: CV GENERATION SERVICE
    # ========================================
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: CV GENERATION SERVICE")
    logger.info("=" * 70)
    
    generation_service = CVGenerationService()
    
    try:
        pdf_bytes = generation_service.generate_cv_pdf(cv_data)
        logger.info(f"✓ PDF generated: {len(pdf_bytes)} bytes")
        
        # Save PDF
        pdf_output = output_path / f"{Path(filename).stem}_generated.pdf"
        with open(pdf_output, 'wb') as f:
            f.write(pdf_bytes)
        
        logger.info(f"✓ Saved PDF to: {pdf_output}")
    
    except Exception as e:
        logger.error(f"✗ PDF generation failed: {e}")
        logger.info("This might be due to missing WeasyPrint or FPDF")
    
    # ========================================
    # SUMMARY
    # ========================================
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    logger.info(f"File: {filename}")
    logger.info(f"Extraction: ✓ {cv_data['extraction_method']}")
    logger.info(f"Sections: ✓ {len(cv_data['sections'])} found")
    logger.info(f"Entities: ✓ {len([k for k, v in entities.items() if v])} extracted")
    logger.info(f"Completeness: {validation_report['completeness_score']:.1f}%")
    logger.info(f"Status: {'✓ COMPLETE' if validation_report['is_valid'] else '⚠ INCOMPLETE'}")
    
    logger.info("\n" + "=" * 70)
    logger.info("ALL TESTS COMPLETED")
    logger.info("=" * 70)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_cv_pipeline.py <path_to_cv_file>")
        print("Example: python test_cv_pipeline.py ../sample_cv.pdf")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    test_extraction_pipeline(file_path)


if __name__ == "__main__":
    main()
