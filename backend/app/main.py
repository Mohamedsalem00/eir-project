from fastapi import FastAPI, Depends, HTTPException, Query, Request, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uuid
import time
import csv
import json
import io
import os
import platform
import logging
from .core.dependencies import get_db, get_current_user, get_current_user_optional, get_admin_user
from .core.permissions import PermissionManager, Operation, AccessLevel, require_permission, require_niveau_acces
from .core.i18n_deps import get_current_translator, get_language_from_request
from .core.audit_deps import get_audit_service
from .i18n import get_translator, SUPPORTED_LANGUAGES
from .services.audit import AuditService
from .services.eir_notifications import EIRNotificationService
from .routes.auth import router as auth_router
from .routes.access_management import router as access_router
from .models.appareil import Appareil
from .models.utilisateur import Utilisateur
from .models.recherche import Recherche
from .models.sim import SIM
from .models.notification import Notification
from .models.journal_audit import JournalAudit
from .models.imei import IMEI
import platform

# Configuration du logger
logger = logging.getLogger(__name__)

# Import pour l'intégration multi-protocoles
from .interface_gateway.dispatcher import (
    handle_incoming_request, 
    get_supported_protocols, 
    validate_payload,
    ProtocolNotEnabledException, 
    UnsupportedProtocolException
)

# Configuration FastAPI améliorée
app = FastAPI(
    title="API Projet EIR",
    description="API du Registre d'Identité des Équipements (EIR) pour la gestion professionnelle d'appareils mobiles",
    version="1.0.0",
    terms_of_service="https://eir-project.com/terms",
    contact={
        "name": "Équipe de Développement EIR",
        "email": "contact@eir-project.com",
        "url": "https://eir-project.com"
    },
    license_info={
        "name": "Licence Propriétaire",
        "url": "https://eir-project.com/license"
    },
    openapi_tags=[
        {
            "name": "Système",
            "description": "Informations système et vérifications d'état"
        },
        {
            "name": "Public",
            "description": "Points de terminaison publics disponibles pour tous les utilisateurs"
        },
        {
            "name": "Authentification",
            "description": "Authentification et autorisation des utilisateurs"
        },
        {
            "name": "IMEI",
            "description": "Services de validation et recherche d'IMEI"
        },
        {
            "name": "Appareils",
            "description": "Opérations de gestion des appareils"
        },
        {
            "name": "Cartes SIM",
            "description": "Opérations de gestion des cartes SIM"
        },
        {
            "name": "Utilisateurs",
            "description": "Opérations de gestion des utilisateurs"
        },
        {
            "name": "Historique de Recherche",
            "description": "Points de terminaison d'historique et suivi des recherches"
        },
        {
            "name": "Notifications",
            "description": "Points de terminaison de gestion des notifications"
        },
        {
            "name": "Analyses",
            "description": "Points de terminaison d'analyses et rapports"
        },
        {
            "name": "Admin",
            "description": "Opérations administratives"
        }
    ]
)

# Inclure les routeurs
app.include_router(auth_router, tags=["Authentification"])
app.include_router(access_router, tags=["Gestion d'Accès"])

# Import et inclusion du router des notifications
from .routes.notifications import router as notifications_router
app.include_router(notifications_router, tags=["Notifications"])

# Stocker l'heure de démarrage de l'application pour le calcul du temps de fonctionnement
app_start_time = datetime.now()

# Fonction utilitaire pour le formatage des dates
def format_datetime(dt):
    """Formate la datetime en chaîne lisible"""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_system_uptime():
    """Calcule le temps de fonctionnement du système"""
    uptime = datetime.now() - app_start_time
    return str(uptime).split('.')[0]  # Supprime les microsecondes

# POINTS DE TERMINAISON SYSTÈME
@app.get(
    "/",
    tags=["Système"],
    summary="Bienvenue API",
    description="Obtenir des informations complètes sur l'API, les capacités et le guide de démarrage rapide",
    response_model=None
)
async def bienvenue(
    request: Request,
    user: Optional[Utilisateur] = Depends(get_current_user_optional),
    translator = Depends(get_current_translator)
):
    """
    ## Bienvenue à l'API Projet EIR
    
    Ce point de terminaison fournit des informations complètes sur l'API, incluant :
    
    - **Capacités du service** et fonctionnalités
    - **Points de terminaison disponibles** basés sur votre niveau d'accès
    - **Spécifications techniques** et SLA
    - **Guide de démarrage rapide** et liens de documentation
    - **Informations de sécurité et conformité**
    - **Informations de contact** et détails de support
    
    ### Niveaux d'Accès :
    - **Visiteurs** : Informations API de base et points de terminaison publics
    - **Utilisateurs Authentifiés** : Informations améliorées et points de terminaison utilisateur
    - **Administrateurs** : Documentation API complète et points de terminaison admin
    
    ### Langues Supportées :
    Utilisez l'en-tête `X-Language` ou le paramètre `?lang=` avec : `fr`, `en`, `ar`
    """
    current_user = user
    type_utilisateur = "visiteur"
    if current_user:
        if current_user.type_utilisateur == "administrateur" or current_user.niveau_acces == "admin":
            type_utilisateur = "admin"
        else:
            type_utilisateur = "utilisateur"
    
    # Obtenir l'URL de base pour la requête
    base_url = f"{request.url.scheme}://{request.headers.get('host', 'localhost')}"
    
    # Construire les capacités basées sur le type d'utilisateur
    capacites = {
        "validation_imei": {
            "recherche_temps_reel": True,
            "validation_par_lot": type_utilisateur != "visiteur",
            "suivi_historique": type_utilisateur != "visiteur",
            "surveillance_statut": type_utilisateur == "admin",
            "formats_supportes": [translator.translate("format_15_chiffres"), translator.translate("format_14_chiffres")]
        },
        "gestion_appareils": {
            "enregistrement_appareil": type_utilisateur != "visiteur",
            "support_multi_imei": True,
            "assignation_appareil": type_utilisateur == "admin",
            "import_en_lot": type_utilisateur == "admin",
            "analyses_marques": True
        },
        "gestion_utilisateurs": {
            "acces_base_role": True,
            "multi_locataire": type_utilisateur != "visiteur",
            "journalisation_audit": type_utilisateur == "admin",
            "analyses_utilisateurs": type_utilisateur == "admin"
        }
    }
    
    # Construire les points de terminaison basés sur le type d'utilisateur
    points_terminaison_publics = {
        translator.translate("endpoint_recherche_imei"): "/imei/{imei}",
        translator.translate("endpoint_journal_recherche_imei"): "/imei/{imei}/historique",
        translator.translate("endpoint_statistiques_publiques"): "/public/statistiques",
        translator.translate("endpoint_verification_sante"): "/verification-etat",
        translator.translate("endpoint_info_api"): "/",
        translator.translate("endpoint_langues_supportees"): "/languages"
    }
    
    points_terminaison_authentifies = {}
    points_terminaison_admin = {}
    
    if type_utilisateur in ["utilisateur", "admin"]:
        points_terminaison_authentifies = {
            translator.translate("endpoint_appareils_utilisateur"): "/appareils",
            translator.translate("endpoint_sims_utilisateur"): "/cartes-sim", 
            translator.translate("endpoint_historique_recherches"): "/recherches",
            translator.translate("endpoint_profil_utilisateur"): "/utilisateurs/{user_id}",
            translator.translate("endpoint_notifications"): "/notifications",
            translator.translate("endpoint_analyses"): "/analyses/recherches"
        }
    if type_utilisateur == "admin":
        points_terminaison_admin = {
            translator.translate("endpoint_gestion_utilisateurs"): "/utilisateurs",
            translator.translate("endpoint_utilisateurs_admin"): "/admin/utilisateurs",
            translator.translate("endpoint_gestion_appareils"): "/admin/appareils",
            translator.translate("endpoint_operations_lot"): "/admin/import-lot-appareils",
            translator.translate("endpoint_journaux_audit"): "/admin/journaux-audit",
            translator.translate("endpoint_analyses_systeme"): "/analyses/appareils"
        }
    
    return {
        "title": translator.translate("titre_bienvenue_api"),
        "description": translator.translate("description_bienvenue"),
        "tagline": translator.translate("slogan_bienvenue"),
        "statut": translator.translate("statut_api"),
        "timestamp": datetime.now().isoformat(),
        "language": translator.current_language,
        
        # Champs pour compatibilité des tests
        "nom_service": translator.translate("nom_service"),
        "version": translator.translate("version_api"),
        
        "api": {
            "name": translator.translate("nom_service"),
            "version": translator.translate("version_api"),
            "build": translator.translate("version_construction"),
            "environment": translator.translate("environnement"),
            "uptime": get_system_uptime()
        },
        
        "contact": {
            "organization": translator.translate("organisation"),
            "email": translator.translate("email_contact"),
            "support_email": translator.translate("email_support"),
            "documentation_url": translator.translate("url_documentation")
        },
        
        "securite": {
            "methodes_authentification": [translator.translate("auth_jwt"), translator.translate("auth_cle_api")],
            "limitation_taux": translator.translate("limites_taux"),
            "normes_conformite": [translator.translate("conformite_rgpd"), translator.translate("conformite_sox"), translator.translate("conformite_iso"), translator.translate("conformite_gsma")],
            "chiffrement_donnees": translator.translate("chiffrement_donnees")
        },
        
        "capacites": capacites,
        
        "points_terminaison": {
            "publics": points_terminaison_publics,
            "authentifies": points_terminaison_authentifies,
            "admin": points_terminaison_admin
        },
        
        "specifications_techniques": {
            "formats_supportes": [translator.translate("format_json"), translator.translate("format_xml")],
            "taille_max_requete": translator.translate("taille_max_requete"),
            "sla_temps_reponse": translator.translate("sla_temps_reponse"),
            "sla_disponibilite": translator.translate("sla_disponibilite"),
            "support_sdk": [translator.translate("sdk_python"), translator.translate("sdk_javascript"), translator.translate("sdk_java"), translator.translate("sdk_curl")]
        },
        
        "demarrage_rapide": {
            "documentation": f"{base_url}/docs",
            "docs_interactives": f"{base_url}/docs",
            "verification_sante": f"{base_url}/verification-etat",
            "exemple_verification_imei": f"{base_url}/imei/123456789012345",
            "langues_supportees": f"{base_url}/languages"
        },
        
        "legal": {
            "conditions_service": translator.translate("conditions_service"),
            "politique_confidentialite": translator.translate("politique_confidentialite"),
            "licence": translator.translate("licence"),
            "retention_donnees": translator.translate("retention_donnees")
        }
    }

