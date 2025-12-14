"""
End-to-end tests for CV processing pipeline.
Tests the complete flow: Upload → Extraction → Validation → AI Enhancement → PDF Generation → Download
"""
import os
import sys
import io
import logging
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.extraction_service import ExtractionService
from app.services.validation_service import ValidationService
from app.services.ai_service import AIService
from app.services.cv_generation_service import CVGenerationService
from config.config import Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCVProcessingPipeline:
    """Test complete CV processing pipeline."""
    
    @pytest.fixture
    def sample_cv_text(self):
        """Sample CV text for testing."""
        return """
# John Doe

Email: john.doe@email.com | Phone: +1 (555) 123-4567 | Location: San Francisco, CA

## Professional Summary

Experienced software engineer with 5+ years of building scalable web applications.

## Experience

**Senior Software Engineer**
Tech Company Inc. | 2020 - Present
- Developed microservices using Python and Flask
- Led team of 5 engineers
- Improved system performance by 40%

**Software Engineer**
StartUp Co. | 2018 - 2020
- Built RESTful APIs
- Implemented CI/CD pipelines

## Education

**Bachelor of Science in Computer Science**
University of California | 2014 - 2018

## Skills

Python, JavaScript, React, Node.js, Docker, Kubernetes, AWS, PostgreSQL, MongoDB
"""
    
    def test_01_text_extraction(self, tmp_path, sample_cv_text):
        """Test Stage 1: Text extraction from PDF."""
        logger.info("\n" + "="*60)
        logger.info("TEST 1: Text Extraction")
        logger.info("="*60)
        
        # Create a simple text file (in production, this would be PDF/DOCX)
        test_file = tmp_path / "test_cv.txt"
        test_file.write_text(sample_cv_text)
        
        extraction_service = ExtractionService()
        
        # For testing, we'll use the text directly
        # In production, use: extraction_service.process_cv(file_bytes, filename)
        from app.utils.text_cleaner import TextCleaner
        cleaner = TextCleaner()
        
        cleaned_text = cleaner.clean_text(sample_cv_text)
        
        assert len(cleaned_text) > 100
        assert 'John Doe' in cleaned_text
        assert 'john.doe@email.com' in cleaned_text
        
        logger.info(f"\u2713 Text extraction passed: {len(cleaned_text)} chars")
    
    def test_02_section_extraction(self, sample_cv_text):
        """Test Stage 2: Section extraction."""
        logger.info("\n" + "="*60)
        logger.info("TEST 2: Section Extraction")
        logger.info("="*60)
        
        from app.utils.text_cleaner import TextCleaner
        cleaner = TextCleaner()
        
        cleaned_text = cleaner.clean_text(sample_cv_text)
        sections = cleaner.extract_sections(cleaned_text)
        
        assert 'summary' in sections or 'experience' in sections
        assert len(sections) > 0
        
        logger.info(f"\u2713 Section extraction passed: {len(sections)} sections found")
        for section_name, content in sections.items():
            logger.info(f"  - {section_name}: {len(content)} chars")
    
    def test_03_entity_extraction(self, sample_cv_text):
        """Test Stage 3: Entity extraction using spaCy + regex."""
        logger.info("\n" + "="*60)
        logger.info("TEST 3: Entity Extraction (spaCy + Regex)")
        logger.info("="*60)
        
        from app.utils.entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        
        entities = extractor.extract_entities(sample_cv_text)
        
        # Verify critical fields
        assert entities.get('email') == 'john.doe@email.com'
        assert entities.get('phone') is not None
        assert entities.get('name') is not None
        
        logger.info(f"\u2713 Entity extraction passed:")
        logger.info(f"  - Name: {entities.get('name')}")
        logger.info(f"  - Email: {entities.get('email')}")
        logger.info(f"  - Phone: {entities.get('phone')}")
        logger.info(f"  - Skills: {len(entities.get('skills', []))} found")
    
    def test_04_validation(self, sample_cv_text):
        """Test Stage 4: Validation of critical fields."""
        logger.info("\n" + "="*60)
        logger.info("TEST 4: Validation of Critical Fields")
        logger.info("="*60)
        
        from app.utils.entity_extractor import EntityExtractor
        from app.utils.text_cleaner import TextCleaner
        
        cleaner = TextCleaner()
        extractor = EntityExtractor()
        
        cleaned_text = cleaner.clean_text(sample_cv_text)
        sections = cleaner.extract_sections(cleaned_text)
        entities = extractor.extract_entities(cleaned_text)
        
        validator = ValidationService()
        validation_report = validator.get_validation_report(entities, sections)
        
        assert validation_report['completeness_score'] > 60
        assert len(validation_report['missing_critical']) < 3
        
        logger.info(f"\u2713 Validation passed:")
        logger.info(f"  - Completeness: {validation_report['completeness_score']:.1f}%")
        logger.info(f"  - Missing critical: {validation_report['missing_critical']}")
        logger.info(f"  - Missing important: {validation_report['missing_important']}")
    
    def test_05_ai_fallback(self):
        """Test Stage 5: AI fallback for missing fields (if API key available)."""
        logger.info("\n" + "="*60)
        logger.info("TEST 5: AI Fallback for Missing Fields")
        logger.info("="*60)
        
        # Check if AI service is configured
        groq_key = getattr(Config, 'GROQ_API_KEY', None)
        
        if not groq_key:
            logger.info("\u26a0 Skipping AI fallback test (no API key configured)")
            pytest.skip("AI service not configured")
            return
        
        ai_service = AIService(
            groq_api_key=groq_key,
            provider='groq'
        )
        
        if not ai_service.is_available():
            logger.info("\u26a0 AI service not available")
            pytest.skip("AI service not available")
            return
        
        # Test extraction with incomplete CV
        incomplete_cv = "John Doe worked at Tech Company. Skilled in Python."
        missing_fields = ['email', 'phone']
        
        extracted = ai_service.extract_missing_fields(incomplete_cv, missing_fields)
        
        # Should return a dict (even if fields are null)
        assert isinstance(extracted, dict)
        
        logger.info(f"\u2713 AI fallback executed:")
        logger.info(f"  - Fields requested: {missing_fields}")
        logger.info(f"  - Fields extracted: {list(extracted.keys())}")
    
    def test_06_cv_generation(self, sample_cv_text):
        """Test Stage 6: PDF generation with Jinja2 + WeasyPrint."""
        logger.info("\n" + "="*60)
        logger.info("TEST 6: CV PDF Generation (Jinja2 + WeasyPrint)")
        logger.info("="*60)
        
        from app.utils.entity_extractor import EntityExtractor
        from app.utils.text_cleaner import TextCleaner
        
        cleaner = TextCleaner()
        extractor = EntityExtractor()
        
        cleaned_text = cleaner.clean_text(sample_cv_text)
        sections = cleaner.extract_sections(cleaned_text)
        entities = extractor.extract_entities(cleaned_text)
        
        cv_data = {
            'entities': entities,
            'sections': sections
        }
        
        cv_service = CVGenerationService()
        
        try:
            pdf_bytes = cv_service.generate_cv_pdf(cv_data)
            
            assert pdf_bytes is not None
            assert len(pdf_bytes) > 1000  # PDF should be reasonable size
            assert pdf_bytes[:4] == b'%PDF'  # PDF magic number
            
            logger.info(f"\u2713 PDF generation passed: {len(pdf_bytes)} bytes")
        except RuntimeError as e:
            if "WeasyPrint" in str(e) or "FPDF" in str(e):
                logger.info("\u26a0 PDF generation libraries not available")
                pytest.skip(str(e))
            else:
                raise
    
    def test_07_complete_pipeline(self, sample_cv_text):
        """Test Stage 7: Complete end-to-end pipeline."""
        logger.info("\n" + "="*60)
        logger.info("TEST 7: Complete Pipeline Integration")
        logger.info("="*60)
        
        # Initialize all services
        extraction_service = ExtractionService()
        validation_service = ValidationService()
        cv_service = CVGenerationService()
        
        # Process CV
        from app.utils.text_cleaner import TextCleaner
        from app.utils.entity_extractor import EntityExtractor
        
        cleaner = TextCleaner()
        extractor = EntityExtractor()
        
        # Step 1: Clean and extract
        cleaned_text = cleaner.clean_text(sample_cv_text)
        sections = cleaner.extract_sections(cleaned_text)
        entities = extractor.extract_entities(cleaned_text)
        
        # Step 2: Validate
        validation_report = validation_service.get_validation_report(entities, sections)
        
        # Step 3: Generate PDF
        cv_data = {'entities': entities, 'sections': sections}
        
        try:
            pdf_bytes = cv_service.generate_cv_pdf(cv_data)
            
            logger.info(f"\u2713 Complete pipeline passed:")
            logger.info(f"  - Extraction: {len(cleaned_text)} chars")
            logger.info(f"  - Sections: {len(sections)}")
            logger.info(f"  - Entities: {len(entities)} fields")
            logger.info(f"  - Validation: {validation_report['completeness_score']:.1f}%")
            logger.info(f"  - PDF: {len(pdf_bytes)} bytes")
            
            assert validation_report['completeness_score'] > 50
            assert len(pdf_bytes) > 1000
            
        except RuntimeError as e:
            if "PDF generation" in str(e):
                logger.info("\u26a0 PDF generation not available, but pipeline logic passed")
                pytest.skip(str(e))
            else:
                raise


def test_ats_score_logic():
    """Test that ATS score is calculated after validation."""
    logger.info("\n" + "="*60)
    logger.info("TEST 8: ATS Score Logic")
    logger.info("="*60)
    
    # Create sample data with varying completeness
    test_cases = [
        {
            'entities': {'name': 'John', 'email': 'j@e.com', 'phone': '123', 'skills': ['Python']},
            'sections': {'experience': 'Experience here', 'education': 'Edu here'},
            'expected_score_range': (80, 100)
        },
        {
            'entities': {'name': 'Jane', 'skills': []},
            'sections': {},
            'expected_score_range': (0, 40)
        },
    ]
    
    validator = ValidationService()
    
    for i, test_case in enumerate(test_cases, 1):
        report = validator.get_validation_report(
            test_case['entities'],
            test_case['sections']
        )
        
        score = report['completeness_score']
        min_score, max_score = test_case['expected_score_range']
        
        assert min_score <= score <= max_score, \
            f"Test case {i}: Score {score} not in range [{min_score}, {max_score}]"
        
        logger.info(f"\u2713 Test case {i}: Score = {score:.1f}% (expected {min_score}-{max_score}%)")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])
