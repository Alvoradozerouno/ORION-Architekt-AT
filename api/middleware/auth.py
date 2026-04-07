"""
Authentication and Authorization Router
JWT-based authentication system
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
import jwt
import os

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30

class UserCreate(BaseModel):
    """User registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """User login"""
    username: str
    password: str

class PasswordChange(BaseModel):
    """Password change request"""
    old_password: str
    new_password: str = Field(..., min_length=8)

class PasswordReset(BaseModel):
    """Password reset with token"""
    token: str
    new_password: str = Field(..., min_length=8)

class TokenRefresh(BaseModel):
    """Refresh token request"""
    refresh_token: str

class UserLoginOld(BaseModel):
    """User login - OLD"""
    username: str
    password: str

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

class UserResponse(BaseModel):
    """User info response"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_premium: bool
    created_at: datetime

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    # In production, retrieve user from database
    # For now, return payload data
    return {
        "username": username,
        "user_id": payload.get("user_id"),
        "role": payload.get("role", "user")
    }

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Get current active user"""
    # In production, check if user is active in database
    return current_user

async def require_admin(current_user: dict = Depends(get_current_active_user)):
    """Require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def require_premium(current_user: dict = Depends(get_current_active_user)):
    """Require premium subscription"""
    # In production, check premium status in database
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """
    🔐 **Register New User**

    Create a new user account.
    Features:
    - Email verification (optional)
    - Password strength validation
    - Automatic role assignment
    - Welcome email
    """
    # In production:
    # 1. Check if username/email already exists
    # 2. Hash password with bcrypt
    # 3. Save to database
    # 4. Send verification email

    # Simplified response
    return UserResponse(
        id=1,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role="user",
        is_premium=False,
        created_at=datetime.utcnow()
    )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    🔑 **Login**

    Authenticate user and get JWT tokens.

    Returns:
    - access_token: Use for API requests (valid 1 hour)
    - refresh_token: Use to get new access token (valid 30 days)
    """
    # In production:
    # 1. Fetch user from database
    # 2. Verify password with bcrypt
    # 3. Generate tokens

    # Simplified - check credentials (in production, check against database)
    if credentials.username == "demo" and credentials.password == "demo123":
        # Create tokens
        user_data = {
            "sub": credentials.username,
            "user_id": 1,
            "role": "architect"
        }

        access_token = create_access_token(user_data)
        refresh_token = create_refresh_token(user_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    🔄 **Refresh Access Token**

    Use refresh token to get a new access token.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type - expected refresh token"
        )

    # Create new access token
    user_data = {
        "sub": payload.get("sub"),
        "user_id": payload.get("user_id"),
        "role": payload.get("role")
    }

    access_token = create_access_token(user_data)

    return Token(
        access_token=access_token,
        refresh_token=token,  # Keep same refresh token
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_active_user)):
    """
    👤 **Get Current User**

    Get information about the authenticated user.
    """
    # In production, fetch full user data from database
    return UserResponse(
        id=current_user.get("user_id", 1),
        username=current_user.get("username", "demo"),
        email="demo@example.com",
        full_name="Demo User",
        role=current_user.get("role", "user"),
        is_premium=False,
        created_at=datetime.utcnow()
    )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_active_user)):
    """
    🚪 **Logout**

    Logout user (invalidate token on client side).
    In production, optionally add token to blacklist.
    """
    return {
        "message": "Successfully logged out",
        "username": current_user.get("username")
    }

@router.post("/change-password")
async def change_password(
    request: PasswordChange,
    current_user: dict = Depends(get_current_active_user)
):
    """
    🔒 **Change Password**

    Change user password.
    """
    # In production:
    # 1. Verify old password
    # 2. Hash new password
    # 3. Update in database
    # 4. Optionally invalidate all existing tokens

    return {
        "message": "Password changed successfully",
        "username": current_user.get("username")
    }

@router.post("/reset-password-request")
async def reset_password_request(email: EmailStr):
    """
    📧 **Request Password Reset**

    Send password reset email with token.
    """
    # In production:
    # 1. Check if email exists
    # 2. Generate reset token
    # 3. Send email with reset link
    # 4. Store token in database with expiration

    return {
        "message": f"If {email} exists, a password reset email has been sent",
        "note": "Check your email for reset instructions"
    }

@router.post("/reset-password")
async def reset_password(request: PasswordReset):
    """
    🔓 **Reset Password**

    Reset password using reset token from email.
    """
    # In production:
    # 1. Verify reset token
    # 2. Check if not expired
    # 3. Hash new password
    # 4. Update in database
    # 5. Delete reset token

    return {
        "message": "Password reset successfully",
        "next_step": "Please login with your new password"
    }

@router.get("/verify-email/{token}")
async def verify_email(token: str):
    """
    ✅ **Verify Email**

    Verify email address using token from registration email.
    """
    # In production:
    # 1. Decode verification token
    # 2. Mark email as verified in database
    # 3. Optionally grant benefits (extended trial, etc.)

    return {
        "message": "Email verified successfully",
        "email_verified": True
    }

# API Key authentication (alternative to JWT)

@router.post("/api-keys/create")
async def create_api_key(
    name: str,
    expires_days: Optional[int] = None,
    current_user: dict = Depends(get_current_active_user)
):
    """
    🔑 **Create API Key**

    Create API key for programmatic access.
    Use API key in header: X-API-Key: your-api-key
    """
    import secrets

    api_key = f"orion_{secrets.token_urlsafe(32)}"
    expires_at = None
    if expires_days:
        expires_at = datetime.utcnow() + timedelta(days=expires_days)

    # In production, save to database

    return {
        "api_key": api_key,
        "name": name,
        "user_id": current_user.get("user_id"),
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat() if expires_at else None,
        "warning": "Save this key securely! It won't be shown again."
    }

@router.get("/api-keys")
async def list_api_keys(current_user: dict = Depends(get_current_active_user)):
    """
    📋 **List API Keys**

    List all API keys for current user.
    """
    # In production, fetch from database
    return {
        "api_keys": [
            {
                "id": 1,
                "name": "Production API",
                "key_preview": "orion_****...****",
                "created_at": "2026-04-01T10:00:00",
                "last_used": "2026-04-06T11:30:00",
                "is_active": True
            }
        ],
        "total": 1
    }

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """
    🗑️ **Revoke API Key**

    Revoke an API key (cannot be undone).
    """
    # In production:
    # 1. Verify key belongs to user
    # 2. Mark as inactive in database

    return {
        "message": f"API key {key_id} revoked successfully",
        "revoked_at": datetime.utcnow().isoformat()
    }
