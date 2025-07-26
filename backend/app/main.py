from fastapi import FastAPI, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from .core.dependencies import (
    get_db, get_current_user, get_admin_user, 
    allow_all_with_limits, require_auth
)
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

app = FastAPI(title="EIR Project API", version="1.0.0")

# Include authentication routes
app.include_router(auth_router)

# Helper function for date formatting
def format_datetime(dt):
    """Format datetime to readable string"""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# PUBLIC ENDPOINTS (All user types with rate limiting for visitors)
@app.get("/")
def read_root():
    return {"message": "EIR Project API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/imei/{imei}")
def check_imei(
    imei: str,
    request: Request,
    db: Session = Depends(get_db),
    user_info: tuple = Depends(allow_all_with_limits)
):
    """Public IMEI check with different access levels"""
    current_user, user_type = user_info
    
    # Search for IMEI
    imei_record = db.query(IMEI).filter(IMEI.imei_number == imei).first()
    
    if imei_record:
        appareil = imei_record.appareil
        
        # Base response for all users
        response = {
            "imei": imei,
            "found": True,
            "status": imei_record.status,
            "slot_number": imei_record.slot_number,
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
        "message": "IMEI not found in database"
    }

@app.post("/imei/{imei}/search")  
def log_imei_search(
    imei: str,
    request: Request,
    db: Session = Depends(get_db),
    user_info: tuple = Depends(allow_all_with_limits)
):
    """Log IMEI search with user tracking"""
    current_user, user_type = user_info
    
    # Log the search in Recherche table
    recherche = Recherche(
        id=uuid.uuid4(),
        date_recherche=datetime.now(),
        imei_recherche=imei,
        utilisateur_id=current_user.id if current_user else None
    )
    
    db.add(recherche)
    db.commit()
    
    # Then perform the search
    return check_imei(imei, request, db, user_info)

# AUTHENTICATED USER ENDPOINTS (user + admin)
@app.get("/devices")
def list_devices(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user"))
):
    """List devices - users see only their devices, admins see all"""
    if current_user.type_utilisateur == "administrateur":
        devices = db.query(Appareil).offset(skip).limit(limit).all()
    else:
        devices = db.query(Appareil).filter(
            Appareil.utilisateur_id == current_user.id
        ).offset(skip).limit(limit).all()
    
    return {
        "devices": [
            {
                "id": str(device.id),
                "marque": device.marque,
                "modele": device.modele,
                "emmc": device.emmc,
                "utilisateur_id": str(device.utilisateur_id) if device.utilisateur_id else None,
                "imeis": [
                    {
                        "imei_number": imei.imei_number,
                        "slot_number": imei.slot_number,
                        "status": imei.status
                    }
                    for imei in device.imeis
                ]
            }
            for device in devices
        ]
    }

@app.get("/searches")
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

# User Management APIs
@app.post("/users")
def create_user(
    user_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin"))
):
    """Admin only - create new user"""
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
    return {"id": str(user.id), "nom": user.nom, "email": user.email}

@app.get("/users")
def list_users(
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

@app.get("/users/{user_id}")
def get_user(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user"))
):
    """Get user details - users can only see their own data, admins see all"""
    # Users can only access their own data
    if current_user.type_utilisateur != "administrateur" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
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
@app.post("/sims")
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

@app.get("/sims")
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

@app.get("/sims/{iccid}")
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

# Device Management APIs
@app.post("/devices")
def register_device(
    device_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("user"))
):
    """Register device - authenticated users only"""
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
    for i, imei_data in enumerate(imeis_data):
        imei = IMEI(
            id=uuid.uuid4(),
            imei_number=imei_data.get("imei_number"),
            slot_number=imei_data.get("slot_number", i + 1),
            status=imei_data.get("status", "active"),
            appareil_id=device.id
        )
        db.add(imei)
    
    db.commit()
    db.refresh(device)
    
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

