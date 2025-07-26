from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import time
from collections import defaultdict
from .database import SessionLocal
from .auth import verify_token
from ..models.utilisateur import Utilisateur

security = HTTPBearer()

def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Utilisateur:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def get_admin_user(current_user: Utilisateur = Depends(get_current_user)) -> Utilisateur:
    """Require admin privileges"""
    if current_user.type_utilisateur != "administrateur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# Optional dependency - allows both authenticated and anonymous users
def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[Utilisateur]:
    """Get current user if authenticated, None otherwise"""
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if user_id:
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            return user
    except:
        pass
    
    return None

# Rate limiting for visitors (in production, use Redis)
visitor_requests = defaultdict(list)
VISITOR_RATE_LIMIT = 10  # requests per hour
VISITOR_TIME_WINDOW = 3600  # 1 hour in seconds

def check_visitor_rate_limit(request: Request):
    """Check rate limit for visitor users"""
    client_ip = request.client.host
    now = time.time()
    
    # Clean old requests
    visitor_requests[client_ip] = [
        req_time for req_time in visitor_requests[client_ip] 
        if now - req_time < VISITOR_TIME_WINDOW
    ]
    
    # Check if limit exceeded
    if len(visitor_requests[client_ip]) >= VISITOR_RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Visitors can make {VISITOR_RATE_LIMIT} requests per hour."
        )
    
    # Add current request
    visitor_requests[client_ip].append(now)



def get_current_user_with_visitor_support(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> tuple[Optional[Utilisateur], str]:
    """Get current user and user type (admin/user/visitor)
    Note: visitors are anonymous - no database record needed"""
    if credentials is None:
        # Anonymous visitor - apply rate limiting
        check_visitor_rate_limit(request)
        return None, "visitor"
    
    try:
        token = credentials.credentials
        payload = verify_token(token)
        user_id = payload.get("sub")
        
        if user_id:
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            if user:
                user_type = "admin" if user.type_utilisateur == "administrateur" else "user"
                return user, user_type
    except:
        # Invalid token, treat as anonymous visitor
        check_visitor_rate_limit(request)
        return None, "visitor"
    
    # No valid user found, treat as anonymous visitor
    check_visitor_rate_limit(request)
    return None, "visitor"


def require_auth(min_level: str = "user"):
    """Dependency factory to require specific authentication level"""
    def auth_dependency(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
    ) -> Utilisateur:
        user, user_type = get_current_user_with_visitor_support(request, credentials, db)
        
        if min_level == "admin" and user_type != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        elif min_level == "user" and user_type == "visitor":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        return user
    
    return auth_dependency

def allow_all_with_limits(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> tuple[Optional[Utilisateur], str]:
    """Allow all user types with appropriate limitations"""
    return get_current_user_with_visitor_support(request, credentials, db)
