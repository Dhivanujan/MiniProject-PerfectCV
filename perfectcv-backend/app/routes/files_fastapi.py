"""
FastAPI File Upload Routes
Handles CV file uploads with JWT authentication
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
from pydantic import BaseModel
import io
import logging
from bson import ObjectId
import gridfs

from app.auth.jwt_handler import get_current_active_user
from app.services.unified_cv_extractor import CVExtractor
from app.services.cv_generator import get_cv_generator
from app.services.cv_scoring_service import CVScoringService

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}


class DownloadOptimizedCVRequest(BaseModel):
    """Request model for downloading optimized CV"""
    structured_cv: Optional[dict] = None
    optimized_text: Optional[str] = None
    template_data: Optional[dict] = None
    filename: Optional[str] = "Optimized_CV.pdf"


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db():
    """Get MongoDB database instance"""
    from app_fastapi import get_mongo_db
    return get_mongo_db()

@router.post("/upload-cv")
async def upload_cv(
    cv_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Upload and process a CV file
    Extracts text, generates structured data, and stores in GridFS
    """
    try:
        # Validate file
        if not cv_file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if not allowed_file(cv_file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Invalid file type. Only PDF, DOC, and DOCX files are allowed"
            )
        
        # Read file content
        file_content = await cv_file.read()
        
        # Get database and GridFS
        db = get_db()
        fs = gridfs.GridFS(db)
        
        # Extract CV data
        logger.info(f"Extracting CV data from {cv_file.filename}")
        extractor = CVExtractor()
        extraction_result = extractor.extract_from_file(
            file_content, 
            filename=cv_file.filename
        )
        
        # The extraction returns entities directly, not wrapped in success/data
        # Check if we got entities (indicates success)
        if not extraction_result.get('entities'):
            raise HTTPException(
                status_code=500,
                detail=f"CV extraction failed: Could not extract entities from file"
            )
        
        cv_data = extraction_result.get('entities', {})
        raw_text = extraction_result.get('raw_text', '')
        
        # Score the CV
        ats_score = 0
        try:
            logger.info("Starting CV scoring...")
            scoring_service = CVScoringService()
            score_result = scoring_service.score_cv(cv_data)
            ats_score = score_result.get('overall_score', 0)
            cv_data['ats_score'] = ats_score
            cv_data['scoring_details'] = score_result
            logger.info(f"CV scoring completed - Score: {ats_score}")
        except Exception as e:
            logger.warning(f"CV scoring failed: {e}", exc_info=True)
            ats_score = 0
        
        # Generate PDF
        pdf_bytes = None
        try:
            logger.info("Starting PDF generation...")
            cv_gen = get_cv_generator()
            pdf_result = cv_gen.generate_cv_pdf(cv_data)
            # Handle both BytesIO (backward compat) and CVGenerationResult
            if pdf_result:
                if hasattr(pdf_result, 'success'):
                    # CVGenerationResult object
                    if pdf_result.success and pdf_result.pdf_bytes:
                        pdf_bytes = pdf_result.pdf_bytes.getvalue()
                        logger.info("PDF generation completed successfully (CVGenerationResult)")
                    else:
                        logger.warning("PDF generation returned unsuccessful result")
                elif hasattr(pdf_result, 'getvalue'):
                    # BytesIO object (backward compatibility)
                    pdf_bytes = pdf_result.getvalue()
                    logger.info("PDF generation completed successfully (BytesIO)")
                else:
                    logger.warning(f"Unexpected pdf_result type: {type(pdf_result)}")
        except Exception as e:
            logger.error(f"PDF generation failed: {e}", exc_info=True)
        
        # Store in GridFS
        logger.info("Starting GridFS storage...")
        user_id = current_user.get('id')
        storage_filename = f"{user_id}_{cv_file.filename}"
        
        # Store original file
        file_id = fs.put(
            file_content,
            filename=storage_filename,
            original_filename=cv_file.filename,
            content_type=cv_file.content_type,
            user_id=user_id,
            cv_data=cv_data,
            raw_text=raw_text,
            ats_score=ats_score
        )
        
        # Store generated PDF if available
        pdf_file_id = None
        if pdf_bytes:
            pdf_filename = f"generated_{storage_filename.rsplit('.', 1)[0]}.pdf"
            pdf_file_id = fs.put(
                pdf_bytes,
                filename=pdf_filename,
                original_filename=pdf_filename,
                content_type='application/pdf',
                user_id=user_id,
                is_generated=True
            )
        
        logger.info(f"CV uploaded successfully - File ID: {file_id}")
        
        # Prepare JSON-safe cv_data for response
        try:
            import json
            # Test if cv_data is JSON serializable
            json.dumps(cv_data)
            response_cv_data = cv_data
        except (TypeError, ValueError) as e:
            logger.warning(f"cv_data not JSON serializable, simplifying: {e}")
            # Return a simplified version
            response_cv_data = {
                "name": cv_data.get("name"),
                "email": cv_data.get("email"),
                "phone": cv_data.get("phone"),
                "skills": cv_data.get("skills", [])[:10] if cv_data.get("skills") else [],
                "summary": cv_data.get("summary", "")[:200] if cv_data.get("summary") else ""
            }
        
        # Build structured_cv for template rendering
        structured_cv = {
            "name": cv_data.get("name", ""),
            "contact": f"{cv_data.get('email', '')} | {cv_data.get('phone', '')}",
            "email": cv_data.get("email", ""),
            "phone": cv_data.get("phone", ""),
            "location": cv_data.get("location", ""),
            "summary": cv_data.get("summary", ""),
            "skills": cv_data.get("skills", []),
            "experience": cv_data.get("experience", []),
            "education": cv_data.get("education", []),
            "projects": cv_data.get("projects", []),
            "certifications": cv_data.get("certifications", []),
        }
        
        # Build ordered sections for frontend display
        ordered_sections = []
        if cv_data.get("summary"):
            ordered_sections.append({"key": "summary", "label": "Professional Summary", "content": cv_data.get("summary")})
        if cv_data.get("skills"):
            ordered_sections.append({"key": "skills", "label": "Skills", "content": cv_data.get("skills", [])})
        if cv_data.get("experience"):
            ordered_sections.append({"key": "experience", "label": "Work Experience", "content": cv_data.get("experience", [])})
        if cv_data.get("education"):
            ordered_sections.append({"key": "education", "label": "Education", "content": cv_data.get("education", [])})
        if cv_data.get("projects"):
            ordered_sections.append({"key": "projects", "label": "Projects", "content": cv_data.get("projects", [])})
        if cv_data.get("certifications"):
            ordered_sections.append({"key": "certifications", "label": "Certifications", "content": cv_data.get("certifications", [])})
        
        # Build optimized text from structured data
        optimized_parts = []
        if cv_data.get("name"):
            optimized_parts.append(f"# {cv_data.get('name')}\n")
        if cv_data.get("email") or cv_data.get("phone"):
            optimized_parts.append(f"{cv_data.get('email', '')} | {cv_data.get('phone', '')}\n")
        if cv_data.get("summary"):
            optimized_parts.append(f"\n## Professional Summary\n{cv_data.get('summary')}\n")
        if cv_data.get("skills"):
            skills_list = cv_data.get("skills", [])
            optimized_parts.append(f"\n## Skills\n" + "\n".join([f"- {s}" for s in skills_list]) + "\n")
        if cv_data.get("experience"):
            optimized_parts.append(f"\n## Work Experience\n")
            for exp in cv_data.get("experience", []):
                title = exp.get("title") or exp.get("role", "Position")
                company = exp.get("company", "")
                duration = exp.get("duration") or exp.get("years", "")
                optimized_parts.append(f"\n### {title}")
                if company:
                    optimized_parts.append(f" at {company}")
                if duration:
                    optimized_parts.append(f" | {duration}")
                optimized_parts.append("\n")
                desc = exp.get("description", "")
                if isinstance(desc, list):
                    for point in desc:
                        optimized_parts.append(f"- {point}\n")
                elif desc:
                    optimized_parts.append(f"{desc}\n")
        if cv_data.get("education"):
            optimized_parts.append(f"\n## Education\n")
            for edu in cv_data.get("education", []):
                degree = edu.get("degree", "Degree")
                institution = edu.get("institution", "")
                year = edu.get("year", "")
                optimized_parts.append(f"\n### {degree}\n")
                if institution:
                    optimized_parts.append(f"{institution}\n")
                if year:
                    optimized_parts.append(f"{year}\n")
        
        optimized_text = "".join(optimized_parts)
        
        # Get recommended keywords based on skills
        found_keywords = cv_data.get("skills", [])[:10] if cv_data.get("skills") else []
        recommended_keywords = []
        
        return JSONResponse({
            "success": True,
            "message": "CV uploaded and processed successfully",
            "file_id": str(file_id),
            "pdf_file_id": str(pdf_file_id) if pdf_file_id else None,
            "cv_data": response_cv_data,
            "structured_cv": structured_cv,
            "template_data": structured_cv,
            "optimized_text": optimized_text,
            "optimized_cv": optimized_text,
            "ordered_sections": ordered_sections,
            "ats_score": ats_score,
            "suggestions": cv_data.get("scoring_details", {}).get("recommendations", []) if cv_data.get("scoring_details") else [],
            "grouped_suggestions": {},
            "recommended_keywords": recommended_keywords,
            "found_keywords": found_keywords,
            "filename": cv_file.filename,
            "file": {
                "_id": str(file_id),
                "filename": cv_file.filename,
                "uploadedAt": None,
                "atsScore": ats_score
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading CV: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload CV: {str(e)}"
        )

@router.get("/current-user")
async def get_current_user_endpoint(current_user: dict = Depends(get_current_active_user)):
    """
    Get current authenticated user information
    """
    try:
        return JSONResponse({
            "success": True,
            "user": {
                "id": current_user.get('id'),
                "email": current_user.get('email'),
                "full_name": current_user.get('full_name'),
                "username": current_user.get('username')
            }
        })
    except Exception as e:
        logger.error(f"Error getting current user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def list_user_files(current_user: dict = Depends(get_current_active_user)):
    """
    List all CV files for the current user
    """
    try:
        db = get_db()
        fs = gridfs.GridFS(db)
        
        user_id = current_user.get('id')
        
        # Find all files for this user
        files = list(fs.find({"user_id": user_id}))
        
        file_list = []
        for file in files:
            file_list.append({
                "_id": str(file._id),
                "filename": getattr(file, 'original_filename', file.filename),
                "uploadedAt": file.upload_date.isoformat() if file.upload_date else None,
                "size": file.length,
                "contentType": getattr(file, 'content_type', None),
                "atsScore": getattr(file, 'ats_score', None)
            })
        
        return JSONResponse({
            "success": True,
            "files": file_list
        })
        
    except Exception as e:
        logger.error(f"Error listing files: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user-files")
async def list_user_files_alias(current_user: dict = Depends(get_current_active_user)):
    """
    Alias for /files endpoint - List all CV files for the current user
    """
    return await list_user_files(current_user)


@router.get("/download/{file_id}")
async def download_file(file_id: str, current_user: dict = Depends(get_current_active_user)):
    """
    Download a CV file by ID
    """
    try:
        db = get_db()
        fs = gridfs.GridFS(db)
        
        # Validate file_id
        try:
            obj_id = ObjectId(file_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid file ID format")
        
        # Find the file
        try:
            grid_file = fs.get(obj_id)
        except gridfs.errors.NoFile:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Verify ownership
        file_user_id = getattr(grid_file, 'user_id', None)
        if file_user_id and file_user_id != current_user.get('id'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get filename and content type
        filename = getattr(grid_file, 'original_filename', grid_file.filename)
        content_type = getattr(grid_file, 'content_type', 'application/octet-stream')
        
        # Read file content
        file_content = grid_file.read()
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download-optimized-cv")
async def download_optimized_cv(
    request: DownloadOptimizedCVRequest,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Generate and download an optimized CV PDF from structured data
    """
    try:
        # Get structured CV data from request
        structured_cv = request.structured_cv or request.template_data
        optimized_text = request.optimized_text
        filename = request.filename or "Optimized_CV.pdf"
        
        if not structured_cv and not optimized_text:
            raise HTTPException(
                status_code=400,
                detail="No CV data provided. Please provide structured_cv or optimized_text."
            )
        
        # Build CV data for generator
        cv_data = {}
        if structured_cv:
            cv_data = {
                "name": structured_cv.get("name", ""),
                "email": structured_cv.get("email", ""),
                "phone": structured_cv.get("phone", ""),
                "location": structured_cv.get("location", ""),
                "summary": structured_cv.get("summary", ""),
                "skills": structured_cv.get("skills", []),
                "experience": structured_cv.get("experience", []),
                "education": structured_cv.get("education", []),
                "projects": structured_cv.get("projects", []),
                "certifications": structured_cv.get("certifications", []),
            }
        
        # Generate PDF
        logger.info("Generating optimized CV PDF...")
        cv_gen = get_cv_generator()
        pdf_result = cv_gen.generate_cv_pdf(cv_data)
        
        # Handle both BytesIO and CVGenerationResult
        pdf_bytes = None
        if pdf_result:
            if hasattr(pdf_result, 'success'):
                if pdf_result.success and pdf_result.pdf_bytes:
                    pdf_bytes = pdf_result.pdf_bytes.getvalue()
            elif hasattr(pdf_result, 'getvalue'):
                pdf_bytes = pdf_result.getvalue()
        
        if not pdf_bytes:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate PDF"
            )
        
        logger.info(f"Generated optimized CV PDF: {len(pdf_bytes)} bytes")
        
        # Return PDF as download
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type='application/pdf',
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating optimized CV: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete-cv/{file_id}")
async def delete_cv(file_id: str, current_user: dict = Depends(get_current_active_user)):
    """
    Delete a CV file by ID
    """
    try:
        db = get_db()
        fs = gridfs.GridFS(db)
        
        # Validate file_id
        try:
            obj_id = ObjectId(file_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid file ID format")
        
        # Find the file first to verify ownership
        try:
            grid_file = fs.get(obj_id)
        except gridfs.errors.NoFile:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Verify ownership
        file_user_id = getattr(grid_file, 'user_id', None)
        if file_user_id and file_user_id != current_user.get('id'):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete the file
        fs.delete(obj_id)
        
        logger.info(f"Deleted CV file: {file_id}")
        
        return JSONResponse({
            "success": True,
            "message": "CV deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