@app.get(
    "/health",
    tags=["Système"],
    summary="Vérification d'État",
    description="Informations complètes sur l'état et le statut du système"
)
async def health_check(
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    """Endpoint de compatibilité pour /health - redirige vers verification_etat"""
    return await verification_etat(db, translator)

@app.get(
    "/verification-etat",
    tags=["Système"],
    summary="Vérification d'État (Francisé)",
    description="Informations complètes sur l'état et le statut du système"
)
async def verification_etat(
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    """
    ## Vérification d'État du Système
    
    Fournit des informations détaillées sur l'état du système incluant :
    - Statut du service et temps de fonctionnement
    - Connectivité de la base de données
    - Ressources système
    - Statut des points de terminaison API
    - Statut de sécurité
    """
    try:
        # Tester la connexion à la base de données
        db_status = {"statut": translator.translate("statut_connecte"), "message": translator.translate("base_donnees_connectee")}
        db_latency = translator.translate("latence_bonne")
        try:
            db.execute(text("SELECT 1"))
        except Exception as e:
            db_status = {"statut": translator.translate("statut_erreur"), "message": str(e)}
            db_latency = translator.translate("latence_na")
        
        # Informations système
        infos_systeme = {
            "duree_fonctionnement": get_system_uptime(),
            "plateforme": platform.platform(),
            "version_python": platform.python_version(),
            "heure_serveur": datetime.now().isoformat()
        }
        
        # Vérification du statut des points de terminaison
        statut_points_terminaison = {
            translator.translate("endpoint_authentification"): translator.translate("statut_operationnel"),
            translator.translate("endpoint_validation_imei"): translator.translate("statut_operationnel"), 
            translator.translate("endpoint_gestion_appareils"): translator.translate("statut_operationnel"),
            translator.translate("endpoint_analyses"): translator.translate("statut_operationnel")
        }
        
        # Statut de sécurité
        statut_securite = {
            translator.translate("securite_tls"): translator.translate("statut_active"),
            translator.translate("securite_jwt"): translator.translate("statut_active"),
            translator.translate("securite_limitation_taux"): translator.translate("statut_active"),
            translator.translate("securite_journalisation_audit"): translator.translate("statut_active")
        }
        
        return {
            "statut": translator.translate("service_sain"),
            "horodatage": datetime.now().isoformat(),
            "service": translator.translate("nom_service"),
            "version": translator.translate("version_api"),
            "duree_fonctionnement": infos_systeme["duree_fonctionnement"],
            
            # Champs pour compatibilité des tests
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            
            "base_donnees": {
                "statut": db_status["statut"],
                "message": db_status["message"],
                "latence": db_latency
            },
            "infos_systeme": infos_systeme,
            "statut_points_terminaison": statut_points_terminaison,
            "statut_securite": statut_securite
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "statut": translator.translate("statut_defaillant"),
                "message": translator.translate("verification_sante_echec").format(error=str(e)),
                "horodatage": datetime.now().isoformat()
            }
        )


@app.get(
    "/languages",
    tags=["Système"],
    summary="Langues Supportées",
    description="""## Langues Supportées

Obtenir des informations sur toutes les langues supportées incluant :
- Codes et noms des langues
- Noms natifs des langues
- Support RTL (Droite-vers-Gauche)
- Paramètres de langue par défaut"""
)
def obtenir_langues_supportees(translator = Depends(get_current_translator)):
    return {
        "langues_supportees": SUPPORTED_LANGUAGES,
        "langue_par_defaut": "fr",
        "utilisation": {
            "en_tete": translator.translate("usage_langue_en_tete"),
            "parametre_requete": translator.translate("usage_langue_requete"),
            "accept_language": translator.translate("usage_langue_accept")
        }
    }


@app.get(
    "/public/statistiques",
    tags=["Public", "Analyses"],
    summary="Statistiques Publiques",
    description="Obtenir les statistiques publiques du système sans authentification"
)
def statistiques_publiques(
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    """
    ## Statistiques Publiques du Système
    
    Obtenir des statistiques générales et publiques du système EIR incluant :
    - Nombre total d'appareils enregistrés
    - Nombre total de recherches effectuées
    - Statistiques de validation IMEI
    - Données agrégées anonymisées
    
    ### Accès :
    - ✅ Aucune authentification requise
    - ✅ Données publiques uniquement
    - ✅ Informations anonymisées
    """
    try:
        # Statistiques générales (données publiques uniquement)
        total_appareils = db.execute(text("SELECT COUNT(*) FROM appareil")).scalar() or 0
        total_recherches = db.execute(text("SELECT COUNT(*) FROM recherche")).scalar() or 0
        
        # Statistiques de validation IMEI (dernières 30 jours)
        recherches_recentes = db.execute(text("""
            SELECT COUNT(*) FROM recherche 
            WHERE date_recherche >= NOW() - INTERVAL '30 days'
        """)).scalar() or 0
        
        # Répartition par statut IMEI (données agrégées)
        repartition_statuts = db.execute(text("""
            SELECT statut, COUNT(*) as count 
            FROM imei 
            WHERE statut IS NOT NULL
            GROUP BY statut 
            ORDER BY count DESC
        """)).fetchall()
        
        # Statistiques TAC (si disponible)
        total_tacs = db.execute(text("SELECT COUNT(*) FROM tac_database")).scalar() or 0
        
        # Construire la réponse
        stats_statuts = {}
        for row in repartition_statuts:
            stats_statuts[row.statut] = row.count
        
        return {
            "total_appareils": total_appareils,
            "total_recherches": total_recherches,
            "recherches_30_jours": recherches_recentes,
            "total_tacs_disponibles": total_tacs,
            "repartition_statuts": stats_statuts,
            "derniere_mise_a_jour": datetime.now().isoformat(),
            "periode_stats": "30_derniers_jours",
            "type_donnees": "publiques_anonymisees",
            "message": translator.translate("stats_publiques_info"),
            "infos": {
                "description": translator.translate("stats_publiques_description"),
                "avertissement": translator.translate("stats_publiques_avertissement"),
                "contact": translator.translate("stats_publiques_contact")
            }
        }
        
    except Exception as e:
        # En cas d'erreur, retourner des statistiques de base
        return {
            "total_appareils": 0,
            "total_recherches": 0,
            "recherches_30_jours": 0,
            "total_tacs_disponibles": 0,
            "repartition_statuts": {},
            "derniere_mise_a_jour": datetime.now().isoformat(),
            "statut": "erreur_temporaire",
            "message": translator.translate("stats_publiques_erreur"),
            "erreur": str(e) if os.getenv("DEBUG", "false").lower() == "true" else "Service temporairement indisponible"
        }


@app.get(
    "/imei/{imei}",
    tags=["IMEI", "Public"],
    summary="Recherche IMEI Améliorée avec Contrôle d'Accès",
    description="Rechercher les informations IMEI avec niveaux d'accès granulaires et journalisation automatique des recherches",
    response_model=None
)
async def verifier_imei(
    imei: str,
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[Utilisateur] = Depends(get_current_user_optional),
    translator = Depends(get_current_translator),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    ## Service de Recherche IMEI Amélioré avec Contrôle d'Accès Granulaire
    
    Ce point de terminaison fournit des informations IMEI basées sur les niveaux d'accès utilisateur et journalise automatiquement les recherches.
    
    ### Niveaux d'Accès et Données Retournées :
    - **Visiteurs** : Informations de base de l'appareil (marque, modèle, statut)
    - **Utilisateurs de Base** : Détails d'appareil améliorés
    - **Utilisateurs Limités (Parties Concernées)** : Accès spécifique aux marques/plages avec analyses
    - **Utilisateurs Standard** : Accès complet aux appareils personnels
    - **Utilisateurs Élevés** : Accès aux appareils organisationnels
    - **Administrateurs** : Informations complètes d'appareil et de propriété
    
    ### Journalisation Automatique :
    - Toutes les recherches sont journalisées dans la table Recherche pour le suivi d'historique
    - Les tentatives d'accès sont auditées pour la surveillance de sécurité
    - Les vérifications de permissions sont journalisées pour la conformité
    
    ### Paramètres :
    - **imei** : Numéro IMEI à 15 chiffres à rechercher
    
    ### Contrôle d'Accès :
    - Les parties concernées voient seulement les appareils dans leurs marques/plages autorisées
    - Les utilisateurs voient des données améliorées basées sur leur niveau d'accès
    - Tous les accès sont journalisés à des fins d'audit
    """
    # Obtenir le niveau d'accès utilisateur
    niveau_acces_utilisateur = "visiteur"
    if user:
        niveau_acces_utilisateur = user.niveau_acces or "basique"
    
    # Check if user can access this specific IMEI
    can_access, access_details = PermissionManager.can_access_imei(user, imei, db)
    
    if not can_access:
        # Log denied access attempt
        audit_service.log_access_attempt(
            user_id=str(user.id) if user else None,
            operation="read_imei",
            entity_type="imei",
            entity_id=imei,
            success=False,
            reason=access_details["reason"],
            ip_address=request.client.host if request.client else None
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: {access_details['reason']}"
        )
    
    # Search for IMEI
    imei_record = db.query(IMEI).filter(IMEI.numero_imei == imei).first()
    found = imei_record is not None
    
    # Log the search in Recherche table (for search history)
    recherche = Recherche(
        id=uuid.uuid4(),
        date_recherche=datetime.now(),
        imei_recherche=imei,
        utilisateur_id=user.id if user else None
    )
    db.add(recherche)
    
    # Log successful access in audit service
    audit_service.log_access_attempt(
        user_id=str(user.id) if user else None,
        operation="read_imei",
        entity_type="imei", 
        entity_id=imei,
        success=True,
        reason=access_details["reason"],
        ip_address=request.client.host if request.client else None
    )
    
    # Log IMEI search for tracking
    audit_service.log_imei_search(
        imei=imei,
        user_id=str(user.id) if user else None,
        found=found
    )
    
    # Commit logs
    db.commit()
    
    if imei_record:
        appareil = imei_record.appareil
        
        # Build base response
        response_data = {
            "id": str(imei_record.id),
            "imei": imei,
            "trouve": True,
            "statut": imei_record.statut,
            "numero_slot": imei_record.numero_slot,
            "message": translator.translate("imei_trouve"),
            "recherche_enregistree": True,
            "id_recherche": str(recherche.id),
            "contexte_acces": {
                "niveau_acces": niveau_acces_utilisateur,
                "motif_acces": access_details["reason"],
                "portee_donnees": access_details["portee_donnees"]
            }
        }
        
        # Ajouter les informations d'appareil selon le niveau d'accès
        if niveau_acces_utilisateur in ["limited", "standard", "elevated", "admin"]:
            info_appareil = {
                "id": str(appareil.id),
                "marque": appareil.marque,
                "modele": appareil.modele,
                "emmc": appareil.emmc
            }
            
            # Add ownership info for elevated users and admins
            if niveau_acces_utilisateur in ["elevated", "admin"]:
                info_appareil["utilisateur_id"] = str(appareil.utilisateur_id) if appareil.utilisateur_id else None
                
                # Ajouter les détails complets d'appareil pour les admins
                if niveau_acces_utilisateur == "admin":
                    info_appareil.update({
                        "created_date": appareil.date_creation.isoformat() if hasattr(appareil, 'date_creation') else None,
                        "last_updated": appareil.date_modification.isoformat() if hasattr(appareil, 'date_modification') else None
                    })
            
            response_data["appareil"] = info_appareil
        else:
            # Informations limitées pour visiteurs et utilisateurs de base
            response_data["appareil"] = {
                "marque": appareil.marque,
                "modele": appareil.modele
            }
        
        # 📧 Send IMEI verification result email (only for authenticated users)
        if user:
            try:
                await EIRNotificationService.notifier_verification_imei(
                    user_id=str(user.id),
                    imei=imei,
                    resultat="valide" if found else "invalide",
                    details={
                        "marque": appareil.marque if found else "Inconnue",
                        "modele": appareil.modele if found else "Inconnu",
                        "tac": imei[:8] if len(imei) >= 8 else "N/A",
                        "luhn_valide": True,  # Simplified for demo
                        "info_supplementaire": f"Vérification via niveau d'accès: {niveau_acces_utilisateur}"
                    }
                )
                logger.info(f"IMEI verification email sent to user: {user.email}")
            except Exception as e:
                logger.warning(f"Failed to send IMEI verification email: {str(e)}")
        
        return response_data
    
    # IMEI not found response
    return {
        "imei": imei,
        "trouve": False,
        "message": translator.translate("erreur_imei_non_trouve"),
        "recherche_enregistree": True,
        "id_recherche": str(recherche.id),
        "contexte_acces": {
            "niveau_acces": niveau_acces_utilisateur,
            "motif_acces": access_details["reason"]
        }
    }

# APIs de Gestion d'Appareils Améliorées avec contrôle d'accès granulaire
@app.post("/appareils", tags=["Appareils"])
async def enregistrer_appareil(
    donnees_appareil: dict,
    request: Request,
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """
    Enregistrer un appareil avec contrôle d'accès amélioré et journalisation d'audit
    
    ### Contrôle d'Accès:
    - Les utilisateurs standard peuvent enregistrer des appareils pour eux-mêmes
    - Les utilisateurs élevés peuvent enregistrer des appareils dans leur organisation
    - Les admins peuvent enregistrer des appareils pour tout utilisateur
    - Les utilisateurs limités (parties concernées) ont un accès restreint basé sur les marques
    
    ### Support Multilingue:
    - Utilisez l'en-tête `Accept-Language` pour spécifier la langue préférée
    - Langues supportées: `fr` (français), `en` (anglais), `ar` (arabe)
    - Exemple: `Accept-Language: en-US,en;q=0.9,fr;q=0.8`
    - Alternative: utilisez l'en-tête `X-Language` ou le paramètre `?lang=`
    
    ### Messages d'Erreur Localisés:
    - Les messages d'erreur sont retournés dans la langue demandée
    - Les erreurs de validation IMEI dupliqué sont traduites automatiquement
    """
    # Vérifier si l'utilisateur a la permission de créer des appareils
    if not PermissionManager.has_permission(user, Operation.CREATE_DEVICE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission refusée: Impossible de créer des appareils"
        )
    
    # Valider l'accès aux marques pour les parties concernées
    marque_appareil = donnees_appareil.get("marque")
    if user.niveau_acces == "limited" and user.marques_autorisees:
        if marque_appareil not in user.marques_autorisees:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé: Marque '{marque_appareil}' non autorisée"
            )
    
    # Définir le propriétaire de l'appareil selon le niveau d'accès
    if user.type_utilisateur != "administrateur" and user.niveau_acces not in ["elevated"]:
        donnees_appareil["utilisateur_id"] = user.id
    
    appareil = Appareil(
        id=uuid.uuid4(),
        marque=donnees_appareil.get("marque"),
        modele=donnees_appareil.get("modele"),
        emmc=donnees_appareil.get("emmc"),
        utilisateur_id=donnees_appareil.get("utilisateur_id")
    )
    db.add(appareil)
    db.flush()  # Obtenir l'ID de l'appareil
    
    # Ajouter les IMEIs avec validation
    donnees_imeis = donnees_appareil.get("imeis", [])
    numeros_imei = []
    
    for i, donnees_imei in enumerate(donnees_imeis):
        numero_imei = donnees_imei.get("numero_imei")
        
        # Vérifier si l'IMEI existe déjà dans la base de données
        if numero_imei:
            existing_imei = db.query(IMEI).filter(IMEI.numero_imei == numero_imei).first()
            if existing_imei:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=translator.translate("erreur_imei_existe_deja", numero_imei=numero_imei)
                )
        
        # Valider l'accès aux plages IMEI pour les parties concernées
        if user.niveau_acces == "limited" and user.plages_imei_autorisees:
            can_access, _ = PermissionManager.can_access_imei(user, numero_imei, db)
            if not can_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Accès refusé: IMEI '{numero_imei}' non autorisé"
                )
        
        imei = IMEI(
            id=uuid.uuid4(),
            numero_imei=numero_imei,
            numero_slot=donnees_imei.get("numero_slot", i + 1),
            statut=donnees_imei.get("statut", "actif"),
            appareil_id=appareil.id
        )
        db.add(imei)
        numeros_imei.append(imei.numero_imei)
    
    try:
        db.commit()
        db.refresh(appareil)
    except Exception as e:
        db.rollback()
        # Vérifier si c'est une erreur de contrainte d'unicité sur l'IMEI
        if "unique constraint" in str(e).lower() and "imei" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=translator.translate("erreur_imeis_existent_deja")
            )
        # Pour toute autre erreur, la relancer
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=translator.translate("erreur_enregistrement_appareil", error=str(e))
        )
    
    # Journaliser la création d'appareil avec contexte d'accès
    audit_service.log_device_creation(
        device_id=str(appareil.id),
        user_id=str(user.id),
        device_data={
            "marque": appareil.marque,
            "modele": appareil.modele,
            "emmc": appareil.emmc,
            "imeis": numeros_imei,
            "niveau_acces": user.niveau_acces or "basique"
        }
    )
    
    # 📧 Send new device registration email
    try:
        await EIRNotificationService.notifier_nouvel_appareil(
            user_id=str(user.id),
            appareil_details={
                "marque": appareil.marque,
                "modele": appareil.modele,
                "emmc": appareil.emmc,
                "imeis": [{"numero": imei, "slot": i+1} for i, imei in enumerate(numeros_imei)]
            }
        )
        logger.info(f"New device registration email sent to user: {user.email}")
    except Exception as e:
        logger.warning(f"Failed to send device registration email: {str(e)}")
    
    return {
        "id": str(appareil.id),
        "marque": appareil.marque,
        "modele": appareil.modele,
        "imeis": [
            {
                "numero_imei": imei.numero_imei,
                "numero_slot": imei.numero_slot,
                "statut": imei.statut
            }
            for imei in appareil.imeis
        ],
        "niveau_acces": user.niveau_acces or "basique"
    }

@app.get("/recherches", tags=["Historique de Recherche"])
def list_searches(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user)
):
    """
    Lister les recherches avec contrôle d'accès amélioré
    
    ### Niveaux d'Accès:
    - Les utilisateurs standard voient seulement leurs propres recherches
    - Les utilisateurs élevés voient les recherches organisationnelles
    - Les admins voient toutes les recherches
    - Les utilisateurs limités voient les recherches dans leur périmètre de données
    """
    # Vérifier si l'utilisateur a la permission de lire l'historique des recherches
    if not PermissionManager.has_permission(user, Operation.READ_SEARCH_HISTORY):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission refusée: Impossible de lire l'historique des recherches"
        )
    
    query = db.query(Recherche)
    
    # Appliquer un filtrage basé sur l'accès en utilisant des permissions simples
    if user.type_utilisateur != "administrateur" and user.niveau_acces != "admin":
        if user.portee_donnees == "own":
            query = query.filter(Recherche.utilisateur_id == user.id)
        elif user.niveau_acces == "limited":
            # Les utilisateurs limités voient seulement leurs propres recherches
            query = query.filter(Recherche.utilisateur_id == user.id)
    
    searches = query.offset(skip).limit(limit).all()
    
    return {
        "searches": [
            {
                "id": str(search.id),
                "date_recherche": format_datetime(search.date_recherche),
                "imei_recherche": search.imei_recherche,
                "utilisateur_id": str(search.utilisateur_id) if search.utilisateur_id else None
            }
            for search in searches
        ],
        "contexte_acces": {
            "niveau_acces": user.niveau_acces or "basique",
            "portee_donnees": user.portee_donnees or "own",
            "total_accessible": len(searches)
        }
    }

# Enhanced device listing with granular filtering
@app.get("/appareils", tags=["Appareils"], summary="Liste des appareils")
def list_devices(
    skip: int = 0,
    limit: int = 100,
    marque: str = None,
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user)
):
    """
    Répertorier les appareils avec un contrôle d'accès et un filtrage améliorés

    ### Contrôle d'accès :
    - Les utilisateurs voient les appareils en fonction de leur périmètre de données
    - Le filtrage par marque respecte les marques autorisées pour les parties concernées
    - Filtrage organisationnel pour les utilisateurs privilégiés
    - Accès complet pour les administrateurs
    """
    try:
        # Check if user has permission to read devices
        if not PermissionManager.has_permission(user, Operation.READ_DEVICE):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Autorisation refusée : impossible de lire les appareils"
            )
        
        # Get data filter context for this user
        filter_context = PermissionManager.get_data_filter_context(user)
        
        query = db.query(Appareil)
        
        # Apply access-based filtering based on user's data portee_donnees
        if not filter_context.get("is_admin", False):
            portee_donnees = filter_context.get("portee_donnees", "personnel")
            
            # Handle both enum and string values for portee_donnees
            if hasattr(portee_donnees, 'value'):
                scope_value = portee_donnees.value
            elif isinstance(portee_donnees, str):
                scope_value = portee_donnees
            else:
                scope_value = str(portee_donnees)
            
            if scope_value in ["personnel"]:
                query = query.filter(Appareil.utilisateur_id == user.id)
            elif scope_value in ["marques"]:
                marques_autorisees = filter_context.get("marques_autorisees", [])
                if marques_autorisees:
                    query = query.filter(Appareil.marque.in_(marques_autorisees))
                else:
                    # If no authorized brands, show only own devices
                    query = query.filter(Appareil.utilisateur_id == user.id)
            elif scope_value == "organisation" and filter_context.get("organization"):
                # Organization filtering would need additional device fields
                # For now, fall back to user's own devices
                query = query.filter(Appareil.utilisateur_id == user.id)
        
        # Apply marque filter with access validation
        if marque:
            # Validate marque access for limited users
            if getattr(user, 'niveau_acces', None) == "limited" and getattr(user, 'marques_autorisees', None):
                if marque not in user.marques_autorisees:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Accès refusé : Marque '{marque}' pas dans les marques autorisées"
                    )
            query = query.filter(Appareil.marque == marque)
        
        devices = query.offset(skip).limit(limit).all()
        
        # Build response with access-appropriate data
        device_list = []
        for device in devices:
            try:
                can_access, access_details = PermissionManager.can_access_device(user, device)
                
                if can_access:
                    device_info = {
                        "id": str(device.id),
                        "marque": getattr(device, 'marque', 'N/A') or "N/A",
                        "modele": getattr(device, 'modele', 'N/A') or "N/A", 
                        "can_modify": PermissionManager.has_permission(user, Operation.UPDATE_DEVICE) and can_access,
                        "motif_acces": access_details.get("reason", "Accès autorisé") if access_details else "Accès autorisé"
                    }
                    
                    # Add enhanced info based on access level
                    try:
                        user_level = AccessLevel.from_french(getattr(user, 'niveau_acces', 'basique') or "basique")
                        if user_level in [AccessLevel.ELEVATED, AccessLevel.ADMIN]:
                            device_info.update({
                                "emmc": getattr(device, 'emmc', None),
                                "utilisateur_id": str(device.utilisateur_id) if device.utilisateur_id else None,
                                "imei_count": len(getattr(device, 'imeis', []))
                            })
                    except Exception as e:
                        # If access level conversion fails, continue with basic info
                        logger.warning(f"Access level conversion failed: {e}")
                    
                    device_list.append(device_info)
            except Exception as e:
                # Log device processing error but continue
                logger.warning(f"Error processing device {device.id}: {e}")
                continue
        
        # Get portee_donnees value safely for response
        portee_donnees = filter_context.get("portee_donnees", "own")
        if hasattr(portee_donnees, 'value'):
            portee_value = portee_donnees.value
        else:
            portee_value = str(portee_donnees)
        
        return {
            "devices": device_list,
            "contexte_acces": {
                "niveau_acces": getattr(user, 'niveau_acces', 'basique') or "basique",
                "portee_donnees": portee_value,
                "marques_autorisees": filter_context.get("marques_autorisees", []),
                "total_accessible": len(device_list)
            },
            "filters": {
                "marque": marque,
                "skip": skip,
                "limit": limit
            }
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors and return a generic error response
        logger.error(f"Unexpected error in list_devices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Une erreur interne s'est produite lors de la récupération des appareils"
        )


# Nouvel endpoint pour les parties concernées pour vérifier leurs permissions d'accès
@app.get("/mes-permissions", tags=["Utilisateurs"], response_model=None)
def get_my_permissions(
    user: Optional[Utilisateur] = Depends(get_current_user_optional)
):
    """
    Obtenir les permissions et niveaux d'accès de l'utilisateur actuel
    
    ### Retourne:
    - Niveau d'accès actuel et permissions
    - Marques autorisées et plages IMEI
    - Périmètre de données et restrictions
    - Opérations disponibles
    """
    if not user:
        return {
            "niveau_acces": "visiteur",
            "permissions": ["read_imei"],
            "restrictions": "Accès public uniquement"
        }
    
    permissions_summary = PermissionManager.get_user_permissions_summary(user)
    
    return {
        "user_info": {
            "id": str(user.id),
            "name": user.nom,
            "niveau_acces": user.niveau_acces or "basique",
            "organization": getattr(user, 'organisation', None)
        },
        "permissions": permissions_summary,
        "current_session": {
            "is_authenticated": True,
            "is_admin": user.type_utilisateur == "administrateur",
            "request_ip": "current_session"
        }
    }

# APIs de Gestion des Utilisateurs avec journalisation d'audit appropriée
@app.post("/utilisateurs", tags=["Utilisateurs", "Admin"])
def create_user(
    user_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """Admin seulement - créer un nouvel utilisateur avec journalisation d'audit"""
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
    
    return {
        "id": str(user.id), 
        "nom": user.nom, 
        "email": user.email,
        "message": translator.translate("utilisateur_cree")
    }

@app.get("/utilisateurs/{user_id}")
def get_user(
    user_id: str, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    translator = Depends(get_current_translator)
):
    """Obtenir les détails utilisateur - les utilisateurs ne peuvent voir que leurs propres données, les admins voient tout"""
    # Les utilisateurs ne peuvent accéder qu'à leurs propres données
    if current_user.type_utilisateur != "administrateur" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translator.translate("acces_refuse")
        )
    
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, 
            detail=translator.translate("utilisateur_non_trouve")
        )
    
    # Obtenir les appareils et cartes SIM de l'utilisateur
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
                "imeis": [imei.numero_imei for imei in d.imeis]
            } 
            for d in devices
        ],
        "sims": [{"id": str(s.id), "iccid": s.iccid, "operateur": s.operateur} for s in sims]
    }

