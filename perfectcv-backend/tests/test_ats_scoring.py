"""
Tests for the enhanced ATS scoring system and conditional CV generation.
"""
import unittest
from app.utils.cv_utils import compute_ats_score, analyze_ats_score_detailed


class TestATSScoring(unittest.TestCase):
    """Test comprehensive ATS scoring algorithm."""
    
    def test_high_quality_cv_scores_above_75(self):
        """A well-formatted CV with all sections should score above 75."""
        high_quality_cv = """
        John Doe
        Email: john.doe@example.com | Phone: +1-555-123-4567 | Location: San Francisco, CA
        LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe
        
        PROFESSIONAL SUMMARY
        Senior Software Engineer with 8+ years of experience developing scalable web applications 
        using Python, React, and cloud technologies. Led teams of 5+ developers and increased 
        system performance by 40% through optimization initiatives.
        
        TECHNICAL SKILLS
        • Programming Languages: Python, JavaScript, TypeScript, Java
        • Frameworks: React, Django, Flask, Node.js
        • Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD
        • Databases: PostgreSQL, MongoDB, Redis
        • Tools: Git, Jira, Jenkins
        
        PROFESSIONAL EXPERIENCE
        Senior Software Engineer | Tech Corp | Jan 2020 - Present
        • Led development of microservices architecture serving 1M+ daily users
        • Improved API response time by 45% through database optimization
        • Mentored 3 junior developers and conducted code reviews
        • Implemented CI/CD pipeline reducing deployment time by 60%
        
        Software Engineer | StartupXYZ | Jun 2017 - Dec 2019
        • Built React-based dashboard used by 10,000+ customers
        • Developed RESTful APIs processing 500K requests/day
        • Reduced server costs by 30% through AWS optimization
        
        EDUCATION
        Bachelor of Science in Computer Science — University of California, Berkeley (2017)
        GPA: 3.8/4.0
        
        CERTIFICATIONS
        • AWS Certified Solutions Architect — 2021
        • Certified Kubernetes Administrator — 2022
        
        ACHIEVEMENTS
        • Winner of Internal Hackathon 2021
        • Published research paper on distributed systems
        """
        
        score, missing, found = compute_ats_score(high_quality_cv, "software")
        self.assertGreaterEqual(score, 75, f"High-quality CV should score >= 75, got {score}")
    
    def test_poor_cv_scores_below_75(self):
        """A poorly formatted CV with missing sections should score below 75."""
        poor_cv = """
        Jane Smith
        I am looking for a job in software engineering.
        I know Python and some web development.
        Worked at a company for 2 years.
        """
        
        score, missing, found = compute_ats_score(poor_cv, "software")
        self.assertLess(score, 75, f"Poor-quality CV should score < 75, got {score}")
    
    def test_detailed_analysis_provides_recommendations(self):
        """Detailed analysis should provide specific recommendations."""
        cv_text = """
        Bob Developer
        bob@email.com
        
        I have experience in programming.
        """
        
        analysis = analyze_ats_score_detailed(cv_text, "software")
        
        self.assertIn("overall_score", analysis)
        self.assertIn("breakdown", analysis)
        self.assertIn("missing_elements", analysis)
        self.assertIn("recommendations", analysis)
        self.assertGreater(len(analysis["recommendations"]), 0, "Should provide recommendations")
        self.assertGreater(len(analysis["missing_elements"]), 0, "Should identify missing elements")
    
    def test_scoring_breakdown_components(self):
        """Test individual scoring components."""
        cv_with_contact = """
        Alice Engineer
        Email: alice@example.com
        Phone: +1-555-999-8888
        Location: New York, NY
        """
        
        analysis = analyze_ats_score_detailed(cv_with_contact)
        breakdown = analysis["breakdown"]
        
        # Should score points for contact info
        self.assertGreater(breakdown.get("Contact Information", 0), 0)
    
    def test_keyword_matching(self):
        """Test domain keyword matching contributes to score."""
        cv_with_keywords = """
        Software Engineer
        john@test.com | +1-555-0000
        
        PROFESSIONAL SUMMARY
        Experienced developer specializing in Python, React, and cloud technologies.
        
        SKILLS
        Python, JavaScript, React, Docker, Kubernetes, AWS, PostgreSQL, Git, CI/CD
        
        EXPERIENCE
        Software Engineer at TechCo (2020-2023)
        • Developed microservices using Python and Docker
        • Implemented CI/CD pipelines
        """
        
        score_with_domain, missing, found = compute_ats_score(cv_with_keywords, "software")
        score_without_domain, _, _ = compute_ats_score(cv_with_keywords, None)
        
        # Score with domain keywords should be higher
        self.assertGreater(score_with_domain, score_without_domain)
        self.assertGreater(len(found), 0, "Should find domain keywords")
    
    def test_action_verbs_scoring(self):
        """Test that action verbs contribute to ATS score."""
        cv_with_action_verbs = """
        Developer
        dev@test.com
        
        EXPERIENCE
        • Led team of 5 developers
        • Developed scalable APIs
        • Managed cloud infrastructure
        • Implemented security features
        • Optimized database queries
        """
        
        score_with_verbs, _, _ = compute_ats_score(cv_with_action_verbs)
        
        cv_without_verbs = """
        Developer
        dev@test.com
        
        EXPERIENCE
        • Responsible for team
        • Worked on APIs
        • Handled infrastructure
        """
        
        score_without_verbs, _, _ = compute_ats_score(cv_without_verbs)
        
        # CV with action verbs should score higher
        self.assertGreater(score_with_verbs, score_without_verbs)
    
    def test_quantifiable_achievements_scoring(self):
        """Test that numbers/metrics improve ATS score."""
        cv_with_metrics = """
        Engineer
        eng@test.com
        
        EXPERIENCE
        • Improved performance by 40%
        • Managed team of 10 developers
        • Reduced costs by $50,000 annually
        • Served 1M+ users
        • Increased revenue by 25%
        """
        
        score_with_metrics, _, _ = compute_ats_score(cv_with_metrics)
        
        cv_without_metrics = """
        Engineer
        eng@test.com
        
        EXPERIENCE
        • Improved performance significantly
        • Managed large team
        • Reduced costs substantially
        • Served many users
        """
        
        score_without_metrics, _, _ = compute_ats_score(cv_without_metrics)
        
        # CV with quantifiable metrics should score higher
        self.assertGreater(score_with_metrics, score_without_metrics)


