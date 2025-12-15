"""
CV Template Generator with Examples
Creates better CV examples based on uploaded CV information.
"""
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CVTemplateGenerator:
    """Generates professional CV templates and examples."""
    
    def __init__(self):
        self.action_verbs = [
            "Developed", "Implemented", "Designed", "Led", "Managed", "Optimized",
            "Architected", "Engineered", "Streamlined", "Automated", "Enhanced",
            "Spearheaded", "Collaborated", "Delivered", "Achieved", "Created",
            "Established", "Improved", "Reduced", "Increased", "Built"
        ]
        
        self.quantifiers = [
            "by 50%", "by 40%", "by 30%", "for 1M+ users", "for 10K+ customers",
            "serving 100K+ requests/day", "handling 5K+ transactions",
            "reducing costs by $50K", "improving performance by 60%"
        ]
    
    def enhance_cv_professionally(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a professionally enhanced version of the CV.
        
        Args:
            cv_data: Original CV data
            
        Returns:
            Enhanced CV data with better formatting and content
        """
        enhanced_cv = cv_data.copy()
        
        # Enhance summary
        enhanced_cv['summary'] = self._enhance_summary(
            cv_data.get('summary', ''),
            cv_data.get('experience', []),
            cv_data.get('skills', [])
        )
        
        # Enhance experience descriptions
        if cv_data.get('experience'):
            enhanced_cv['experience'] = [
                self._enhance_experience(exp) 
                for exp in cv_data['experience']
            ]
        
        # Enhance skills with categorization
        if cv_data.get('skills'):
            enhanced_cv['skills_categorized'] = self._categorize_skills(
                cv_data['skills']
            )
        
        # Add achievement highlights
        enhanced_cv['highlights'] = self._extract_highlights(
            cv_data.get('experience', []),
            cv_data.get('projects', [])
        )
        
        return enhanced_cv
    
    def _enhance_summary(self, original_summary: str, experience: List, skills: List) -> str:
        """Enhance professional summary."""
        if not original_summary or len(original_summary) < 50:
            # Generate a new summary
            years_exp = len(experience)
            top_skills = skills[:5] if len(skills) >= 5 else skills
            
            if years_exp >= 3:
                level = "Senior"
            elif years_exp >= 1:
                level = "Experienced"
            else:
                level = "Skilled"
            
            summary = f"{level} professional with proven expertise in {', '.join(top_skills[:3])}. "
            summary += f"Demonstrated track record of delivering high-quality solutions and driving technical excellence. "
            summary += f"Proficient in {', '.join(top_skills[3:5])} with strong problem-solving abilities and collaborative mindset."
            
            return summary
        
        # Enhance existing summary
        enhanced = original_summary
        if not any(word in enhanced.lower() for word in ['experienced', 'skilled', 'professional']):
            enhanced = "Experienced " + enhanced.lower()
        
        return enhanced
    
    def _enhance_experience(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance work experience with action verbs and metrics."""
        enhanced_exp = experience.copy()
        
        description = experience.get('description', '')
        
        # If description is too short or doesn't have action verbs
        if len(description) < 100 or not any(verb in description for verb in self.action_verbs):
            # Enhance the description
            role = experience.get('role', '')
            company = experience.get('company', '')
            
            bullets = []
            
            # Create impact-driven bullet points
            if 'senior' in role.lower() or 'lead' in role.lower():
                bullets.append(f"Led development team in delivering critical features and technical solutions")
                bullets.append(f"Architected scalable systems serving thousands of concurrent users")
                bullets.append(f"Mentored junior developers and established best practices")
            else:
                bullets.append(f"Developed and maintained high-performance applications and features")
                bullets.append(f"Collaborated with cross-functional teams to deliver project objectives")
                bullets.append(f"Implemented code optimizations improving system efficiency")
            
            enhanced_exp['description'] = ' • '.join(bullets)
        
        return enhanced_exp
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into groups."""
        categories = {
            'Programming Languages': [],
            'Frameworks & Libraries': [],
            'Databases': [],
            'Cloud & DevOps': [],
            'Tools & Technologies': []
        }
        
        programming_keywords = ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'php', 'ruby']
        framework_keywords = ['react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'express', 'node', 'spring']
        database_keywords = ['sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'dynamodb', 'cassandra']
        cloud_keywords = ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins', 'ci/cd']
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized = False
            
            if any(kw in skill_lower for kw in programming_keywords):
                categories['Programming Languages'].append(skill)
                categorized = True
            elif any(kw in skill_lower for kw in framework_keywords):
                categories['Frameworks & Libraries'].append(skill)
                categorized = True
            elif any(kw in skill_lower for kw in database_keywords):
                categories['Databases'].append(skill)
                categorized = True
            elif any(kw in skill_lower for kw in cloud_keywords):
                categories['Cloud & DevOps'].append(skill)
                categorized = True
            
            if not categorized:
                categories['Tools & Technologies'].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}
    
    def _extract_highlights(self, experience: List, projects: List) -> List[str]:
        """Extract key achievements and highlights."""
        highlights = []
        
        # Extract from experience
        for exp in experience:
            desc = exp.get('description', '')
            # Look for quantifiable achievements
            if any(char.isdigit() for char in desc):
                # Extract first sentence with numbers
                sentences = desc.split('.')
                for sentence in sentences:
                    if any(char.isdigit() for char in sentence):
                        highlights.append(sentence.strip())
                        break
        
        # Extract from projects
        for proj in projects:
            desc = proj.get('description', '')
            if any(char.isdigit() for char in desc):
                highlights.append(f"{proj.get('name', 'Project')}: {desc[:100]}")
        
        return highlights[:5]  # Top 5 highlights
    
    def create_example_cvs(self, field: str, level: str = "mid") -> List[Dict[str, Any]]:
        """
        Create example CVs for a specific field and level.
        
        Args:
            field: Career field (Data Science, Web Development, etc.)
            level: Experience level (junior, mid, senior)
            
        Returns:
            List of example CV templates
        """
        templates = []
        
        if field.lower() == "data science":
            templates.append(self._create_data_science_cv(level))
        elif field.lower() in ["web development", "full stack"]:
            templates.append(self._create_web_dev_cv(level))
        elif field.lower() == "mobile development":
            templates.append(self._create_mobile_dev_cv(level))
        else:
            templates.append(self._create_generic_cv(field, level))
        
        return templates
    
    def _create_data_science_cv(self, level: str) -> Dict[str, Any]:
        """Create a Data Science CV template."""
        if level == "senior":
            return {
                "name": "Dr. Sarah Chen",
                "email": "sarah.chen@example.com",
                "phone": "+1-555-234-5678",
                "summary": "Senior Data Scientist with 8+ years of experience building ML models at scale. Expertise in deep learning, NLP, and MLOps. Led teams delivering business impact through advanced analytics and AI solutions.",
                "skills": [
                    "Python", "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy",
                    "SQL", "Spark", "AWS SageMaker", "MLflow", "Docker", "Kubernetes",
                    "Deep Learning", "NLP", "Computer Vision", "Statistical Modeling"
                ],
                "experience": [
                    {
                        "role": "Senior Data Scientist",
                        "company": "Tech Innovations Inc.",
                        "years": "2020 - Present",
                        "description": "Led ML team of 5 data scientists building recommendation systems serving 5M+ users. Architected end-to-end ML pipeline reducing model deployment time by 70%. Implemented deep learning models improving prediction accuracy by 25%."
                    },
                    {
                        "role": "Data Scientist",
                        "company": "Analytics Corp",
                        "years": "2017 - 2020",
                        "description": "Developed predictive models for customer churn reducing attrition by 30%. Built NLP solution processing 1M+ documents monthly. Collaborated with engineering teams to productionize 10+ ML models."
                    }
                ],
                "education": [
                    {
                        "degree": "Ph.D. in Computer Science (Machine Learning)",
                        "institution": "Stanford University",
                        "year": "2017",
                        "details": "Thesis: Deep Learning for Natural Language Understanding"
                    }
                ],
                "projects": [
                    {
                        "name": "Real-time Fraud Detection System",
                        "description": "Built ML system detecting fraudulent transactions with 95% accuracy, processing 10K+ transactions/second",
                        "technologies": ["Python", "TensorFlow", "Kafka", "Redis", "AWS"]
                    }
                ],
                "certifications": [
                    "AWS Certified Machine Learning Specialty",
                    "TensorFlow Developer Certificate"
                ]
            }
        else:
            return {
                "name": "Alex Johnson",
                "email": "alex.johnson@example.com",
                "phone": "+1-555-345-6789",
                "summary": "Data Scientist with 3+ years experience in machine learning and data analysis. Skilled in Python, ML algorithms, and data visualization. Passionate about solving business problems through data-driven insights.",
                "skills": [
                    "Python", "Pandas", "NumPy", "Scikit-learn", "Matplotlib", "Seaborn",
                    "SQL", "Jupyter", "Git", "Machine Learning", "Data Visualization", "Statistics"
                ],
                "experience": [
                    {
                        "role": "Data Scientist",
                        "company": "StartupXYZ",
                        "years": "2021 - Present",
                        "description": "Developed ML models for customer segmentation improving marketing ROI by 40%. Created data pipelines processing 100K+ records daily. Built dashboards visualizing key business metrics for stakeholders."
                    }
                ],
                "education": [
                    {
                        "degree": "Master of Science in Data Science",
                        "institution": "University of California",
                        "year": "2021",
                        "details": "GPA: 3.9/4.0"
                    }
                ],
                "projects": [
                    {
                        "name": "Customer Churn Prediction",
                        "description": "ML model predicting customer churn with 85% accuracy using Random Forest and XGBoost",
                        "technologies": ["Python", "Scikit-learn", "Pandas", "Flask"]
                    }
                ],
                "certifications": [
                    "Google Data Analytics Professional Certificate"
                ]
            }
    
    def _create_web_dev_cv(self, level: str) -> Dict[str, Any]:
        """Create a Web Development CV template."""
        return {
            "name": "Maria Rodriguez",
            "email": "maria.rodriguez@example.com",
            "phone": "+1-555-456-7890",
            "summary": "Full-Stack Developer with 5+ years building scalable web applications. Expert in React, Node.js, and cloud technologies. Delivered 20+ production applications serving millions of users.",
            "skills": [
                "JavaScript", "TypeScript", "React", "Node.js", "Express", "Python",
                "MongoDB", "PostgreSQL", "AWS", "Docker", "Git", "REST APIs", "GraphQL"
            ],
            "experience": [
                {
                    "role": "Senior Full-Stack Developer",
                    "company": "WebTech Solutions",
                    "years": "2021 - Present",
                    "description": "Architected microservices handling 1M+ daily requests. Led frontend team building responsive React applications. Optimized database queries reducing response time by 60%. Implemented CI/CD pipeline automating deployments."
                },
                {
                    "role": "Full-Stack Developer",
                    "company": "Digital Agency",
                    "years": "2019 - 2021",
                    "description": "Developed 15+ client websites using React and Node.js. Built RESTful APIs serving mobile and web applications. Collaborated with design team implementing pixel-perfect UI/UX."
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Science in Computer Science",
                    "institution": "State University",
                    "year": "2019",
                    "details": "Focus: Web Technologies and Software Engineering"
                }
            ],
            "projects": [
                {
                    "name": "E-Commerce Platform",
                    "description": "Full-featured e-commerce solution with payment integration, inventory management, and admin dashboard",
                    "technologies": ["React", "Node.js", "MongoDB", "Stripe", "AWS S3"]
                },
                {
                    "name": "Real-time Collaboration Tool",
                    "description": "WebSocket-based collaboration app supporting 500+ concurrent users with real-time updates",
                    "technologies": ["React", "Socket.io", "Redis", "PostgreSQL"]
                }
            ],
            "certifications": [
                "AWS Certified Developer Associate",
                "Meta React Developer Certificate"
            ]
        }
    
    def _create_mobile_dev_cv(self, level: str) -> Dict[str, Any]:
        """Create a Mobile Development CV template."""
        return {
            "name": "James Kim",
            "email": "james.kim@example.com",
            "phone": "+1-555-567-8901",
            "summary": "Mobile Developer with 4+ years creating iOS and Android applications. Expertise in Swift, Kotlin, and React Native. Published 10+ apps with 500K+ combined downloads.",
            "skills": [
                "Swift", "Kotlin", "React Native", "iOS", "Android", "Firebase",
                "REST APIs", "Git", "Xcode", "Android Studio", "UI/UX Design"
            ],
            "experience": [
                {
                    "role": "Senior Mobile Developer",
                    "company": "MobileFirst Inc.",
                    "years": "2022 - Present",
                    "description": "Led development of flagship iOS app with 200K+ active users. Implemented offline-first architecture improving user retention by 35%. Optimized app performance reducing crashes by 90%."
                },
                {
                    "role": "Mobile Developer",
                    "company": "App Studios",
                    "years": "2020 - 2022",
                    "description": "Developed cross-platform apps using React Native. Integrated third-party APIs and payment systems. Maintained 4.5+ star rating across App Store and Google Play."
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Engineering in Software Engineering",
                    "institution": "Tech University",
                    "year": "2020",
                    "details": "Specialization: Mobile Application Development"
                }
            ],
            "projects": [
                {
                    "name": "Fitness Tracking App",
                    "description": "iOS app with 50K+ downloads featuring workout tracking, social features, and health data integration",
                    "technologies": ["Swift", "HealthKit", "Firebase", "Core Data"]
                }
            ],
            "certifications": [
                "Apple iOS Developer Certification",
                "Google Associate Android Developer"
            ]
        }
    
    def _create_generic_cv(self, field: str, level: str) -> Dict[str, Any]:
        """Create a generic CV template."""
        return {
            "name": "Professional Name",
            "email": "professional@example.com",
            "phone": "+1-555-678-9012",
            "summary": f"Experienced {field} professional with proven track record of delivering high-quality results. Strong technical skills and collaborative mindset.",
            "skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
            "experience": [
                {
                    "role": f"Senior {field} Specialist",
                    "company": "Company Name",
                    "years": "2020 - Present",
                    "description": "Led projects delivering measurable business impact. Collaborated with teams to achieve organizational goals."
                }
            ],
            "education": [
                {
                    "degree": "Bachelor's Degree",
                    "institution": "University",
                    "year": "2020",
                    "details": "Relevant coursework and achievements"
                }
            ],
            "projects": [],
            "certifications": []
        }


# Singleton instance
cv_template_generator = CVTemplateGenerator()


if __name__ == "__main__":
    # Test the generator
    generator = CVTemplateGenerator()
    
    # Create example CVs
    ds_cv = generator.create_example_cvs("Data Science", "senior")[0]
    print(json.dumps(ds_cv, indent=2))