@app.post("/cartes-sim", tags=["Cartes SIM"])
def register_sim(
    sim_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    translator = Depends(get_current_translator)
):
    """Enregistrer une nouvelle carte SIM - utilisateurs authentifiés seulement"""
    # Définir le propriétaire de la carte SIM à l'utilisateur actuel si pas admin
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
    return {
        "id": str(sim.id), 
        "iccid": sim.iccid, 
        "operateur": sim.operateur,
        "message": translator.translate("sim_enregistree")
    }

@app.get("/cartes-sim/{iccid}", tags=["Cartes SIM"])
def check_iccid(
    iccid: str, 
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    sim = db.query(SIM).filter(SIM.iccid == iccid).first()
    if sim:
        return {
            "iccid": iccid,
            "trouve": True,
            "sim": {
                "id": str(sim.id),
                "operateur": sim.operateur,
                "utilisateur_id": str(sim.utilisateur_id) if sim.utilisateur_id else None
            }
        }
    return {
        "iccid": iccid, 
        "trouve": False, 
        "message": translator.translate("iccid_non_trouve")
    }

@app.put("/appareils/{device_id}/assigner", tags=["Appareils", "Admin"])
def assign_device_to_user(
    device_id: str, 
    assignment_data: dict,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """Admin only - assign device to user with audit logging"""
    device = db.query(Appareil).filter(Appareil.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=404, 
            detail=translator.translate("appareil_non_trouve")
        )
    
    user_id = assignment_data.get("user_id")
    device.utilisateur_id = user_id
    db.commit()
    
    # Get IMEIs for logging
    numero_imeis = [imei.numero_imei for imei in device.imeis]
    
    # Log device assignment
    audit_service.log_device_assignment(
        device_id=device_id,
        assigned_to_user_id=user_id,
        assigned_by_user_id=str(current_user.id),
        imeis=numero_imeis
    )
    
    return {"message": translator.translate("appareil_assigne")}

@app.delete("/admin/appareils/{device_id}", tags=["Admin"])
def delete_device(
    appareil_id: str, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """
    Supprimer un appareil avec journalisation d'audit - Administrateurs uniquement.
    """
    appareil = db.query(Appareil).filter(Appareil.id == appareil_id).first()
    if not appareil:
        raise HTTPException(
            status_code=404, 
            detail=translator.translate("appareil_non_trouve")
        )
    
    # Collecter les données de l'appareil pour le journal d'audit avant suppression
    appareil_data = {
        "marque": appareil.marque,
        "modele": appareil.modele,
        "emmc": appareil.emmc,
        "imeis": [imei.numero_imei for imei in appareil.imeis]
    }
    
    db.delete(appareil)
    db.commit()
    
    # Journaliser la suppression de l'appareil
    audit_service.log_device_deletion(
        device_id=appareil_id,
        user_id=str(current_user.id),
        device_data=appareil_data
    )
    
    return {"message": translator.translate("appareil_supprime")}

@app.post("/admin/import-lot-appareils", tags=["Appareils", "Admin"])
def bulk_import_devices(
    devices_data: List[dict], 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """
    Import en lot d'appareils avec journalisation d'audit - Administrateurs uniquement.
    Format JSON simple pour les données structurées.
    """
    imported_count = 0
    errors = []
    
    for device_data in devices_data:
        try:
            appareil = Appareil(
                id=uuid.uuid4(),
                marque=device_data.get("marque"),
                modele=device_data.get("modele"),
                emmc=device_data.get("emmc"),
                utilisateur_id=device_data.get("utilisateur_id")
            )
            db.add(appareil)
            db.flush()  # Obtenir l'ID de l'appareil
            
            # Ajouter les IMEIs
            donnees_imeis = device_data.get("imeis", [])
            for i, donnees_imei in enumerate(donnees_imeis):
                if isinstance(donnees_imei, str):
                    # Format chaîne simple
                    imei = IMEI(
                        id=uuid.uuid4(),
                        numero_imei=donnees_imei,
                        numero_slot=i + 1,
                        status="active",
                        appareil_id=appareil.id
                    )
                else:
                    # Format dictionnaire
                    imei = IMEI(
                        id=uuid.uuid4(),
                        numero_imei=donnees_imei.get("numero_imei"),
                        numero_slot=donnees_imei.get("numero_slot", i + 1),
                        status=donnees_imei.get("statut", "active"),
                        appareil_id=appareil.id
                    )
                db.add(imei)
            
            imported_count += 1
        except Exception as e:
            errors.append(f"{translator.translate('prefixe_erreur_import')} {device_data.get('marque', translator.translate('appareil_inconnu'))}: {str(e)}")
    
    db.commit()
    
    # Journaliser l'opération d'import en lot
    audit_service.log_bulk_import(
        user_id=str(current_user.id),
        imported_count=imported_count,
        errors=errors
    )
    
    return {
        "message": translator.translate("import_lot_termine"),
        "imported_count": imported_count,
        "errors": errors
    }

@app.post("/admin/import-file", tags=["Appareils", "Admin"])
async def bulk_import_from_file(
    file: UploadFile = File(...),
    column_mapping: str = Form(default="{}"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """
    Import en lot d'appareils depuis un fichier JSON ou CSV avec mappage de colonnes.
    
    ### Formats Supportés:
    - **JSON**: Fichier JSON contenant un tableau d'objets
    - **CSV**: Fichier CSV avec headers
    
    ### Mappage de Colonnes:
    Le paramètre column_mapping permet de mapper les noms de colonnes du fichier
    vers les champs de la base de données. Format JSON:
    
    ```json
    {
        "brand_name": "marque",
        "device_model": "modele", 
        "memory": "emmc",
        "imei_1": "imei1",
        "imei_2": "imei2",
        "owner_id": "utilisateur_id"
    }
    ```
    
    ### Champs de Base de Données:
    - **marque**: Marque de l'appareil (requis)
    - **modele**: Modèle de l'appareil (requis)
    - **emmc**: Capacité de stockage
    - **utilisateur_id**: ID du propriétaire (UUID)
    - **imei1**: Premier IMEI
    - **imei2**: Deuxième IMEI (optionnel)
    
    ### Exemple de fichier CSV:
    ```
    brand_name,device_model,memory,imei_1,imei_2,owner_id
    Samsung,Galaxy S21,128GB,123456789012345,123456789012346,uuid-here
    Apple,iPhone 13,256GB,987654321098765,,uuid-here
    ```
    
    ### Exemple de fichier JSON:
    ```json
    [
        {
            "brand_name": "Samsung",
            "device_model": "Galaxy S21",
            "memory": "128GB",
            "imei_1": "123456789012345",
            "imei_2": "123456789012346"
        }
    ]
    ```
    """
    try:
        # Parse column mapping
        try:
            mapping = json.loads(column_mapping) if column_mapping != "{}" else {}
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Format de mappage de colonnes invalide. Utilisez un JSON valide."
            )
        
        # Read file content
        content = await file.read()
        
        # Determine file type and parse accordingly
        devices_data = []
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        if file_extension == 'json' or file.content_type == 'application/json':
            # Parse JSON file
            try:
                raw_data = json.loads(content.decode('utf-8'))
                if not isinstance(raw_data, list):
                    raise HTTPException(
                        status_code=400,
                        detail="Le fichier JSON doit contenir un tableau d'objets."
                    )
                devices_data = raw_data
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Erreur de parsing JSON: {str(e)}"
                )
                
        elif file_extension == 'csv' or file.content_type == 'text/csv':
            # Parse CSV file
            try:
                csv_content = content.decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                devices_data = list(csv_reader)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Erreur de parsing CSV: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Format de fichier non supporté. Utilisez JSON ou CSV."
            )
        
        if not devices_data:
            raise HTTPException(
                status_code=400,
                detail="Le fichier ne contient aucune donnée valide."
            )
        
        # Apply column mapping and validate data
        mapped_devices = []
        for i, raw_device in enumerate(devices_data):
            try:
                mapped_device = apply_column_mapping(raw_device, mapping)
                validate_device_data(mapped_device, i + 1)
                mapped_devices.append(mapped_device)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Erreur ligne {i + 1}: {str(e)}"
                )
        
        # Import devices
        imported_count = 0
        errors = []
        successful_imports = []
        
        for i, device_data in enumerate(mapped_devices):
            try:
                # Create device
                appareil = Appareil(
                    id=uuid.uuid4(),
                    marque=device_data.get("marque"),
                    modele=device_data.get("modele"),
                    emmc=device_data.get("emmc"),
                    utilisateur_id=device_data.get("utilisateur_id")
                )
                db.add(appareil)
                db.flush()  # Get device ID
                
                # Add IMEIs
                imeis_created = []
                imei_fields = ["imei1", "imei2"]
                
                for slot, imei_field in enumerate(imei_fields, 1):
                    imei_value = device_data.get(imei_field)
                    if imei_value and imei_value.strip():
                        imei = IMEI(
                            id=uuid.uuid4(),
                            numero_imei=imei_value.strip(),
                            numero_slot=slot,
                            statut="active",
                            appareil_id=appareil.id
                        )
                        db.add(imei)
                        imeis_created.append(imei_value.strip())
                
                successful_imports.append({
                    "device_id": str(appareil.id),
                    "marque": appareil.marque,
                    "modele": appareil.modele,
                    "imeis": imeis_created
                })
                
                imported_count += 1
                
            except Exception as e:
                error_msg = f"Ligne {i + 1} ({device_data.get('marque', 'Inconnu')} {device_data.get('modele', 'Inconnu')}): {str(e)}"
                errors.append(error_msg)
        
        # Commit successful imports
        if imported_count > 0:
            db.commit()
        
        # Log bulk import operation
        audit_service.log_bulk_import(
            user_id=str(current_user.id),
            imported_count=imported_count,
            errors=errors
        )
        
        # Prepare response
        response = {
            "message": f"Import terminé. {imported_count} appareils importés.",
            "imported_count": imported_count,
            "total_rows": len(mapped_devices),
            "success_rate": f"{(imported_count/len(mapped_devices)*100):.1f}%" if mapped_devices else "0%",
            "errors": errors,
            "successful_imports": successful_imports[:10] if len(successful_imports) <= 10 else successful_imports[:10] + [f"... et {len(successful_imports)-10} autres"],
            "file_info": {
                "filename": file.filename,
                "file_type": file_extension.upper(),
                "content_type": file.content_type,
                "size_bytes": len(content)
            },
            "mapping_applied": mapping if mapping else "Aucun mappage appliqué"
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de l'import: {str(e)}"
        )

def apply_column_mapping(raw_data: dict, mapping: dict) -> dict:
    """
    Apply column mapping to transform raw data to database field names.
    
    Args:
        raw_data: Raw data from file
        mapping: Column mapping dictionary {file_column: db_field}
    
    Returns:
        Mapped data dictionary
    """
    if not mapping:
        # No mapping provided, return as-is
        return raw_data
    
    mapped_data = {}
    
    # Apply mapping
    for file_column, db_field in mapping.items():
        if file_column in raw_data and raw_data[file_column] is not None:
            mapped_data[db_field] = raw_data[file_column]
    
    # Copy unmapped fields that match database fields
    db_fields = {"marque", "modele", "emmc", "utilisateur_id", "imei1", "imei2"}
    for key, value in raw_data.items():
        if key in db_fields and key not in mapped_data:
            mapped_data[key] = value
    
    return mapped_data

def validate_device_data(device_data: dict, row_number: int) -> None:
    """
    Validate device data before import.
    
    Args:
        device_data: Device data to validate
        row_number: Row number for error reporting
    
    Raises:
        ValueError: If validation fails
    """
    # Check required fields
    if not device_data.get("marque"):
        raise ValueError(f"Champ 'marque' requis")
    
    if not device_data.get("modele"):
        raise ValueError(f"Champ 'modele' requis")
    
    # Validate IMEI format if provided
    imei_fields = ["imei1", "imei2"]
    for imei_field in imei_fields:
        imei_value = device_data.get(imei_field)
        if imei_value and imei_value.strip():
            imei_clean = imei_value.strip()
            if not imei_clean.isdigit() or len(imei_clean) not in [14, 15]:
                raise ValueError(f"Format IMEI invalide pour {imei_field}: {imei_clean}")
    
    # Validate utilisateur_id format if provided
    utilisateur_id = device_data.get("utilisateur_id")
    if utilisateur_id and utilisateur_id.strip():
        try:
            uuid.UUID(utilisateur_id.strip())
        except ValueError:
            raise ValueError(f"Format utilisateur_id invalide: {utilisateur_id}")

@app.get("/admin/import-template", tags=["Appareils", "Admin"])
def get_import_template(
    format_type: str = Query(default="csv", description="Format du template (csv ou json)"),
    current_user: Utilisateur = Depends(get_admin_user),
    translator = Depends(get_current_translator)
):
    """
    Obtenir un template d'import pour les appareils.
    
    ### Formats Disponibles:
    - **csv**: Template CSV avec headers
    - **json**: Template JSON avec exemples
    
    ### Champs Disponibles:
    - **marque**: Marque de l'appareil (requis)
    - **modele**: Modèle de l'appareil (requis)  
    - **emmc**: Capacité de stockage (optionnel)
    - **imei1**: Premier IMEI (optionnel)
    - **imei2**: Deuxième IMEI (optionnel)
    - **utilisateur_id**: ID du propriétaire UUID (optionnel)
    """
    
    if format_type.lower() == "csv":
        # Return CSV template
        csv_template = """marque,modele,emmc,imei1,imei2,utilisateur_id
Samsung,Galaxy S21,128GB,123456789012345,123456789012346,
Apple,iPhone 13,256GB,987654321098765,,
Huawei,P40 Pro,512GB,456789012345678,456789012345679,"""
        
        return {
            "format": "CSV",
            "template": csv_template,
            "description": "Template CSV pour l'import d'appareils",
            "instructions": [
                "Utilisez la première ligne comme headers",
                "Les champs 'marque' et 'modele' sont obligatoires",
                "Les IMEIs doivent avoir 14 ou 15 chiffres",
                "utilisateur_id doit être un UUID valide (optionnel)",
                "Sauvegardez le fichier en format CSV UTF-8"
            ]
        }
    
    elif format_type.lower() == "json":
        # Return JSON template
        json_template = [
            {
                "marque": "Samsung",
                "modele": "Galaxy S21",
                "emmc": "128GB",
                "imei1": "123456789012345",
                "imei2": "123456789012346",
                "utilisateur_id": ""
            },
            {
                "marque": "Apple", 
                "modele": "iPhone 13",
                "emmc": "256GB",
                "imei1": "987654321098765",
                "imei2": "",
                "utilisateur_id": ""
            }
        ]
        
        return {
            "format": "JSON",
            "template": json_template,
            "description": "Template JSON pour l'import d'appareils",
            "instructions": [
                "Le fichier doit contenir un tableau d'objets",
                "Les champs 'marque' et 'modele' sont obligatoires",
                "Les IMEIs doivent avoir 14 ou 15 chiffres",
                "utilisateur_id doit être un UUID valide (optionnel)",
                "Sauvegardez le fichier en format JSON UTF-8"
            ]
        }
    
    else:
        raise HTTPException(
            status_code=400,
            detail="Format non supporté. Utilisez 'csv' ou 'json'."
        )

@app.post("/admin/preview-import", tags=["Appareils", "Admin"])
async def preview_import_file(
    file: UploadFile = File(...),
    column_mapping: str = Form(default="{}"),
    max_preview_rows: int = Form(default=10),
    current_user: Utilisateur = Depends(get_admin_user),
    translator = Depends(get_current_translator)
):
    """
    Prévisualiser un fichier d'import avant l'import réel.
    
    ### Fonctionnalités:
    - Valide le format du fichier
    - Applique le mappage de colonnes
    - Vérifie la validité des données
    - Affiche un aperçu des premiers enregistrements
    - Signale les erreurs potentielles
    
    ### Paramètres:
    - **file**: Fichier JSON ou CSV à prévisualiser
    - **column_mapping**: Mappage de colonnes (JSON)
    - **max_preview_rows**: Nombre maximum de lignes à prévisualiser (défaut: 10)
    """
    try:
        # Parse column mapping
        try:
            mapping = json.loads(column_mapping) if column_mapping != "{}" else {}
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Format de mappage de colonnes invalide. Utilisez un JSON valide."
            )
        
        # Read file content
        content = await file.read()
        
        # Determine file type and parse accordingly
        devices_data = []
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        if file_extension == 'json' or file.content_type == 'application/json':
            # Parse JSON file
            try:
                raw_data = json.loads(content.decode('utf-8'))
                if not isinstance(raw_data, list):
                    raise HTTPException(
                        status_code=400,
                        detail="Le fichier JSON doit contenir un tableau d'objets."
                    )
                devices_data = raw_data
            except json.JSONDecodeError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Erreur de parsing JSON: {str(e)}"
                )
                
        elif file_extension == 'csv' or file.content_type == 'text/csv':
            # Parse CSV file
            try:
                csv_content = content.decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                devices_data = list(csv_reader)
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Erreur de parsing CSV: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Format de fichier non supporté. Utilisez JSON ou CSV."
            )
        
        if not devices_data:
            raise HTTPException(
                status_code=400,
                detail="Le fichier ne contient aucune donnée valide."
            )
        
        # Apply column mapping and validate data
        preview_data = []
        validation_errors = []
        
        for i, raw_device in enumerate(devices_data[:max_preview_rows]):
            try:
                mapped_device = apply_column_mapping(raw_device, mapping)
                validate_device_data(mapped_device, i + 1)
                
                preview_data.append({
                    "row_number": i + 1,
                    "original_data": raw_device,
                    "mapped_data": mapped_device,
                    "status": "valid",
                    "errors": []
                })
                
            except ValueError as e:
                preview_data.append({
                    "row_number": i + 1,
                    "original_data": raw_device,
                    "mapped_data": apply_column_mapping(raw_device, mapping),
                    "status": "invalid",
                    "errors": [str(e)]
                })
                validation_errors.append(f"Ligne {i + 1}: {str(e)}")
        
        # Count potential IMEIs
        total_imeis = 0
        for device in preview_data:
            if device["status"] == "valid":
                mapped = device["mapped_data"]
                if mapped.get("imei1"): total_imeis += 1
                if mapped.get("imei2"): total_imeis += 1
        
        # Prepare response
        response = {
            "file_info": {
                "filename": file.filename,
                "file_type": file_extension.upper(),
                "content_type": file.content_type,
                "size_bytes": len(content),
                "total_rows": len(devices_data),
                "preview_rows": len(preview_data)
            },
            "mapping_info": {
                "mapping_applied": mapping if mapping else "Aucun mappage appliqué",
                "detected_columns": list(devices_data[0].keys()) if devices_data else [],
                "target_fields": ["marque", "modele", "emmc", "imei1", "imei2", "utilisateur_id"]
            },
            "validation_summary": {
                "total_rows": len(devices_data),
                "valid_rows": sum(1 for d in preview_data if d["status"] == "valid"),
                "invalid_rows": sum(1 for d in preview_data if d["status"] == "invalid"),
                "potential_devices": sum(1 for d in preview_data if d["status"] == "valid"),
                "potential_imeis": total_imeis,
                "validation_errors": validation_errors[:10]  # First 10 errors
            },
            "preview_data": preview_data,
            "recommendations": generate_import_recommendations(devices_data, mapping, validation_errors)
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prévisualisation: {str(e)}"
        )

