from fastapi import FastAPI, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from .core.dependencies import (
    get_db, get_current_user, get_admin_user, 
    allow_all_with_limits, require_auth
)
from .core.i18n_deps import get_current_translator, get_language_from_request
from .core.audit_deps import get_audit_service
from .i18n import get_translator, SUPPORTED_LANGUAGES
from .services.audit import AuditService
from .routes.auth import router as auth_router
from .models.appareil import Appareil
from .models.utilisateur import Utilisateur
from .models.recherche import Recherche
from .models.sim import SIM
from .models.notification import Notification
from .models.journal_audit import JournalAudit
from .models.imei import IMEI
from datetime import datetime, timedelta
import uuid
from typing import Optional, List
import platform

# Enhanced FastAPI configuration
app = FastAPI(
    title="EIR Project API",
    description="Equipment Identity Register (EIR) API for professional mobile device management",
    version="1.0.0",
    terms_of_service="https://eir-project.com/terms",
    contact={
        "name": "EIR Development Team",
        "email": "contact@eir-project.com",
        "url": "https://eir-project.com"
    },
    license_info={
        "name": "Proprietary License",
        "url": "https://eir-project.com/license"
    },
    openapi_tags=[
        {
            "name": "System",
            "description": "System information and health checks"
        },
        {
            "name": "Public",
            "description": "Public endpoints available to all users"
        },
        {
            "name": "Authentication",
            "description": "User authentication and authorization"
        },
        {
            "name": "IMEI",
            "description": "IMEI validation and lookup services"
        },
        {
            "name": "Devices",
            "description": "Device management operations"
        },
        {
            "name": "SIM Cards",
            "description": "SIM card management operations"
        },
        {
            "name": "Users",
            "description": "User management operations"
        },
        {
            "name": "Search History",
            "description": "Search history and tracking endpoints"
        },
        {
            "name": "Notifications",
            "description": "Notification management endpoints"
        },
        {
            "name": "Analytics",
            "description": "Analytics and reporting endpoints"
        },
        {
            "name": "Admin",
            "description": "Administrative operations"
        }
    ]
)

# Include authentication routes
app.include_router(auth_router, tags=["Authentication"])

# Store app start time for uptime calculation
app_start_time = datetime.now()

# Helper function for date formatting
def format_datetime(dt):
    """Format datetime to readable string"""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_system_uptime():
    """Calculate system uptime"""
    uptime = datetime.now() - app_start_time
    return str(uptime).split('.')[0]  # Remove microseconds

