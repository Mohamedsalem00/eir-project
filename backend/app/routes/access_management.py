"""
API Administratif pour la gestion des niveaux d'accès et permissions utilisateur
Fournit des points de terminaison pour que les administrateurs configurent le contrôle d'accès granulaire
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..core.dependencies import get_db, require_niveau_acces, get_access_context
from ..core.permissions import AccessLevel, Operation, PermissionManager, PorteeDonnees
from ..models.utilisateur import Utilisateur
from ..services.audit import AuditService
from ..core.audit_deps import get_audit_service
from pydantic import BaseModel, Field
import uuid

router = APIRouter(prefix="/admin/gestion-acces", tags=["Gestion d'Accès"])

# Modèles Pydantic pour les requêtes/réponses
class MiseAJourPermission(BaseModel):
    niveau_acces: Optional[str] = Field(None, description="Nouveau niveau d'accès pour l'utilisateur")
    portee_donnees: Optional[str] = Field(None, description="Portée d'accès aux données")
    organisation: Optional[str] = Field(None, description="Assignation d'organisation")
    marques_autorisees: Optional[List[str]] = Field(None, description="Marques d'appareils autorisées")
    plages_imei_autorisees: Optional[List[Dict[str, Any]]] = Field(None, description="Plages IMEI autorisées")
    operations_personnalisees: Optional[List[str]] = Field(None, description="Permissions d'opérations personnalisées")
    est_actif: Optional[bool] = Field(None, description="Statut du compte")

class InfoNiveauAcces(BaseModel):
    niveau: str
    description: str
    permissions_par_defaut: List[str]
    portee_donnees: str

class ResumePermissionUtilisateur(BaseModel):
    id_utilisateur: str
    nom: str
    email: str
    niveau_acces: str
    portee_donnees: str
    organisation: Optional[str]
    est_actif: bool
    nombre_permissions: int
    nombre_restrictions: int

@router.get("/niveaux-acces", response_model=List[InfoNiveauAcces])
def obtenir_niveaux_acces(
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN))
):
    """Obtenir tous les niveaux d'accès disponibles et leurs permissions par défaut"""
    niveaux = []
    
    for niveau in AccessLevel:
        permissions = PermissionManager.ACCESS_PERMISSIONS.get(niveau, [])
        portee = PermissionManager.SCOPE_PERMISSIONS.get(niveau, PorteeDonnees.NONE)
        
        # Créer une description basée sur le niveau
        descriptions = {
            AccessLevel.VISITOR: "Utilisateurs anonymes avec accès public de base",
            AccessLevel.BASIC: "Utilisateurs authentifiés avec accès de lecture limité",
            AccessLevel.LIMITED: "Parties concernées avec accès spécifique aux données",
            AccessLevel.STANDARD: "Utilisateurs réguliers avec accès complet aux données personnelles",
            AccessLevel.ELEVATED: "Utilisateurs améliorés avec accès aux données organisationnelles",
            AccessLevel.ADMIN: "Administrateurs avec accès complet au système"
        }
        
        niveaux.append(InfoNiveauAcces(
            niveau=niveau.value,
            description=descriptions[niveau],
            permissions_par_defaut=[op.value for op in permissions],
            portee_donnees=portee.value
        ))
    
    return niveaux

@router.get("/utilisateurs", response_model=List[ResumePermissionUtilisateur])
def lister_utilisateurs_avec_permissions(
    ignorer: int = Query(0, ge=0),
    limite: int = Query(100, ge=1, le=1000),
    filtre_niveau_acces: Optional[str] = Query(None),
    filtre_organisation: Optional[str] = Query(None),
    actifs_seulement: bool = Query(True),
    db: Session = Depends(get_db),
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN))
):
    """Lister tous les utilisateurs avec leurs résumés de permissions"""
    requete = db.query(Utilisateur)
    
    # Appliquer les filtres
    if filtre_niveau_acces:
        requete = requete.filter(Utilisateur.niveau_acces == filtre_niveau_acces)
    
    if filtre_organisation:
        requete = requete.filter(Utilisateur.organization == filtre_organisation)
    
    if actifs_seulement:
        requete = requete.filter(Utilisateur.est_actif == True)
    
    utilisateurs = requete.offset(ignorer).limit(limite).all()
    
    resumes = []
    for utilisateur in utilisateurs:
        resume_permissions = PermissionManager.get_user_permissions_summary(utilisateur)
        
        resumes.append(ResumePermissionUtilisateur(
            id_utilisateur=str(utilisateur.id),
            nom=utilisateur.nom,
            email=utilisateur.email,
            niveau_acces=utilisateur.niveau_acces or "basique",
            portee_donnees=utilisateur.portee_donnees or "propre",
            organisation=utilisateur.organization,
            est_actif=getattr(utilisateur, 'est_actif', True),
            nombre_permissions=len(resume_permissions["permissions"]["effective"]),
            nombre_restrictions=len(utilisateur.marques_autorisees or []) + len(utilisateur.plages_imei_autorisees or [])
        ))
    
    return resumes