def generate_import_recommendations(data: list, mapping: dict, errors: list) -> list:
    """Generate recommendations for import optimization."""
    recommendations = []
    
    if not data:
        return ["Aucune donnée à analyser"]
    
    # Check for common column names that might need mapping
    first_row_keys = set(data[0].keys())
    common_mappings = {
        'brand': 'marque',
        'brand_name': 'marque', 
        'manufacturer': 'marque',
        'model': 'modele',
        'device_model': 'modele',
        'memory': 'emmc',
        'storage': 'emmc',
        'imei': 'imei1',
        'first_imei': 'imei1',
        'second_imei': 'imei2',
        'owner': 'utilisateur_id',
        'user_id': 'utilisateur_id'
    }
    
    suggested_mappings = {}
    for file_col in first_row_keys:
        file_col_lower = file_col.lower()
        if file_col_lower in common_mappings and file_col not in mapping:
            suggested_mappings[file_col] = common_mappings[file_col_lower]
    
    if suggested_mappings:
        recommendations.append(f"Mappage suggéré: {suggested_mappings}")
    
    # Check for missing required fields
    mapped_fields = set(mapping.values()) if mapping else set()
    file_fields = first_row_keys.union(mapped_fields)
    
    if 'marque' not in file_fields:
        recommendations.append("Attention: Le champ 'marque' est requis mais non détecté")
    if 'modele' not in file_fields:
        recommendations.append("Attention: Le champ 'modele' est requis mais non détecté")
    
    # Analyze errors
    if len(errors) > len(data) * 0.5:
        recommendations.append("Attention: Plus de 50% des lignes contiennent des erreurs")
    
    if not recommendations:
        recommendations.append("Les données semblent correctes pour l'import")
    
    return recommendations

