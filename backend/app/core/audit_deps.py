from fastapi import Depends
from sqlalchemy.orm import Session
from .dependencies import get_db
from ..services.audit import AuditService

def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Dependency to get audit service"""
    return AuditService(db)