@router.get("/utilisateurs/{id_utilisateur}/permissions")
def obtenir_permissions_utilisateur(
    id_utilisateur: str,
    db: Session = Depends(get_db),
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN))
):
    """Obtenir les permissions détaillées pour un utilisateur spécifique"""
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id == id_utilisateur).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return PermissionManager.get_user_permissions_summary(utilisateur)

@router.put("/utilisateurs/{id_utilisateur}/permissions")
def mettre_a_jour_permissions_utilisateur(
    id_utilisateur: str,
    mise_a_jour_permission: MiseAJourPermission,
    db: Session = Depends(get_db),
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN)),
    service_audit: AuditService = Depends(get_audit_service)
):
    """Mettre à jour les permissions et niveaux d'accès utilisateur"""
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id == id_utilisateur).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    admin_actuel = contexte_acces["user"]
    changements = {}
    
    # Suivre les changements pour le journal d'audit
    if mise_a_jour_permission.niveau_acces is not None:
        ancien_niveau = utilisateur.niveau_acces
        utilisateur.niveau_acces = mise_a_jour_permission.niveau_acces
        changements["niveau_acces"] = {"de": ancien_niveau, "vers": mise_a_jour_permission.niveau_acces}
    
    if mise_a_jour_permission.portee_donnees is not None:
        ancienne_portee = utilisateur.portee_donnees
        utilisateur.portee_donnees = mise_a_jour_permission.portee_donnees
        changements["portee_donnees"] = {"de": ancienne_portee, "vers": mise_a_jour_permission.portee_donnees}
    
    if mise_a_jour_permission.organisation is not None:
        ancienne_org = utilisateur.organization
        utilisateur.organization = mise_a_jour_permission.organisation
        changements["organisation"] = {"de": ancienne_org, "vers": mise_a_jour_permission.organisation}
    
    if mise_a_jour_permission.marques_autorisees is not None:
        anciennes_marques = utilisateur.marques_autorisees
        utilisateur.marques_autorisees = mise_a_jour_permission.marques_autorisees
        changements["marques_autorisees"] = {"de": anciennes_marques, "vers": mise_a_jour_permission.marques_autorisees}
    
    if mise_a_jour_permission.plages_imei_autorisees is not None:
        anciennes_plages = utilisateur.plages_imei_autorisees
        utilisateur.plages_imei_autorisees = mise_a_jour_permission.plages_imei_autorisees
        changements["plages_imei_autorisees"] = {"de": anciennes_plages, "vers": mise_a_jour_permission.plages_imei_autorisees}
    
    if mise_a_jour_permission.operations_personnalisees is not None:
        anciennes_permissions = utilisateur.permissions
        utilisateur.permissions = {"operations": mise_a_jour_permission.operations_personnalisees}
        changements["permissions_personnalisees"] = {"de": anciennes_permissions, "vers": utilisateur.permissions}
    
    if mise_a_jour_permission.est_actif is not None:
        ancien_statut = getattr(utilisateur, 'est_actif', True)
        utilisateur.est_actif = mise_a_jour_permission.est_actif
        changements["est_actif"] = {"de": ancien_statut, "vers": mise_a_jour_permission.est_actif}
    
    db.commit()
    
    # Journaliser les changements de permissions
    service_audit.log_permission_change(
        target_user_id=str(utilisateur.id),
        admin_user_id=str(admin_actuel.id),
        changes=changements
    )
    
    return {
        "message": "Permissions mises à jour avec succès",
        "id_utilisateur": str(utilisateur.id),
        "changements": changements
    }