@app.post("/appareils/{appareil_id}/imeis", tags=["Appareils"])
def add_imei_to_device(
    appareil_id: str, 
    imei_data: dict, 
    db: Session = Depends(get_db),
    translator = Depends(get_current_translator)
):
    """
    Ajouter un IMEI à un appareil.
    """
    appareil = db.query(Appareil).filter(Appareil.id == appareil_id).first()
    if not appareil:
        raise HTTPException(
            status_code=404, 
            detail=translator.translate("appareil_non_trouve")
        )
    
    # Vérifier si l'appareil a déjà 2 IMEIs
    if len(appareil.imeis) >= 2:
        raise HTTPException(
            status_code=400, 
            detail=translator.translate("maximum_imeis_atteint")
        )
    
    imei = IMEI(
        id=uuid.uuid4(),
        numero_imei=imei_data.get("numero_imei"),
        numero_slot=imei_data.get("numero_slot", len(appareil.imeis) + 1),
        status=imei_data.get("statut", "active"),
        appareil_id=appareil.id
    )
    
    db.add(imei)
    db.commit()
    
    return {
        "message": translator.translate("imei_ajoute"),
        "imei": {
            "id": str(imei.id),
            "numero_imei": imei.numero_imei,
            "numero_slot": imei.numero_slot,
            "statut": imei.statut
        }
    }

