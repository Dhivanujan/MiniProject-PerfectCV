"""
FastAPI Authentication Routes
Handles user registration, login, password reset
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import random
from pymongo.database import Database

router = APIRouter()

# Request/Response Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    username: Optional[str] = None

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None

# Dependency to get MongoDB instance
def get_db() -> Database:
    from app_fastapi import get_mongo_db
    return get_mongo_db()

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Database = Depends(get_db)):
    """
    User login endpoint
    """
    try:
        user = db.users.find_one({'email': request.email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not check_password_hash(user['password'], request.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        user_public = UserResponse(
            id=str(user.get('_id')),
            email=user.get('email'),
            full_name=user.get('full_name'),
            username=user.get('username')
        )
        
        return AuthResponse(
            success=True,
            message="Logged in successfully",
            user=user_public
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error during login: {str(e)}"
        )

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Database = Depends(get_db)):
    """
    User registration endpoint
    """
    try:
        # Check if user already exists
        existing_user = db.users.find_one({'email': request.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = generate_password_hash(request.password)
        
        # Create user document
        user_doc = {
            'email': request.email,
            'password': hashed_password,
            'created_at': datetime.utcnow()
        }
        
        # Add optional fields
        if request.full_name:
            user_doc['full_name'] = request.full_name
        if request.username:
            user_doc['username'] = request.username
        if request.phone:
            user_doc['phone'] = request.phone
        
        # Insert user
        result = db.users.insert_one(user_doc)
        
        user_public = UserResponse(
            id=str(result.inserted_id),
            email=request.email,
            full_name=request.full_name,
            username=request.username
        )
        
        return AuthResponse(
            success=True,
            message="Registered successfully",
            user=user_public
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error during registration: {str(e)}"
        )

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Database = Depends(get_db)):
    """
    Request password reset code
    """
    try:
        user = db.users.find_one({'email': request.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email not found"
            )
        
        # Generate 6-digit code
        code = f"{random.randint(0, 999999):06d}"
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=15)
        
        reset_doc = {
            'email': request.email,
            'code': code,
            'created_at': now,
            'expires_at': expires_at,
            'attempts': 0,
            'used': False,
            'verified': False
        }
        
        db.password_resets.insert_one(reset_doc)
        
        # Send email (import and use email utils)
        try:
            from app.utils.email_utils import send_reset_code_email
            send_reset_code_email(request.email, code)
        except Exception as email_error:
            print(f"Warning: Failed to send email: {email_error}")
        
        return {
            "success": True,
            "message": "Password reset code sent to your email"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )

@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest, db: Database = Depends(get_db)):
    """
    Verify password reset code
    """
    try:
        reset = db.password_resets.find_one({
            'email': request.email,
            'code': request.code,
            'used': False
        })
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired code"
            )
        
        # Check if expired
        if datetime.utcnow() > reset['expires_at']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code has expired"
            )
        
        # Mark as verified
        db.password_resets.update_one(
            {'_id': reset['_id']},
            {'$set': {'verified': True}}
        )
        
        return {
            "success": True,
            "message": "Code verified successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Database = Depends(get_db)):
    """
    Reset password with verified code
    """
    try:
        reset = db.password_resets.find_one({
            'email': request.email,
            'code': request.code,
            'verified': True,
            'used': False
        })
        
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or unverified code"
            )
        
        # Check if expired
        if datetime.utcnow() > reset['expires_at']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Code has expired"
            )
        
        # Update password
        hashed_password = generate_password_hash(request.new_password)
        db.users.update_one(
            {'email': request.email},
            {'$set': {'password': hashed_password}}
        )
        
        # Mark reset as used
        db.password_resets.update_one(
            {'_id': reset['_id']},
            {'$set': {'used': True}}
        )
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )

@router.post("/logout")
async def logout():
    """
    User logout endpoint
    """
    return {
        "success": True,
        "message": "Logged out successfully"
    }