@router.post("/utilisateurs/{id_utilisateur}/regles-acces")
def ajouter_regle_acces(
    id_utilisateur: str,
    donnees_regle: Dict[str, Any],
    db: Session = Depends(get_db),
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN)),
    service_audit: AuditService = Depends(get_audit_service)
):
    """Ajouter une règle d'accès spécifique pour les parties concernées"""
    utilisateur = db.query(Utilisateur).filter(Utilisateur.id == id_utilisateur).first()
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    type_regle = donnees_regle.get("type")  # "plage_imei", "marque", "organisation"
    
    if type_regle == "plage_imei":
        # Ajouter une règle de plage IMEI
        nouvelle_plage = {
            "type": donnees_regle.get("type_plage", "prefixe"),  # prefixe, plage, regex, exact
            "description": donnees_regle.get("description", ""),
            **{k: v for k, v in donnees_regle.items() if k not in ["type", "description"]}
        }
        
        plages_actuelles = utilisateur.plages_imei_autorisees or []
        plages_actuelles.append(nouvelle_plage)
        utilisateur.plages_imei_autorisees = plages_actuelles
    
    elif type_regle == "marque":
        # Ajouter un accès à une marque
        marque = donnees_regle.get("marque")
        if marque:
            marques_actuelles = utilisateur.marques_autorisees or []
            if marque not in marques_actuelles:
                marques_actuelles.append(marque)
                utilisateur.marques_autorisees = marques_actuelles
    
    elif type_regle == "organisation":
        # Définir l'accès organisation
        utilisateur.organization = donnees_regle.get("organisation")
        utilisateur.portee_donnees = "organisation"
    
    db.commit()
    
    # Journaliser l'ajout de règle
    admin_actuel = contexte_acces["user"]
    service_audit.log_access_rule_change(
        target_user_id=str(utilisateur.id),
        admin_user_id=str(admin_actuel.id),
        action="ajouter_regle",
        rule_data=donnees_regle
    )
    
    return {
        "message": f"Règle d'accès ajoutée avec succès",
        "type_regle": type_regle,
        "id_utilisateur": str(utilisateur.id)
    }

@router.delete("/utilisateurs/{id_utilisateur}/regles-acces/{index_regle}")
def supprimer_regle_acces(
    id_utilisateur: str,
    index_regle: int,
    type_regle: str,  # "imei_range", "marque"
    db: Session = Depends(get_db),
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN)),
    service_audit: AuditService = Depends(get_audit_service)
):
    """Remove specific access rule"""
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    removed_rule = None
    
    if rule_type == "imei_range":
        ranges = user.plages_imei_autorisees or []
        if 0 <= rule_index < len(ranges):
            removed_rule = ranges.pop(rule_index)
            user.plages_imei_autorisees = ranges
    
    elif rule_type == "marque":
        brands = user.marques_autorisees or []
        if 0 <= rule_index < len(brands):
            removed_rule = brands.pop(rule_index)
            user.marques_autorisees = brands
    
    if removed_rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.commit()
    
    # Log the rule removal
    current_admin = contexte_acces["user"]
    audit_service.log_access_rule_change(
        target_user_id=str(user.id),
        admin_user_id=str(current_admin.id),
        action="remove_rule",
        rule_data={"type": rule_type, "removed": removed_rule}
    )
    
    return {
        "message": "Access rule removed successfully",
        "removed_rule": removed_rule
    }

@router.get("/audit/changements-permissions")
def obtenir_journal_audit_permissions(
    user_id: Optional[str] = Query(None),
    admin_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN))
):
    """Get audit log of permission changes"""
    from ..models.journal_audit import JournalAudit
    from datetime import datetime, timedelta
    
    start_date = datetime.now() - timedelta(days=days)
    
    query = db.query(JournalAudit).filter(
        JournalAudit.date >= start_date,
        JournalAudit.action.contains("permission")
    )
    
    if user_id:
        query = query.filter(JournalAudit.action.contains(user_id))
    
    if admin_id:
        query = query.filter(JournalAudit.utilisateur_id == admin_id)
    
    logs = query.order_by(JournalAudit.date.desc()).offset(skip).limit(limit).all()
    
    return {
        "audit_logs": [
            {
                "id": str(log.id),
                "action": log.action,
                "date": log.date.isoformat(),
                "admin_user_id": str(log.utilisateur_id) if log.utilisateur_id else None,
                "admin_name": log.utilisateur.nom if log.utilisateur else "System"
            }
            for log in logs
        ],
        "total_count": query.count(),
        "period_days": days
    }