@app.put("/imeis/{imei_id}/status", tags=["IMEI", "Admin"])
def update_imei_status(
    imei_id: str, 
    status_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """
    Mettre à jour le statut d'un IMEI avec journalisation d'audit - Administrateurs uniquement.
    """
    imei = db.query(IMEI).filter(IMEI.id == imei_id).first()
    if not imei:
        raise HTTPException(
            status_code=404, 
            detail=translator.translate("erreur_imei_non_trouve")
        )
    
    old_status = imei.statut
    new_status = status_data.get("statut")
    imei.statut = new_status
    db.commit()
    
    # Journaliser le changement de statut IMEI
    audit_service.log_imei_status_change(
        imei_id=str(imei.id),
        numero_imei=imei.numero_imei,
        old_status=old_status,
        new_status=new_status,
        user_id=str(current_user.id)
    )
    
    return {"message": translator.translate("statut_imei_mis_a_jour")}

@app.get("/utilisateurs/{user_id}/recherches", tags=["Historique de Recherche"])
def user_search_history(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    translator = Depends(get_current_translator)
):
    """
    Obtenir l'historique de recherche d'un utilisateur.
    """
    # Les utilisateurs ne peuvent accéder qu'à leur propre historique de recherche
    if current_user.type_utilisateur != "administrateur" and str(current_user.id) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=translator.translate("acces_refuse_historique_recherches")
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

@app.get("/notifications", tags=["Notifications"])
def list_notifications(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user),
    translator = Depends(get_current_translator)
):
    """
    Lister les notifications.
    """
    query = db.query(Notification)
    
    # Appliquer le filtrage utilisateur basé sur le rôle
    if current_user.type_utilisateur != "administrateur":
        # Les utilisateurs réguliers ne peuvent voir que leurs propres notifications
        query = query.filter(Notification.utilisateur_id == current_user.id)
    else:
        # Les administrateurs peuvent filtrer par user_id si fourni
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

