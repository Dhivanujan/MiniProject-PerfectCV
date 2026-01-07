"""
Complete Integration Demo: Shows the full CV generation workflow
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

def demo_cv_generation():
    """Demonstrate complete CV generation with sample data"""
    print("=" * 70)
    print("CV GENERATION WORKFLOW DEMO")
    print("Using Jinja2 Templates + xhtml2pdf")
    print("=" * 70)
    
    try:
        from app.services.cv_generator import get_cv_generator
        
        # Comprehensive sample CV data (simulating extraction result)
        sample_cv_data = {
            'name': 'Sarah Martinez',
            'email': 'sarah.martinez@email.com',
            'phone': '+1 (555) 234-5678',
            'location': 'San Francisco, CA',
            'linkedin': 'linkedin.com/in/sarahmartinez',
            'github': 'github.com/smartinez',
            'summary': 'Full-stack software engineer with 6+ years of experience building scalable web applications. Specialized in React, Node.js, and cloud infrastructure. Passionate about clean code, system design, and mentoring junior developers.',
            'skills': [
                'JavaScript', 'TypeScript', 'Python', 'React', 'Node.js', 'Express',
                'MongoDB', 'PostgreSQL', 'Redis', 'Docker', 'Kubernetes', 'AWS',
                'Git', 'CI/CD', 'REST APIs', 'GraphQL', 'Microservices', 'TDD'
            ],
            'experience': [
                {
                    'title': 'Senior Software Engineer',
                    'company': 'TechCorp Inc.',
                    'location': 'San Francisco, CA',
                    'start_date': '2021-03',
                    'end_date': 'Present',
                    'description': 'Lead development of microservices architecture serving 2M+ users. Architected and implemented real-time notification system using WebSockets and Redis. Mentored team of 4 junior engineers. Reduced API response time by 60% through caching strategies and database optimization. Implemented CI/CD pipeline reducing deployment time from 2 hours to 15 minutes.'
                },
                {
                    'title': 'Software Engineer',
                    'company': 'StartupXYZ',
                    'location': 'San Francisco, CA',
                    'start_date': '2019-01',
                    'end_date': '2021-02',
                    'description': 'Developed React frontend and Node.js backend for SaaS platform. Built RESTful APIs serving 100K+ daily requests. Implemented authentication system with OAuth2 and JWT. Collaborated with design team to create responsive UI components. Increased test coverage from 40% to 85%.'
                },
                {
                    'title': 'Junior Developer',
                    'company': 'WebDev Agency',
                    'location': 'Oakland, CA',
                    'start_date': '2017-06',
                    'end_date': '2018-12',
                    'description': 'Built client websites using JavaScript, HTML, and CSS. Integrated third-party APIs for payment processing and analytics. Maintained WordPress sites and developed custom plugins. Participated in code reviews and agile development process.'
                }
            ],
            'education': [
                {
                    'degree': 'B.S. Computer Science',
                    'institution': 'University of California, Berkeley',
                    'location': 'Berkeley, CA',
                    'graduation_year': '2017',
                    'gpa': '3.8/4.0'
                }
            ],
            'certifications': [
                'AWS Certified Solutions Architect - Associate',
                'MongoDB Certified Developer'
            ],
            'projects': [
                {
                    'name': 'Open Source Task Manager',
                    'description': 'Built collaborative task management app with React and Firebase. 500+ GitHub stars.',
                    'technologies': 'React, Firebase, Material-UI'
                }
            ]
        }
        
        print("\n✓ Sample CV data prepared")
        print(f"  Name: {sample_cv_data['name']}")
        print(f"  Email: {sample_cv_data['email']}")
        print(f"  Skills: {len(sample_cv_data['skills'])} skills")
        print(f"  Experience: {len(sample_cv_data['experience'])} positions")
        print(f"  Education: {len(sample_cv_data['education'])} degrees")
        
        # Get CV generator
        cv_gen = get_cv_generator()
        print("\n✓ CV generator initialized")
        
        # Create output directory
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF
        print("\n" + "-" * 70)
        print("Generating Professional CV PDF...")
        print("-" * 70)
        
        pdf_path = os.path.join(output_dir, 'demo_sarah_martinez_cv.pdf')
        pdf_io = cv_gen.generate_cv_pdf(
            sample_cv_data,
            template_name='modern_cv.html',
            output_path=pdf_path
        )
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"\n✅ PDF Generated Successfully!")
            print(f"   Location: {pdf_path}")
            print(f"   Size: {file_size:,} bytes")
        
        # Generate HTML preview
        print("\n" + "-" * 70)
        print("Generating HTML Preview...")
        print("-" * 70)
        
        html_content = cv_gen.generate_cv_html(sample_cv_data, template_name='modern_cv.html')
        html_path = os.path.join(output_dir, 'demo_sarah_martinez_cv.html')
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ HTML Preview Generated!")
        print(f"   Location: {html_path}")
        print(f"   Size: {len(html_content):,} bytes")
        
        # Show template features
        print("\n" + "=" * 70)
        print("🎨 Template Features")
        print("=" * 70)
        print("  ✓ Modern gradient design (purple gradient sidebar)")
        print("  ✓ Professional typography (Segoe UI)")
        print("  ✓ A4 page size optimization")
        print("  ✓ Responsive layout")
        print("  ✓ Skills displayed as badges")
        print("  ✓ Contact information with icons")
        print("  ✓ Experience timeline")
        print("  ✓ Education section")
        print("  ✓ ATS-friendly structure")
        
        # Show technology stack
        print("\n" + "=" * 70)
        print("🛠 Technology Stack")
        print("=" * 70)
        print("  ✓ pdfplumber: PDF text extraction with layout analysis")
        print("  ✓ Jinja2: HTML templating engine")
        print("  ✓ xhtml2pdf: HTML to PDF conversion (Windows-compatible)")
        print("  ✓ Python: Backend processing")
        
        # Show API endpoints
        print("\n" + "=" * 70)
        print("🌐 Updated API Endpoints")
        print("=" * 70)
        print("  ✓ /api/download-optimized-cv (Flask)")
        print("    → Uses cv_generator with Jinja2 templates")
        print("  ✓ /api/generate-cv (FastAPI)")
        print("    → Extract + generate with modern template")
        print("  ✓ /api/generate-pdf-from-json (FastAPI)")
        print("    → Generate PDF from JSON data")
        
        print("\n" + "=" * 70)
        print("✅ DEMO COMPLETE!")
        print("=" * 70)
        print(f"\n📂 Output files saved to: {os.path.abspath(output_dir)}")
        print("   • demo_sarah_martinez_cv.pdf - Professional CV PDF")
        print("   • demo_sarah_martinez_cv.html - HTML preview")
        
        print("\n🎯 Next Steps:")
        print("   1. Open the PDF to see the professional design")
        print("   2. Open HTML in browser to view styling")
        print("   3. Use API endpoints in your application")
        print("   4. Customize templates in app/templates/")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = demo_cv_generation()
    sys.exit(0 if success else 1)
