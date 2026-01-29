"""
FastAPI Chatbot Routes
Handles chatbot interactions with JWT authentication
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import gridfs
from bson import ObjectId

from app.auth.jwt_handler import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    """Get MongoDB database instance"""
    from app_fastapi import get_mongo_db
    return get_mongo_db()

class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

@router.get("/cv-info")
async def get_cv_info(current_user: dict = Depends(get_current_active_user)):
    """
    Get CV information for the current user
    """
    try:
        db = get_db()
        fs = gridfs.GridFS(db)
        
        user_id = current_user.get('id')
        
        # Find the most recent CV file for this user
        files = list(fs.find({"user_id": user_id}).sort([("uploadDate", -1)]).limit(1))
        
        if not files:
            return JSONResponse({
                "success": True,
                "has_cv": False,
                "message": "No CV uploaded yet"
            })
        
        file = files[0]
        cv_data = getattr(file, 'cv_data', {})
        raw_text = getattr(file, 'raw_text', '')
        ats_score = getattr(file, 'ats_score', None)
        
        return JSONResponse({
            "success": True,
            "has_cv": True,
            "cv_data": cv_data,
            "raw_text": raw_text[:500] if raw_text else None,  # First 500 chars
            "ats_score": ats_score,
            "filename": getattr(file, 'original_filename', file.filename),
            "uploaded_at": file.upload_date.isoformat() if file.upload_date else None
        })
        
    except Exception as e:
        logger.error(f"Error getting CV info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(
    message: ChatMessage,
    current_user: dict = Depends(get_current_active_user)
):
    """
    Chat with the AI assistant about CV
    """
    try:
        # This is a placeholder - implement actual chatbot logic
        return JSONResponse({
            "success": True,
            "response": "Chatbot functionality is being migrated to FastAPI. Please check back soon.",
            "message": message.message
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
