from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..models.journal_audit import JournalAudit
from ..models.utilisateur import Utilisateur
import uuid
import json

class AuditService:
    """Service for handling audit logging"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(
        self,
        action: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> JournalAudit:
        """
        Log an audit action
        
        Args:
            action: Description of the action performed
            user_id: ID of the user performing the action
            details: Additional details about the action
            entity_type: Type of entity being acted upon (e.g., 'device', 'user', 'imei')
            entity_id: ID of the entity being acted upon
            old_values: Previous values (for updates)
            new_values: New values (for updates)
        
        Returns:
            JournalAudit: The created audit log entry
        """
        
        # Build comprehensive action description
        action_details = {
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_id": entity_id
        }
        
        if details:
            action_details["details"] = details
            
        if old_values:
            action_details["old_values"] = old_values
            
        if new_values:
            action_details["new_values"] = new_values
        
        # Create formatted action string
        formatted_action = self._format_action_string(action_details)
        
        # Create audit log entry
        audit_log = JournalAudit(
            id=uuid.uuid4(),
            action=formatted_action,
            date=datetime.now(),
            utilisateur_id=user_id
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return audit_log
    
    def _format_action_string(self, action_details: Dict[str, Any]) -> str:
        """Format action details into a readable string"""
        base_action = action_details["action"]
        
        if action_details.get("entity_type") and action_details.get("entity_id"):
            base_action += f" on {action_details['entity_type']} {action_details['entity_id']}"
        
        # Add change details for updates
        if action_details.get("old_values") and action_details.get("new_values"):
            changes = []
            old_vals = action_details["old_values"]
            new_vals = action_details["new_values"]
            
            for key in new_vals:
                if key in old_vals and old_vals[key] != new_vals[key]:
                    changes.append(f"{key}: '{old_vals[key]}' → '{new_vals[key]}'")
            
            if changes:
                base_action += f" - Changes: {', '.join(changes)}"
        
        # Add additional details
        if action_details.get("details"):
            details_str = json.dumps(action_details["details"], default=str)
            base_action += f" - Details: {details_str}"
        
        return base_action
    
    def log_login(self, user_id: str, success: bool, ip_address: Optional[str] = None):
        """Log user login attempt"""
        action = "User login successful" if success else "User login failed"
        details = {"ip_address": ip_address} if ip_address else None
        
        return self.log_action(
            action=action,
            user_id=user_id if success else None,
            details=details,
            entity_type="user",
            entity_id=user_id
        )
    
    def log_logout(self, user_id: str):
        """Log user logout"""
        return self.log_action(
            action="User logout",
            user_id=user_id,
            entity_type="user",
            entity_id=user_id
        )
    
    def log_imei_search(self, imei: str, user_id: Optional[str] = None, found: bool = False):
        """Log IMEI search"""
        action = f"IMEI search: {imei} - {'Found' if found else 'Not found'}"
        
        return self.log_action(
            action=action,
            user_id=user_id,
            entity_type="imei",
            entity_id=imei,
            details={"search_result": "trouve" if found else "non_trouve"}
        )
    
    def log_device_creation(self, device_id: str, user_id: str, device_data: Dict[str, Any]):
        """Log device creation"""
        return self.log_action(
            action="Device created",
            user_id=user_id,
            entity_type="appareil",
            entity_id=device_id,
            new_values=device_data
        )
    
    def log_device_update(self, device_id: str, user_id: str, old_data: Dict[str, Any], new_data: Dict[str, Any]):
        """Log device update"""
        return self.log_action(
            action="Device updated",
            user_id=user_id,
            entity_type="appareil",
            entity_id=device_id,
            old_values=old_data,
            new_values=new_data
        )
    
    def log_device_deletion(self, device_id: str, user_id: str, device_data: Dict[str, Any]):
        """Log device deletion"""
        return self.log_action(
            action="Device deleted",
            user_id=user_id,
            entity_type="appareil",
            entity_id=device_id,
            old_values=device_data
        )
    
    def log_device_assignment(self, device_id: str, assigned_to_user_id: str, assigned_by_user_id: str, imeis: list):
        """Log device assignment"""
        return self.log_action(
            action=f"Device assigned to user {assigned_to_user_id}",
            user_id=assigned_by_user_id,
            entity_type="appareil",
            entity_id=device_id,
            details={
                "assigned_to": assigned_to_user_id,
                "imeis": imeis
            }
        )
    
    def log_user_creation(self, new_user_id: str, created_by_user_id: str, user_data: Dict[str, Any]):
        """Log user creation"""
        # Remove sensitive data
        safe_user_data = {k: v for k, v in user_data.items() if k != "mot_de_passe"}
        
        return self.log_action(
            action="User created",
            user_id=created_by_user_id,
            entity_type="user",
            entity_id=new_user_id,
            new_values=safe_user_data
        )
    
    def log_imei_status_change(self, imei_id: str, numero_imei: str, old_status: str, new_status: str, user_id: str):
        """Log IMEI status change"""
        return self.log_action(
            action=f"IMEI status changed",
            user_id=user_id,
            entity_type="imei",
            entity_id=imei_id,
            old_values={"statut": old_status, "numero_imei": numero_imei},
            new_values={"statut": new_status, "numero_imei": numero_imei}
        )
    
    def log_bulk_import(self, user_id: str, imported_count: int, errors: list):
        """Log bulk import operation"""
        return self.log_action(
            action=f"Bulk import completed - {imported_count} devices imported",
            user_id=user_id,
            entity_type="bulk_operation",
            details={
                "imported_count": imported_count,
                "error_count": len(errors),
                "errors": errors[:5]  # Limit errors to first 5
            }
        )
    
    # Enhanced Permission Management Audit Methods
    
    def log_permission_change(self, target_user_id: str, admin_user_id: str, changes: Dict[str, Any]):
        """Log user permission changes"""
        return self.log_action(
            action=f"User permissions modified for user {target_user_id}",
            user_id=admin_user_id,
            entity_type="user_permissions",
            entity_id=target_user_id,
            details={
                "changes": changes,
                "change_count": len(changes)
            }
        )
    
    def log_access_rule_change(self, target_user_id: str, admin_user_id: str, action: str, rule_data: Dict[str, Any]):
        """Log access rule additions/removals"""
        return self.log_action(
            action=f"Access rule {action} for user {target_user_id}",
            user_id=admin_user_id,
            entity_type="access_rule",
            entity_id=target_user_id,
            details={
                "rule_action": action,
                "rule_data": rule_data
            }
        )
    
    def log_bulk_permission_update(self, admin_user_id: str, user_ids: list, changes: Dict[str, Any], errors: list):
        """Log bulk permission updates"""
        return self.log_action(
            action=f"Bulk permission update - {len(user_ids)} users affected",
            user_id=admin_user_id,
            entity_type="bulk_permissions",
            details={
                "affected_users": user_ids,
                "changes": changes,
                "success_count": len(user_ids),
                "error_count": len(errors),
                "errors": errors[:5]  # Limit errors to first 5
            }
        )
    
    def log_template_application(self, target_user_id: str, admin_user_id: str, template_name: str, additional_config: Dict[str, Any]):
        """Log permission template application"""
        return self.log_action(
            action=f"Permission template '{template_name}' applied to user {target_user_id}",
            user_id=admin_user_id,
            entity_type="permission_template",
            entity_id=target_user_id,
            details={
                "template_name": template_name,
                "additional_config": additional_config
            }
        )
    
    def log_access_attempt(self, user_id: Optional[str], operation: str, entity_type: str, entity_id: str, 
                          success: bool, raison: str, ip_address: Optional[str] = None):
        """Log access attempts for security monitoring"""
        action = f"Access {'granted' if success else 'denied'}: {operation} on {entity_type} {entity_id}"
        
        return self.log_action(
            action=action,
            user_id=user_id,
            entity_type="access_control",
            entity_id=f"{entity_type}:{entity_id}",
            details={
                "operation": operation,
                "success": success,
                "raison": raison,
                "ip_address": ip_address
            }
        )
    
    def log_data_access(self, user_id: Optional[str], data_type: str, access_scope: str, 
                       filter_applied: bool, record_count: int):
        """Log data access patterns for analytics"""
        return self.log_action(
            action=f"Data access: {data_type} with portee_donnees {access_scope}",
            user_id=user_id,
            entity_type="data_access",
            details={
                "data_type": data_type,
                "access_scope": access_scope,
                "filter_applied": filter_applied,
                "record_count": record_count
            }
        )
    
    def log_security_event(self, event_type: str, severity: str, user_id: Optional[str] = None, 
                          details: Optional[Dict[str, Any]] = None):
        """Log security-related events"""
        return self.log_action(
            action=f"Security event: {event_type} (severity: {severity})",
            user_id=user_id,
            entity_type="security_event",
            details={
                "event_type": event_type,
                "severity": severity,
                **(details or {})
            }
        )
    
    def log_device_sync(self, user_id: Optional[str], sync_id: str, source_system: str, 
                       stats: Dict[str, Any], processing_time_ms: float):
        """Log device synchronization from external DMS systems"""
        return self.log_action(
            action=f"Synchronisation d'appareils depuis {source_system}",
            user_id=user_id,
            entity_type="device_sync",
            entity_id=sync_id,
            details={
                "source_system": source_system,
                "sync_id": sync_id,
                "appareils_traités": stats.get("traités", 0),
                "appareils_créés": stats.get("créés", 0),
                "appareils_mis_à_jour": stats.get("mis_à_jour", 0),
                "appareils_ignorés": stats.get("ignorés", 0),
                "erreurs": stats.get("erreurs", 0),
                "processing_time_ms": processing_time_ms,
                "success_rate": round((stats.get("traités", 0) - stats.get("erreurs", 0)) / max(stats.get("traités", 1), 1) * 100, 2)
            }
        )

    def log_tac_sync(self, user_id: str, source: str, result: Dict[str, Any]):
        """Log TAC database synchronization operations"""
        return self.log_action(
            action=f"Synchronisation TAC depuis {source}",
            user_id=user_id,
            entity_type="tac_sync",
            entity_id=result.get("sync_id", "unknown"),
            details={
                "source": source,
                "sync_id": result.get("sync_id"),
                "records_imported": result.get("imported", 0),
                "records_updated": result.get("updated", 0),
                "records_errors": result.get("errors", 0),
                "format": result.get("format"),
                "status": "partial" if result.get("note") else "completed",
                "error_message": result.get("error_message"),
                "note": result.get("note")
            }
        )

    def log_tac_import(self, user_id: str, filename: str, format_source: str, result: Dict[str, Any]):
        """Log TAC database import operations from uploaded files"""
        return self.log_action(
            action=f"Import TAC depuis fichier {filename} (format: {format_source})",
            user_id=user_id,
            entity_type="tac_import",
            entity_id=result.get("import_id", f"file_{filename}"),
            details={
                "filename": filename,
                "format_source": format_source,
                "import_id": result.get("import_id"),
                "records_imported": result.get("imported", 0),
                "records_updated": result.get("updated", 0),
                "records_errors": result.get("errors", 0),
                "file_size": result.get("file_size"),
                "processing_time_ms": result.get("processing_time_ms"),
                "status": result.get("status", "completed"),
                "error_message": result.get("error_message"),
                "validation_errors": result.get("validation_errors", [])
            }
        )