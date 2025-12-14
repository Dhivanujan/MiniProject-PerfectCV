"""
Extraction service - orchestrates text extraction and entity recognition.
"""
import logging
from typing import Dict, Tuple
from app.utils.text_extractor import TextExtractor
from app.utils.text_cleaner import TextCleaner
from app.utils.entity_extractor import EntityExtractor

logger = logging.getLogger(__name__)


class ExtractionService:
    """Service for extracting and processing CV data."""
    
    def __init__(self):
        """Initialize extraction service with required components."""
        self.text_extractor = TextExtractor()
        self.text_cleaner = TextCleaner()
        self.entity_extractor = EntityExtractor()
    
    def process_cv(self, file_bytes: bytes, filename: str) -> Dict:
        """
        Complete CV processing pipeline.
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            
        Returns:
            Dictionary with all extracted and processed data
        """
        logger.info("="*60)
        logger.info(f"📄 Starting CV processing for: {filename}")
        logger.info("="*60)
        
        # Stage 1: Extract raw text
        logger.info("Stage 1: Extracting text from file")
        raw_text, extraction_method = self.text_extractor.extract_text(file_bytes, filename)
        logger.info(f"Extracted {len(raw_text)} characters using {extraction_method}")
        
        # Stage 2: Clean and normalize text
        logger.info("Stage 2: Cleaning and normalizing text")
        cleaned_text = self.text_cleaner.clean_text(raw_text)
        logger.info(f"Cleaned text: {len(cleaned_text)} characters")
        
        # Stage 3: Extract sections
        logger.info("Stage 3: Extracting CV sections")
        sections = self.text_cleaner.extract_sections(cleaned_text)
        logger.info(f"Extracted {len(sections)} sections: {list(sections.keys())}")
        for section_name, content in sections.items():
            logger.info(f"  - {section_name}: {len(content)} chars")
        
        # Stage 4: Extract entities
        logger.info("Stage 4: Extracting entities using spaCy + Regex")
        entities = self.entity_extractor.extract_entities(cleaned_text)
        logger.info(f"Entity extraction complete:")
        logger.info(f"  - Name: {entities.get('name') or 'NOT FOUND'}")
        logger.info(f"  - Email: {entities.get('email') or 'NOT FOUND'}")
        logger.info(f"  - Phone: {entities.get('phone') or 'NOT FOUND'}")
        logger.info(f"  - Location: {entities.get('location') or 'NOT FOUND'}")
        logger.info(f"  - Skills: {len(entities.get('skills', []))} found")
        logger.info(f"  - Organizations: {len(entities.get('organizations', []))} found")
        
        # Compile results
        result = {
            'raw_text': raw_text,
            'cleaned_text': cleaned_text,
            'extraction_method': extraction_method,
            'sections': sections,
            'entities': entities,
            'filename': filename,
        }
        
        logger.info("="*60)
        logger.info(f"CV processing completed successfully for: {filename}")
        logger.info("="*60)
        return result
    
    def extract_text_only(self, file_bytes: bytes, filename: str) -> str:
        """
        Quick extraction - just get cleaned text without full processing.
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            
        Returns:
            Cleaned text string
        """
        raw_text, _ = self.text_extractor.extract_text(file_bytes, filename)
        return self.text_cleaner.clean_text(raw_text)
