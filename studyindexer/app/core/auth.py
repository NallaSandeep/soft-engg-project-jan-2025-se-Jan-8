"""Authentication middleware and dependencies"""
from typing import Optional, List, Union
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from pydantic import BaseModel
import logging
from app.core.config import settings
from app.core.errors import StudyIndexerError

logger = logging.getLogger(__name__)
security = HTTPBearer()

class UserContext(BaseModel):
    """User context extracted from JWT token"""
    user_id: str
    role: str
    username: Optional[str] = None
    courses: List[str] = []

    def __init__(self, **data):
        super().__init__(**data)
        if not self.username:
            self.username = f"user_{self.user_id}"
        if not self.courses:
            self.courses = []

class AuthError(StudyIndexerError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            code="AUTH_ERROR",
            status_code=401
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserContext:
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        return UserContext(
            user_id=payload["sub"],
            role=payload.get("role", "user"),
            username=payload.get("username"),
            courses=payload.get("courses", [])
        )
    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )

def require_role(allowed_roles: List[str]):
    """Dependency factory for role-based access control"""
    async def role_checker(user: UserContext = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role {user.role} not allowed to access this endpoint"
            )
        return user
    return role_checker

# Role-based dependencies
require_admin = require_role(["admin"])
require_teacher = require_role(["admin", "teacher"])
require_student = require_role(["admin", "teacher", "student"])

class AuthMiddleware:
    """Middleware to validate JWT tokens and add user context"""
    async def __call__(self, request: Request, call_next):
        # Skip auth for public endpoints
        public_paths = [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            f"{settings.API_V1_STR}/docs",
            f"{settings.API_V1_STR}/redoc",
            f"{settings.API_V1_STR}/openapi.json"
        ]
        
        if any(request.url.path.endswith(path) for path in public_paths):
            return await call_next(request)
            
        try:
            # Get token from header
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                return JSONResponse(
                    status_code=401,
                    content={
                        "success": False,
                        "message": "Missing authentication token",
                        "error": {
                            "code": "AUTH_ERROR",
                            "details": None
                        }
                    }
                )
                
            token = auth.split(" ")[1]
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Add user context to request state
            request.state.user = UserContext(
                user_id=payload["sub"],
                role=payload["role"],
                username=payload.get("username"),
                courses=payload.get("courses", [])
            )
            
            return await call_next(request)
            
        except AuthError as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "message": str(e),
                    "error": {
                        "code": e.code,
                        "details": e.details
                    }
                }
            )
        except Exception as e:
            logger.error(f"Authentication middleware error: {str(e)}")
            return JSONResponse(
                status_code=401,
                content={
                    "success": False,
                    "message": "Authentication failed",
                    "error": {
                        "code": "AUTH_ERROR",
                        "details": {"error": str(e)} if str(e) else None
                    }
                }
            ) 