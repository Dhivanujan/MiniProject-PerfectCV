"""
Validation service - validates extracted CV data.
"""
import re
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating extracted CV data."""
    
    # Required fields for a valid CV
    CRITICAL_FIELDS = ['name', 'email', 'phone']
    IMPORTANT_FIELDS = ['skills', 'experience']
    
    @staticmethod
    def validate_cv_data(entities: Dict, sections: Dict) -> Tuple[bool, List[str], List[str]]:
        """
        Validate completeness of extracted CV data.
        
        Args:
            entities: Extracted entities dictionary
            sections: Extracted sections dictionary
            
        Returns:
            Tuple of (is_complete, missing_critical, missing_important)
        """
        missing_critical = []
        missing_important = []
        
        # Check critical fields
        for field in ValidationService.CRITICAL_FIELDS:
            if not entities.get(field):
                missing_critical.append(field)
                logger.warning(f"Missing critical field: {field}")
        
        # Check important fields
        for field in ValidationService.IMPORTANT_FIELDS:
            # Skills can be in entities or sections
            if field == 'skills':
                has_skills = bool(entities.get('skills') or sections.get('skills'))
                if not has_skills:
                    missing_important.append(field)
                    logger.warning(f"Missing important field: {field}")
            
            # Experience in sections
            elif field == 'experience':
                has_experience = bool(sections.get('experience'))
                if not has_experience:
                    missing_important.append(field)
                    logger.warning(f"Missing important field: {field}")
        
        is_complete = len(missing_critical) == 0
        
        if is_complete:
            logger.info("CV data validation passed - all critical fields present")
        else:
            logger.warning(f"CV data validation failed - missing: {missing_critical}")
        
        return is_complete, missing_critical, missing_important
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        if not email:
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number (basic check)."""
        if not phone:
            return False
        # Remove common separators
        digits = re.sub(r'[^\d]', '', phone)
        # Should have 10-15 digits
        return 10 <= len(digits) <= 15
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate name field."""
        if not name:
            return False
        # Should have at least 2 words, each > 1 character
        words = name.strip().split()
        return len(words) >= 2 and all(len(w) > 1 for w in words)
    
    @staticmethod
    def get_validation_report(entities: Dict, sections: Dict) -> Dict:
        """
        Get detailed validation report.
        
        Args:
            entities: Extracted entities
            sections: Extracted sections
            
        Returns:
            Validation report dictionary
        """
        report = {
            'is_valid': False,
            'completeness_score': 0.0,
            'missing_critical': [],
            'missing_important': [],
            'field_validity': {},
            'warnings': [],
            'suggestions': []
        }
        
        # Validate completeness
        is_complete, missing_critical, missing_important = ValidationService.validate_cv_data(
            entities, sections
        )
        
        report['missing_critical'] = missing_critical
        report['missing_important'] = missing_important
        report['is_valid'] = is_complete
        
        # Validate individual fields
        if entities.get('email'):
            is_valid = ValidationService.validate_email(entities['email'])
            report['field_validity']['email'] = is_valid
            if not is_valid:
                report['warnings'].append('Email format appears invalid')
        
        if entities.get('phone'):
            is_valid = ValidationService.validate_phone(entities['phone'])
            report['field_validity']['phone'] = is_valid
            if not is_valid:
                report['warnings'].append('Phone number format appears invalid')
        
        if entities.get('name'):
            is_valid = ValidationService.validate_name(entities['name'])
            report['field_validity']['name'] = is_valid
            if not is_valid:
                report['warnings'].append('Name format appears invalid')
        
        # Calculate completeness score
        total_fields = len(ValidationService.CRITICAL_FIELDS) + len(ValidationService.IMPORTANT_FIELDS)
        found_fields = total_fields - len(missing_critical) - len(missing_important)
        report['completeness_score'] = (found_fields / total_fields) * 100
        
        # Generate suggestions
        if missing_critical:
            report['suggestions'].append(
                f"Critical information missing: {', '.join(missing_critical)}. "
                "AI fallback will be used to extract these fields."
            )
        
        if missing_important:
            report['suggestions'].append(
                f"Important sections missing: {', '.join(missing_important)}. "
                "Consider adding these to improve your CV."
            )
        
        if not entities.get('skills'):
            report['suggestions'].append(
                "No skills detected. Add a skills section to improve your CV."
            )
        
        logger.info(f"Validation report: completeness={report['completeness_score']:.1f}%, "
                   f"valid={report['is_valid']}, warnings={len(report['warnings'])}")
        
        return report
