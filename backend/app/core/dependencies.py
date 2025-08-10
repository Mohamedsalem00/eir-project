from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import time
from collections import defaultdict
from .database import SessionLocal
from .auth import verify_token
from .permissions import PermissionManager, Operation, AccessLevel, PorteeDonnees
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
    
    # Check if user is active
    if hasattr(user, 'est_actif') and not user.est_actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
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
            # Check if user is active
            if user and hasattr(user, 'est_actif') and not user.est_actif:
                return None
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
    """Get current user and user type with enhanced access level detection
    Returns: (user, niveau_acces_string)"""
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
                # Check if user is active
                if hasattr(user, 'est_actif') and not user.est_actif:
                    check_visitor_rate_limit(request)
                    return None, "visitor"
                
                # Return user with their specific access level
                niveau_acces = user.niveau_acces or "basic"
                if user.type_utilisateur == "administrateur":
                    niveau_acces = "admin"
                
                return user, niveau_acces
    except:
        # Invalid token, treat as anonymous visitor
        check_visitor_rate_limit(request)
        return None, "visitor"
    
    # No valid user found, treat as anonymous visitor
    check_visitor_rate_limit(request)
    return None, "visitor"

def get_access_context(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get comprehensive access context for advanced permission checking"""
    user, niveau_acces = get_current_user_with_visitor_support(request, credentials, db)
    
    # Get permission context from PermissionManager
    filter_context = PermissionManager.get_data_filter_context(user)
    
    return {
        "user": user,
        "niveau_acces": niveau_acces,
        "is_authenticated": user is not None,
        "is_admin": filter_context["is_admin"],
        "permissions": PermissionManager.get_user_permissions_summary(user) if user else {},
        "data_filter": filter_context,
        "request_ip": request.client.host if request.client else "unknown"
    }

def require_operation_permission(operation: Operation):
    """Enhanced dependency factory for operation-specific permission checking"""
    def permission_dependency(
        contexte_acces: Dict[str, Any] = Depends(get_access_context)
    ) -> Dict[str, Any]:
        user = contexte_acces["user"]
        
        if not PermissionManager.has_permission(user, operation):
            # Provide detailed error message based on user status
            if not user:
                detail = f"Authentication required for operation: {operation.value}"
                status_code = status.HTTP_401_UNAUTHORIZED
            else:
                detail = f"Insufficient permissions for operation: {operation.value}. Current access level: {contexte_acces['niveau_acces']}"
                status_code = status.HTTP_403_FORBIDDEN
            
            raise HTTPException(status_code=status_code, detail=detail)
        
        return contexte_acces
    
    return permission_dependency

def require_niveau_acces(min_level: AccessLevel):
    """Enhanced dependency factory for access level checking"""
    def level_dependency(
        contexte_acces: Dict[str, Any] = Depends(get_access_context)
    ) -> Dict[str, Any]:
        user = contexte_acces["user"]
        current_level_str = contexte_acces["niveau_acces"]
        
        try:
            current_level = AccessLevel.from_french(current_level_str)
        except ValueError:
            current_level = AccessLevel.VISITOR
        
        # Check if current level meets minimum requirement
        level_hierarchy = [
            AccessLevel.VISITOR,
            AccessLevel.BASIC,
            AccessLevel.LIMITED,
            AccessLevel.STANDARD,
            AccessLevel.ELEVATED,
            AccessLevel.ADMIN
        ]
        
        if level_hierarchy.index(current_level) < level_hierarchy.index(min_level):
            if current_level == AccessLevel.VISITOR:
                status_code = status.HTTP_401_UNAUTHORIZED
                detail = f"Authentication required. Minimum access level: {min_level.value}"
            else:
                status_code = status.HTTP_403_FORBIDDEN
                detail = f"Insufficient access level. Required: {min_level.value}, Current: {current_level.value}"
            
            raise HTTPException(status_code=status_code, detail=detail)
        
        return contexte_acces
    
    return level_dependency

def require_auth(min_level: str = "user"):
    """Enhanced authentication dependency with access level support"""
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
    """Allow all user types with appropriate limitations and enhanced context"""
    return get_current_user_with_visitor_support(request, credentials, db)

def filter_query_by_access(query, contexte_acces: Dict[str, Any], entity_type: str):
    """Apply access-based filtering to database queries"""
    user = contexte_acces["user"]
    filter_context = contexte_acces["data_filter"]
    
    if filter_context["is_admin"]:
        return query  # Admin sees everything
    
    if not user:
        # Anonymous users get no data
        return query.filter(False)
    
    # Apply filtering based on data portee_donnees
    portee_donnees = filter_context["portee_donnees"]
    
    if portee_donnees == PorteeDonnees.OWN:
        # User sees only their own data
        if entity_type == "device":
            query = query.filter_by(utilisateur_id=user.id)
        elif entity_type == "search":
            query = query.filter_by(utilisateur_id=user.id)
        elif entity_type == "sim":
            query = query.filter_by(utilisateur_id=user.id)
    
    elif portee_donnees == PorteeDonnees.BRANDS:
        # User sees data for specific brands
        allowed_brands = filter_context["marques_autorisees"]
        if allowed_brands and entity_type == "device":
            query = query.filter(query.modele.marque.in_(allowed_brands))
    
    elif portee_donnees == PorteeDonnees.ORGANIZATION:
        # User sees organization data (would need organization field on entities)
        if filter_context["organization"] and hasattr(query.modele, 'organization'):
            query = query.filter_by(organization=filter_context["organization"])
    
    elif portee_donnees == PorteeDonnees.RANGES:
        # Apply IMEI range filtering (complex logic for IMEI-related queries)
        pass  # Implement based on specific needs
    
    return query
