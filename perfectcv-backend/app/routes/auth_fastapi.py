"""
FastAPI Authentication Routes with JWT
Handles user registration, login, password reset with JWT tokens
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import random
from pymongo.database import Database
from app.auth.jwt_handler import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_current_user,
    get_current_active_user
)

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

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = "bearer"

# Dependency to get MongoDB instance
def get_db() -> Database:
    from app_fastapi import get_mongo_db
    return get_mongo_db()

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Database = Depends(get_db)):
    """
    User login endpoint - Returns JWT tokens
    """
    try:
        # Authenticate user
        user = authenticate_user(db, request.email, request.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create JWT tokens
        access_token = create_access_token(
            data={"sub": str(user['_id']), "email": user['email']}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user['_id']), "email": user['email']}
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
            user=user_public,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
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
    User registration endpoint - Returns JWT tokens
    """
    try:
        # Check if user already exists
        existing_user = db.users.find_one({'email': request.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password using JWT handler
        hashed_password = get_password_hash(request.password)
        
        # Create user document
        user_doc = {
            'email': request.email,
            'password': hashed_password,
            'created_at': datetime.utcnow(),
            'disabled': False
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
        
        # Create JWT tokens
        access_token = create_access_token(
            data={"sub": str(result.inserted_id), "email": request.email}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(result.inserted_id), "email": request.email}
        )
        
        user_public = UserResponse(
            id=str(result.inserted_id),
            email=request.email,
            full_name=request.full_name,
            username=request.username
        )
        
        return AuthResponse(
            success=True,
            message="Registered successfully",
            user=user_public,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
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
        
        # Update password using JWT handler
        hashed_password = get_password_hash(request.new_password)
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
    User logout endpoint (client should discard tokens)
    """
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """
    Get current authenticated user information
    """
    return UserResponse(
        id=current_user['id'],
        email=current_user['email'],
        full_name=current_user.get('full_name'),
        username=current_user.get('username')
    )

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(request: RefreshTokenRequest, db: Database = Depends(get_db)):
    """
    Refresh access token using refresh token
    """
    try:
        from app.auth.jwt_handler import verify_token
        from bson import ObjectId
        
        # Verify refresh token
        payload = verify_token(request.refresh_token)
        
        # Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        
        # Get user from database
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new tokens
        access_token = create_access_token(
            data={"sub": str(user['_id']), "email": user['email']}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user['_id']), "email": user['email']}
        )
        
        user_public = UserResponse(
            id=str(user['_id']),
            email=user['email'],
            full_name=user.get('full_name'),
            username=user.get('username')
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user_public
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server error: {str(e)}"
        )
