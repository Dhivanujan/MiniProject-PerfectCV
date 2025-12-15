"""
CV Data Validation Service
Validates completeness of extracted CV data and determines if AI fallback is needed.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class CVDataValidator:
    """Validates extracted CV data for completeness and quality"""
    
    # Critical fields that must be present
    CRITICAL_FIELDS = ['name', 'email', 'phone']
    
    # Important fields that improve CV quality
    IMPORTANT_FIELDS = ['skills', 'experience', 'education']
    
    def __init__(self):
        pass
    
    def validate_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted CV data and determine if AI fallback is needed.
        
        Args:
            data: Extracted CV data dictionary containing:
                - contact_info: dict with name, email, phone, etc.
                - skills: dict or list
                - experience: list
                - education: list
                - sections: dict (optional)
                
        Returns:
            Validation result with:
                - is_complete: bool
                - needs_ai_fallback: bool
                - missing_critical: list of missing critical fields
                - missing_important: list of missing important fields
                - completeness_score: float (0-100)
                - validation_details: dict
        """
        logger.info("🔍 Validating extracted CV data...")
        
        # Extract relevant data
        contact_info = data.get('contact_info', {}) or {}
        skills = data.get('skills', {}) or {}
        experience = data.get('experience', []) or []
        education = data.get('education', []) or []
        
        # Check critical fields (contact info)
        missing_critical = []
        for field in self.CRITICAL_FIELDS:
            value = contact_info.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_critical.append(field)
        
        # Check important fields (CV content)
        missing_important = []
        
        # Skills validation
        if not self._has_valid_skills(skills):
            missing_important.append('skills')
        
        # Experience validation
        if not self._has_valid_experience(experience):
            missing_important.append('experience')
        
        # Education validation
        if not self._has_valid_education(education):
            missing_important.append('education')
        
        # Calculate completeness score
        total_fields = len(self.CRITICAL_FIELDS) + len(self.IMPORTANT_FIELDS)
        missing_count = len(missing_critical) + len(missing_important)
        completeness_score = ((total_fields - missing_count) / total_fields) * 100
        
        # Determine if AI fallback is needed
        # AI fallback triggered if ANY critical field is missing
        needs_ai_fallback = len(missing_critical) > 0
        
        # Consider it complete if all critical fields are present
        is_complete = len(missing_critical) == 0
        
        result = {
            'is_complete': is_complete,
            'needs_ai_fallback': needs_ai_fallback,
            'missing_critical': missing_critical,
            'missing_important': missing_important,
            'completeness_score': round(completeness_score, 1),
            'validation_details': {
                'has_name': bool(contact_info.get('name')),
                'has_email': bool(contact_info.get('email')),
                'has_phone': bool(contact_info.get('phone')),
                'has_skills': not ('skills' in missing_important),
                'has_experience': not ('experience' in missing_important),
                'has_education': not ('education' in missing_important),
            }
        }
        
        # Log validation results
        if is_complete:
            logger.info(f"✅ Validation PASSED: {completeness_score:.1f}% complete")
        else:
            logger.warning(f"⚠️ Validation INCOMPLETE: {completeness_score:.1f}% complete")
            logger.warning(f"   Missing critical: {missing_critical}")
            if missing_important:
                logger.warning(f"   Missing important: {missing_important}")
        
        if needs_ai_fallback:
            logger.info("🤖 AI fallback REQUIRED to complete extraction")
        else:
            logger.info("✅ No AI fallback needed - extraction sufficient")
        
        return result
    
    def _has_valid_skills(self, skills: Any) -> bool:
        """Check if skills data is valid and non-empty"""
        if not skills:
            return False
        
        if isinstance(skills, dict):
            # Check if any category has skills
            for category, skill_list in skills.items():
                if isinstance(skill_list, list) and len(skill_list) > 0:
                    return True
            return False
        
        if isinstance(skills, list):
            return len(skills) > 0
        
        return False
    
    def _has_valid_experience(self, experience: Any) -> bool:
        """Check if experience data is valid and non-empty"""
        if not isinstance(experience, list) or len(experience) == 0:
            return False
        
        # Check if at least one experience entry has meaningful data
        for exp in experience:
            if isinstance(exp, dict):
                # Must have at least title or company
                if exp.get('title') or exp.get('company') or exp.get('position'):
                    return True
        
        return False
    
    def _has_valid_education(self, education: Any) -> bool:
        """Check if education data is valid and non-empty"""
        if not isinstance(education, list) or len(education) == 0:
            return False
        
        # Check if at least one education entry has meaningful data
        for edu in education:
            if isinstance(edu, dict):
                # Must have at least degree or institution
                if edu.get('degree') or edu.get('institution') or edu.get('school'):
                    return True
        
        return False
    
    def merge_ai_results(
        self, 
        original_data: Dict[str, Any], 
        ai_data: Dict[str, Any], 
        missing_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Merge AI extraction results with original data, filling only missing fields.
        
        Args:
            original_data: Original extracted data
            ai_data: Data extracted by AI
            missing_fields: List of fields that were missing
            
        Returns:
            Merged data dictionary
        """
        logger.info("🔄 Merging AI results with original data...")
        
        merged = original_data.copy()
        contact_info = merged.get('contact_info', {}) or {}
        
        # Merge critical fields (name, email, phone)
        for field in ['name', 'email', 'phone', 'location']:
            if field in missing_fields and ai_data.get(field):
                contact_info[field] = ai_data[field]
                logger.info(f"  ✅ Filled missing {field}: {ai_data[field]}")
        
        merged['contact_info'] = contact_info
        
        # Merge important fields
        if 'skills' in missing_fields and ai_data.get('skills'):
            merged['skills'] = ai_data['skills']
            logger.info(f"  ✅ Filled missing skills: {len(ai_data['skills'])} items")
        
        if 'experience' in missing_fields and ai_data.get('experience'):
            merged['experience'] = ai_data['experience']
            logger.info(f"  ✅ Filled missing experience: {len(ai_data['experience'])} entries")
        
        if 'education' in missing_fields and ai_data.get('education'):
            merged['education'] = ai_data['education']
            logger.info(f"  ✅ Filled missing education: {len(ai_data['education'])} entries")
        
        # Also merge optional fields if provided
        if not merged.get('summary') and ai_data.get('summary'):
            merged['summary'] = ai_data['summary']
            logger.info(f"  ✅ Added summary from AI")
        
        if not merged.get('certifications') and ai_data.get('certifications'):
            merged['certifications'] = ai_data['certifications']
            logger.info(f"  ✅ Added certifications from AI")
        
        return merged


# Singleton instance
_validator = None

def get_cv_validator() -> CVDataValidator:
    """Get singleton instance of CVDataValidator"""
    global _validator
    if _validator is None:
        _validator = CVDataValidator()
    return _validator