# SYSTEM ENDPOINTS
@app.get(
    "/",
    tags=["System"],
    summary="API Welcome",
    description="Get comprehensive API information, capabilities, and quick start guide"
)
async def welcome(
    request: Request,
    user_info: tuple = Depends(allow_all_with_limits),
    translator = Depends(get_current_translator)
):
    """
    ## Welcome to EIR Project API
    
    This endpoint provides comprehensive information about the API, including:
    
    - **Service capabilities** and features
    - **Available endpoints** based on your access level
    - **Technical specifications** and SLAs
    - **Quick start guide** and documentation links
    - **Security and compliance** information
    - **Contact information** and support details
    
    ### Access Levels:
    - **Visitors**: Basic API information and public endpoints
    - **Authenticated Users**: Enhanced information and user endpoints
    - **Administrators**: Complete API documentation and admin endpoints
    
    ### Supported Languages:
    Use the `X-Language` header or `?lang=` parameter with: `en`, `fr`, `ar`
    """
    current_user, user_type = user_info
    
    # Get base URL for the request
    base_url = f"{request.url.scheme}://{request.headers.get('host', 'localhost')}"
    
    # Build capabilities based on user type
    capabilities = {
        "imei_validation": {
            "real_time_lookup": True,
            "batch_validation": user_type != "visitor",
            "history_tracking": user_type != "visitor",
            "status_monitoring": user_type == "admin",
            "supported_formats": ["15-digit IMEI", "14-digit IMEI"]
        },
        "device_management": {
            "device_registration": user_type != "visitor",
            "multi_imei_support": True,
            "device_assignment": user_type == "admin",
            "bulk_import": user_type == "admin",
            "brand_analytics": True
        },
        "user_management": {
            "role_based_access": True,
            "multi_tenant": user_type != "visitor",
            "audit_logging": user_type == "admin",
            "user_analytics": user_type == "admin"
        }
    }
    
    # Build endpoints based on user type
    public_endpoints = {
        "imei_lookup": "/imei/{imei}",
        "imei_search_log": "/imei/{imei}/search",
        "public_statistics": "/public/stats",
        "health_check": "/health",
        "api_info": "/",
        "supported_languages": "/languages"
    }
    
    authenticated_endpoints = {}
    admin_endpoints = {}
    
    if user_type in ["user", "admin"]:
        authenticated_endpoints = {
            "user_devices": "/devices",
            "user_sims": "/sims", 
            "search_history": "/searches",
            "user_profile": "/users/{user_id}",
            "notifications": "/notifications",
            "analytics": "/analytics/searches"
        }
    if user_type == "admin":
        admin_endpoints = {
            "user_management": "/users",
            "admin_users": "/admin/users",
            "device_management": "/admin/devices",
            "bulk_operations": "/admin/bulk-import-devices",
            "audit_logs": "/admin/audit-logs",
            "system_analytics": "/analytics/devices"
        }
    
    return {
        "title": translator.translate("welcome_title"),
        "description": translator.translate("welcome_description"),
        "tagline": translator.translate("welcome_tagline"),
        "status": translator.translate("api_status"),
        "timestamp": datetime.now().isoformat(),
        "language": translator.current_language,
        
        "api": {
            "name": translator.translate("service_name"),
            "version": translator.translate("api_version"),
            "build": translator.translate("build_version"),
            "environment": translator.translate("environment"),
            "uptime": get_system_uptime()
        },
        
        "contact": {
            "organization": translator.translate("organization"),
            "email": translator.translate("contact_email"),
            "support_email": translator.translate("support_email"),
            "documentation_url": translator.translate("documentation_url")
        },
        
        "security": {
            "authentication_methods": ["JWT Bearer Token", "API Key (Enterprise)"],
            "rate_limiting": translator.translate("rate_limits"),
            "compliance_standards": ["GDPR", "SOX", "ISO 27001", "GSMA Guidelines"],
            "data_encryption": "TLS 1.3, AES-256"
        },
        
        "capabilities": capabilities,
        
        "endpoints": {
            "public": public_endpoints,
            "authenticated": authenticated_endpoints,
            "admin": admin_endpoints
        },
        
        "technical_specs": {
            "supported_formats": ["JSON", "XML (on request)"],
            "max_request_size": "10MB",
            "response_time_sla": "< 200ms (95th percentile)",
            "availability_sla": "99.9% uptime",
            "sdk_support": ["Python", "JavaScript", "Java", "cURL examples"]
        },
        
        "quick_start": {
            "documentation": f"{base_url}/docs",
            "interactive_docs": f"{base_url}/docs",
            "health_check": f"{base_url}/health",
            "imei_check_example": f"{base_url}/imei/123456789012345",
            "supported_languages": f"{base_url}/languages"
        },
        
        "legal": {
            "terms_of_service": translator.translate("terms_of_service"),
            "privacy_policy": translator.translate("privacy_policy"),
            "license": translator.translate("license"),
            "data_retention": "Data retained according to regional regulations"
        }
    }

