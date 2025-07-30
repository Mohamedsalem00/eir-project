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
            details={"search_result": "found" if found else "not_found"}
        )
    
    def log_device_creation(self, device_id: str, user_id: str, device_data: Dict[str, Any]):
        """Log device creation"""
        return self.log_action(
            action="Device created",
            user_id=user_id,
            entity_type="device",
            entity_id=device_id,
            new_values=device_data
        )
    
    def log_device_update(self, device_id: str, user_id: str, old_data: Dict[str, Any], new_data: Dict[str, Any]):
        """Log device update"""
        return self.log_action(
            action="Device updated",
            user_id=user_id,
            entity_type="device",
            entity_id=device_id,
            old_values=old_data,
            new_values=new_data
        )
    
    def log_device_deletion(self, device_id: str, user_id: str, device_data: Dict[str, Any]):
        """Log device deletion"""
        return self.log_action(
            action="Device deleted",
            user_id=user_id,
            entity_type="device",
            entity_id=device_id,
            old_values=device_data
        )
    
    def log_device_assignment(self, device_id: str, assigned_to_user_id: str, assigned_by_user_id: str, imeis: list):
        """Log device assignment"""
        return self.log_action(
            action=f"Device assigned to user {assigned_to_user_id}",
            user_id=assigned_by_user_id,
            entity_type="device",
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
    
    def log_imei_status_change(self, imei_id: str, imei_number: str, old_status: str, new_status: str, user_id: str):
        """Log IMEI status change"""
        return self.log_action(
            action=f"IMEI status changed",
            user_id=user_id,
            entity_type="imei",
            entity_id=imei_id,
            old_values={"status": old_status, "imei_number": imei_number},
            new_values={"status": new_status, "imei_number": imei_number}
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