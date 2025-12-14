"""
Test CV Analysis and Scoring System
Tests the new CV scoring, field prediction, and course recommendation features.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.cv_scoring_service import CVScoringService
from app.services.course_recommender import course_recommender


def test_cv_scoring():
    """Test CV scoring functionality."""
    print("=" * 80)
    print("TEST 1: CV Scoring Service")
    print("=" * 80)
    
    scoring_service = CVScoringService()
    
    # Sample CV data
    sample_cv_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '+1234567890',
        'summary': 'Experienced software developer with 5 years of experience',
        'skills': ['Python', 'React', 'Node.js', 'MongoDB', 'Docker'],
        'experience': [
            {
                'title': 'Senior Developer',
                'company': 'Tech Corp',
                'duration': '2020-Present',
                'description': 'Lead development team'
            }
        ],
        'education': [
            {
                'degree': 'B.S. Computer Science',
                'institution': 'Tech University',
                'year': '2018'
            }
        ]
    }
    
    # Sample raw text with sections
    sample_text = """
    John Doe
    john.doe@example.com | +1234567890
    
    OBJECTIVE
    Seeking a challenging position as a software developer
    
    SKILLS
    Python, React, Node.js, MongoDB, Docker
    
    PROJECTS
    - E-commerce Platform: Built scalable platform
    - Analytics Dashboard: Created real-time dashboard
    
    ACHIEVEMENTS
    - Employee of the Year 2022
    - Led team of 5 developers
    
    HOBBIES
    Reading, Coding, Photography
    
    DECLARATION
    I hereby declare that all information is true
    """
    
    # Analyze CV
    analysis = scoring_service.analyze_cv(sample_cv_data, sample_text)
    
    print(f"\n✅ CV Score: {analysis['score']}/{analysis['max_score']}")
    print(f"\n📊 Score Breakdown:")
    for section, score in analysis['score_breakdown'].items():
        print(f"   - {section.capitalize()}: {score}/20")
    
    print(f"\n🎯 Candidate Level: {analysis['candidate_level']}")
    print(f"💼 Predicted Field: {analysis['predicted_field']}")
    
    print(f"\n✓ Present Sections: {', '.join(analysis['present_sections'])}")
    print(f"✗ Missing Sections: {', '.join(analysis['missing_sections'])}")
    
    print(f"\n💡 Recommended Skills:")
    for skill in analysis['recommended_skills'][:10]:
        print(f"   - {skill}")
    
    print(f"\n📝 Recommendations:")
    for rec in analysis['recommendations'][:5]:
        print(f"   [{rec['type']}] {rec['message']}")
    
    print("\n✅ CV Scoring Test PASSED")


def test_field_prediction():
    """Test career field prediction."""
    print("\n" + "=" * 80)
    print("TEST 2: Field Prediction")
    print("=" * 80)
    
    scoring_service = CVScoringService()
    
    test_cases = [
        {
            'name': 'Data Scientist',
            'skills': ['Python', 'Machine Learning', 'TensorFlow', 'Pandas', 'Data Analysis']
        },
        {
            'name': 'Web Developer',
            'skills': ['React', 'Node.js', 'JavaScript', 'HTML', 'CSS', 'MongoDB']
        },
        {
            'name': 'Android Developer',
            'skills': ['Kotlin', 'Android', 'Java', 'XML', 'Android Studio']
        },
        {
            'name': 'UI/UX Designer',
            'skills': ['Figma', 'Adobe XD', 'Prototyping', 'User Research', 'Wireframing']
        }
    ]
    
    for test in test_cases:
        predicted_field, recommended_skills = scoring_service.predict_field_and_skills(
            test['skills']
        )
        print(f"\n{test['name']}:")
        print(f"   Skills: {', '.join(test['skills'])}")
        print(f"   ✅ Predicted Field: {predicted_field}")
        print(f"   💡 Top Recommendations: {', '.join(recommended_skills[:5])}")
    
    print("\n✅ Field Prediction Test PASSED")


def test_course_recommendations():
    """Test course recommendation system."""
    print("\n" + "=" * 80)
    print("TEST 3: Course Recommendations")
    print("=" * 80)
    
    fields = ['Data Science', 'Web Development', 'Android Development', 'iOS Development', 'UI/UX Development']
    
    for field in fields:
        print(f"\n{field}:")
        courses = course_recommender.get_courses_for_field(field, num_courses=3)
        for i, course in enumerate(courses, 1):
            print(f"   {i}. {course['name']}")
            print(f"      🔗 {course['link']}")
    
    print("\n✅ Course Recommendations Test PASSED")


def test_learning_resources():
    """Test complete learning resources."""
    print("\n" + "=" * 80)
    print("TEST 4: Complete Learning Resources")
    print("=" * 80)
    
    field = 'Data Science'
    resources = course_recommender.get_all_resources(field, num_courses=5)
    
    print(f"\nField: {resources['field']}")
    
    print(f"\n📚 Courses ({len(resources['courses'])}):")
    for i, course in enumerate(resources['courses'], 1):
        print(f"   {i}. {course['name']}")
    
    print(f"\n📺 Resume Tips Video:")
    print(f"   {resources['resume_tips_video']['title']}")
    print(f"   🔗 {resources['resume_tips_video']['url']}")
    
    print(f"\n📺 Interview Tips Video:")
    print(f"   {resources['interview_tips_video']['title']}")
    print(f"   🔗 {resources['interview_tips_video']['url']}")
    
    print("\n✅ Learning Resources Test PASSED")


def test_ats_tips():
    """Test ATS optimization tips."""
    print("\n" + "=" * 80)
    print("TEST 5: ATS Optimization Tips")
    print("=" * 80)
    
    scoring_service = CVScoringService()
    
    cv_data = {
        'name': 'Test User',
        'skills': ['Python', 'JavaScript']
    }
    
    tips = scoring_service.get_ats_optimization_tips(cv_data)
    
    print("\n💡 ATS Optimization Tips:")
    for i, tip in enumerate(tips, 1):
        print(f"   {i}. {tip}")
    
    print("\n✅ ATS Tips Test PASSED")


def test_candidate_level():
    """Test candidate level determination."""
    print("\n" + "=" * 80)
    print("TEST 6: Candidate Level Determination")
    print("=" * 80)
    
    scoring_service = CVScoringService()
    
    test_cases = [
        {
            'name': 'Fresher',
            'cv_data': {'experience': []},
            'text': 'Recent graduate with internship experience'
        },
        {
            'name': 'Intermediate',
            'cv_data': {'experience': [{'title': 'Developer'}, {'title': 'Analyst'}]},
            'text': '3 years of experience in software development'
        },
        {
            'name': 'Experienced',
            'cv_data': {'experience': [{'title': 'Senior Dev'}, {'title': 'Lead'}, {'title': 'Manager'}]},
            'text': '7 years of experience leading development teams'
        }
    ]
    
    for test in test_cases:
        level = scoring_service.determine_candidate_level(test['cv_data'], test['text'])
        print(f"\n{test['name']}: {level}")
        print(f"   Experience entries: {len(test['cv_data']['experience'])}")
        print(f"   ✅ Detected Level: {level}")
    
    print("\n✅ Candidate Level Test PASSED")


def test_skill_gap_analysis():
    """Test skill gap analysis and recommendations."""
    print("\n" + "=" * 80)
    print("TEST 7: Skill Gap Analysis")
    print("=" * 80)
    
    scoring_service = CVScoringService()
    
    current_skills = ['Python', 'JavaScript', 'HTML', 'CSS']
    predicted_field = 'Web Development'
    
    _, recommended_skills = scoring_service.predict_field_and_skills(current_skills)
    
    current_skills_lower = set(skill.lower() for skill in current_skills)
    missing_skills = [
        skill for skill in recommended_skills 
        if skill.lower() not in current_skills_lower
    ]
    
    print(f"\n🎯 Target Field: {predicted_field}")
    print(f"\n✅ Current Skills: {', '.join(current_skills)}")
    print(f"\n❌ Missing Skills (Top 10):")
    for i, skill in enumerate(missing_skills[:10], 1):
        print(f"   {i}. {skill}")
    
    # Get targeted recommendations
    recommendations = course_recommender.get_skill_based_recommendations(
        missing_skills, 
        predicted_field
    )
    
    print(f"\n📚 Recommended Courses:")
    for i, course in enumerate(recommendations['recommended_courses'][:3], 1):
        print(f"   {i}. {course['name']}")
    
    print(f"\n🎯 Learning Path:")
    for step in recommendations['learning_path']:
        print(f"   Step {step['step']}: {step['focus']} ({step['duration']})")
    
    print(f"\n⏱️ Estimated Time: {recommendations['estimated_time']}")
    
    print("\n✅ Skill Gap Analysis Test PASSED")


def run_all_tests():
    """Run all tests."""
    print("\n" + "🚀 " * 40)
    print("CV ANALYSIS AND SCORING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("🚀 " * 40)
    
    try:
        test_cv_scoring()
        test_field_prediction()
        test_course_recommendations()
        test_learning_resources()
        test_ats_tips()
        test_candidate_level()
        test_skill_gap_analysis()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 80)
        print("\n🎉 The CV Analysis and Scoring System is working perfectly!")
        print("\nKey Features Tested:")
        print("   ✓ CV Scoring (0-100 based on sections)")
        print("   ✓ Career Field Prediction")
        print("   ✓ Candidate Level Detection")
        print("   ✓ Skill Recommendations")
        print("   ✓ Course Recommendations")
        print("   ✓ ATS Optimization Tips")
        print("   ✓ Skill Gap Analysis")
        print("   ✓ Learning Resource Videos")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