class TestConditionalOptimization(unittest.TestCase):
    """Test that CV optimization is conditional based on ATS score."""
    
    def test_high_score_cv_needs_no_optimization(self):
        """CV with score >= 75 should not need full optimization."""
        high_score_cv = """
        Senior Engineer with comprehensive experience
        email@test.com | +1-555-1234
        
        PROFESSIONAL SUMMARY
        Seasoned software engineer with 10 years of experience in full-stack development.
        
        TECHNICAL SKILLS
        Python, Java, React, AWS, Docker, Kubernetes, PostgreSQL, MongoDB, Git, CI/CD
        
        PROFESSIONAL EXPERIENCE
        Senior Software Engineer | BigTech Corp | 2018 - Present
        • Led development of cloud-native applications serving 5M+ users
        • Improved system reliability from 99.5% to 99.99% uptime
        • Managed team of 8 engineers and established best practices
        • Reduced infrastructure costs by 35% through optimization
        
        Software Engineer | StartupInc | 2014 - 2018  
        • Built scalable microservices handling 1M requests/day
        • Implemented automated testing reducing bugs by 50%
        
        EDUCATION
        Master of Science in Computer Science — Stanford University (2014)
        
        CERTIFICATIONS
        • AWS Solutions Architect Professional
        • Google Cloud Professional
        """
        
        score, _, _ = compute_ats_score(high_score_cv, "software")
        self.assertGreaterEqual(score, 75)
        
        # In the upload route, this would skip full AI optimization
        # and just return the original with minimal processing
    
    def test_low_score_cv_needs_optimization(self):
        """CV with score < 75 should trigger full optimization."""
        low_score_cv = """
        Developer
        Looking for software job
        Know Python
        """
        
        score, _, _ = compute_ats_score(low_score_cv, "software")
        self.assertLess(score, 75)
        
        # In the upload route, this would trigger full AI optimization
        # with keyword injection and proper formatting


if __name__ == "__main__":
    unittest.main()
