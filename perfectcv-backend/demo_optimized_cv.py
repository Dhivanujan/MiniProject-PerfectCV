"""
Demo: Generate an optimized CV using the enhanced template
This script creates a sample CV to showcase the improved formatting
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.cv_generator import get_cv_generator, CVGenerationConfig

# Sample CV data - Professional Software Engineer
sample_cv_data = {
    "entities": {
        "name": "Sampath Menuka Chandimal",
        "email": "sampathwgw@gmail.com",
        "phone": "+94 77 801 5196",
        "location": "Colombo, Sri Lanka",
        "linkedin": "linkedin.com/in/sampath-menuka",
        "github": "github.com/sampathmenuka",
        
        "job_titles": ["Full Stack Software Engineer"],
        
        "summary": "Results-driven Full Stack Software Engineer with 3+ years of experience in designing and developing scalable web applications. Expertise in modern JavaScript frameworks, Python, and cloud technologies. Proven track record of delivering high-quality solutions that improve user experience and drive business growth. Strong problem-solving abilities with excellent collaboration skills in agile environments.",
        
        "skills": [
            # Frontend
            "React.js", "Vue.js", "Next.js", "TypeScript", "JavaScript (ES6+)",
            "HTML5", "CSS3", "Tailwind CSS", "Redux", "Material-UI",
            # Backend
            "Node.js", "Express.js", "Python", "Django", "FastAPI",
            "Flask", "RESTful APIs", "GraphQL", "WebSockets",
            # Database
            "MongoDB", "PostgreSQL", "MySQL", "Redis", "Prisma ORM",
            # DevOps & Tools
            "Git", "Docker", "AWS", "CI/CD", "GitHub Actions",
            "Jest", "Pytest", "Postman", "VS Code", "Agile/Scrum",
            # Additional
            "Microservices", "System Design", "API Integration", "JWT Authentication",
            "Socket.io", "Webpack", "Babel", "Nginx", "Linux"
        ],
        
        "experience": [
            {
                "title": "Senior Full Stack Developer",
                "company": "TechVision Solutions Pvt Ltd",
                "duration": "January 2023 - Present",
                "location": "Colombo, Sri Lanka",
                "description": [
                    "Led development of a cloud-based SaaS platform serving 10,000+ users, resulting in 40% increase in customer retention",
                    "Architected and implemented microservices architecture using Node.js and Docker, improving system scalability by 60%",
                    "Developed real-time collaboration features using WebSockets and Redis, enhancing user engagement by 35%",
                    "Mentored team of 4 junior developers, conducting code reviews and implementing best practices",
                    "Optimized database queries and API performance, reducing average response time from 800ms to 200ms"
                ],
                "achievements": "Received 'Outstanding Performance Award' for delivering critical features ahead of schedule"
            },
            {
                "title": "Full Stack Developer",
                "company": "Digital Innovations Inc",
                "duration": "June 2021 - December 2022",
                "location": "Remote",
                "description": [
                    "Built responsive e-commerce platform using React, Node.js, and MongoDB, processing $500K+ monthly transactions",
                    "Implemented secure payment gateway integration with Stripe and PayPal APIs",
                    "Created RESTful APIs and integrated third-party services for inventory management and shipping",
                    "Developed admin dashboard with analytics and reporting features using Chart.js and Material-UI",
                    "Collaborated with UI/UX team to implement mobile-first design approach, increasing mobile conversions by 45%"
                ],
                "achievements": "Successfully launched platform within 6-month timeline with zero critical bugs in production"
            },
            {
                "title": "Junior Software Developer",
                "company": "StartupHub Technologies",
                "duration": "January 2021 - May 2021",
                "location": "Kandy, Sri Lanka",
                "description": [
                    "Developed and maintained company website and internal tools using Vue.js and Python/Flask",
                    "Created automated testing scripts using Pytest, improving code coverage from 45% to 85%",
                    "Participated in agile ceremonies and contributed to sprint planning and retrospectives",
                    "Fixed bugs and implemented new features based on user feedback and business requirements"
                ]
            }
        ],
        
        "projects": [
            {
                "name": "PerfectCV - AI-Powered Resume Builder",
                "role": "Lead Developer",
                "duration": "2024 - Present",
                "description": "Full-stack application that uses AI to extract, analyze, and optimize resumes. Features include PDF parsing, ATS scoring, AI-powered content improvement, and professional CV generation.",
                "technologies": "React, FastAPI, Python, MongoDB, Google Gemini AI, JWT Authentication, GridFS"
            },
            {
                "name": "Real-Time Chat Application",
                "role": "Full Stack Developer",
                "duration": "2023",
                "description": "Built scalable chat application supporting 1000+ concurrent users with features like private messaging, group chats, file sharing, and typing indicators.",
                "technologies": "Next.js, Socket.io, Node.js, Redis, PostgreSQL, Docker"
            },
            {
                "name": "Task Management System",
                "role": "Developer",
                "duration": "2022",
                "description": "Developed Kanban-style task management tool with drag-and-drop functionality, real-time updates, and team collaboration features.",
                "technologies": "React, Redux, Express.js, MongoDB, JWT, Material-UI"
            }
        ],
        
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of Peradeniya",
                "year": "2017 - 2021",
                "location": "Peradeniya, Sri Lanka",
                "gpa": "3.65/4.00",
                "honors": "First Class Honors, Dean's List (2019-2021)"
            }
        ],
        
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect - Associate",
                "issuer": "Amazon Web Services",
                "date": "2024"
            },
            {
                "name": "Professional Scrum Master (PSM I)",
                "issuer": "Scrum.org",
                "date": "2023"
            },
            {
                "name": "MongoDB Certified Developer",
                "issuer": "MongoDB University",
                "date": "2023"
            },
            {
                "name": "Meta Front-End Developer Professional Certificate",
                "issuer": "Meta (Facebook)",
                "date": "2022"
            }
        ],
        
        "languages": [
            "English (Fluent)",
            "Sinhala (Native)",
            "Tamil (Intermediate)"
        ]
    }
}

def main():
    """Generate optimized CV"""
    print("="*70)
    print("🚀 Generating Optimized CV Demo")
    print("="*70)
    
    # Initialize CV generator with enhanced template
    config = CVGenerationConfig(
        default_template="enhanced_cv.html",
        enable_logging=True
    )
    
    cv_gen = get_cv_generator(config=config)
    
    print(f"\n📝 Candidate: {sample_cv_data['entities']['name']}")
    print(f"📧 Email: {sample_cv_data['entities']['email']}")
    print(f"💼 Title: {sample_cv_data['entities']['job_titles'][0]}")
    print(f"🎯 Skills: {len(sample_cv_data['entities']['skills'])} skills")
    print(f"💼 Experience: {len(sample_cv_data['entities']['experience'])} positions")
    print(f"🚀 Projects: {len(sample_cv_data['entities']['projects'])} projects")
    
    print("\n⏳ Generating PDF...")
    
    # Generate CV
    output_path = Path(__file__).parent / "output" / "demo_optimized_cv.pdf"
    output_path.parent.mkdir(exist_ok=True)
    
    try:
        result = cv_gen.generate_cv_pdf(
            cv_data=sample_cv_data,
            output_path=output_path
        )
        
        # Check if result is BytesIO or CVGenerationResult
        if hasattr(result, 'success'):
            # CVGenerationResult
            if result.success:
                print(f"\n✅ Success! CV generated successfully")
                print(f"📄 File: {output_path}")
                print(f"📏 Size: {result.file_size / 1024:.2f} KB")
                print(f"⚡ Time: {result.generation_time_ms:.0f} ms")
                print(f"📋 Template: {result.template_used}")
                
                if result.warnings:
                    print(f"\n⚠️  Warnings:")
                    for warning in result.warnings:
                        print(f"   - {warning}")
            else:
                print(f"\n❌ Error: {result.error_message}")
        else:
            # BytesIO - write to file
            with open(output_path, 'wb') as f:
                f.write(result.getvalue())
            
            file_size = output_path.stat().st_size
            print(f"\n✅ Success! CV generated successfully")
            print(f"📄 File: {output_path}")
            print(f"📏 Size: {file_size / 1024:.2f} KB")
            print(f"📋 Template: enhanced_cv.html")
    
    except Exception as e:
        print(f"\n❌ Error generating CV: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*70)
    print("✨ Optimized CV Features:")
    print("="*70)
    print("✓ Professional header with large name and title")
    print("✓ Clean contact information bar")
    print("✓ Compelling professional summary")
    print("✓ Skills organized in grid format (4 columns)")
    print("✓ Detailed experience with bullet points")
    print("✓ Key achievements highlighted")
    print("✓ Project showcase with technologies")
    print("✓ Education with honors and GPA")
    print("✓ Professional certifications")
    print("✓ Language proficiencies")
    print("✓ ATS-friendly formatting")
    print("✓ Clean, modern design")
    print("="*70)
    
    print(f"\n🎉 Your optimized CV is ready!")
    print(f"📂 Open: {output_path}")

if __name__ == "__main__":
    main()

