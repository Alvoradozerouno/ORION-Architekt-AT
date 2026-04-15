"""
API Authentication Middleware for ORION Architekt AT
"""
from fastapi import Depends, HTTPException, Security, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
import os
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Create auth router
router = APIRouter()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
if not SECRET_KEY:
    import secrets
    SECRET_KEY = secrets.token_hex(32)
    logger.warning(
        "JWT_SECRET_KEY not set - using a randomly generated key. "
        "Tokens will be invalidated on restart. Set JWT_SECRET_KEY in environment for production."
    )
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

class User(BaseModel):
    user_id: str
    username: str
    email: str
    roles: List[str] = []
    is_active: bool = True

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> User:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return User(
            user_id=payload.get("user_id"),
            username=payload.get("username"),
            email=payload.get("email"),
            roles=payload.get("roles", [])
        )
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user

async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role"""
    if "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def require_premium(current_user: User = Depends(get_current_active_user)) -> User:
    """Require premium subscription"""
    if "premium" not in current_user.roles and "admin" not in current_user.roles:
        raise HTTPException(status_code=403, detail="Premium subscription required")
    return current_user