@router.post("/mise-a-jour-lot-permissions")
def mettre_a_jour_permissions_lot(
    update_data: Dict[str, Any],
    db: Session = Depends(get_db),
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN)),
    service_audit: AuditService = Depends(get_audit_service)
):
    """Bulk update permissions for multiple users"""
    user_ids = update_data.get("user_ids", [])
    permission_changes = update_data.get("changes", {})
    
    if not user_ids or not permission_changes:
        raise HTTPException(
            status_code=400, 
            detail="user_ids and changes are required"
        )
    
    updated_users = []
    errors = []
    
    for user_id in user_ids:
        try:
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            if not user:
                errors.append(f"User {user_id} not found")
                continue
            
            # Apply changes
            if "niveau_acces" in permission_changes:
                user.niveau_acces = permission_changes["niveau_acces"]
            
            if "portee_donnees" in permission_changes:
                user.portee_donnees = permission_changes["portee_donnees"]
            
            if "organization" in permission_changes:
                user.organization = permission_changes["organization"]
            
            if "est_actif" in permission_changes:
                user.est_actif = permission_changes["est_actif"]
            
            updated_users.append(str(user.id))
            
        except Exception as e:
            errors.append(f"Error updating user {user_id}: {str(e)}")
    
    db.commit()
    
    # Log bulk update
    current_admin = contexte_acces["user"]
    audit_service.log_bulk_permission_update(
        admin_user_id=str(current_admin.id),
        user_ids=updated_users,
        changes=permission_changes,
        errors=errors
    )
    
    return {
        "message": "Bulk update completed",
        "updated_users": updated_users,
        "errors": errors,
        "success_count": len(updated_users),
        "error_count": len(errors)
    }

@router.get("/modeles")
def obtenir_modeles_permissions(
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN))
):
    """Get predefined permission templates for common use cases"""
    templates = {
        "insurance_company": {
            "name": "Insurance Company",
            "niveau_acces": "limited",
            "portee_donnees": "brands",
            "description": "Access to specific device brands for insurance purposes",
            "default_permissions": ["read_imei", "search_imei", "read_device", "read_analytics"]
        },
        "law_enforcement": {
            "name": "Law Enforcement",
            "niveau_acces": "limited",
            "portee_donnees": "ranges",
            "description": "Access to specific IMEI ranges for investigations",
            "default_permissions": ["read_imei", "search_imei", "read_device", "read_analytics"]
        },
        "manufacturer": {
            "name": "Device Manufacturer",
            "niveau_acces": "elevated",
            "portee_donnees": "brands",
            "description": "Access to their own manufactured devices",
            "default_permissions": ["read_imei", "search_imei", "read_device", "create_device", "update_device", "read_analytics"]
        },
        "regulatory_body": {
            "name": "Regulatory Body",
            "niveau_acces": "elevated",
            "portee_donnees": "all",
            "description": "Regulatory oversight with comprehensive monitoring access",
            "default_permissions": ["read_imei", "search_imei", "read_device", "read_analytics", "read_audit"]
        },
        "partner_organization": {
            "name": "Partner Organization",
            "niveau_acces": "standard",
            "portee_donnees": "organization",
            "description": "Standard access within organizational boundaries",
            "default_permissions": ["read_imei", "search_imei", "read_device", "create_device", "update_device", "read_sim", "create_sim"]
        }
    }
    
    return {"templates": templates}

@router.post("/appliquer-modele/{nom_modele}/{id_utilisateur}")
def appliquer_modele_permissions(
    nom_modele: str,
    id_utilisateur: str,
    config_supplementaire: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN)),
    service_audit: AuditService = Depends(get_audit_service)
):
    """Apply a permission template to a user"""
    # Get templates
    templates_response = get_permission_templates(contexte_acces)
    templates = templates_response["templates"]
    
    if template_name not in templates:
        raise HTTPException(status_code=404, detail="Template not found")
    
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    template = templates[template_name]
    
    # Apply template settings
    user.niveau_acces = template["niveau_acces"]
    user.portee_donnees = template["portee_donnees"]
    user.permissions = {"operations": template["default_permissions"]}
    
    # Apply additional configuration
    if additional_config:
        if "organization" in additional_config:
            user.organization = additional_config["organization"]
        if "marques_autorisees" in additional_config:
            user.marques_autorisees = additional_config["marques_autorisees"]
        if "plages_imei_autorisees" in additional_config:
            user.plages_imei_autorisees = additional_config["plages_imei_autorisees"]
    
    db.commit()
    
    # Log template application
    current_admin = contexte_acces["user"]
    audit_service.log_template_application(
        target_user_id=str(user.id),
        admin_user_id=str(current_admin.id),
        template_name=template_name,
        additional_config=additional_config or {}
    )
    
    return {
        "message": f"Template '{template_name}' applied successfully",
        "user_id": str(user.id),
        "template": template,
        "additional_config": additional_config
    }
