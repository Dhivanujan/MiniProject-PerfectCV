"""
FastAPI File Upload Routes
Handles CV file uploads with JWT authentication
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from typing import Optional
import io
import logging
from bson import ObjectId
import gridfs

from app.auth.jwt_handler import get_current_active_user
from app.services.unified_cv_extractor import UnifiedCVExtractor
from app.services.cv_generator import get_cv_generator
from app.services.cv_scoring_service import CVScoringService

logger = logging.getLogger(__name__)

router = APIRouter()

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

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
        extractor = UnifiedCVExtractor()
        extraction_result = extractor.extract_from_bytes(
            file_content, 
            filename=cv_file.filename
        )
        
        if not extraction_result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=f"CV extraction failed: {extraction_result.get('error', 'Unknown error')}"
            )
        
        cv_data = extraction_result.get('data', {})
        raw_text = extraction_result.get('raw_text', '')
        
        # Score the CV
        try:
            scoring_service = CVScoringService()
            score_result = scoring_service.score_cv(cv_data)
            ats_score = score_result.get('overall_score', 0)
            cv_data['ats_score'] = ats_score
            cv_data['scoring_details'] = score_result
        except Exception as e:
            logger.warning(f"CV scoring failed: {e}")
            ats_score = 0
        
        # Generate PDF
        pdf_bytes = None
        try:
            cv_gen = get_cv_generator()
            pdf_result = cv_gen.generate_cv_pdf(cv_data)
            if pdf_result and pdf_result.success:
                pdf_bytes = pdf_result.pdf_bytes.getvalue() if pdf_result.pdf_bytes else None
        except Exception as e:
            logger.warning(f"PDF generation failed: {e}")
        
        # Store in GridFS
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
        
        return JSONResponse({
            "success": True,
            "message": "CV uploaded and processed successfully",
            "file_id": str(file_id),
            "pdf_file_id": str(pdf_file_id) if pdf_file_id else None,
            "cv_data": cv_data,
            "ats_score": ats_score,
            "filename": cv_file.filename
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
    return JSONResponse({
        "success": True,
        "user": {
            "id": current_user.get('id'),
            "email": current_user.get('email'),
            "full_name": current_user.get('full_name'),
            "username": current_user.get('username')
        }
    })

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
