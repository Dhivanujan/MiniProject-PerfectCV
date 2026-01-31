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
    
    def score_cv(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a CV based on its content.
        
        Args:
            cv_data: Structured CV data (entities)
            
        Returns:
            Dictionary with overall_score and breakdown
        """
        # Build raw text from cv_data for scoring
        text_parts = []
        if cv_data.get('summary'):
            text_parts.append(cv_data.get('summary'))
        if cv_data.get('skills'):
            text_parts.append(' '.join(cv_data.get('skills', [])))
        if cv_data.get('experience'):
            for exp in cv_data.get('experience', []):
                if isinstance(exp, dict):
                    text_parts.append(exp.get('title', ''))
                    text_parts.append(exp.get('company', ''))
                    desc = exp.get('description', '')
                    if isinstance(desc, list):
                        text_parts.extend(desc)
                    elif desc:
                        text_parts.append(desc)
        if cv_data.get('education'):
            for edu in cv_data.get('education', []):
                if isinstance(edu, dict):
                    text_parts.append(edu.get('degree', ''))
                    text_parts.append(edu.get('institution', ''))
        if cv_data.get('projects'):
            for proj in cv_data.get('projects', []):
                if isinstance(proj, dict):
                    text_parts.append(proj.get('name', ''))
                    text_parts.append(proj.get('description', ''))
        
        raw_text = ' '.join(filter(None, text_parts))
        
        # Use calculate_resume_score
        score_result = self.calculate_resume_score(raw_text, cv_data)
        
        # Get recommendations
        predicted_field, recommended_skills = self.predict_field_and_skills(cv_data.get('skills', []))
        
        return {
            'overall_score': score_result['score'],
            'score': score_result['score'],
            'max_score': 100,
            'breakdown': score_result['breakdown'],
            'missing_sections': score_result['missing_sections'],
            'present_sections': score_result['present_sections'],
            'predicted_field': predicted_field,
            'recommended_skills': recommended_skills,
            'recommendations': self.generate_recommendations(raw_text, cv_data, score_result['score'], predicted_field)
        }
    
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
        Calculate resume score based on comprehensive criteria.
        
        Score breakdown (100 points total):
        - Contact Information: 10 points (name, email, phone)
        - Professional Summary: 15 points
        - Work Experience: 25 points
        - Education: 15 points
        - Skills: 15 points
        - Projects: 10 points
        - Certifications/Achievements: 5 points
        - Additional Sections: 5 points (hobbies, languages, etc.)
        
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
        
        # 1. Contact Information (10 points)
        contact_score = 0
        if cv_data.get('name'):
            contact_score += 4
        if cv_data.get('email'):
            contact_score += 3
        if cv_data.get('phone'):
            contact_score += 3
        breakdown['contact_info'] = contact_score
        score += contact_score
        if contact_score >= 7:
            present_sections.append('Contact Information')
        else:
            missing_sections.append('Contact Information')
        
        # 2. Professional Summary/Objective (15 points)
        summary_score = 0
        summary = cv_data.get('summary', '') or ''
        if self._has_objective(text_lower, cv_data):
            summary_score = 8  # Base score for having summary
            # Bonus for length/quality
            if len(summary) > 50:
                summary_score += 3
            if len(summary) > 150:
                summary_score += 2
            if len(summary) > 250:
                summary_score += 2
        breakdown['summary'] = min(summary_score, 15)
        score += breakdown['summary']
        if summary_score >= 8:
            present_sections.append('Professional Summary')
        else:
            missing_sections.append('Professional Summary')
        
        # 3. Work Experience (25 points)
        exp_score = 0
        experience = cv_data.get('experience', []) or []
        if experience:
            exp_count = len(experience)
            exp_score = min(exp_count * 6, 15)  # Up to 15 for having experiences
            
            # Bonus for detailed descriptions
            for exp in experience[:3]:  # Check first 3
                if isinstance(exp, dict):
                    desc = exp.get('description', '')
                    if isinstance(desc, list) and len(desc) >= 2:
                        exp_score += 3
                    elif isinstance(desc, str) and len(desc) > 50:
                        exp_score += 2
        breakdown['experience'] = min(exp_score, 25)
        score += breakdown['experience']
        if exp_score >= 6:
            present_sections.append('Work Experience')
        else:
            missing_sections.append('Work Experience')
        
        # 4. Education (15 points)
        edu_score = 0
        education = cv_data.get('education', []) or []
        if education:
            edu_score = 8  # Base score
            for edu in education:
                if isinstance(edu, dict):
                    if edu.get('degree'):
                        edu_score += 2
                    if edu.get('institution'):
                        edu_score += 2
                    if edu.get('year') or edu.get('gpa'):
                        edu_score += 1
        breakdown['education'] = min(edu_score, 15)
        score += breakdown['education']
        if edu_score >= 8:
            present_sections.append('Education')
        else:
            missing_sections.append('Education')
        
        # 5. Skills (15 points)
        skills_score = 0
        skills = cv_data.get('skills', []) or []
        if skills:
            skill_count = len(skills)
            if skill_count >= 3:
                skills_score = 6
            if skill_count >= 6:
                skills_score = 9
            if skill_count >= 10:
                skills_score = 12
            if skill_count >= 15:
                skills_score = 15
        breakdown['skills'] = skills_score
        score += skills_score
        if skills_score >= 6:
            present_sections.append('Skills')
        else:
            missing_sections.append('Skills')
        
        # 6. Projects (10 points)
        proj_score = 0
        projects = cv_data.get('projects', []) or []
        if projects or self._has_projects(text_lower, cv_data):
            proj_count = len(projects) if projects else 1
            proj_score = min(proj_count * 3, 7)  # Up to 7 for count
            
            # Bonus for detailed projects
            for proj in projects[:2]:
                if isinstance(proj, dict):
                    if proj.get('description') and len(str(proj.get('description', ''))) > 30:
                        proj_score += 1
                    if proj.get('technologies'):
                        proj_score += 1
        breakdown['projects'] = min(proj_score, 10)
        score += breakdown['projects']
        if proj_score >= 3:
            present_sections.append('Projects')
        else:
            missing_sections.append('Projects')
        
        # 7. Certifications/Achievements (5 points)
        cert_score = 0
        certs = cv_data.get('certifications', []) or []
        if certs or self._has_achievements(text_lower):
            cert_score = min(len(certs) * 2 + 1, 5) if certs else 3
        breakdown['certifications'] = cert_score
        score += cert_score
        if cert_score >= 1:
            present_sections.append('Certifications/Achievements')
        else:
            missing_sections.append('Certifications/Achievements')
        
        # 8. Additional Sections (5 points)
        additional_score = 0
        if self._has_hobbies(text_lower):
            additional_score += 2
        if cv_data.get('languages') or 'languages' in text_lower or 'language' in text_lower:
            additional_score += 2
        if self._has_declaration(text_lower):
            additional_score += 1
        breakdown['additional'] = min(additional_score, 5)
        score += breakdown['additional']
        if additional_score >= 2:
            present_sections.append('Additional Sections')
        
        # Ensure score doesn't exceed 100
        final_score = min(score, 100)
        
        return {
            'score': final_score,
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
        elif len(skills) < 10:
            recommendations.append({
                'type': 'tip',
                'message': 'Consider adding a few more technical and soft skills to strengthen your profile.'
            })
        
        # Experience recommendations
        experience = cv_data.get('experience', [])
        if not experience:
            recommendations.append({
                'type': 'warning',
                'message': 'Add work experience or internship details to demonstrate your professional background.'
            })
        elif len(experience) < 2:
            recommendations.append({
                'type': 'tip',
                'message': 'Add more work experience entries or include volunteer/freelance work.'
            })
        
        # Education recommendations
        education = cv_data.get('education', [])
        if not education:
            recommendations.append({
                'type': 'warning',
                'message': 'Add your educational qualifications to strengthen your resume.'
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