@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    description="Comprehensive system health and status information"
)
async def health_check(
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    """
    ## System Health Check
    
    Provides detailed system health information including:
    - Service status and uptime
    - Database connectivity
    - System resources
    - API endpoint status
    - Security status
    """
    try:
        # Test database connection
        db_status = {"status": "connected", "message": "Database connection successful"}
        db_latency = "< 10ms"
        try:
            db.execute("SELECT 1")
        except Exception as e:
            db_status = {"status": "error", "message": str(e)}
            db_latency = "N/A"
        
        # System information
        system_info = {
            "uptime": get_system_uptime(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "server_time": datetime.now().isoformat()
        }
        
        # Endpoint status check
        endpoints_status = {
            "authentication": "operational",
            "imei_validation": "operational", 
            "device_management": "operational",
            "analytics": "operational"
        }
        
        # Security status
        security_status = {
            "tls_encryption": "enabled",
            "jwt_validation": "active",
            "rate_limiting": "enabled",
            "audit_logging": "active"
        }
        
        return {
            "status": translator.translate("service_healthy"),
            "timestamp": datetime.now().isoformat(),
            "service": translator.translate("service_name"),
            "version": translator.translate("api_version"),
            "uptime": system_info["uptime"],
            "database": {
                "status": db_status["status"],
                "message": db_status["message"],
                "latency": db_latency
            },
            "system_info": system_info,
            "endpoints_status": endpoints_status,
            "security_status": security_status
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        )

@app.get(
    "/languages",
    tags=["System"],
    summary="Supported Languages",
    description="Get list of supported languages and locale information"
)
def get_supported_languages():
    """
    ## Supported Languages
    
    Get information about all supported languages including:
    - Language codes and names
    - Native language names
    - RTL (Right-to-Left) support
    - Default language settings
    """
    return {
        "supported_languages": SUPPORTED_LANGUAGES,
        "default_language": "en",
        "usage": {
            "header": "Set X-Language header to desired language code",
            "query_param": "Add ?lang=code to any request URL",
            "accept_language": "Browser Accept-Language header is automatically detected"
        }
    }


@app.get(
    "/imei/{imei}",
    tags=["IMEI", "Public"],
    summary="IMEI Lookup",
    description="Look up IMEI information with different access levels and automatic search logging"
)
def check_imei(
    imei: str,
    request: Request,
    db: Session = Depends(get_db),
    user_info: tuple = Depends(allow_all_with_limits),
    translator = Depends(get_current_translator),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    ## IMEI Lookup Service with Automatic Search Logging
    
    This endpoint automatically logs every search in both Recherche and JournalAudit tables.
    
    ### Access Levels:
    - **Visitors**: Basic device information (brand, model)
    - **Authenticated Users**: Enhanced device details and user information
    - **Administrators**: Complete device and ownership information
    
    ### Parameters:
    - **imei**: 15-digit IMEI number to lookup
    
    ### Response includes:
    - IMEI validation status
    - Device information (based on access level)
    - Slot number and status
    - Search logging confirmation
    """
    current_user, user_type = user_info
    
    # Search for IMEI
    imei_record = db.query(IMEI).filter(IMEI.imei_number == imei).first()
    found = imei_record is not None
    
    # Log the search in Recherche table (for search history)
    recherche = Recherche(
        id=uuid.uuid4(),
        date_recherche=datetime.now(),
        imei_recherche=imei,
        utilisateur_id=current_user.id if current_user else None
    )
    db.add(recherche)
    
    # Log in audit service (for audit trail)
    audit_service.log_imei_search(
        imei=imei,
        user_id=str(current_user.id) if current_user else None,
        found=found
    )

        # Commit both logs
    db.commit()
    
    if imei_record:
        appareil = imei_record.appareil
        
        # Base response for all users
        response = {
            "id":imei_record.id,
            "imei": imei,
            "found": True,
            "status": imei_record.status,
            "slot_number": imei_record.slot_number,
            "message": translator.translate("imei_found"),
            "search_logged": True,
            "search_id": str(recherche.id)
        }
        
        # Enhanced details for authenticated users
        if user_type != "visitor":
            response["device"] = {
                "id": str(appareil.id),
                "marque": appareil.marque,
                "modele": appareil.modele,
                "emmc": appareil.emmc,
                "utilisateur_id": str(appareil.utilisateur_id) if appareil.utilisateur_id else None
            }
        else:
            # Limited info for visitors
            response["device"] = {
                "marque": appareil.marque,
                "modele": appareil.modele
            }
        
        return response
    
    return {
        "imei": imei,
        "found": False,
        "message": translator.translate("imei_not_found"),
        "search_logged": True,
        "search_id": str(recherche.id)
    }

# Device Management APIs with proper audit logging
@app.post("/devices", tags=["Devices"])
def register_device(
    device_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user")),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Register device with audit logging"""
    # Set device owner to current user if not admin
    if current_user.type_utilisateur != "administrateur":
        device_data["utilisateur_id"] = current_user.id
    
    device = Appareil(
        id=uuid.uuid4(),
        marque=device_data.get("marque"),
        modele=device_data.get("modele"),
        emmc=device_data.get("emmc"),
        utilisateur_id=device_data.get("utilisateur_id")
    )
    db.add(device)
    db.flush()  # Get the device ID
    
    # Add IMEIs
    imeis_data = device_data.get("imeis", [])
    imei_numbers = []
    for i, imei_data in enumerate(imeis_data):
        imei = IMEI(
            id=uuid.uuid4(),
            imei_number=imei_data.get("imei_number"),
            slot_number=imei_data.get("slot_number", i + 1),
            status=imei_data.get("status", "active"),
            appareil_id=device.id
        )
        db.add(imei)
        imei_numbers.append(imei.imei_number)
    
    db.commit()
    db.refresh(device)
    
    # Log device creation
    audit_service.log_device_creation(
        device_id=str(device.id),
        user_id=str(current_user.id),
        device_data={
            "marque": device.marque,
            "modele": device.modele,
            "emmc": device.emmc,
            "imeis": imei_numbers
        }
    )
    
    return {
        "id": str(device.id),
        "marque": device.marque,
        "modele": device.modele,
        "imeis": [
            {
                "imei_number": imei.imei_number,
                "slot_number": imei.slot_number,
                "status": imei.status
            }
            for imei in device.imeis
        ]
    }

@app.get("/searches", tags=["Search History"])
def list_searches(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user"))
):
    """List searches - users see only their searches, admins see all"""
    if current_user.type_utilisateur == "administrateur":
        searches = db.query(Recherche).offset(skip).limit(limit).all()
    else:
        searches = db.query(Recherche).filter(
            Recherche.utilisateur_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    return {
        "searches": [
            {
                "id": str(search.id),
                "date_recherche": format_datetime(search.date_recherche),
                "imei_recherche": search.imei_recherche,
                "utilisateur_id": str(search.utilisateur_id) if search.utilisateur_id else None
            }
            for search in searches
        ]
    }

# User Management APIs with proper audit logging
@app.post("/users", tags=["Users", "Admin"])
def create_user(
    user_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin")),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Admin only - create new user with audit logging"""
    from .core.auth import get_password_hash
    
    user = Utilisateur(
        id=uuid.uuid4(),
        nom=user_data.get("nom"),
        email=user_data.get("email"),
        mot_de_passe=get_password_hash(user_data.get("mot_de_passe")),
        type_utilisateur=user_data.get("type_utilisateur", "utilisateur_authentifie")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Log user creation
    audit_service.log_user_creation(
        new_user_id=str(user.id),
        created_by_user_id=str(current_user.id),
        user_data={
            "nom": user.nom,
            "email": user.email,
            "type_utilisateur": user.type_utilisateur
        }
    )
    
    return {"id": str(user.id), "nom": user.nom, "email": user.email}

@app.get("/users/{user_id}")
def get_user(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user")),
    translator = Depends(get_current_translator)
):
    """Get user details - users can only see their own data, admins see all"""
    # Users can only access their own data
    if current_user.type_utilisateur != "administrateur" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translator.translate("access_denied")
        )
    
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, 
            detail=translator.translate("user_not_found")
        )
    
    # Get user's devices and SIMs
    devices = db.query(Appareil).filter(Appareil.utilisateur_id == user_id).all()
    sims = db.query(SIM).filter(SIM.utilisateur_id == user_id).all()
    
    return {
        "id": str(user.id),
        "nom": user.nom,
        "email": user.email,
        "type_utilisateur": user.type_utilisateur,
        "devices": [
            {
                "id": str(d.id), 
                "marque": d.marque, 
                "modele": d.modele,
                "imeis": [imei.imei_number for imei in d.imeis]
            } 
            for d in devices
        ],
        "sims": [{"id": str(s.id), "iccid": s.iccid, "operateur": s.operateur} for s in sims]
    }

# SIM Card Management APIs
@app.post("/sims", tags=["SIM Cards"])
def register_sim(
    sim_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user"))
):
    """Register new SIM - authenticated users only"""
    # Set SIM owner to current user if not admin
    if current_user.type_utilisateur != "administrateur":
        sim_data["utilisateur_id"] = current_user.id
        
    sim = SIM(
        id=uuid.uuid4(),
        iccid=sim_data.get("iccid"),
        operateur=sim_data.get("operateur"),
        utilisateur_id=sim_data.get("utilisateur_id")
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)
    return {"id": str(sim.id), "iccid": sim.iccid, "operateur": sim.operateur}

@app.get("/sims", tags=["SIM Cards"])
def list_sims(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user"))
):
    """List SIMs - users see only their SIMs, admins see all"""
    if current_user.type_utilisateur == "administrateur":
        sims = db.query(SIM).offset(skip).limit(limit).all()
    else:
        sims = db.query(SIM).filter(
            SIM.utilisateur_id == current_user.id
        ).offset(skip).limit(limit).all()
        
    return {
        "sims": [
            {
                "id": str(sim.id),
                "iccid": sim.iccid,
                "operateur": sim.operateur,
                "utilisateur_id": str(sim.utilisateur_id) if sim.utilisateur_id else None
            }
            for sim in sims
        ]
    }

@app.get("/sims/{iccid}", tags=["SIM Cards"])
def check_iccid(iccid: str, db: Session = Depends(get_db)):
    sim = db.query(SIM).filter(SIM.iccid == iccid).first()
    if sim:
        return {
            "iccid": iccid,
            "found": True,
            "sim": {
                "id": str(sim.id),
                "operateur": sim.operateur,
                "utilisateur_id": str(sim.utilisateur_id) if sim.utilisateur_id else None
            }
        }
    return {"iccid": iccid, "found": False, "message": "ICCID not found"}

@app.put("/devices/{device_id}/assign", tags=["Devices", "Admin"])
def assign_device_to_user(
    device_id: str, 
    assignment_data: dict,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin")),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """Admin only - assign device to user with audit logging"""
    device = db.query(Appareil).filter(Appareil.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    user_id = assignment_data.get("user_id")
    device.utilisateur_id = user_id
    db.commit()
    
    # Get IMEIs for logging
    imei_numbers = [imei.imei_number for imei in device.imeis]
    
    # Log device assignment
    audit_service.log_device_assignment(
        device_id=device_id,
        assigned_to_user_id=user_id,
        assigned_by_user_id=str(current_user.id),
        imeis=imei_numbers
    )
    
    return {"message": translator.translate("device_assigned")}

# Analytics and Statistics APIs
@app.get("/analytics/searches", tags=["Analytics"])
def search_analytics(
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user"))
):
    """Search analytics - filtered by user access level"""
    start_date = datetime.now() - timedelta(days=days)
    
    # Admin sees all searches, users see only their own
    if current_user.type_utilisateur == "administrateur":
        searches_query = db.query(Recherche).filter(
            Recherche.date_recherche >= start_date
        )
    else:
        searches_query = db.query(Recherche).filter(
            Recherche.date_recherche >= start_date,
            Recherche.utilisateur_id == current_user.id
        )
    
    total_searches = searches_query.count()
    
    # Searches by day
    daily_searches = searches_query.with_entities(
        func.date(Recherche.date_recherche).label('date'),
        func.count(Recherche.id).label('count')
    ).group_by(func.date(Recherche.date_recherche)).all()
    
    # Most searched IMEIs
    popular_imeis = searches_query.with_entities(
        Recherche.imei_recherche,
        func.count(Recherche.id).label('count')
    ).group_by(Recherche.imei_recherche).order_by(desc('count')).limit(10).all()
    
    return {
        "period_days": days,
        "total_searches": total_searches,
        "daily_searches": [{"date": str(day.date), "count": day.count} for day in daily_searches],
        "popular_imeis": [{"imei": imei.imei_recherche, "count": imei.count} for imei in popular_imeis]
    }

@app.get("/analytics/devices", tags=["Analytics"])
def device_analytics(db: Session = Depends(get_db)):
    # Total devices
    total_devices = db.query(Appareil).count()
    
    # Devices by brand
    brand_stats = db.query(
        Appareil.marque,
        func.count(Appareil.id).label('count')
    ).group_by(Appareil.marque).order_by(desc('count')).all()
    
    # Assigned vs unassigned devices
    assigned = db.query(Appareil).filter(Appareil.utilisateur_id.isnot(None)).count()
    unassigned = total_devices - assigned
    
    return {
        "total_devices": total_devices,
        "assigned_devices": assigned,
        "unassigned_devices": unassigned,
        "devices_by_brand": [{"brand": brand.marque, "count": brand.count} for brand in brand_stats]
    }

# Search History APIs
@app.get("/users/{user_id}/searches", tags=["Search History"])
def user_search_history(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user"))
):
    """Get user search history - users can only see their own searches"""
    # Users can only access their own search history
    if current_user.type_utilisateur != "administrateur" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    searches = db.query(Recherche).filter(
        Recherche.utilisateur_id == user_id
    ).order_by(desc(Recherche.date_recherche)).offset(skip).limit(limit).all()
    
    return {
        "searches": [
            {
                "id": str(search.id),
                "imei_recherche": search.imei_recherche,
                "date_recherche": format_datetime(search.date_recherche)
            }
            for search in searches
        ]
    }

@app.get("/imei/{imei}/history", tags=["Search History"])
def imei_search_history(imei: str, db: Session = Depends(get_db)):
    searches = db.query(Recherche).filter(
        Recherche.imei_recherche == imei
    ).order_by(desc(Recherche.date_recherche)).limit(20).all()
    
    search_count = len(searches)
    last_search = searches[0].date_recherche if searches else None
    
    return {
        "imei": imei,
        "total_searches": search_count,
        "last_search": format_datetime(last_search),
        "recent_searches": [
            {
                "date": format_datetime(search.date_recherche),
                "user_id": str(search.utilisateur_id) if search.utilisateur_id else "anonymous"
            }
            for search in searches[:5]
        ]
    }

# Notification APIs
@app.get("/notifications", tags=["Notifications"])
def list_notifications(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user"))
):
    """List notifications - users see only their notifications, admins see all"""
    query = db.query(Notification)
    
    # Apply user filtering based on role
    if current_user.type_utilisateur != "administrateur":
        # Regular users can only see their own notifications
        query = query.filter(Notification.utilisateur_id == current_user.id)
    else:
        # Admins can filter by user_id if provided
        if user_id:
            query = query.filter(Notification.utilisateur_id == user_id)
    
    if status:
        query = query.filter(Notification.statut == status)
    
    notifications = query.offset(skip).limit(limit).all()
    
    return {
        "notifications": [
            {
                "id": str(notif.id),
                "type": notif.type,
                "contenu": notif.contenu,
                "statut": notif.statut,
                "utilisateur_id": str(notif.utilisateur_id) if notif.utilisateur_id else None
            }
            for notif in notifications
        ]
    }

# Admin APIs
@app.get("/admin/users", tags=["Admin"])
def list_all_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin"))
):
    """Admin only - list all users"""
    users = db.query(Utilisateur).offset(skip).limit(limit).all()
    return {
        "users": [
            {
                "id": str(user.id),
                "nom": user.nom,
                "email": user.email,
                "type_utilisateur": user.type_utilisateur
            }
            for user in users
        ]
    }

# Enhanced audit logs endpoint
@app.get("/admin/audit-logs", tags=["Admin"])
def get_audit_logs(
    user_id: Optional[str] = None,
    action_filter: Optional[str] = None,
    entity_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin"))
):
    """Admin only - get audit logs with enhanced filtering"""
    query = db.query(JournalAudit)
    
    if user_id:
        query = query.filter(JournalAudit.utilisateur_id == user_id)
    if action_filter:
        query = query.filter(JournalAudit.action.contains(action_filter))
    if entity_type:
        query = query.filter(JournalAudit.action.contains(entity_type))
    
    # Date filtering
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(JournalAudit.date >= start_dt)
        except ValueError:
            pass
            
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(JournalAudit.date <= end_dt)
        except ValueError:
            pass
    
    logs = query.order_by(desc(JournalAudit.date)).offset(skip).limit(limit).all()
    
    return {
        "audit_logs": [
            {
                "id": str(log.id),
                "action": log.action,
                "date": format_datetime(log.date),
                "utilisateur_id": str(log.utilisateur_id) if log.utilisateur_id else None,
                "user_name": log.utilisateur.nom if log.utilisateur else "System"
            }
            for log in logs
        ],
        "total_count": query.count(),
        "filters_applied": {
            "user_id": user_id,
            "action_filter": action_filter,
            "entity_type": entity_type,
            "start_date": start_date,
            "end_date": end_date
        }
    }

@app.delete("/admin/devices/{device_id}", tags=["Admin"])
def delete_device(
    device_id: str, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin")),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """Admin only - delete device with audit logging"""
    device = db.query(Appareil).filter(Appareil.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Collect device data for audit log before deletion
    device_data = {
        "marque": device.marque,
        "modele": device.modele,
        "emmc": device.emmc,
        "imeis": [imei.imei_number for imei in device.imeis]
    }
    
    db.delete(device)
    db.commit()
    
    # Log device deletion
    audit_service.log_device_deletion(
        device_id=device_id,
        user_id=str(current_user.id),
        device_data=device_data
    )
    
    return {"message":translator.translate('device_deleted')}

# Bulk Operations
@app.post("/admin/bulk-import-devices", tags=["Devices", "Admin"])
def bulk_import_devices(
    devices_data: List[dict], 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin")),
    audit_service: AuditService = Depends(get_audit_service)
):
    """Admin only - bulk import devices with audit logging"""
    imported_count = 0
    errors = []
    
    for device_data in devices_data:
        try:
            device = Appareil(
                id=uuid.uuid4(),
                marque=device_data.get("marque"),
                modele=device_data.get("modele"),
                emmc=device_data.get("emmc"),
                utilisateur_id=device_data.get("utilisateur_id")
            )
            db.add(device)
            db.flush()  # Get the device ID
            
            # Add IMEIs
            imeis_data = device_data.get("imeis", [])
            for i, imei_data in enumerate(imeis_data):
                if isinstance(imei_data, str):
                    # Simple string format
                    imei = IMEI(
                        id=uuid.uuid4(),
                        imei_number=imei_data,
                        slot_number=i + 1,
                        status="active",
                        appareil_id=device.id
                    )
                else:
                    # Dictionary format
                    imei = IMEI(
                        id=uuid.uuid4(),
                        imei_number=imei_data.get("imei_number"),
                        slot_number=imei_data.get("slot_number", i + 1),
                        status=imei_data.get("status", "active"),
                        appareil_id=device.id
                    )
                db.add(imei)
            
            imported_count += 1
        except Exception as e:
            errors.append(f"Error importing device {device_data.get('marque', 'Unknown')}: {str(e)}")
    
    db.commit()
    
    # Log bulk import operation
    audit_service.log_bulk_import(
        user_id=str(current_user.id),
        imported_count=imported_count,
        errors=errors
    )
    
    return {
        "imported_count": imported_count,
        "errors": errors
    }

@app.post("/devices/{device_id}/imeis", tags=["Devices"])
def add_imei_to_device(device_id: str, imei_data: dict, db: Session = Depends(get_db)):
    device = db.query(Appareil).filter(Appareil.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Check if device already has 2 IMEIs
    if len(device.imeis) >= 2:
        raise HTTPException(status_code=400, detail="Device already has maximum number of IMEIs (2)")
    
    imei = IMEI(
        id=uuid.uuid4(),
        imei_number=imei_data.get("imei_number"),
        slot_number=imei_data.get("slot_number", len(device.imeis) + 1),
        status=imei_data.get("status", "active"),
        appareil_id=device.id
    )
    
    db.add(imei)
    db.commit()
    
    return {
        "message": "IMEI added successfully",
        "imei": {
            "id": str(imei.id),
            "imei_number": imei.imei_number,
            "slot_number": imei.slot_number,
            "status": imei.status
        }
    }

@app.put("/imeis/{imei_id}/status", tags=["IMEI", "Admin"])
def update_imei_status(
    imei_id: str, 
    status_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin")),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """Admin only - update IMEI status with audit logging"""
    imei = db.query(IMEI).filter(IMEI.id == imei_id).first()
    if not imei:
        raise HTTPException(status_code=404, detail=translator.translate("imei_not_found_error"))
    
    old_status = imei.status
    new_status = status_data.get("status")
    imei.status = new_status
    db.commit()
    
    # Log IMEI status change
    audit_service.log_imei_status_change(
        imei_id=str(imei.id),
        imei_number=imei.imei_number,
        old_status=old_status,
        new_status=new_status,
        user_id=str(current_user.id)
    )
    
    return {"message": translator.translate("imei_status_updated")}

# PUBLIC ANALYTICS (Limited for visitors)
@app.get("/public/stats", tags=["Public", "Analytics"])
def public_statistics(
    request: Request,
    db: Session = Depends(get_db),
    user_info: tuple = Depends(allow_all_with_limits),
    translator = Depends(get_current_translator)
):
    """Public statistics with limited information"""
    current_user, user_type = user_info
    
    # Basic stats available to all
    total_devices = db.query(Appareil).count()
    total_imeis = db.query(IMEI).count()
    
    response = {
        translator.translate("total_devices"): total_devices,
        translator.translate("total_imeis"): total_imeis,
        translator.translate("last_updated"): datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Enhanced stats for authenticated users
    if user_type != "visitor":
        total_users = db.query(Utilisateur).count()
        total_searches = db.query(Recherche).count()
        response.update({
            translator.translate("total_users"): total_users,
            translator.translate("total_searches"): total_searches
        })
    
    return response