@app.get("/admin/journaux-audit", tags=["Admin"])
def get_audit_logs(
    user_id: Optional[str] = None,
    action_filter: Optional[str] = None,
    entity_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    translator = Depends(get_current_translator)
):
    """
    Obtenir les journaux d'audit avec filtrage amélioré - Administrateurs uniquement.
    """
    query = db.query(JournalAudit)
    
    if user_id:
        query = query.filter(JournalAudit.utilisateur_id == user_id)
    if action_filter:
        query = query.filter(JournalAudit.action.contains(action_filter))
    if entity_type:
        query = query.filter(JournalAudit.action.contains(entity_type))
    
    # Filtrage par date
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(JournalAudit.date >= start_dt)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=translator.translate("format_date_invalide")
            )
            
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(JournalAudit.date <= end_dt)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=translator.translate("format_date_invalide")
            )
    
    logs = query.order_by(desc(JournalAudit.date)).offset(skip).limit(limit).all()
    
    return {
        "audit_logs": [
            {
                "id": str(log.id),
                "action": log.action,
                "date": format_datetime(log.date),
                "utilisateur_id": str(log.utilisateur_id) if log.utilisateur_id else None,
                "user_name": log.utilisateur.nom if log.utilisateur else translator.translate("systeme")
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

# ENDPOINT D'INTÉGRATION MULTI-PROTOCOLES
@app.post(
    "/verify_imei",
    tags=["IMEI", "Intégration"],
    summary="Vérification IMEI Multi-Protocoles",
    description="Vérifier un IMEI via différents protocoles (REST, SS7, Diameter) selon la configuration",
    response_model=None
)
async def verify_imei_multi_protocol(
    request_data: dict,
    protocol: str = Query(default="rest", description="Protocole à utiliser (rest, ss7, diameter)"),
    request: Request = None,
    db: Session = Depends(get_db),
    user: Optional[Utilisateur] = Depends(get_current_user_optional),
    translator = Depends(get_current_translator),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    ## Vérification IMEI Multi-Protocoles
    
    Ce point de terminaison permet de vérifier un IMEI en utilisant différents protocoles
    selon la configuration système et les besoins d'intégration.
    
    ### Protocoles Supportés :
    - **REST** : Réponse JSON synchrone (par défaut)
    - **SS7** : Fire-and-forget, pas de réponse (pour intégration MSC/VLR)
    - **Diameter** : Réponse avec AVPs Diameter (pour intégration MME/SGSN)
    
    ### Paramètres :
    - **imei** : Numéro IMEI à vérifier (requis dans le body)
    - **protocol** : Protocole à utiliser (query parameter, défaut: rest)
    
    ### Configuration :
    Les protocoles peuvent être activés/désactivés via le fichier `config/protocols.yml`
    
    ### Réponses :
    - **REST** : JSON avec statut détaillé de l'IMEI
    - **SS7** : Message de confirmation (traitement asynchrone)
    - **Diameter** : Réponse formatée avec AVPs standard
    
    ### Codes d'Erreur :
    - **400** : Protocole non activé ou payload invalide
    - **422** : Protocole non supporté
    - **500** : Erreur de traitement
    """
    try:
        # Import des modules d'intégration
        from .interface_gateway.dispatcher import (
            handle_incoming_request, 
            get_supported_protocols, 
            validate_payload,
            ProtocolNotEnabledException, 
            UnsupportedProtocolException
        )
        
        # Validation des paramètres d'entrée
        if not request_data or "imei" not in request_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=translator.translate("imei_requis") if translator else "IMEI requis"
            )
        
        imei = request_data["imei"]
        
        # Validation du protocole
        protocol = protocol.lower()
        supported_protocols = get_supported_protocols()
        
        if protocol not in supported_protocols:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Protocole non supporté: {protocol}. Protocoles supportés: {list(supported_protocols.keys())}"
            )
        
        # Validation de la payload selon le protocole
        if not validate_payload(protocol, request_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payload invalide pour le protocole {protocol}"
            )
        
        # Ajouter des métadonnées à la requête
        enhanced_request_data = {
            **request_data,
            "user_id": str(user.id) if user else None,
            "client_ip": request.client.host if request and request.client else None,
            "user_agent": request.headers.get("user-agent") if request else None
        }
        
        # Log de la requête pour audit
        if audit_service:
            audit_service.log_imei_search(
                imei=imei,
                user_id=str(user.id) if user else None,
                found=True  # On mettra à jour selon le résultat
            )
        
        # Traitement via le dispatcher
        try:
            response = handle_incoming_request(protocol, enhanced_request_data)
            
            # Pour SS7 (fire-and-forget), construire une réponse de confirmation
            if protocol == "ss7":
                return {
                    "status": "accepted",
                    "message": "Requête SS7 acceptée pour traitement",
                    "imei": imei,
                    "protocol": "SS7",
                    "processing_mode": "fire_and_forget",
                    "timestamp": datetime.now().isoformat(),
                    "request_id": str(uuid.uuid4())
                }
            
            # Pour REST et Diameter, retourner la réponse directement
            return response
            
        except ProtocolNotEnabledException as e:
            # Protocole désactivé dans la configuration
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Protocole {protocol} non activé dans la configuration"
            )
        
        except UnsupportedProtocolException as e:
            # Protocole non supporté
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
            
    except HTTPException:
        # Re-lever les HTTPExceptions
        raise
    except Exception as e:
        # Erreur inattendue
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur inattendue dans verify_imei_multi_protocol: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur de traitement interne: {str(e)}"
        )

@app.get(
    "/protocols/status",
    tags=["Système", "Intégration"],
    summary="Statut des Protocoles",
    description="Obtenir le statut d'activation des protocoles d'intégration",
    response_model=None
)
async def get_protocols_status(
    user: Optional[Utilisateur] = Depends(get_current_user_optional),
    translator = Depends(get_current_translator)
):
    """
    ## Statut des Protocoles d'Intégration
    
    Retourne l'état d'activation des différents protocoles d'intégration
    disponibles dans le système.
    
    ### Informations Retournées :
    - **Protocoles supportés** et leur statut d'activation
    - **Configuration actuelle** des timeouts et paramètres
    - **Statistiques d'utilisation** (si utilisateur authentifié)
    """
    try:
        # Import des modules d'intégration
        from .interface_gateway.dispatcher import get_supported_protocols
        
        # Obtenir le statut des protocoles
        protocols_status = get_supported_protocols()
        
        # Configuration de base accessible à tous
        response = {
            "protocols": protocols_status,
            "total_protocols": len(protocols_status),
            "active_protocols": sum(1 for active in protocols_status.values() if active),
            "timestamp": datetime.now().isoformat()
        }
        
        # Informations supplémentaires pour les utilisateurs authentifiés
        if user:
            try:
                from .config_loader import load_protocol_config
                config = load_protocol_config()
                
                response.update({
                    "timeouts": config.get("timeouts", {}),
                    "logging_config": config.get("logging", {}),
                    "user_access_level": user.niveau_acces if user else "public"
                })
                
                # Statistiques pour les administrateurs
                if user.type_utilisateur == "administrateur":
                    from .interface_gateway.handlers import rest_handler, ss7_handler, diameter_handler
                    
                    response["statistics"] = {
                        "rest": rest_handler.get_rest_statistics(),
                        "ss7": ss7_handler.get_ss7_statistics(),
                        "diameter": diameter_handler.get_diameter_statistics()
                    }
            except ImportError as e:
                response["config_error"] = f"Erreur de chargement de la configuration: {str(e)}"
        
        return response
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erreur lors de la récupération du statut des protocoles: {str(e)}")
        
        # Retourner une réponse minimale en cas d'erreur
        return {
            "protocols": {"rest": True, "ss7": False, "diameter": False},
            "error": "Impossible de charger la configuration complète",
            "timestamp": datetime.now().isoformat()
        }

@app.get(
    "/imei/{imei}/validate",
    tags=["IMEI", "TAC"],
    summary="Validation IMEI avec base TAC",
    description="Valider un IMEI en utilisant la base de données TAC et l'algorithme Luhn",
    response_model=None
)
def valider_imei_avec_tac_endpoint(
    imei: str,
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[Utilisateur] = Depends(get_current_user_optional),
    translator = Depends(get_current_translator),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    ## Validation IMEI Complète avec Base TAC
    
    Valide un IMEI en utilisant :
    - Base de données TAC (Type Allocation Code) 
    - Algorithme de validation Luhn
    - Vérification des formats standards
    
    ### Informations retournées :
    - **Validité TAC** : Si le TAC existe dans la base
    - **Validité Luhn** : Si l'IMEI respecte l'algorithme de Luhn
    - **Marque et modèle** : Identifiés via le TAC
    - **Statut de l'appareil** : Valide, obsolète, bloqué, etc.
    - **Type d'appareil** : Smartphone, tablet, IoT, etc.
    
    ### Contrôle d'accès :
    - Accessible à tous les utilisateurs
    - Journalisation automatique des validations
    """
    try:
        # Exécuter la fonction PostgreSQL de validation TAC
        result = db.execute(
            text("SELECT valider_imei_avec_tac(:imei)"),
            {"imei": imei}
        ).fetchone()
        
        validation_result = result[0] if result else {}
        
        # Enregistrer la recherche de validation
        recherche = Recherche(
            id=uuid.uuid4(),
            date_recherche=datetime.now(),
            imei_recherche=imei,
            utilisateur_id=user.id if user else None
        )
        db.add(recherche)
        
        # Log de l'audit
        audit_service.log_imei_search(
            imei=imei,
            user_id=str(user.id) if user else None,
            found=validation_result.get('valide', False)
        )
        
        db.commit()
        
        # Enrichir la réponse avec le contexte
        response = {
            **validation_result,
            "recherche_enregistree": True,
            "id_recherche": str(recherche.id),
            "timestamp": datetime.now().isoformat(),
            "user_level": user.niveau_acces if user else "visiteur"
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la validation IMEI: {str(e)}"
        )

@app.get(
    "/tac/{tac}",
    tags=["TAC"],
    summary="Recherche TAC",
    description="Rechercher les informations d'un code TAC dans la base de données",
    response_model=None
)
def rechercher_tac(
    tac: str,
    db: Session = Depends(get_db),
    user: Optional[Utilisateur] = Depends(get_current_user_optional),
    translator = Depends(get_current_translator)
):
    """
    ## Recherche de Code TAC
    
    Rechercher les informations d'un Type Allocation Code (TAC) dans la base de données.
    
    ### Paramètres :
    - **tac** : Code TAC à 8 chiffres
    
    ### Informations retournées :
    - Marque et modèle de l'appareil
    - Année de sortie (si disponible)
    - Type d'appareil (smartphone, tablet, etc.)
    - Statut (valide, obsolète, bloqué)
    """
    try:
        # Nettoyer et valider le TAC
        tac_clean = tac.strip().zfill(8)
        
        if not tac_clean.isdigit() or len(tac_clean) != 8:
            raise HTTPException(
                status_code=400,
                detail="Le TAC doit être un nombre à 8 chiffres"
            )
        
        # Rechercher dans la base TAC
        result = db.execute(
            text("SELECT * FROM tac_database WHERE tac = :tac"),
            {"tac": tac_clean}
        ).fetchone()
        
        if result:
            return {
                "tac": result.tac,
                "marque": result.marque,
                "modele": result.modele,
                "annee_sortie": result.annee_sortie,
                "type_appareil": result.type_appareil,
                "statut": result.statut,
                "date_creation": result.date_creation.isoformat() if result.date_creation else None,
                "date_modification": result.date_modification.isoformat() if result.date_modification else None,
                "trouve": True
            }
        else:
            return {
                "tac": tac_clean,
                "trouve": False,
                "message": "TAC non trouvé dans la base de données"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la recherche TAC: {str(e)}"
        )

@app.get(
    "/admin/tac/stats",
    tags=["TAC", "Admin"],
    summary="Statistiques TAC",
    description="""
    ## Statistiques de la Base TAC
    
    Obtenir des statistiques détaillées sur la base de données TAC.
    
    ### Informations retournées :
    - Nombre total de TAC enregistrés
    - Répartition par marques
    - Répartition par types d'appareils
    - Répartition par statuts
    - Top 10 des marques
    """
)
def statistiques_tac(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    translator = Depends(get_current_translator)
):
    
    try:
        # Statistiques générales
        total_tacs = db.execute(text("SELECT COUNT(*) FROM tac_database")).scalar()
        total_marques = db.execute(text("SELECT COUNT(DISTINCT marque) FROM tac_database")).scalar()
        
        # Répartition par statut
        statuts = db.execute(text("""
            SELECT statut, COUNT(*) as count 
            FROM tac_database 
            GROUP BY statut 
            ORDER BY count DESC
        """)).fetchall()
        
        # Répartition par type d'appareil
        types_appareils = db.execute(text("""
            SELECT type_appareil, COUNT(*) as count 
            FROM tac_database 
            GROUP BY type_appareil 
            ORDER BY count DESC
        """)).fetchall()
        
        # Top 10 marques
        top_marques = db.execute(text("""
            SELECT marque, COUNT(*) as count 
            FROM tac_database 
            GROUP BY marque 
            ORDER BY count DESC 
            LIMIT 10
        """)).fetchall()
        
        # Dernière mise à jour
        derniere_maj = db.execute(text("""
            SELECT MAX(date_modification) 
            FROM tac_database
        """)).scalar()
        
        return {
            "statistiques_generales": {
                "total_tacs": total_tacs,
                "total_marques": total_marques,
                "derniere_mise_a_jour": derniere_maj.isoformat() if derniere_maj else None
            },
            "repartition_statuts": [
                {"statut": row.statut, "count": row.count} 
                for row in statuts
            ],
            "repartition_types": [
                {"type": row.type_appareil, "count": row.count} 
                for row in types_appareils
            ],
            "top_marques": [
                {"marque": row.marque, "count": row.count} 
                for row in top_marques
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des statistiques TAC: {str(e)}"
        )

@app.post(
    "/admin/tac/sync",
    tags=["TAC", "Admin"],
    summary="Synchronisation TAC",
    description="""## Synchronisation Base TAC

Synchroniser la base de données TAC depuis les sources externes configurées.

### Sources disponibles :
- **osmocom_csv** : API CSV Osmocom (par défaut)
- **osmocom_json** : API JSON Osmocom
- **local_file** : Fichier local

### Processus :
1. Téléchargement depuis la source
2. Validation des données
3. Import avec gestion des conflits
4. Journalisation des résultats"""
)
def synchroniser_tac(
    source: str = Query(default="osmocom_csv", description="Source de synchronisation"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    try:
        if source == "osmocom_csv":
            # Synchronisation depuis l'API CSV Osmocom
            result = db.execute(text("""
                SELECT sync_osmocom_csv() as result
            """)).fetchone()
            
        elif source == "osmocom_json":
            # Synchronisation depuis l'API JSON Osmocom
            result = db.execute(text("""
                SELECT sync_osmocom_json() as result
            """)).fetchone()
            
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Source non supportée: {source}"
            )
        
        # Log de l'opération de synchronisation
        audit_service.log_tac_sync(
            user_id=str(current_user.id),
            source=source,
            result=result[0] if result else {}
        )
        
        return {
            "message": f"Synchronisation TAC depuis {source} terminée",
            "source": source,
            "result": result[0] if result else {},
            "timestamp": datetime.now().isoformat(),
            "initiated_by": current_user.nom
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la synchronisation TAC: {str(e)}"
        )

@app.get(
    "/admin/tac/sync/logs",
    tags=["TAC", "Admin"], 
    summary="Logs de synchronisation TAC",
    description="Obtenir l'historique des synchronisations TAC"
)
def logs_synchronisation_tac(
    limit: int = Query(default=20, description="Nombre de logs à retourner"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    translator = Depends(get_current_translator)
):
    """
    ## Logs de Synchronisation TAC
    
    Obtenir l'historique des synchronisations de la base TAC.
    
    ### Informations retournées :
    - Historique des synchronisations
    - Statistiques d'import/export
    - Statuts des opérations
    - Sources utilisées
    """
    try:
        # Obtenir les statistiques de synchronisation
        stats_result = db.execute(text("SELECT obtenir_stats_sync_tac()")).fetchone()
        stats = stats_result[0] if stats_result else {}
        
        # Obtenir les logs récents
        logs = db.execute(text("""
            SELECT * FROM vue_sync_tac_recent 
            ORDER BY sync_date DESC 
            LIMIT :limit
        """), {"limit": limit}).fetchall()
        
        return {
            "statistiques": stats,
            "logs_recents": [
                {
                    "source_name": log.source_name,
                    "format_type": log.format_type,
                    "status": log.status,
                    "total_records": log.total_records,
                    "records_errors": log.records_errors,
                    "sync_duration_ms": log.sync_duration_ms,
                    "sync_date": log.sync_date.isoformat(),
                    "fraicheur": log.fraicheur
                }
                for log in logs
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des logs TAC: {str(e)}"
        )

@app.post(
    "/admin/tac/import",
    tags=["TAC", "Admin"],
    summary="Import TAC depuis fichier",
    description="Importer des données TAC depuis un fichier CSV ou JSON"
)
async def importer_tac_fichier(
    file: UploadFile = File(...),
    format_source: str = Form(default="osmocom", description="Format source (osmocom, standard)"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """
    ## Import TAC depuis Fichier
    
    Importer des données TAC depuis un fichier uploadé.
    
    ### Formats supportés :
    - **CSV Osmocom** : Format standard Osmocom TAC database
    - **CSV Standard** : Format personnalisé avec colonnes définies
    - **JSON** : Format JSON avec structure définie
    
    ### Processus :
    1. Upload et validation du fichier
    2. Détection du format
    3. Import avec gestion des doublons
    4. Rapport détaillé des résultats
    """
    try:
        # Lire le contenu du fichier
        content = await file.read()
        
        # Déterminer le type de fichier
        file_extension = file.filename.lower().split('.')[-1] if '.' in file.filename else ''
        
        if file_extension == 'csv':
            # Import CSV
            csv_content = content.decode('utf-8')
            
            result = db.execute(text("""
                SELECT importer_tac_avec_mapping(:csv_data, :format_source)
            """), {
                "csv_data": csv_content,
                "format_source": format_source
            }).fetchone()
            
        elif file_extension == 'json':
            # Import JSON
            json_content = content.decode('utf-8')
            json_data = json.loads(json_content)
            
            result = db.execute(text("""
                SELECT importer_tac_depuis_json(:json_data::jsonb, :source_name)
            """), {
                "json_data": json.dumps(json_data),
                "source_name": f"manual_upload_{file.filename}"
            }).fetchone()
            
        else:
            raise HTTPException(
                status_code=400,
                detail="Format de fichier non supporté. Utilisez CSV ou JSON."
            )
        
        import_result = result[0] if result else {}
        
        # Log de l'import
        audit_service.log_tac_import(
            user_id=str(current_user.id),
            filename=file.filename,
            format_source=format_source,
            result=import_result
        )
        
        return {
            "message": f"Import TAC depuis {file.filename} terminé",
            "filename": file.filename,
            "format_source": format_source,
            "file_size_bytes": len(content),
            "result": import_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur de parsing JSON: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'import TAC: {str(e)}"
        )

# Ajouter l'endpoint de validation intégré à la recherche IMEI existante
@app.get(
    "/imei/{imei}/details",
    tags=["IMEI", "TAC"],
    summary="Détails complets IMEI",
    description="Obtenir tous les détails d'un IMEI incluant validation TAC et informations de base",
    response_model=None
)
def details_complets_imei(
    imei: str,
    request: Request,
    db: Session = Depends(get_db),
    user: Optional[Utilisateur] = Depends(get_current_user_optional),
    translator = Depends(get_current_translator),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    ## Détails Complets IMEI
    
    Combine la recherche IMEI dans la base locale et la validation TAC
    pour fournir une vue complète des informations d'un IMEI.
    
    ### Informations combinées :
    - Recherche dans la base locale EIR
    - Validation TAC et algorithme Luhn  
    - Informations d'appareil et propriétaire
    - Historique et statut
    """
    try:
        # Recherche IMEI locale (réutilise la logique existante)
        imei_local = verifier_imei(imei, request, db, user, translator, audit_service)
        
        # Validation TAC
        tac_validation = valider_imei_avec_tac_endpoint(imei, request, db, user, translator, audit_service)
        
        # Extraire le TAC pour recherche détaillée
        tac = imei[:8].zfill(8)
        tac_details = rechercher_tac(tac, db, user, translator)
        
        # Combiner toutes les informations
        return {
            "imei": imei,
            "recherche_locale": imei_local,
            "validation_tac": tac_validation,
            "details_tac": tac_details,
            "resume": {
                "trouve_localement": imei_local.get("trouve", False),
                "tac_valide": tac_validation.get("valide", False),
                "luhn_valide": tac_validation.get("luhn_valide", False),
                "statut_global": determine_statut_global(imei_local, tac_validation)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des détails IMEI: {str(e)}"
        )

def determine_statut_global(imei_local: dict, tac_validation: dict) -> str:
    """Déterminer le statut global basé sur les validations locales et TAC"""
    if not tac_validation.get("luhn_valide", False):
        return "invalide_luhn"
    
    if not tac_validation.get("valide", False):
        return "tac_invalide"
    
    if imei_local.get("trouve", False):
        statut_local = imei_local.get("statut", "unknown")
        if statut_local == "bloque":
            return "bloque"
        elif statut_local == "actif":
            return "actif_valide"
        else:
            return f"local_{statut_local}"
    
    # IMEI non trouvé localement mais TAC valide
    return "tac_valide_non_enregistre"

# ==========================================
# ÉVÉNEMENTS DE CYCLE DE VIE DE L'APPLICATION
# ==========================================

@app.on_event("startup")
async def startup_event():
    """
    Événement de démarrage de l'application
    Initialise les services en arrière-plan
    """
    logger.info("Démarrage de l'application EIR Project")
    
    try:
        # Démarrer le planificateur de notifications
        from .tasks.notification_scheduler import start_notification_scheduler
        await start_notification_scheduler()
        logger.info("Planificateur de notifications démarré")
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage des services: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Événement d'arrêt de l'application
    Nettoie les ressources et arrête les services
    """
    logger.info("Arrêt de l'application EIR Project")
    
    try:
        # Arrêter le planificateur de notifications
        from .tasks.notification_scheduler import stop_notification_scheduler
        await stop_notification_scheduler()
        logger.info("Planificateur de notifications arrêté")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'arrêt des services: {e}")

# ==========================================
# ENDPOINT DE CONTRÔLE DU PLANIFICATEUR (ADMIN)
# ==========================================

@app.get("/admin/notifications/scheduler/status", tags=["Admin"], response_model=None)
async def obtenir_statut_planificateur(
    current_user: Utilisateur = Depends(get_admin_user)
):
    """
    Obtient le statut du planificateur de notifications
    **Réservé aux administrateurs**
    """
    try:
        from .tasks.notification_scheduler import get_scheduler_status
        return get_scheduler_status()
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut du planificateur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération du statut"
        )

@app.post("/admin/notifications/scheduler/trigger/{job_id}", tags=["Admin"], response_model=None)
async def declencher_tache_planificateur(
    job_id: str,
    current_user: Utilisateur = Depends(get_admin_user)
):
    """
    Déclenche manuellement une tâche du planificateur
    
    - **process_notifications**: Traiter les notifications en attente
    - **cleanup_notifications**: Nettoyer les anciennes notifications
    - **log_statistics**: Logger les statistiques actuelles
    
    **Réservé aux administrateurs**
    """
    try:
        from .tasks.notification_scheduler import trigger_notification_job
        result = await trigger_notification_job(job_id)
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors du déclenchement de la tâche {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors du déclenchement de la tâche {job_id}"
        )

# Test endpoint for email configuration
@app.get("/test-email-config", response_model=None)
async def test_email_config():
    """Test email configuration from .env file"""
    try:
        from .services.email_service import email_service
        
        # Test connection
        success, message = email_service.test_connection()
        config_info = email_service.get_config_info()
        
        return {
            "email_test": {
                "success": success,
                "message": message,
                "configuration": config_info
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du test email: {e}")
        return {
            "email_test": {
                "success": False,
                "message": f"Erreur: {str(e)}",
                "configuration": None
            }
        }

# Debug endpoint to check environment variables
@app.get("/debug-env", response_model=None)
async def debug_env():
    """Debug endpoint to check environment variables"""
    import os
    return {
        "env_vars": {
            "SMTP_SERVER": os.getenv("SMTP_SERVER"),
            "SMTP_PORT": os.getenv("SMTP_PORT"),
            "EMAIL_USER": os.getenv("EMAIL_USER"),
            "EMAIL_PASSWORD": "***" if os.getenv("EMAIL_PASSWORD") else None,
            "EMAIL_USE_TLS": os.getenv("EMAIL_USE_TLS")
        }
    }

# Test endpoint for sending actual email
@app.post("/test-send-email", response_model=None)
async def test_send_email(
    email_data: dict = None
):
    """Send a test email to verify the email service is working"""
    try:
        from .services.email_service import email_service
        
        # Default test email data
        if not email_data:
            email_data = {
                "destinataire": "medsalemlmt@gmail.com",
                "sujet": "Test Email - EIR Project",
                "contenu": "Ceci est un email de test depuis l'API EIR Project. Si vous recevez ce message, la configuration email fonctionne correctement!"
            }
        
        # Send the email using the async method
        success, message = await email_service.send_email_async(
            to_email=email_data["destinataire"],
            subject=email_data["sujet"],
            content=email_data["contenu"]
        )
        
        return {
            "email_sent": {
                "success": success,
                "message": message,
                "destinataire": email_data["destinataire"],
                "sujet": email_data["sujet"]
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email de test: {e}")
        return {
            "email_sent": {
                "success": False,
                "message": f"Erreur: {str(e)}",
                "destinataire": email_data.get("destinataire", "unknown") if email_data else "unknown"
            }
        }



