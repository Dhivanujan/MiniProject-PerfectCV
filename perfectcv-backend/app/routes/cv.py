"""
CV Generation API Routes
FastAPI endpoints for CV extraction, enhancement, and PDF generation.
"""
import os
import logging
import tempfile
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.services.unified_cv_extractor import get_cv_extractor
from app.services.cv_ai_service import improve_cv_data, score_ats_compatibility
from app.services.cv_scoring_service import CVScoringService
from app.services.course_recommender import course_recommender
from app.utils.cv_template_generator import cv_template_generator
from app.services.cv_generator import get_cv_generator
from config.config import Config

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize CV Scoring Service
cv_scoring_service = CVScoringService()

# Initialize AI client (Groq preferred, fallback to OpenAI)
ai_client = None

try:
    from groq import Groq
    if Config.GROQ_API_KEY:
        ai_client = Groq(api_key=Config.GROQ_API_KEY)
        logger.info("Groq AI client initialized")
except ImportError:
    logger.warning("Groq package not installed")

if not ai_client:
    try:
        from openai import OpenAI
        if Config.OPENAI_API_KEY:
            ai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
    except ImportError:
        logger.warning("OpenAI package not installed")

if not ai_client:
    logger.error("No AI client available. Set GROQ_API_KEY or OPENAI_API_KEY in environment")


class CVData(BaseModel):
    """Model for CV data"""
    name: str = ""
    email: str = ""
    phone: str = ""
    summary: str = ""
    skills: list = []
    experience: list = []
    education: list = []
    projects: list = []
    certifications: list = []


@router.post("/generate-cv")
async def generate_cv(
    file: UploadFile = File(...),
    improve: bool = True,
    background_tasks: BackgroundTasks = None
):
    """
    Complete CV Generation Pipeline:
    1. Extract text from uploaded PDF/DOCX
    2. Parse into structured JSON
    3. Optionally improve with AI
    4. Generate professional PDF
    5. Return downloadable PDF
    
    Args:
        file: Uploaded CV file (PDF or DOCX)
        improve: Whether to enhance CV with AI (default: True)
        
    Returns:
        FileResponse with generated PDF
    """
    temp_input_path = None
    temp_output_path = None
    
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload PDF or DOCX file."
            )
        
        logger.info(f"Processing CV upload: {file.filename}")
        
        # Step 1: Save uploaded file temporarily
        suffix = '.pdf' if file.filename.lower().endswith('.pdf') else '.docx'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_input_path = tmp_file.name
        
        logger.info(f"Saved uploaded file to: {temp_input_path}")
        
        # Step 2: Extract structured CV data using unified spaCy extractor
        logger.info("Extracting CV data...")
        extractor = get_cv_extractor()
        with open(temp_input_path, 'rb') as f:
            file_content = f.read()
        extraction_result = extractor.extract_from_file(file_content, file.filename)
        cv_data = extraction_result['entities']
        
        # Step 3: Improve with AI if requested
        if improve and ai_client:
            logger.info("Improving CV with AI...")
            cv_data = improve_cv_data(cv_data, ai_client)
        elif improve and not ai_client:
            logger.warning("AI improvement requested but no AI client available")
        
        # Step 4: Generate PDF using new Jinja2 + xhtml2pdf service
        logger.info("Generating PDF with modern template...")
        cv_gen = get_cv_generator()
        
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = f"cv_{cv_data.get('name', 'resume').replace(' ', '_')}.pdf"
        temp_output_path = os.path.join(output_dir, output_filename)
        
        # Generate PDF using Jinja2 template (enhanced_cv.html - same format as demo_optimized_cv.pdf)
        cv_gen.generate_cv_pdf(cv_data, template_name='enhanced_cv.html', output_path=temp_output_path)
        
        # Schedule cleanup of temporary input file
        if background_tasks:
            background_tasks.add_task(cleanup_file, temp_input_path)
        
        # Step 5: Return PDF file
        logger.info(f"Returning generated PDF: {temp_output_path}")
        return FileResponse(
            path=temp_output_path,
            media_type='application/pdf',
            filename=output_filename,
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating CV: {e}", exc_info=True)
        
        # Cleanup on error
        if temp_input_path and os.path.exists(temp_input_path):
            try:
                os.unlink(temp_input_path)
            except:
                pass
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate CV: {str(e)}"
        )


@router.post("/extract-cv")
async def extract_cv(file: UploadFile = File(...)):
    """
    Extract structured data from CV without generating PDF.
    Useful for preview or editing before final generation.
    
    Args:
        file: Uploaded CV file (PDF or DOCX)
        
    Returns:
        JSON with structured CV data
    """
    temp_path = None
    
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload PDF or DOCX file."
            )
        
        logger.info(f"Extracting data from: {file.filename}")
        
        # Extract data using unified extractor
        content = await file.read()
        extractor = get_cv_extractor()
        extraction_result = extractor.extract_from_file(content, file.filename)
        cv_data = extraction_result['entities']
        
        # Get ATS score
        ats_score_result = score_ats_compatibility(cv_data)
        
        return JSONResponse(content={
            "success": True,
            "data": cv_data,
            "ats_score": ats_score_result['score'],
            "ats_details": ats_score_result
        })
        
    except Exception as e:
        logger.error(f"Error extracting CV: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract CV data: {str(e)}"
        )
    
    finally:
        # Cleanup
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass


@router.post("/improve-cv")
async def improve_cv_endpoint(cv_data: CVData):
    """
    Improve existing CV data with AI optimization.
    
    Args:
        cv_data: Structured CV data as JSON
        
    Returns:
        Improved CV data
    """
    try:
        if not ai_client:
            raise HTTPException(
                status_code=503,
                detail="AI service not available. Configure GROQ_API_KEY or OPENAI_API_KEY."
            )
        
        logger.info("Improving CV data...")
        
        # Convert Pydantic model to dict
        cv_dict = cv_data.model_dump()
        
        # Improve with AI
        improved_cv = improve_cv_data(cv_dict, ai_client)
        
        # Get ATS score
        ats_score_result = score_ats_compatibility(improved_cv)
        
        return JSONResponse(content={
            "success": True,
            "data": improved_cv,
            "ats_score": ats_score_result['score'],
            "ats_details": ats_score_result
        })
        
    except Exception as e:
        logger.error(f"Error improving CV: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to improve CV: {str(e)}"
        )


@router.post("/generate-pdf-from-json")
async def generate_pdf_from_json(cv_data: CVData):
    """
    Generate PDF from structured CV data (JSON).
    Useful when user has edited the extracted data.
    
    Args:
        cv_data: Structured CV data
        
    Returns:
        FileResponse with generated PDF
    """
    temp_output_path = None
    
    try:
        logger.info("Generating PDF from JSON data...")
        
        # Convert to dict
        cv_dict = cv_data.model_dump()
        
        # Generate PDF using new Jinja2 + xhtml2pdf service
        cv_gen = get_cv_generator()
        
        output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        output_filename = f"cv_{cv_dict.get('name', 'resume').replace(' ', '_')}.pdf"
        temp_output_path = os.path.join(output_dir, output_filename)
        
        # Generate PDF using enhanced template (same format as demo_optimized_cv.pdf)
        cv_gen.generate_cv_pdf(cv_dict, template_name='enhanced_cv.html', output_path=temp_output_path)
        
        logger.info(f"Generated PDF: {temp_output_path}")
        return FileResponse(
            path=temp_output_path,
            media_type='application/pdf',
            filename=output_filename,
            headers={
                "Content-Disposition": f"attachment; filename={output_filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF from JSON: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate PDF: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_service": "available" if ai_client else "unavailable"
    }


@router.post("/analyze-cv")
async def analyze_cv_comprehensive(file: UploadFile = File(...)):
    """
    Comprehensive CV Analysis with Scoring and Recommendations.
    
    Provides:
    - CV Score (0-100)
    - Predicted career field
    - Candidate experience level
    - Recommended skills to add
    - Course recommendations
    - ATS optimization tips
    - Detailed recommendations
    
    Args:
        file: Uploaded CV file (PDF or DOCX)
        
    Returns:
        JSON with comprehensive analysis
    """
    temp_path = None
    
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload PDF or DOCX file."
            )
        
        logger.info(f"Starting comprehensive analysis for: {file.filename}")
        
        # Save temporarily
        suffix = '.pdf' if file.filename.lower().endswith('.pdf') else '.docx'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            temp_path = tmp_file.name
        
        # Extract raw text
        raw_text = extract_text_from_pdf(temp_path)
        
        # Extract structured data
        cv_data = extract_cv_data(temp_path, ai_client)
        
        # Perform comprehensive analysis
        analysis = cv_scoring_service.analyze_cv(cv_data, raw_text)
        
        # Get course recommendations based on predicted field
        num_courses = 8  # Default number of courses
        courses = course_recommender.get_all_resources(
            analysis['predicted_field'], 
            num_courses
        )
        
        # Get ATS score
        ats_score_result = score_ats_compatibility(cv_data)
        
        # Get ATS optimization tips
        ats_tips = cv_scoring_service.get_ats_optimization_tips(cv_data)
        
        return JSONResponse(content={
            "success": True,
            "cv_data": cv_data,
            "analysis": {
                "score": analysis['score'],
                "max_score": analysis['max_score'],
                "score_breakdown": analysis['score_breakdown'],
                "candidate_level": analysis['candidate_level'],
                "predicted_field": analysis['predicted_field'],
                "recommended_skills": analysis['recommended_skills'],
                "missing_sections": analysis['missing_sections'],
                "present_sections": analysis['present_sections'],
                "recommendations": analysis['recommendations'],
                "timestamp": analysis['analysis_timestamp']
            },
            "ats": {
                "score": ats_score_result['score'],
                "percentage": ats_score_result['percentage'],
                "suggestions": ats_score_result['suggestions'],
                "optimization_tips": ats_tips
            },
            "learning_resources": courses
        })
        
    except Exception as e:
        logger.error(f"Error analyzing CV: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze CV: {str(e)}"
        )
    
    finally:
        # Cleanup
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass


@router.post("/get-recommendations")
async def get_skill_recommendations(cv_data: CVData):
    """
    Get personalized skill and course recommendations based on CV data.
    
    Args:
        cv_data: Structured CV data
        
    Returns:
        Recommendations including skills, courses, and learning paths
    """
    try:
        logger.info("Generating recommendations...")
        
        # Convert to dict
        cv_dict = cv_data.model_dump()
        
        # Predict field and get recommended skills
        predicted_field, recommended_skills = cv_scoring_service.predict_field_and_skills(
            cv_dict.get('skills', [])
        )
        
        # Get current skills
        current_skills = set(skill.lower() for skill in cv_dict.get('skills', []))
        
        # Find missing skills (recommended but not present)
        missing_skills = [
            skill for skill in recommended_skills 
            if skill.lower() not in current_skills
        ]
        
        # Get targeted recommendations based on missing skills
        skill_recommendations = course_recommender.get_skill_based_recommendations(
            missing_skills, 
            predicted_field
        )
        
        return JSONResponse(content={
            "success": True,
            "predicted_field": predicted_field,
            "current_skills": list(current_skills),
            "recommended_skills": recommended_skills,
            "missing_skills": missing_skills[:10],  # Top 10 missing skills
            "learning_resources": skill_recommendations
        })
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get("/courses/{field}")
async def get_courses_by_field(field: str, num_courses: int = 5):
    """
    Get course recommendations for a specific field.
    
    Args:
        field: Career field (Data Science, Web Development, etc.)
        num_courses: Number of courses to return (default: 5)
        
    Returns:
        List of recommended courses
    """
    try:
        courses = course_recommender.get_courses_for_field(field, num_courses)
        
        return JSONResponse(content={
            "success": True,
            "field": field,
            "courses": courses,
            "total": len(courses)
        })
        
    except Exception as e:
        logger.error(f"Error fetching courses: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch courses: {str(e)}"
        )


@router.get("/learning-videos")
async def get_learning_videos():
    """
    Get random resume writing and interview preparation videos.
    
    Returns:
        Video links for resume tips and interview preparation
    """
    try:
        resume_video = course_recommender.get_resume_tips_video()
        interview_video = course_recommender.get_interview_tips_video()
        
        return JSONResponse(content={
            "success": True,
            "videos": {
                "resume_tips": resume_video,
                "interview_prep": interview_video
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching videos: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch videos: {str(e)}"
        )


@router.post("/enhance-cv-example")
async def enhance_cv_example(cv_data: CVData):
    """
    Create an enhanced, professional version of the CV.
    Provides a better example based on the uploaded CV data.
    
    Args:
        cv_data: Structured CV data
        
    Returns:
        Enhanced CV example with professional improvements
    """
    try:
        logger.info("Creating enhanced CV example...")
        
        # Convert to dict
        cv_dict = cv_data.model_dump()
        
        # Enhance the CV
        enhanced_cv = cv_template_generator.enhance_cv_professionally(cv_dict)
        
        # Get ATS score for both versions
        original_ats = score_ats_compatibility(cv_dict)
        enhanced_ats = score_ats_compatibility(enhanced_cv)
        
        return JSONResponse(content={
            "success": True,
            "original_cv": cv_dict,
            "enhanced_cv": enhanced_cv,
            "improvements": {
                "ats_score_before": original_ats['score'],
                "ats_score_after": enhanced_ats['score'],
                "improvement": enhanced_ats['score'] - original_ats['score'],
                "highlights_added": enhanced_cv.get('highlights', []),
                "skills_categorized": enhanced_cv.get('skills_categorized', {})
            },
            "message": "CV enhanced with professional formatting and content improvements"
        })
        
    except Exception as e:
        logger.error(f"Error enhancing CV example: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance CV: {str(e)}"
        )


@router.get("/cv-examples/{field}")
async def get_cv_examples(field: str, level: str = "mid"):
    """
    Get professional CV examples for a specific field and level.
    
    Args:
        field: Career field (Data Science, Web Development, Mobile Development, etc.)
        level: Experience level (junior, mid, senior) - default: mid
        
    Returns:
        Professional CV templates for the specified field
    """
    try:
        logger.info(f"Generating CV examples for {field} - {level} level")
        
        examples = cv_template_generator.create_example_cvs(field, level)
        
        if not examples:
            raise HTTPException(
                status_code=404,
                detail=f"No templates found for field: {field}"
            )
        
        # Get ATS scores for examples
        for example in examples:
            ats_result = score_ats_compatibility(example)
            example['ats_score'] = ats_result['score']
            example['ats_percentage'] = ats_result['percentage']
        
        return JSONResponse(content={
            "success": True,
            "field": field,
            "level": level,
            "examples": examples,
            "total": len(examples)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating CV examples: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate CV examples: {str(e)}"
        )


def cleanup_file(file_path: str):
    """Background task to cleanup temporary files"""
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {e}")
