"""
Enhanced Permission Management System for EIR Project
Provides granular access control for concerned parties and data management
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..models.utilisateur import Utilisateur
from ..models.appareil import Appareil
from ..models.imei import IMEI
import re

class AccessLevel(Enum):
    """Hierarchical access levels for users"""
    VISITOR = "visitor"          # Anonymous users - public access only
    BASIC = "basic"             # Basic authenticated users - limited read access
    LIMITED = "limited"         # Concerned parties - specific data access
    STANDARD = "standard"       # Regular users - full personal data access
    ELEVATED = "elevated"       # Enhanced users - organizational data access
    ADMIN = "admin"            # Administrators - full system access

class Operation(Enum):
    """Available operations in the system"""
    # IMEI Operations
    READ_IMEI = "read_imei"
    SEARCH_IMEI = "search_imei"
    UPDATE_IMEI_STATUS = "update_imei_status"
    
    # Device Operations
    READ_DEVICE = "read_device"
    CREATE_DEVICE = "create_device"
    UPDATE_DEVICE = "update_device"
    DELETE_DEVICE = "delete_device"
    ASSIGN_DEVICE = "assign_device"
    
    # SIM Operations
    READ_SIM = "read_sim"
    CREATE_SIM = "create_sim"
    UPDATE_SIM = "update_sim"
    DELETE_SIM = "delete_sim"
    
    # User Operations
    READ_USER = "read_user"
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Analytics and Reporting
    READ_ANALYTICS = "read_analytics"
    READ_SEARCH_HISTORY = "read_search_history"
    READ_AUDIT = "read_audit"
    
    # Administrative Operations
    BULK_OPERATIONS = "bulk_operations"
    MANAGE_PERMISSIONS = "manage_permissions"
    SYSTEM_CONFIG = "system_config"

class DataScope(Enum):
    """Data access scope definitions"""
    NONE = "none"              # No data access
    OWN = "own"               # Only user's own data
    ORGANIZATION = "organization"  # Organization-level data
    BRANDS = "brands"         # Specific brand data
    RANGES = "ranges"         # Specific IMEI ranges
    ALL = "all"              # All data (admin level)

class PermissionManager:
    """Advanced permission management with granular access control"""
    
    # Default permissions matrix for access levels
    ACCESS_PERMISSIONS = {
        AccessLevel.VISITOR: [
            Operation.READ_IMEI,
        ],
        AccessLevel.BASIC: [
            Operation.READ_IMEI,
            Operation.SEARCH_IMEI,
        ],
        AccessLevel.LIMITED: [
            Operation.READ_IMEI,
            Operation.SEARCH_IMEI,
            Operation.READ_DEVICE,
            Operation.READ_ANALYTICS,  # Limited analytics for concerned parties
        ],
        AccessLevel.STANDARD: [
            Operation.READ_IMEI,
            Operation.SEARCH_IMEI,
            Operation.READ_DEVICE,
            Operation.CREATE_DEVICE,
            Operation.UPDATE_DEVICE,
            Operation.READ_SIM,
            Operation.CREATE_SIM,
            Operation.UPDATE_SIM,
            Operation.READ_USER,
            Operation.READ_SEARCH_HISTORY,
        ],
        AccessLevel.ELEVATED: [
            Operation.READ_IMEI,
            Operation.SEARCH_IMEI,
            Operation.UPDATE_IMEI_STATUS,
            Operation.READ_DEVICE,
            Operation.CREATE_DEVICE,
            Operation.UPDATE_DEVICE,
            Operation.DELETE_DEVICE,
            Operation.READ_SIM,
            Operation.CREATE_SIM,
            Operation.UPDATE_SIM,
            Operation.DELETE_SIM,
            Operation.READ_USER,
            Operation.READ_ANALYTICS,
            Operation.READ_SEARCH_HISTORY,
            Operation.READ_AUDIT,
        ],
        AccessLevel.ADMIN: list(Operation),  # All operations
    }
    
    # Data scope permissions for access levels
    SCOPE_PERMISSIONS = {
        AccessLevel.VISITOR: DataScope.NONE,
        AccessLevel.BASIC: DataScope.OWN,
        AccessLevel.LIMITED: DataScope.BRANDS,  # Can be customized to RANGES
        AccessLevel.STANDARD: DataScope.OWN,
        AccessLevel.ELEVATED: DataScope.ORGANIZATION,
        AccessLevel.ADMIN: DataScope.ALL,
    }
    
    @staticmethod
    def has_permission(user: Optional[Utilisateur], operation: Operation) -> bool:
        """Check if user has permission for specific operation"""
        if not user:
            # Anonymous visitor permissions
            return operation in PermissionManager.ACCESS_PERMISSIONS[AccessLevel.VISITOR]
        
        # Get user's access level
        user_level = AccessLevel(user.access_level or "basic")
        
        # Check if user is active
        if hasattr(user, 'is_active') and not user.is_active:
            return False
        
        # Check custom permissions first
        custom_operations = user.permissions.get("operations", [])
        if custom_operations:
            return operation.value in custom_operations
        
        # Check default permissions for access level
        default_permissions = PermissionManager.ACCESS_PERMISSIONS[user_level]
        return operation in default_permissions
    
    @staticmethod
    def can_access_imei(user: Optional[Utilisateur], imei: str, db: Session = None) -> tuple[bool, dict]:
        """
        Check if user can access specific IMEI with detailed reasoning
        Returns: (can_access: bool, context: dict)
        """
        context = {
            "reason": "",
            "scope": "none",
            "restrictions": []
        }
        
        if not user:
            context.update({
                "reason": "public_access",
                "scope": "basic_info"
            })
            return True, context
        
        # Admin has full access
        if user.type_utilisateur == "administrateur":
            context.update({
                "reason": "admin_access",
                "scope": "full"
            })
            return True, context
        
        # Check IMEI range restrictions for concerned parties
        allowed_ranges = user.allowed_imei_ranges or []
        if allowed_ranges:
            for range_rule in allowed_ranges:
                if PermissionManager._imei_matches_rule(imei, range_rule):
                    context.update({
                        "reason": "imei_range_match",
                        "scope": "range_limited",
                        "matched_rule": range_rule
                    })
                    return True, context
            
            # IMEI doesn't match any allowed range
            context.update({
                "reason": "imei_range_mismatch",
                "restrictions": allowed_ranges
            })
            return False, context
        
        # Check device brand restrictions
        if db and user.allowed_brands:
            imei_record = db.query(IMEI).filter(IMEI.imei_number == imei).first()
            if imei_record and imei_record.appareil:
                if imei_record.appareil.marque in user.allowed_brands:
                    context.update({
                        "reason": "brand_access",
                        "scope": "brand_limited",
                        "brand": imei_record.appareil.marque
                    })
                    return True, context
                else:
                    context.update({
                        "reason": "brand_restriction",
                        "device_brand": imei_record.appareil.marque,
                        "allowed_brands": user.allowed_brands
                    })
                    return False, context
        
        # Default access for standard users
        context.update({
            "reason": "standard_access",
            "scope": "standard"
        })
        return True, context
    
    @staticmethod
    def can_access_device(user: Optional[Utilisateur], device: Appareil) -> tuple[bool, dict]:
        """
        Check if user can access specific device with detailed reasoning
        Returns: (can_access: bool, context: dict)
        """
        context = {
            "reason": "",
            "scope": "none",
            "restrictions": []
        }
        
        if not user:
            context.update({
                "reason": "anonymous_denied",
                "scope": "none"
            })
            return False, context
        
        # Admin has full access
        if user.type_utilisateur == "administrateur":
            context.update({
                "reason": "admin_access",
                "scope": "full"
            })
            return True, context
        
        # Users can access their own devices
        if device.utilisateur_id == user.id:
            context.update({
                "reason": "owner_access",
                "scope": "full"
            })
            return True, context
        
        # Check brand restrictions for concerned parties
        allowed_brands = user.allowed_brands or []
        if allowed_brands:
            if device.marque in allowed_brands:
                context.update({
                    "reason": "brand_access",
                    "scope": "brand_limited",
                    "brand": device.marque
                })
                return True, context
            else:
                context.update({
                    "reason": "brand_restriction",
                    "device_brand": device.marque,
                    "allowed_brands": allowed_brands
                })
                return False, context
        
        # Check organization access
        if user.data_scope == "organization" and user.organization:
            # This would require organization field on devices - placeholder logic
            context.update({
                "reason": "organization_access",
                "scope": "organization"
            })
            return True, context
        
        # Default deny for non-matching cases
        context.update({
            "reason": "access_denied",
            "scope": "none"
        })
        return False, context
    
    @staticmethod
    def get_data_filter_context(user: Optional[Utilisateur]) -> dict:
        """Get data filtering context for database queries"""
        if not user:
            return {
                "scope": DataScope.NONE,
                "user_id": None,
                "allowed_brands": [],
                "allowed_ranges": [],
                "organization": None,
                "is_admin": False
            }
        
        return {
            "scope": DataScope(user.data_scope or "own"),
            "user_id": user.id,
            "allowed_brands": user.allowed_brands or [],
            "allowed_ranges": user.allowed_imei_ranges or [],
            "organization": user.organization,
            "is_admin": user.type_utilisateur == "administrateur",
            "access_level": AccessLevel(user.access_level or "basic")
        }
    
    @staticmethod
    def filter_response_data(user: Optional[Utilisateur], data: dict, data_type: str) -> dict:
        """Filter response data based on user permissions"""
        if not user:
            # Minimal data for anonymous users
            if data_type == "imei":
                return {
                    "imei": data.get("imei"),
                    "found": data.get("found"),
                    "status": data.get("status"),
                    "message": data.get("message")
                }
            elif data_type == "device":
                return {
                    "marque": data.get("marque"),
                    "modele": data.get("modele")
                }
        
        # Admin gets full data
        if user and user.type_utilisateur == "administrateur":
            return data
        
        # Filter based on access level
        user_level = AccessLevel(user.access_level or "basic") if user else AccessLevel.VISITOR
        
        if data_type == "imei":
            base_data = {
                "imei": data.get("imei"),
                "found": data.get("found"),
                "status": data.get("status"),
                "message": data.get("message")
            }
            
            if user_level in [AccessLevel.LIMITED, AccessLevel.ELEVATED]:
                base_data.update({
                    "device": data.get("device", {}),
                    "search_logged": data.get("search_logged")
                })
            
            return base_data
        
        elif data_type == "device":
            if user_level == AccessLevel.LIMITED:
                return {
                    "id": data.get("id"),
                    "marque": data.get("marque"),
                    "modele": data.get("modele"),
                    "imeis": data.get("imeis", [])
                }
        
        return data
    
    @staticmethod
    def _imei_matches_rule(imei: str, rule: dict) -> bool:
        """Check if IMEI matches a specific access rule"""
        rule_type = rule.get("type", "prefix")
        
        if rule_type == "prefix":
            prefix = rule.get("prefix", "")
            return imei.startswith(prefix)
        
        elif rule_type == "range":
            start = rule.get("start", "")
            end = rule.get("end", "")
            return start <= imei <= end
        
        elif rule_type == "regex":
            pattern = rule.get("pattern", "")
            return bool(re.match(pattern, imei))
        
        elif rule_type == "exact":
            exact_imeis = rule.get("imeis", [])
            return imei in exact_imeis
        
        return False
    
    @staticmethod
    def get_user_permissions_summary(user: Utilisateur) -> dict:
        """Get comprehensive summary of user permissions"""
        if not user:
            return {"access_level": "visitor", "permissions": [], "restrictions": []}
        
        user_level = AccessLevel(user.access_level or "basic")
        default_permissions = PermissionManager.ACCESS_PERMISSIONS[user_level]
        
        return {
            "user_id": str(user.id),
            "access_level": user_level.value,
            "data_scope": user.data_scope or "own",
            "organization": user.organization,
            "is_active": getattr(user, 'is_active', True),
            "permissions": {
                "default": [op.value for op in default_permissions],
                "effective": [op.value for op in default_permissions]
            },
            "restrictions": {
                "allowed_brands": user.allowed_brands or [],
                "allowed_imei_ranges": user.allowed_imei_ranges or []
            }
        }

def require_permission(operation: Operation):
    """Dependency factory for operation-specific permission checking"""
    def permission_dependency(user: Optional[Utilisateur] = None):
        if not PermissionManager.has_permission(user, operation):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for operation: {operation.value}"
            )
        return user
    
    return permission_dependency

def require_access_level(min_level: AccessLevel):
    """Dependency factory for access level checking"""
    def level_dependency(user: Optional[Utilisateur] = None):
        if not user:
            current_level = AccessLevel.VISITOR
        else:
            current_level = AccessLevel(user.access_level or "basic")
        
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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Minimum access level required: {min_level.value}"
            )
        
        return user
    
    return level_dependency
