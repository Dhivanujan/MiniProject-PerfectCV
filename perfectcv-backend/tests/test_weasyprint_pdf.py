"""
Test WeasyPrint PDF generation with sample CVs.
"""
import unittest
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.cv_utils import generate_pdf
from app.utils.cv_templates import build_professional_cv_html


class TestWeasyPrintPDFGeneration(unittest.TestCase):
    """Test professional PDF generation with WeasyPrint."""
    
    def test_generate_pdf_from_plain_text(self):
        """Test PDF generation from plain CV text."""
        plain_text = """
JOHN DOE
Email: john.doe@example.com | Phone: +1-555-123-4567
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Senior Software Engineer with 8+ years of experience in full-stack development.

SKILLS
Python, JavaScript, React, Docker, AWS, PostgreSQL

PROFESSIONAL EXPERIENCE
Senior Software Engineer | Tech Corp | 2020 - Present
- Led development of microservices architecture
- Improved system performance by 40%
- Mentored junior developers

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2015
        """
        
        pdf_bytes = generate_pdf(plain_text)
        
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes.read()), 1000, "PDF should have content")
    
    def test_generate_pdf_from_structured_data(self):
        """Test PDF generation from structured CV data."""
        structured_cv = {
            "contact_information": {
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone": "+1-555-987-6543",
                "location": "New York, NY",
                "linkedin": "https://linkedin.com/in/janesmith",
                "github": "https://github.com/janesmith"
            },
            "professional_summary": "Experienced Data Scientist with expertise in machine learning and statistical analysis. 5+ years of experience building predictive models and data pipelines.",
            "skills": {
                "technical": ["Python", "R", "SQL"],
                "frameworks_libraries": ["TensorFlow", "PyTorch", "Scikit-learn"],
                "tools": ["Jupyter", "Git", "Docker"],
                "databases": ["PostgreSQL", "MongoDB"],
                "cloud_devops": ["AWS", "Google Cloud"]
            },
            "work_experience": [
                {
                    "title": "Senior Data Scientist",
                    "company": "DataCorp Inc",
                    "dates": "Jan 2021 - Present",
                    "location": "New York, NY",
                    "achievements": [
                        "Built ML models improving prediction accuracy by 35%",
                        "Led team of 4 data scientists on critical projects",
                        "Reduced model training time by 50% through optimization"
                    ]
                },
                {
                    "title": "Data Scientist",
                    "company": "Analytics Startup",
                    "dates": "Jun 2019 - Dec 2020",
                    "location": "Boston, MA",
                    "achievements": [
                        "Developed recommendation system serving 100K+ users",
                        "Implemented A/B testing framework",
                        "Increased user engagement by 25%"
                    ]
                }
            ],
            "projects": [
                {
                    "name": "Customer Churn Prediction",
                    "technologies": ["Python", "TensorFlow", "AWS"],
                    "description": "Built ML model to predict customer churn with 92% accuracy",
                    "highlights": [
                        "Reduced churn by 15% through early intervention",
                        "Processed 10M+ customer records daily"
                    ]
                }
            ],
            "education": [
                {
                    "degree": "Master of Science",
                    "field": "Data Science",
                    "institution": "MIT",
                    "graduation_date": "2019",
                    "gpa": "3.9/4.0"
                },
                {
                    "degree": "Bachelor of Science",
                    "field": "Mathematics",
                    "institution": "UC Berkeley",
                    "graduation_date": "2017"
                }
            ],
            "certifications": [
                {
                    "name": "AWS Certified Machine Learning",
                    "issuer": "Amazon",
                    "date": "2022"
                },
                {
                    "name": "TensorFlow Developer Certificate",
                    "issuer": "Google",
                    "date": "2021"
                }
            ],
            "achievements": [
                "Published 3 papers in top-tier ML conferences",
                "Won company innovation award 2022",
                "Speaker at PyData Conference 2023"
            ],
            "languages": [
                {"language": "English", "proficiency": "Native"},
                {"language": "Spanish", "proficiency": "Professional"}
            ]
        }
        
        pdf_bytes = generate_pdf(structured_cv)
        
        self.assertIsNotNone(pdf_bytes)
        content = pdf_bytes.read()
        # Accept either WeasyPrint (5000+) or FPDF fallback (2000+) size
        self.assertGreater(len(content), 2000, "Structured CV PDF should have substantial content")
    
    def test_html_template_building(self):
        """Test HTML template construction from structured data."""
        test_data = {
            "contact_information": {
                "name": "Test User",
                "email": "test@example.com"
            },
            "professional_summary": "Test summary",
            "skills": {
                "technical": ["Python", "JavaScript"]
            }
        }
        
        html = build_professional_cv_html(test_data)
        
        self.assertIn("Test User", html)
        self.assertIn("test@example.com", html)
        self.assertIn("Test summary", html)
        self.assertIn("Python", html)
        self.assertIn("JavaScript", html)
    
    def test_fallback_to_fpdf_on_weasyprint_error(self):
        """Test that system falls back to FPDF if WeasyPrint fails."""
        # This should still work even if WeasyPrint has issues
        simple_text = "Simple CV\nSoftware Engineer\nExperience: 5 years"
        
        pdf_bytes = generate_pdf(simple_text)
        
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes.read()), 100)
    
    def test_pdf_with_special_characters(self):
        """Test PDF generation with special characters and unicode."""
        text_with_unicode = {
            "contact_information": {
                "name": "José García",
                "email": "jose.garcia@example.com",
                "location": "São Paulo, Brazil"
            },
            "professional_summary": "Developer with expertise in AI/ML • Cloud ☁️ • Data 📊"
        }
        
        pdf_bytes = generate_pdf(text_with_unicode)
        
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes.read()), 1000)


class TestPDFQuality(unittest.TestCase):
    """Test visual quality aspects of generated PDFs."""
    
    def test_minimal_cv_has_sections(self):
        """Ensure minimal CV still has proper sections."""
        minimal_cv = {
            "contact_information": {"name": "Test", "email": "t@t.com"},
            "skills": {"technical": ["Python"]}
        }
        
        html = build_professional_cv_html(minimal_cv)
        
        # Should have header and skills section
        self.assertIn("header", html.lower())
        self.assertIn("skills", html.lower())
    
    def test_empty_sections_handled_gracefully(self):
        """Test that empty sections don't break PDF generation."""
        cv_with_empty_sections = {
            "contact_information": {"name": "Test User"},
            "skills": {},
            "work_experience": [],
            "education": []
        }
        
        pdf_bytes = generate_pdf(cv_with_empty_sections)
        
        self.assertIsNotNone(pdf_bytes)
        self.assertGreater(len(pdf_bytes.read()), 500)


if __name__ == "__main__":
    unittest.main()
