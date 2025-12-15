"""
CV Extraction Orchestrator with Phi-3 Integration
Coordinates rule-based extraction, validation, and AI fallback using Phi-3.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from app.services.phi3_service import get_phi3_service
from app.services.cv_validation_service import get_cv_validator

logger = logging.getLogger(__name__)


class CVExtractionOrchestrator:
    """
    Orchestrates CV extraction with multiple strategies:
    1. Primary: Rule-based + spaCy + Regex
    2. Validation: Check completeness
    3. Fallback: Phi-3 AI extraction for missing data
    """
    
    def __init__(self):
        self.phi3 = get_phi3_service()
        self.validator = get_cv_validator()
        self.phi3_available = False
        self._check_phi3_availability()
    
    def _check_phi3_availability(self):
        """Check if Phi-3 is available at startup"""
        try:
            self.phi3_available = self.phi3.check_availability()
            if self.phi3_available:
                logger.info("✅ Phi-3 is available for AI fallback")
            else:
                logger.warning("⚠️ Phi-3 not available - AI fallback disabled")
        except Exception as e:
            logger.warning(f"⚠️ Cannot check Phi-3: {str(e)}")
            self.phi3_available = False
    
    def extract_with_fallback(
        self, 
        text: str, 
        primary_extraction: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Extract CV data with AI fallback if needed.
        
        Args:
            text: Raw CV text
            primary_extraction: Results from primary extraction (spaCy + regex)
                Expected keys: contact_info, skills, experience, education, etc.
        
        Returns:
            Tuple of (final_data, metadata)
            - final_data: Complete CV data (with AI fallback if needed)
            - metadata: Extraction metadata (validation, fallback_used, etc.)
        """
        logger.info("=" * 70)
        logger.info("🚀 CV EXTRACTION ORCHESTRATOR - STARTING")
        logger.info("=" * 70)
        
        # Step 1: Validate primary extraction
        logger.info("\n📋 STEP 1: Validating primary extraction...")
        validation_result = self.validator.validate_extraction(primary_extraction)
        
        metadata = {
            'primary_extraction_complete': validation_result['is_complete'],
            'completeness_score': validation_result['completeness_score'],
            'missing_critical': validation_result['missing_critical'],
            'missing_important': validation_result['missing_important'],
            'ai_fallback_triggered': False,
            'ai_fallback_successful': False,
            'extraction_method': 'rule_based',
        }
        
        # Step 2: Decide if AI fallback is needed
        if not validation_result['needs_ai_fallback']:
            logger.info("\n✅ STEP 2: Primary extraction sufficient - no AI fallback needed")
            logger.info(f"   Completeness: {validation_result['completeness_score']:.1f}%")
            logger.info("=" * 70)
            return primary_extraction, metadata
        
        # Step 3: Attempt AI fallback with Phi-3
        logger.info("\n🤖 STEP 2: Primary extraction incomplete - attempting AI fallback")
        logger.info(f"   Missing critical fields: {validation_result['missing_critical']}")
        logger.info(f"   Missing important fields: {validation_result['missing_important']}")
        
        if not self.phi3_available:
            logger.warning("   ⚠️ Phi-3 not available - returning incomplete data")
            metadata['ai_fallback_triggered'] = True
            metadata['ai_fallback_error'] = 'Phi-3 not available'
            logger.info("=" * 70)
            return primary_extraction, metadata
        
        # Call Phi-3 for extraction
        logger.info("   🔄 Calling Phi-3 for data extraction...")
        metadata['ai_fallback_triggered'] = True
        
        ai_data = self.phi3.extract_cv_data(text)
        
        if not ai_data:
            logger.error("   ❌ Phi-3 extraction failed")
            metadata['ai_fallback_error'] = 'Phi-3 extraction returned no data'
            logger.info("=" * 70)
            return primary_extraction, metadata
        
        # Step 4: Merge AI results with primary extraction
        logger.info("\n🔄 STEP 3: Merging AI results with primary extraction...")
        missing_fields = validation_result['missing_critical'] + validation_result['missing_important']
        
        final_data = self.validator.merge_ai_results(
            original_data=primary_extraction,
            ai_data=ai_data,
            missing_fields=missing_fields
        )
        
        # Step 5: Validate final result
        logger.info("\n✅ STEP 4: Validating final merged data...")
        final_validation = self.validator.validate_extraction(final_data)
        
        metadata['ai_fallback_successful'] = True
        metadata['extraction_method'] = 'hybrid_rule_based_ai'
        metadata['final_completeness_score'] = final_validation['completeness_score']
        metadata['final_is_complete'] = final_validation['is_complete']
        
        logger.info(f"   Final completeness: {final_validation['completeness_score']:.1f}%")
        if final_validation['is_complete']:
            logger.info("   ✅ Extraction now complete!")
        else:
            logger.warning(f"   ⚠️ Still missing: {final_validation['missing_critical']}")
        
        logger.info("=" * 70)
        logger.info("🎉 CV EXTRACTION ORCHESTRATOR - COMPLETED")
        logger.info("=" * 70)
        
        return final_data, metadata
    
    def improve_cv_content(self, cv_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Improve CV content using Phi-3 (rewrite summary, enhance descriptions).
        
        Args:
            cv_data: Complete CV data dictionary
            
        Returns:
            Improved CV data, or None if improvement fails
        """
        if not self.phi3_available:
            logger.warning("⚠️ Phi-3 not available - skipping CV improvement")
            return None
        
        logger.info("=" * 70)
        logger.info("✨ CV IMPROVEMENT WITH PHI-3 - STARTING")
        logger.info("=" * 70)
        
        improved_data = self.phi3.improve_cv_content(cv_data)
        
        if improved_data:
            logger.info("✅ CV improvement successful")
        else:
            logger.warning("⚠️ CV improvement failed")
        
        logger.info("=" * 70)
        
        return improved_data


# Singleton instance
_orchestrator = None

def get_extraction_orchestrator() -> CVExtractionOrchestrator:
    """Get singleton instance of CVExtractionOrchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CVExtractionOrchestrator()
    return _orchestrator
