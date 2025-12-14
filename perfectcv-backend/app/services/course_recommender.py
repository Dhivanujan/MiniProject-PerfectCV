"""
Course and Learning Resource Recommendations
Provides personalized course recommendations based on career field and skill gaps.
"""
from typing import List, Dict, Tuple
import random


class CourseRecommender:
    """Recommends courses and learning resources based on career field."""
    
    # Data Science Courses
    DS_COURSES = [
        ('Machine Learning Crash Course by Google [Free]', 'https://developers.google.com/machine-learning/crash-course'),
        ('Machine Learning A-Z by Udemy', 'https://www.udemy.com/course/machinelearning/'),
        ('Machine Learning by Andrew NG', 'https://www.coursera.org/learn/machine-learning'),
        ('Data Scientist Master Program (IBM)', 'https://www.simplilearn.com/big-data-and-analytics/senior-data-scientist-masters-program-training'),
        ('Data Science Foundations by LinkedIn', 'https://www.linkedin.com/learning/data-science-foundations-fundamentals-5'),
        ('Data Scientist with Python', 'https://www.datacamp.com/tracks/data-scientist-with-python'),
        ('Programming for Data Science with Python', 'https://www.udacity.com/course/programming-for-data-science-nanodegree--nd104'),
        ('Programming for Data Science with R', 'https://www.udacity.com/course/programming-for-data-science-nanodegree-with-R--nd118'),
        ('Introduction to Data Science', 'https://www.udacity.com/course/introduction-to-data-science--cd0017'),
        ('Intro to Machine Learning with TensorFlow', 'https://www.udacity.com/course/intro-to-machine-learning-with-tensorflow-nanodegree--nd230'),
        ('Deep Learning Specialization', 'https://www.coursera.org/specializations/deep-learning'),
        ('Applied Data Science with Python', 'https://www.coursera.org/specializations/data-science-python'),
        ('Data Analysis with Python', 'https://www.freecodecamp.org/learn/data-analysis-with-python/'),
        ('Python for Data Science [Free]', 'https://www.youtube.com/watch?v=LHBE6Q9XlzI')
    ]
    
    # Web Development Courses
    WEB_COURSES = [
        ('Django Crash Course [Free]', 'https://youtu.be/e1IyzVyrLSU'),
        ('Python and Django Full Stack Bootcamp', 'https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp'),
        ('React Crash Course [Free]', 'https://youtu.be/Dorf8i6lCuk'),
        ('ReactJS Project Development Training', 'https://www.dotnettricks.com/training/masters-program/reactjs-certification-training'),
        ('Full Stack Web Developer - MEAN Stack', 'https://www.simplilearn.com/full-stack-web-developer-mean-stack-certification-training'),
        ('Node.js and Express.js [Free]', 'https://youtu.be/Oe421EPjeBE'),
        ('Flask: Develop Web Applications in Python', 'https://www.educative.io/courses/flask-develop-web-applications-in-python'),
        ('Full Stack Web Developer by Udacity', 'https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044'),
        ('Front End Web Developer by Udacity', 'https://www.udacity.com/course/front-end-web-developer-nanodegree--nd0011'),
        ('Become a React Developer by Udacity', 'https://www.udacity.com/course/react-nanodegree--nd019'),
        ('The Complete Web Developer Course', 'https://www.udemy.com/course/the-complete-web-developer-course-2/'),
        ('Modern JavaScript From The Beginning', 'https://www.udemy.com/course/modern-javascript-from-the-beginning/'),
        ('Vue.js Complete Guide', 'https://www.udemy.com/course/vuejs-2-the-complete-guide/'),
        ('Next.js & React Tutorial [Free]', 'https://www.youtube.com/watch?v=mTz0GXj8NN0')
    ]
    
    # Android Development Courses
    ANDROID_COURSES = [
        ('Android Development for Beginners [Free]', 'https://youtu.be/fis26HvvDII'),
        ('Android App Development Specialization', 'https://www.coursera.org/specializations/android-app-development'),
        ('Associate Android Developer Certification', 'https://grow.google/androiddev/#?modal_active=none'),
        ('Become an Android Kotlin Developer', 'https://www.udacity.com/course/android-kotlin-developer-nanodegree--nd940'),
        ('Android Basics by Google', 'https://www.udacity.com/course/android-basics-nanodegree-by-google--nd803'),
        ('The Complete Android Developer Course', 'https://www.udemy.com/course/complete-android-n-developer-course/'),
        ('Building an Android App with Architecture', 'https://www.linkedin.com/learning/building-an-android-app-with-architecture-components'),
        ('Android App Development Masterclass', 'https://www.udemy.com/course/android-oreo-kotlin-app-masterclass/'),
        ('Flutter & Dart Complete Course', 'https://www.udemy.com/course/flutter-dart-the-complete-flutter-app-development-course/'),
        ('Flutter App Development [Free]', 'https://youtu.be/rZLR5olMR64'),
        ('Jetpack Compose for Android Developers', 'https://www.udemy.com/course/jetpack-compose/'),
        ('Android Testing Masterclass', 'https://www.udemy.com/course/android-testing/')
    ]
    
    # iOS Development Courses
    IOS_COURSES = [
        ('iOS App Development by LinkedIn', 'https://www.linkedin.com/learning/subscription/topics/ios'),
        ('iOS & Swift Complete Bootcamp', 'https://www.udemy.com/course/ios-13-app-development-bootcamp/'),
        ('Become an iOS Developer', 'https://www.udacity.com/course/ios-developer-nanodegree--nd003'),
        ('iOS App Development with Swift', 'https://www.coursera.org/specializations/app-development'),
        ('Mobile App Development with Swift', 'https://www.edx.org/professional-certificate/curtinx-mobile-app-development-with-swift'),
        ('Swift Course by LinkedIn', 'https://www.linkedin.com/learning/subscription/topics/swift-2'),
        ('Objective-C Crash Course', 'https://www.udemy.com/course/objectivec/'),
        ('Learn Swift by Codecademy', 'https://www.codecademy.com/learn/learn-swift'),
        ('Swift Tutorial - Full Course [Free]', 'https://youtu.be/comQ1-x2a1Q'),
        ('Learn Swift Fast [Free]', 'https://youtu.be/FcsY1YPBwzQ'),
        ('SwiftUI Masterclass', 'https://www.udemy.com/course/swiftui-masterclass-course-ios-development-with-swift/'),
        ('iOS Design Patterns', 'https://www.raywenderlich.com/ios/paths/iosdesignpatterns')
    ]
    
    # UI/UX Design Courses
    UIUX_COURSES = [
        ('Google UX Design Professional Certificate', 'https://www.coursera.org/professional-certificates/google-ux-design'),
        ('UI/UX Design Specialization', 'https://www.coursera.org/specializations/ui-ux-design'),
        ('Complete App Design Course - UX & UI', 'https://www.udemy.com/course/the-complete-app-design-course-ux-and-ui-design/'),
        ('UX & Web Design Master Course', 'https://www.udemy.com/course/ux-web-design-master-course-strategy-design-development/'),
        ('DESIGN RULES: Principles for Great UI', 'https://www.udemy.com/course/design-rules/'),
        ('Become a UX Designer by Udacity', 'https://www.udacity.com/course/ux-designer-nanodegree--nd578'),
        ('Adobe XD Tutorial [Free]', 'https://youtu.be/68w2VwalD5w'),
        ('Adobe XD for Beginners [Free]', 'https://youtu.be/WEljsc2jorI'),
        ('Adobe XD in Simple Way', 'https://learnux.io/course/adobe-xd'),
        ('Figma UI UX Design Tutorial [Free]', 'https://www.youtube.com/watch?v=FTFaQWZBqQ8'),
        ('User Research Methods', 'https://www.nngroup.com/courses/'),
        ('Interaction Design Specialization', 'https://www.coursera.org/specializations/interaction-design')
    ]
    
    # Resume Writing Video Resources
    RESUME_VIDEOS = [
        'https://youtu.be/3agP4x8LYFM',
        'https://youtu.be/fS_t3yS8v5s',
        'https://youtu.be/aArb68OBFPg',
        'https://youtu.be/h-NuvOeWWh0',
        'https://youtu.be/BdQniERyw8I',
        'https://youtu.be/Tt08KmFfIYQ',
        'https://youtu.be/CLUsplI4xMU',
        'https://youtu.be/bhwEsfXS6y8'
    ]
    
    # Interview Preparation Video Resources
    INTERVIEW_VIDEOS = [
        'https://youtu.be/Tt08KmFfIYQ',
        'https://youtu.be/KukmClH1KoA',
        'https://youtu.be/7_aAicmPB3A',
        'https://youtu.be/1mHjMNZZvFo',
        'https://youtu.be/WfdtKbAJOmE',
        'https://youtu.be/wFbU185CvDU',
        'https://youtu.be/TZ3C_syg9Ow'
    ]
    
    def __init__(self):
        """Initialize course recommender."""
        pass
    
    def get_courses_for_field(
        self, 
        field: str, 
        num_courses: int = 5
    ) -> List[Dict[str, str]]:
        """
        Get recommended courses for a specific field.
        
        Args:
            field: Career field (Data Science, Web Development, etc.)
            num_courses: Number of courses to recommend
            
        Returns:
            List of course dictionaries with name and link
        """
        course_map = {
            'Data Science': self.DS_COURSES,
            'Web Development': self.WEB_COURSES,
            'Android Development': self.ANDROID_COURSES,
            'iOS Development': self.IOS_COURSES,
            'UI/UX Development': self.UIUX_COURSES
        }
        
        courses = course_map.get(field, self.WEB_COURSES)  # Default to web dev
        
        # Shuffle to provide variety
        shuffled_courses = random.sample(courses, min(num_courses, len(courses)))
        
        return [
            {'name': name, 'link': link}
            for name, link in shuffled_courses
        ]
    
    def get_resume_tips_video(self) -> Dict[str, str]:
        """Get a random resume writing tips video."""
        video_url = random.choice(self.RESUME_VIDEOS)
        return {
            'title': 'Resume Writing Tips',
            'url': video_url,
            'type': 'resume_tips'
        }
    
    def get_interview_tips_video(self) -> Dict[str, str]:
        """Get a random interview preparation video."""
        video_url = random.choice(self.INTERVIEW_VIDEOS)
        return {
            'title': 'Interview Preparation Tips',
            'url': video_url,
            'type': 'interview_tips'
        }
    
    def get_all_resources(
        self, 
        field: str, 
        num_courses: int = 5
    ) -> Dict[str, any]:
        """
        Get comprehensive learning resources including courses and videos.
        
        Args:
            field: Career field
            num_courses: Number of courses to recommend
            
        Returns:
            Dictionary with courses, resume tips, and interview tips
        """
        return {
            'courses': self.get_courses_for_field(field, num_courses),
            'resume_tips_video': self.get_resume_tips_video(),
            'interview_tips_video': self.get_interview_tips_video(),
            'field': field
        }
    
    def get_skill_based_recommendations(
        self, 
        missing_skills: List[str], 
        field: str
    ) -> Dict[str, any]:
        """
        Get targeted recommendations based on missing skills.
        
        Args:
            missing_skills: List of skills the candidate should add
            field: Predicted career field
            
        Returns:
            Recommendations with courses and learning paths
        """
        courses = self.get_courses_for_field(field, num_courses=8)
        
        # Create learning path based on skills
        learning_path = []
        
        if any('machine learning' in skill.lower() or 'ml' in skill.lower() for skill in missing_skills):
            learning_path.append({
                'step': 1,
                'focus': 'Machine Learning Fundamentals',
                'duration': '2-3 months',
                'resources': ['Andrew NG ML Course', 'Google ML Crash Course']
            })
        
        if any('web' in skill.lower() or 'javascript' in skill.lower() for skill in missing_skills):
            learning_path.append({
                'step': 1,
                'focus': 'Web Development Basics',
                'duration': '1-2 months',
                'resources': ['HTML/CSS/JavaScript Fundamentals', 'React or Vue.js']
            })
        
        if any('android' in skill.lower() or 'kotlin' in skill.lower() for skill in missing_skills):
            learning_path.append({
                'step': 1,
                'focus': 'Android Development',
                'duration': '2-3 months',
                'resources': ['Kotlin Basics', 'Android Architecture Components']
            })
        
        return {
            'recommended_courses': courses,
            'learning_path': learning_path,
            'estimated_time': '3-6 months for comprehensive skill development',
            'tips': [
                'Focus on hands-on projects to reinforce learning',
                'Build a portfolio showcasing your new skills',
                'Contribute to open-source projects',
                'Network with professionals in your target field',
                'Stay updated with industry trends and technologies'
            ]
        }


# Singleton instance for easy import
course_recommender = CourseRecommender()
