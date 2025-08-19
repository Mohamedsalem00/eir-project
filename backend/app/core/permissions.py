"""
Enhanced Permission Management System for EIR Project
Provides granular access control for concerned parties and data management
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status, Depends
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

    @classmethod
    def from_french(cls, french_level: str) -> 'AccessLevel':
        """Convert French access level names to English AccessLevel enum values"""
        french_to_english = {
            "visiteur": cls.VISITOR,
            "basique": cls.BASIC,
            "limite": cls.LIMITED,
            "standard": cls.STANDARD,
            "eleve": cls.ELEVATED,
            "admin": cls.ADMIN
        }
        return french_to_english.get(french_level.lower(), cls.BASIC)

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

class PorteeDonnees(Enum):
    """Data access portee_donnees definitions"""
    NONE = "aucun"             # No data access
    OWN = "personnel"          # Only user's own data  
    ORGANIZATION = "organisation"  # Organization-level data
    BRANDS = "marques"         # Specific marque data
    RANGES = "plages"          # Specific IMEI ranges
    ALL = "tout"               # All data (admin level)

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
    
    # Data portee_donnees permissions for access levels
    SCOPE_PERMISSIONS = {
        AccessLevel.VISITOR: PorteeDonnees.NONE,
        AccessLevel.BASIC: PorteeDonnees.OWN,
        AccessLevel.LIMITED: PorteeDonnees.BRANDS,  # Can be customized to RANGES
        AccessLevel.STANDARD: PorteeDonnees.OWN,
        AccessLevel.ELEVATED: PorteeDonnees.ORGANIZATION,
        AccessLevel.ADMIN: PorteeDonnees.ALL,
    }
    
    @staticmethod
    def has_permission(user: Optional[Utilisateur], operation: Operation) -> bool:
        """Check if user has permission for specific operation"""
        if not user:
            # Anonymous visitor permissions
            return operation in PermissionManager.ACCESS_PERMISSIONS[AccessLevel.VISITOR]
        
        # Get user's access level
        user_level = AccessLevel.from_french(user.niveau_acces or "basique")
        
        # Check if user is active
        if hasattr(user, 'est_actif') and not user.est_actif:
            return False
        
        # Check custom permissions first (if permissions attribute exists)
        if hasattr(user, 'permissions') and user.permissions:
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
            "raison": "",
            "portee_donnees": "aucune",
            "restrictions": []
        }
        
        if not user:
            context.update({
                "raison": "acces_public",
                "portee_donnees": "basic_info"
            })
            return True, context
        
        # Admin has full access
        if user.type_utilisateur == "administrateur":
            context.update({
                "raison": "admin_access",
                "portee_donnees": "complete"
            })
            return True, context
        
        # Check IMEI range restrictions for concerned parties
        allowed_ranges = user.plages_imei_autorisees or []
        if allowed_ranges:
            for range_rule in allowed_ranges:
                if PermissionManager._imei_matches_rule(imei, range_rule):
                    context.update({
                        "raison": "plage_imei_correspondance",
                        "portee_donnees": "plages_limitees",
                        "regle_correspondante": range_rule
                    })
                    return True, context
            
            # L’IMEI ne correspond à aucune plage autorisée
            context.update({
                "raison": "plage_imei_non_correspondante",
                "restrictions": allowed_ranges
            })
            return False, context
        
        # Check device marque restrictions
        if db and user.marques_autorisees:
            imei_record = db.query(IMEI).filter(IMEI.numero_imei == imei).first()
            if imei_record and imei_record.appareil:
                if imei_record.appareil.marque in user.marques_autorisees:
                    context.update({
                        "raison": "acces_marque",
                        "portee_donnees": "limite_marque",
                        "marque": imei_record.appareil.marque
                    })
                    return True, context
                else:
                    context.update({
                        "raison": "restriction_marque",
                        "marque_appareil": imei_record.appareil.marque,
                        "marques_autorisees": user.marques_autorisees
                    })
                    return False, context
        
        # Default access for standard users
        context.update({
            "raison": "standard_access",
            "portee_donnees": "standard"
        })
        return True, context
    
    @staticmethod
    def can_access_device(user: Optional[Utilisateur], device: Appareil) -> tuple[bool, dict]:
        """
        Check if user can access specific device with detailed reasoning
        Returns: (can_access: bool, context: dict)
        """
        context = {
            "raison": "",
            "portee_donnees": "aucune",
            "restrictions": []
        }
        
        if not user:
            context.update({
                "raison": "anonymous_denied",
                "portee_donnees": "aucune"
            })
            return False, context
        
        # Admin has full access
        if user.type_utilisateur == "administrateur":
            context.update({
                "raison": "acces_admin",
                "portee_donnees": "complete"
            })
            return True, context
        
        # Users can access their own devices
        if device.utilisateur_id == user.id:
            context.update({
                "raison": "acces_proprietaire",
                "portee_donnees": "complete"
            })
            return True, context
        
        # Check marque restrictions for concerned parties
        allowed_brands = user.marques_autorisees or []
        if allowed_brands:
            if device.marque in allowed_brands:
                context.update({
                    "raison": "acces_marque",
                    "portee_donnees": "limite_marque",
                    "marque": device.marque
                })
                return True, context
            else:
                context.update({
                    "raison": "restriction_marque",
                    "marque_appareil": device.marque,
                    "marques_autorisees": allowed_brands
                })
                return False, context
        
        # Check organization access
        if user.portee_donnees == "organisation" and getattr(user, 'organisation', None):
            # This would require organization field on devices - placeholder logic
            context.update({
                "raison": "organization_access",
                "portee_donnees": "organization"
            })
            return True, context
        
        # Default deny for non-matching cases
        context.update({
            "raison": "acces_refuse",
            "portee_donnees": "aucune"
        })
        return False, context
    
    @staticmethod
    def get_data_filter_context(user: Optional[Utilisateur]) -> dict:
        """Get data filtering context for database queries"""
        if not user:
            return {
                "portee_donnees": PorteeDonnees.NONE,
                "utilisateur_id": None,
                "marques_autorisees": [],
                "plages_imei_autorisees": [],
                "organisation": None,
                "est_admin": False
            }
        
        # Handle portee_donnees safely with French database values
        portee_donnees_value = user.portee_donnees or "personnel"
        try:
            portee_donnees = PorteeDonnees(portee_donnees_value)
        except ValueError:
            # Fallback to personnel if the value doesn't match any enum
            portee_donnees = PorteeDonnees.OWN
        
        return {
            "portee_donnees": portee_donnees,
            "utilisateur_id": user.id,
            "marques_autorisees": user.marques_autorisees or [],
            "plages_imei_autorisees": user.plages_imei_autorisees or [],
            "organisation": getattr(user, 'organisation', None),
            "est_admin": user.type_utilisateur == "administrateur",
            "niveau_acces": AccessLevel.from_french(user.niveau_acces or "basique")
        }
    
    @staticmethod
    def filter_response_data(user: Optional[Utilisateur], data: dict, data_type: str) -> dict:
        """Filtrer les données de réponse en fonction des permissions de l'utilisateur"""
        if not user:
            # Minimal data for anonymous users
            if data_type == "imei":
                return {
                    "imei": data.get("imei"),
                    "trouve": data.get("trouve"),
                    "statut": data.get("statut"),
                    "message": data.get("message")
                }
            elif data_type == "appareil":
                return {
                    "marque": data.get("marque"),
                    "modele": data.get("modele")
                }
        
        # Admin gets full data
        if user and user.type_utilisateur == "administrateur":
            return data
        
        # Filter based on access level
        user_level = AccessLevel.from_french(user.niveau_acces or "basique") if user else AccessLevel.VISITOR
        
        if data_type == "imei":
            base_data = {
                "imei": data.get("imei"),
                "trouve": data.get("trouve"),
                "statut": data.get("statut"),
                "message": data.get("message")
            }
            
            if user_level in [AccessLevel.LIMITED, AccessLevel.ELEVATED]:
                base_data.update({
                    "appareil": data.get("appareil", {}),
                    "recherche_loggee": data.get("recherche_loggee")
                })
            
            return base_data
        
        elif data_type == "appareil":
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
            return {"niveau_acces": "visitor", "permissions": [], "restrictions": []}
        
        user_level = AccessLevel.from_french(user.niveau_acces or "basique")
        default_permissions = PermissionManager.ACCESS_PERMISSIONS[user_level]
        
        return {
            "user_id": str(user.id),
            "niveau_acces": user_level.value,
            "portee_donnees": user.portee_donnees or "personnel",
            "organization": getattr(user, 'organisation', None),
            "est_actif": getattr(user, 'est_actif', True),
            "permissions": {
                "default": [op.value for op in default_permissions],
                "effective": [op.value for op in default_permissions]
            },
            "restrictions": {
                "marques_autorisees": user.marques_autorisees or [],
                "plages_imei_autorisees": user.plages_imei_autorisees or []
            }
        }

def require_permission(operation: Operation):
    """Dependency factory for operation-specific permission checking"""
    def permission_dependency(user=None):
        if not PermissionManager.has_permission(user, operation):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions for operation: {operation.value}"
            )
        return user
    
    return permission_dependency

def require_niveau_acces(min_level: AccessLevel):
    """Dependency factory for access level checking"""
    def level_dependency(user=None):
        if not user:
            current_level = AccessLevel.VISITOR
        else:
            current_level = AccessLevel.from_french(user.niveau_acces or "basique")
        
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
        
        return {
            "user": user,
            "access_level": current_level.value,
            "permissions": PermissionManager.get_user_permissions_summary(user) if user else {}
        }
    
    return level_dependency
