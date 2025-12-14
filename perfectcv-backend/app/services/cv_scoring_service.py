"""
CV Scoring and Analysis Service
Provides comprehensive CV scoring, recommendations, and field predictions.
Based on ATS optimization principles.
"""
import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CVScoringService:
    """Analyzes and scores CVs based on content quality and ATS optimization."""
    
    # Keywords for field prediction
    DS_KEYWORDS = [
        'tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 
        'flask', 'streamlit', 'data science', 'data analysis', 'pandas', 'numpy',
        'scikit-learn', 'data visualization', 'statistics', 'neural networks'
    ]
    
    WEB_KEYWORDS = [
        'react', 'django', 'node js', 'nodejs', 'react js', 'php', 'laravel', 
        'magento', 'wordpress', 'javascript', 'angular js', 'angular', 'c#', 
        'flask', 'vue', 'vue.js', 'next.js', 'express', 'fastapi'
    ]
    
    ANDROID_KEYWORDS = [
        'android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy',
        'java', 'android studio', 'gradle', 'jetpack compose'
    ]
    
    IOS_KEYWORDS = [
        'ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode',
        'objective-c', 'swiftui', 'uikit'
    ]
    
    UIUX_KEYWORDS = [
        'ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping',
        'wireframes', 'storyframes', 'adobe photoshop', 'photoshop', 'editing',
        'adobe illustrator', 'illustrator', 'adobe after effects', 'after effects',
        'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign',
        'wireframe', 'user research', 'user experience', 'sketch'
    ]
    
    def __init__(self):
        """Initialize CV scoring service."""
        pass
    
    def analyze_cv(self, cv_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """
        Comprehensive CV analysis including scoring, field prediction, and recommendations.
        
        Args:
            cv_data: Structured CV data (name, email, skills, experience, etc.)
            raw_text: Raw extracted text from CV
            
        Returns:
            Analysis results with score, recommendations, predicted field, etc.
        """
        logger.info(f"Starting comprehensive CV analysis for: {cv_data.get('name', 'Unknown')}")
        
        # Calculate resume score
        score_result = self.calculate_resume_score(raw_text, cv_data)
        
        # Predict field based on skills
        predicted_field, recommended_skills = self.predict_field_and_skills(cv_data.get('skills', []))
        
        # Determine candidate level
        candidate_level = self.determine_candidate_level(cv_data, raw_text)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(
            raw_text, 
            cv_data, 
            score_result['score'],
            predicted_field
        )
        
        return {
            'score': score_result['score'],
            'max_score': 100,
            'score_breakdown': score_result['breakdown'],
            'candidate_level': candidate_level,
            'predicted_field': predicted_field,
            'recommended_skills': recommended_skills,
            'recommendations': recommendations,
            'missing_sections': score_result['missing_sections'],
            'present_sections': score_result['present_sections'],
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def calculate_resume_score(self, text: str, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate resume score based on key sections and content quality.
        
        Score breakdown (100 points total):
        - Objective/Summary: 20 points
        - Declaration: 20 points
        - Hobbies/Interests: 20 points
        - Achievements: 20 points
        - Projects: 20 points
        
        Args:
            text: Raw CV text
            cv_data: Structured CV data
            
        Returns:
            Score result with breakdown
        """
        score = 0
        breakdown = {}
        missing_sections = []
        present_sections = []
        text_lower = text.lower()
        
        # Check for Objective/Summary (20 points)
        if self._has_objective(text_lower, cv_data):
            score += 20
            breakdown['objective'] = 20
            present_sections.append('Objective/Summary')
        else:
            breakdown['objective'] = 0
            missing_sections.append('Objective/Summary')
        
        # Check for Declaration (20 points)
        if self._has_declaration(text_lower):
            score += 20
            breakdown['declaration'] = 20
            present_sections.append('Declaration')
        else:
            breakdown['declaration'] = 0
            missing_sections.append('Declaration')
        
        # Check for Hobbies/Interests (20 points)
        if self._has_hobbies(text_lower):
            score += 20
            breakdown['hobbies'] = 20
            present_sections.append('Hobbies/Interests')
        else:
            breakdown['hobbies'] = 0
            missing_sections.append('Hobbies/Interests')
        
        # Check for Achievements (20 points)
        if self._has_achievements(text_lower):
            score += 20
            breakdown['achievements'] = 20
            present_sections.append('Achievements')
        else:
            breakdown['achievements'] = 0
            missing_sections.append('Achievements')
        
        # Check for Projects (20 points)
        if self._has_projects(text_lower, cv_data):
            score += 20
            breakdown['projects'] = 20
            present_sections.append('Projects')
        else:
            breakdown['projects'] = 0
            missing_sections.append('Projects')
        
        return {
            'score': score,
            'breakdown': breakdown,
            'missing_sections': missing_sections,
            'present_sections': present_sections
        }
    
    def _has_objective(self, text: str, cv_data: Dict[str, Any]) -> bool:
        """Check if CV has objective or summary section."""
        objective_keywords = ['objective', 'career objective', 'professional summary', 'summary', 'profile']
        
        # Check in text
        for keyword in objective_keywords:
            if keyword in text:
                return True
        
        # Check in structured data
        if cv_data.get('summary') or cv_data.get('objective'):
            return True
        
        return False
    
    def _has_declaration(self, text: str) -> bool:
        """Check if CV has declaration section."""
        declaration_keywords = ['declaration', 'i hereby declare', 'i declare', 'declared']
        return any(keyword in text for keyword in declaration_keywords)
    
    def _has_hobbies(self, text: str) -> bool:
        """Check if CV has hobbies or interests section."""
        hobby_keywords = ['hobbies', 'interests', 'personal interests', 'activities']
        return any(keyword in text for keyword in hobby_keywords)
    
    def _has_achievements(self, text: str) -> bool:
        """Check if CV has achievements section."""
        achievement_keywords = [
            'achievements', 'accomplishments', 'awards', 'honors', 
            'recognition', 'certifications', 'certificates'
        ]
        return any(keyword in text for keyword in achievement_keywords)
    
    def _has_projects(self, text: str, cv_data: Dict[str, Any]) -> bool:
        """Check if CV has projects section."""
        project_keywords = ['projects', 'portfolio', 'work samples', 'project experience']
        
        # Check in text
        for keyword in project_keywords:
            if keyword in text:
                return True
        
        # Check in structured data
        if cv_data.get('projects') and len(cv_data.get('projects', [])) > 0:
            return True
        
        return False
    
    def predict_field_and_skills(self, current_skills: List[str]) -> Tuple[str, List[str]]:
        """
        Predict career field based on skills and recommend additional skills.
        
        Args:
            current_skills: List of skills from CV
            
        Returns:
            Tuple of (predicted_field, recommended_skills)
        """
        if not current_skills:
            return 'General', []
        
        # Normalize skills
        skills_lower = [skill.lower().strip() for skill in current_skills]
        
        # Count matches for each field
        field_scores = {
            'Data Science': sum(1 for skill in skills_lower if any(kw in skill for kw in self.DS_KEYWORDS)),
            'Web Development': sum(1 for skill in skills_lower if any(kw in skill for kw in self.WEB_KEYWORDS)),
            'Android Development': sum(1 for skill in skills_lower if any(kw in skill for kw in self.ANDROID_KEYWORDS)),
            'iOS Development': sum(1 for skill in skills_lower if any(kw in skill for kw in self.IOS_KEYWORDS)),
            'UI/UX Development': sum(1 for skill in skills_lower if any(kw in skill for kw in self.UIUX_KEYWORDS))
        }
        
        # Get field with highest score
        predicted_field = max(field_scores.items(), key=lambda x: x[1])
        
        if predicted_field[1] == 0:
            return 'General', []
        
        # Get recommended skills for predicted field
        recommended_skills = self._get_recommended_skills(predicted_field[0])
        
        return predicted_field[0], recommended_skills
    
    def _get_recommended_skills(self, field: str) -> List[str]:
        """Get recommended skills for a specific field."""
        recommendations = {
            'Data Science': [
                'Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                'Data Mining', 'Clustering & Classification', 'Data Analytics',
                'Quantitative Analysis', 'Web Scraping', 'ML Algorithms',
                'Keras', 'PyTorch', 'Probability', 'Scikit-learn', 'TensorFlow',
                'Flask', 'Streamlit', 'Pandas', 'NumPy', 'Matplotlib', 'Seaborn'
            ],
            'Web Development': [
                'React', 'Django', 'Node.js', 'React.js', 'PHP', 'Laravel',
                'Magento', 'WordPress', 'JavaScript', 'Angular', 'C#', 'Flask',
                'SDK', 'RESTful APIs', 'GraphQL', 'TypeScript', 'Vue.js',
                'Next.js', 'Express.js', 'MongoDB', 'PostgreSQL', 'Redis'
            ],
            'Android Development': [
                'Android', 'Android Development', 'Flutter', 'Kotlin', 'XML',
                'Java', 'Kivy', 'Git', 'SDK', 'SQLite', 'Jetpack Compose',
                'Material Design', 'Retrofit', 'Room Database', 'Firebase'
            ],
            'iOS Development': [
                'iOS', 'iOS Development', 'Swift', 'Cocoa', 'Cocoa Touch',
                'Xcode', 'Objective-C', 'SQLite', 'Plist', 'StoreKit',
                'UIKit', 'AV Foundation', 'Auto-Layout', 'SwiftUI', 'Core Data'
            ],
            'UI/UX Development': [
                'UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin',
                'Balsamiq', 'Prototyping', 'Wireframes', 'Storyframes',
                'Adobe Photoshop', 'Editing', 'Illustrator', 'After Effects',
                'Premier Pro', 'InDesign', 'Wireframe', 'User Research',
                'Sketch', 'InVision', 'Usability Testing'
            ]
        }
        
        return recommendations.get(field, [])
    
    def determine_candidate_level(self, cv_data: Dict[str, Any], text: str) -> str:
        """
        Determine candidate experience level.
        
        Criteria:
        - Fresher: 0-1 years experience or minimal content
        - Intermediate: 2-4 years experience
        - Experienced: 5+ years experience
        
        Args:
            cv_data: Structured CV data
            text: Raw CV text
            
        Returns:
            Candidate level (Fresher, Intermediate, Experienced)
        """
        # Try to extract years of experience
        experience_years = self._extract_experience_years(cv_data, text)
        
        if experience_years is not None:
            if experience_years <= 1:
                return 'Fresher'
            elif experience_years <= 4:
                return 'Intermediate'
            else:
                return 'Experienced'
        
        # Fallback: analyze experience entries
        experience_list = cv_data.get('experience', [])
        if not experience_list or len(experience_list) == 0:
            return 'Fresher'
        elif len(experience_list) <= 2:
            return 'Intermediate'
        else:
            return 'Experienced'
    
    def _extract_experience_years(self, cv_data: Dict[str, Any], text: str) -> Optional[int]:
        """Extract total years of experience from CV."""
        # Check structured data first
        if 'total_experience_years' in cv_data:
            return cv_data['total_experience_years']
        
        # Try to find patterns like "5 years of experience"
        patterns = [
            r'(\d+)\+?\s*years?\s+of\s+experience',
            r'experience:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s+experience'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return None
    
    def generate_recommendations(
        self, 
        text: str, 
        cv_data: Dict[str, Any], 
        score: int,
        predicted_field: str
    ) -> List[Dict[str, str]]:
        """
        Generate actionable recommendations to improve CV.
        
        Args:
            text: Raw CV text
            cv_data: Structured CV data
            score: Current resume score
            predicted_field: Predicted career field
            
        Returns:
            List of recommendations with type and message
        """
        recommendations = []
        text_lower = text.lower()
        
        # Score-based recommendations
        if score < 40:
            recommendations.append({
                'type': 'critical',
                'message': 'Your resume needs significant improvement. Focus on adding missing sections.'
            })
        elif score < 70:
            recommendations.append({
                'type': 'warning',
                'message': 'Your resume is good but can be improved. Add missing sections to increase your score.'
            })
        else:
            recommendations.append({
                'type': 'success',
                'message': 'Excellent! Your resume has most of the essential sections.'
            })
        
        # Section-specific recommendations
        if not self._has_objective(text_lower, cv_data):
            recommendations.append({
                'type': 'tip',
                'message': 'Add a career objective or professional summary to give recruiters insight into your career goals.'
            })
        
        if not self._has_declaration(text_lower):
            recommendations.append({
                'type': 'tip',
                'message': 'Add a declaration to assure recruiters that all information is true and acknowledged by you.'
            })
        
        if not self._has_hobbies(text_lower):
            recommendations.append({
                'type': 'tip',
                'message': 'Add hobbies/interests to showcase your personality and cultural fit.'
            })
        
        if not self._has_achievements(text_lower):
            recommendations.append({
                'type': 'tip',
                'message': 'Add achievements, awards, or certifications to demonstrate your capabilities.'
            })
        
        if not self._has_projects(text_lower, cv_data):
            recommendations.append({
                'type': 'tip',
                'message': 'Add relevant projects to showcase practical experience and skills application.'
            })
        
        # Field-specific recommendations
        if predicted_field != 'General':
            recommendations.append({
                'type': 'info',
                'message': f'Based on your skills, you appear to be targeting {predicted_field} roles. Consider adding relevant keywords and technologies.'
            })
        
        # Contact information recommendations
        if not cv_data.get('email'):
            recommendations.append({
                'type': 'critical',
                'message': 'Add your email address for recruiters to contact you.'
            })
        
        if not cv_data.get('phone'):
            recommendations.append({
                'type': 'warning',
                'message': 'Add your phone number for direct contact.'
            })
        
        # Skills recommendations
        skills = cv_data.get('skills', [])
        if len(skills) < 5:
            recommendations.append({
                'type': 'tip',
                'message': 'Add more relevant skills to your resume. Aim for at least 8-10 key skills.'
            })
        
        return recommendations
    
    def get_ats_optimization_tips(self, cv_data: Dict[str, Any]) -> List[str]:
        """
        Generate ATS optimization tips.
        
        Args:
            cv_data: Structured CV data
            
        Returns:
            List of ATS optimization tips
        """
        tips = []
        
        tips.append("Use standard section headings like 'Work Experience', 'Education', 'Skills'")
        tips.append("Include relevant keywords from job descriptions")
        tips.append("Use simple, clean formatting without tables or graphics")
        tips.append("Save resume as .docx or .pdf format")
        tips.append("Use bullet points for easy readability")
        tips.append("Quantify achievements with numbers and metrics")
        tips.append("Avoid headers and footers as ATS may not read them")
        tips.append("Use standard fonts like Arial, Calibri, or Times New Roman")
        tips.append("Include both acronyms and full terms (e.g., 'AI' and 'Artificial Intelligence')")
        tips.append("Tailor your resume for each job application")
        
        return tips