@app.put("/devices/{device_id}/assign")
def assign_device_to_user(
    device_id: str, 
    assignment_data: dict,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin"))
):
    """Admin only - assign device to user"""
    device = db.query(Appareil).filter(Appareil.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    user_id = assignment_data.get("user_id")
    device.utilisateur_id = user_id
    db.commit()
    
    # Get IMEIs for logging
    imei_numbers = [imei.imei_number for imei in device.imeis]
    imei_list = ", ".join(imei_numbers)
    
    # Log the action
    audit = JournalAudit(
        id=uuid.uuid4(),
        action=f"Device with IMEIs [{imei_list}] assigned to user {user_id}",
        date=datetime.now(),
        utilisateur_id=current_user.id
    )
    db.add(audit)
    db.commit()
    
    return {"message": "Device assigned successfully"}

# Analytics and Statistics APIs
@app.get("/analytics/searches")
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

@app.get("/analytics/devices")
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
@app.get("/users/{user_id}/searches")
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

@app.get("/imei/{imei}/history")
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
@app.get("/notifications")
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
@app.get("/admin/users")
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

@app.get("/admin/audit-logs")
def get_audit_logs(
    user_id: Optional[str] = None,
    action_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin"))
):
    """Admin only - get audit logs"""
    query = db.query(JournalAudit)
    
    if user_id:
        query = query.filter(JournalAudit.utilisateur_id == user_id)
    if action_filter:
        query = query.filter(JournalAudit.action.contains(action_filter))
    
    logs = query.order_by(desc(JournalAudit.date)).offset(skip).limit(limit).all()
    
    return {
        "audit_logs": [
            {
                "id": str(log.id),
                "action": log.action,
                "date": format_datetime(log.date),
                "utilisateur_id": str(log.utilisateur_id) if log.utilisateur_id else None
            }
            for log in logs
        ]
    }

@app.delete("/admin/devices/{device_id}")
def delete_device(
    device_id: str, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin"))
):
    """Admin only - delete device"""
    device = db.query(Appareil).filter(Appareil.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(device)
    db.commit()
    return {"message": "Device deleted successfully"}

# Bulk Operations
@app.post("/admin/bulk-import-devices")
def bulk_import_devices(
    devices_data: List[dict], 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin"))
):
    """Admin only - bulk import devices"""
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
    return {
        "imported_count": imported_count,
        "errors": errors
    }

@app.post("/devices/{device_id}/imeis")
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

@app.put("/imeis/{imei_id}/status")
def update_imei_status(
    imei_id: str, 
    status_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_auth("admin"))
):
    """Admin only - update IMEI status"""
    imei = db.query(IMEI).filter(IMEI.id == imei_id).first()
    if not imei:
        raise HTTPException(status_code=404, detail="IMEI not found")
    
    old_status = imei.status
    imei.status = status_data.get("status")
    db.commit()
    
    # Log the status change
    audit = JournalAudit(
        id=uuid.uuid4(),
        action=f"IMEI {imei.imei_number} status changed from {old_status} to {imei.status}",
        date=datetime.now(),
        utilisateur_id=status_data.get("user_id")
    )
    db.add(audit)
    db.commit()
    
    return {"message": "IMEI status updated successfully"}

# ANALYTICS - Different access levels
@app.get("/analytics/searches")
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

@app.get("/analytics/devices")
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

# PUBLIC ANALYTICS (Limited for visitors)
@app.get("/public/stats")
def public_statistics(
    request: Request,
    db: Session = Depends(get_db),
    user_info: tuple = Depends(allow_all_with_limits)
):
    """Public statistics with limited information"""
    current_user, user_type = user_info
    
    # Basic stats available to all
    total_devices = db.query(Appareil).count()
    total_imeis = db.query(IMEI).count()
    
    response = {
        "total_devices": total_devices,
        "total_imeis": total_imeis,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Enhanced stats for authenticated users
    if user_type != "visitor":
        total_users = db.query(Utilisateur).count()
        total_searches = db.query(Recherche).count()
        response.update({
            "total_users": total_users,
            "total_searches": total_searches
        })
    
    return response

