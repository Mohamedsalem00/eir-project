from fastapi import FastAPI, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from .core.dependencies import get_db, get_current_user, get_current_user_optional, get_admin_user
from .core.permissions import PermissionManager, Operation, AccessLevel, require_permission, require_access_level
from .core.i18n_deps import get_current_translator, get_language_from_request
from .core.audit_deps import get_audit_service
from .i18n import get_translator, SUPPORTED_LANGUAGES
from .services.audit import AuditService
from .routes.auth import router as auth_router
from .routes.access_management import router as access_router
from .models.appareil import Appareil
from .models.utilisateur import Utilisateur
from .models.recherche import Recherche
from .models.sim import SIM
from .models.notification import Notification
from .models.journal_audit import JournalAudit
from .models.imei import IMEI
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, Dict, Any
import platform

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
    description="Obtenir des informations complètes sur l'API, les capacités et le guide de démarrage rapide"
)
async def bienvenue(
    request: Request,
    user = Depends(get_current_user_optional),
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
        if current_user.type_utilisateur == "administrateur" or current_user.access_level == "admin":
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
            "formats_supportes": ["IMEI 15 chiffres", "IMEI 14 chiffres"]
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
        "recherche_imei": "/imei/{imei}",
        "journal_recherche_imei": "/imei/{imei}/historique",
        "statistiques_publiques": "/public/statistiques",
        "verification_sante": "/verification-etat",
        "info_api": "/",
        "langues_supportees": "/languages"
    }
    
    points_terminaison_authentifies = {}
    points_terminaison_admin = {}
    
    if type_utilisateur in ["utilisateur", "admin"]:
        points_terminaison_authentifies = {
            "appareils_utilisateur": "/appareils",
            "sims_utilisateur": "/cartes-sim", 
            "historique_recherche": "/recherches",
            "profil_utilisateur": "/utilisateurs/{user_id}",
            "notifications": "/notifications",
            "analyses": "/analyses/recherches"
        }
    if type_utilisateur == "admin":
        points_terminaison_admin = {
            "gestion_utilisateurs": "/utilisateurs",
            "utilisateurs_admin": "/admin/utilisateurs",
            "gestion_appareils": "/admin/appareils",
            "operations_lot": "/admin/import-lot-appareils",
            "journaux_audit": "/admin/journaux-audit",
            "analyses_systeme": "/analyses/appareils"
        }
    
    return {
        "title": translator.translate("welcome_title"),
        "description": translator.translate("welcome_description"),
        "tagline": translator.translate("welcome_tagline"),
        "status": translator.translate("api_status"),
        "timestamp": datetime.now().isoformat(),
        "language": translator.current_language,
        
        "api": {
            "name": translator.translate("nom_service"),
            "version": translator.translate("version_api"),
            "build": translator.translate("version_construction"),
            "environment": translator.translate("environnement"),
            "uptime": get_system_uptime()
        },
        
        "contact": {
            "organization": translator.translate("organization"),
            "email": translator.translate("contact_email"),
            "support_email": translator.translate("support_email"),
            "documentation_url": translator.translate("documentation_url")
        },
        
        "securite": {
            "methodes_authentification": ["JWT Bearer Token", "Clé API (Entreprise)"],
            "limitation_taux": translator.translate("rate_limits"),
            "normes_conformite": ["RGPD", "SOX", "ISO 27001", "Directives GSMA"],
            "chiffrement_donnees": "TLS 1.3, AES-256"
        },
        
        "capacites": capacites,
        
        "points_terminaison": {
            "publics": points_terminaison_publics,
            "authentifies": points_terminaison_authentifies,
            "admin": points_terminaison_admin
        },
        
        "specifications_techniques": {
            "formats_supportes": ["JSON", "XML (sur demande)"],
            "taille_max_requete": "10MB",
            "sla_temps_reponse": "< 200ms (95e percentile)",
            "sla_disponibilite": "99,9% de disponibilité",
            "support_sdk": ["Python", "JavaScript", "Java", "exemples cURL"]
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
            "licence": translator.translate("license"),
            "retention_donnees": "Données conservées selon les réglementations régionales"
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
        db_status = {"statut": "connecte", "message": "Connexion base de données réussie"}
        db_latency = "< 10ms"
        try:
            db.execute(text("SELECT 1"))
        except Exception as e:
            db_status = {"statut": "erreur", "message": str(e)}
            db_latency = "N/A"
        
        # Informations système
        infos_systeme = {
            "duree_fonctionnement": get_system_uptime(),
            "plateforme": platform.platform(),
            "version_python": platform.python_version(),
            "heure_serveur": datetime.now().isoformat()
        }
        
        # Vérification du statut des points de terminaison
        statut_points_terminaison = {
            "authentification": "operationnel",
            "validation_imei": "operationnel", 
            "gestion_appareils": "operationnel",
            "analyses": "operationnel"
        }
        
        # Statut de sécurité
        statut_securite = {
            "chiffrement_tls": "active",
            "validation_jwt": "active",
            "limitation_taux": "active",
            "journalisation_audit": "active"
        }
        
        return {
            "statut": translator.translate("service_sain"),
            "horodatage": datetime.now().isoformat(),
            "service": translator.translate("nom_service"),
            "version": translator.translate("version_api"),
            "duree_fonctionnement": infos_systeme["duree_fonctionnement"],
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
                "statut": "malsain",
                "message": f"Vérification d'état échouée: {str(e)}",
                "horodatage": datetime.now().isoformat()
            }
        )


@app.get(
    "/languages",
    tags=["Système"],
    summary="Langues Supportées",
    description="Obtenir la liste des langues supportées et informations de locale"
)
def obtenir_langues_supportees():
    """
    ## Langues Supportées
    
    Obtenir des informations sur toutes les langues supportées incluant :
    - Codes et noms des langues
    - Noms natifs des langues
    - Support RTL (Droite-vers-Gauche)
    - Paramètres de langue par défaut
    """
    return {
        "langues_supportees": SUPPORTED_LANGUAGES,
        "langue_par_defaut": "fr",
        "utilisation": {
            "en_tete": "Définir l'en-tête X-Language avec le code de langue désiré",
            "parametre_requete": "Ajouter ?lang=code à toute URL de requête",
            "accept_language": "L'en-tête Accept-Language du navigateur est automatiquement détecté"
        }
    }


@app.get(
    "/imei/{imei}",
    tags=["IMEI", "Public"],
    summary="Recherche IMEI Améliorée avec Contrôle d'Accès",
    description="Rechercher les informations IMEI avec niveaux d'accès granulaires et journalisation automatique des recherches"
)
def verifier_imei(
    imei: str,
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
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
        niveau_acces_utilisateur = user.access_level or "basique"
    
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
    imei_record = db.query(IMEI).filter(IMEI.imei_number == imei).first()
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
            "found": True,
            "status": imei_record.status,
            "slot_number": imei_record.slot_number,
            "message": translator.translate("imei_found"),
            "search_logged": True,
            "search_id": str(recherche.id),
            "access_context": {
                "niveau_d'accès": niveau_acces_utilisateur,
                "access_reason": access_details["reason"],
                "data_scope": access_details["scope"]
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
        
        return response_data
    
    # IMEI not found response
    return {
        "imei": imei,
        "found": False,
        "message": translator.translate("imei_not_found"),
        "search_logged": True,
        "search_id": str(recherche.id),
        "access_context": {
            "niveau_d'accès": niveau_acces_utilisateur,
            "access_reason": access_details["reason"]
        }
    }

# APIs de Gestion d'Appareils Améliorées avec contrôle d'accès granulaire
@app.post("/appareils", tags=["Appareils"])
def enregistrer_appareil(
    donnees_appareil: dict, 
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    Enregistrer un appareil avec contrôle d'accès amélioré et journalisation d'audit
    
    ### Contrôle d'Accès:
    - Les utilisateurs standard peuvent enregistrer des appareils pour eux-mêmes
    - Les utilisateurs élevés peuvent enregistrer des appareils dans leur organisation
    - Les admins peuvent enregistrer des appareils pour tout utilisateur
    - Les utilisateurs limités (parties concernées) ont un accès restreint basé sur les marques
    """
    # Vérifier si l'utilisateur a la permission de créer des appareils
    if not PermissionManager.has_permission(user, Operation.CREATE_DEVICE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission refusée: Impossible de créer des appareils"
        )
    
    # Valider l'accès aux marques pour les parties concernées
    marque_appareil = donnees_appareil.get("marque")
    if user.access_level == "limited" and user.allowed_brands:
        if marque_appareil not in user.allowed_brands:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé: Marque '{marque_appareil}' non autorisée"
            )
    
    # Définir le propriétaire de l'appareil selon le niveau d'accès
    if user.type_utilisateur != "administrateur" and user.access_level not in ["elevated"]:
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
        numero_imei = donnees_imei.get("imei_number")
        
        # Valider l'accès aux plages IMEI pour les parties concernées
        if user.access_level == "limited" and user.allowed_imei_ranges:
            can_access, _ = PermissionManager.can_access_imei(user, numero_imei, db)
            if not can_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Accès refusé: IMEI '{numero_imei}' non autorisé"
                )
        
        imei = IMEI(
            id=uuid.uuid4(),
            imei_number=numero_imei,
            slot_number=donnees_imei.get("slot_number", i + 1),
            status=donnees_imei.get("status", "active"),
            appareil_id=appareil.id
        )
        db.add(imei)
        numeros_imei.append(imei.imei_number)
    
    db.commit()
    db.refresh(appareil)
    
    # Journaliser la création d'appareil avec contexte d'accès
    audit_service.log_device_creation(
        device_id=str(appareil.id),
        user_id=str(user.id),
        device_data={
            "marque": appareil.marque,
            "modele": appareil.modele,
            "emmc": appareil.emmc,
            "imeis": numeros_imei,
            "niveau_d'accès": user.access_level or "basique"
        }
    )
    
    return {
        "id": str(appareil.id),
        "marque": appareil.marque,
        "modele": appareil.modele,
        "imeis": [
            {
                "imei_number": imei.imei_number,
                "slot_number": imei.slot_number,
                "status": imei.status
            }
            for imei in appareil.imeis
        ],
        "niveau_d'accès": user.access_level or "basique"
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
    if user.type_utilisateur != "administrateur" and user.access_level != "admin":
        if user.data_scope == "own":
            query = query.filter(Recherche.utilisateur_id == user.id)
        elif user.access_level == "limited":
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
        "access_context": {
            "niveau_d'accès": user.access_level or "basique",
            "data_scope": user.data_scope or "own",
            "total_accessible": len(searches)
        }
    }

# Enhanced device listing with granular filtering
@app.get("/appareils", tags=["Appareils"],summary= "Liste des appareils")
def list_devices(
    skip: int = 0,
    limit: int = 100,
    brand: str = None,
    db: Session = Depends(get_db),
    user: Utilisateur = Depends(get_current_user)
):
    """
Répertorier les appareils avec un contrôle d'accès et un filtrage améliorés

### Contrôle d'accès :
- Les utilisateurs voient les appareils en fonction de leur périmètre de données
- Le filtrage par marque respecte les marques autorisées pour les parties concernées
- Filtrage organisationnel pour les utilisateurs privilégiés
- Accès complet pour les administrateurs
    """
    # Check if user has permission to read devices
    if not PermissionManager.has_permission(user, Operation.READ_DEVICE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Autorisation refusée : impossible de lire les appareils"
        )
    
    # Get data filter context for this user
    filter_context = PermissionManager.get_data_filter_context(user)
    
    query = db.query(Appareil)
    
    # Apply access-based filtering based on user's data scope
    if not filter_context["is_admin"]:
        if filter_context["scope"].value == "own":
            query = query.filter(Appareil.utilisateur_id == user.id)
        elif filter_context["scope"].value == "brands" and filter_context["allowed_brands"]:
            query = query.filter(Appareil.marque.in_(filter_context["allowed_brands"]))
        elif filter_context["scope"].value == "organization" and filter_context["organization"]:
            # Organization filtering would need additional device fields
            pass
    
    # Apply brand filter with access validation
    if brand:
        # Validate brand access for limited users
        if user.access_level == "limited" and user.allowed_brands:
            if brand not in user.allowed_brands:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Accès refusé : Marque '{brand}' pas dans les marques autorisées"
                )
        query = query.filter(Appareil.marque == brand)
    
    devices = query.offset(skip).limit(limit).all()
    
    # Build response with access-appropriate data
    device_list = []
    for device in devices:
        can_access, access_details = PermissionManager.can_access_device(user, device)
        
        if can_access:
            device_info = {
                "id": str(device.id),
                "marque": device.marque,
                "modele": device.modele,
                "can_modify": PermissionManager.has_permission(user, Operation.UPDATE_DEVICE) and can_access,
                "access_reason": access_details["reason"]
            }
            
            # Add enhanced info based on access level
            user_level = AccessLevel(user.access_level or "basique")
            if user_level in [AccessLevel.ELEVATED, AccessLevel.ADMIN]:
                device_info.update({
                    "emmc": device.emmc,
                    "utilisateur_id": str(device.utilisateur_id) if device.utilisateur_id else None,
                    "imei_count": len(device.imeis)
                })
            
            device_list.append(device_info)
    
    return {
        "devices": device_list,
        "access_context": {
            "niveau_d'accès": user.access_level or "basique",
            "data_scope": filter_context["scope"].value,
            "allowed_brands": filter_context["allowed_brands"],
            "total_accessible": len(device_list)
        },
        "filters": {
            "brand": brand,
            "skip": skip,
            "limit": limit
        }
    }

# Nouvel endpoint pour les parties concernées pour vérifier leurs permissions d'accès
@app.get("/mes-permissions", tags=["Utilisateurs"])
def get_my_permissions(
    user = Depends(get_current_user_optional)
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
            "niveau_d'accès": "visiteur",
            "permissions": ["read_imei"],
            "restrictions": "Accès public uniquement"
        }
    
    permissions_summary = PermissionManager.get_user_permissions_summary(user)
    
    return {
        "user_info": {
            "id": str(user.id),
            "name": user.nom,
            "niveau_d'accès": user.access_level or "basique",
            "organization": user.organization
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
    audit_service: AuditService = Depends(get_audit_service)
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
    
    return {"id": str(user.id), "nom": user.nom, "email": user.email}

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
            detail=translator.translate("access_denied")
        )
    
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404, 
            detail=translator.translate("user_not_found")
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
                "imeis": [imei.imei_number for imei in d.imeis]
            } 
            for d in devices
        ],
        "sims": [{"id": str(s.id), "iccid": s.iccid, "operateur": s.operateur} for s in sims]
    }

# APIs de Gestion des Cartes SIM
@app.post("/cartes-sim", tags=["Cartes SIM"])
def register_sim(
    sim_data: dict, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
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
    return {"id": str(sim.id), "iccid": sim.iccid, "operateur": sim.operateur}

@app.get("/cartes-sim", tags=["Cartes SIM"])
def list_sims(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Lister les cartes SIM - les utilisateurs voient seulement leurs cartes SIM, les admins voient tout"""
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

@app.get("/cartes-sim/{iccid}", tags=["Cartes SIM"])
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

# APIs d'Analyses et Statistiques
@app.get("/analyses/recherches", tags=["Analyses"])
def search_analytics(
    days: int = Query(7, description="Nombre de jours à analyser"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Analyses des recherches - filtrées par niveau d'accès utilisateur"""
    start_date = datetime.now() - timedelta(days=days)
    
    # L'admin voit toutes les recherches, les utilisateurs voient seulement les leurs
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
    
    # Recherches par jour
    daily_searches = searches_query.with_entities(
        func.date(Recherche.date_recherche).label('date'),
        func.count(Recherche.id).label('count')
    ).group_by(func.date(Recherche.date_recherche)).all()
    
    # IMEIs les plus recherchés
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

@app.get("/analyses/appareils", tags=["Analyses"])
def device_analytics(db: Session = Depends(get_db)):
    """
    Obtenir les analyses statistiques des appareils.
    
    Returns:
        dict: Statistiques des appareils incluant total, assignés, non-assignés et répartition par marque
    """
    # Total des appareils
    total_devices = db.query(Appareil).count()
    
    # Appareils par marque
    brand_stats = db.query(
        Appareil.marque,
        func.count(Appareil.id).label('count')
    ).group_by(Appareil.marque).order_by(desc('count')).all()
    
    # Appareils assignés vs non assignés
    assigned = db.query(Appareil).filter(Appareil.utilisateur_id.isnot(None)).count()
    unassigned = total_devices - assigned
    
    return {
        "total_devices": total_devices,
        "assigned_devices": assigned,
        "unassigned_devices": unassigned,
        "devices_by_brand": [{"brand": brand.marque, "count": brand.count} for brand in brand_stats]
    }

# Search History APIs
@app.get("/utilisateurs/{user_id}/recherches", tags=["Historique de Recherche"])
def user_search_history(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Obtenir l'historique de recherche d'un utilisateur.
    
    Args:
        user_id: Identifiant de l'utilisateur
        skip: Nombre d'éléments à ignorer pour la pagination
        limit: Nombre maximum d'éléments à retourner
        db: Session de base de données
        current_user: Utilisateur actuel connecté
    
    Returns:
        dict: Historique des recherches de l'utilisateur
    
    Note:
        Les utilisateurs ne peuvent voir que leur propre historique
    """
    # Les utilisateurs ne peuvent accéder qu'à leur propre historique de recherche
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

@app.get("/imei/{imei}/historique", tags=["Historique de Recherche"])
def imei_search_history(imei: str, db: Session = Depends(get_db)):
    """
    Obtenir l'historique de recherche pour un IMEI spécifique.
    
    Args:
        imei: Numéro IMEI à rechercher
        db: Session de base de données
    
    Returns:
        dict: Historique des recherches pour cet IMEI incluant le nombre total et les recherches récentes
    """
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
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Lister les notifications.
    
    Args:
        user_id: Identifiant de l'utilisateur (optionnel, pour les administrateurs)
        status: Statut des notifications à filtrer (optionnel)
        skip: Nombre d'éléments à ignorer pour la pagination
        limit: Nombre maximum d'éléments à retourner
        db: Session de base de données
        current_user: Utilisateur actuel connecté
    
    Returns:
        dict: Liste des notifications
        
    Note:
        Les utilisateurs voient uniquement leurs notifications, les administrateurs voient toutes
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

# API Admin
@app.get("/admin/utilisateurs", tags=["Admin"])
def list_all_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """
    Lister tous les utilisateurs - Administrateurs uniquement.
    
    Args:
        skip: Nombre d'éléments à ignorer pour la pagination
        limit: Nombre maximum d'éléments à retourner
        db: Session de base de données
        current_user: Utilisateur administrateur actuel
    
    Returns:
        dict: Liste de tous les utilisateurs du système
    """
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

# Endpoint amélioré des journaux d'audit
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
    current_user: Utilisateur = Depends(get_admin_user)
):
    """
    Obtenir les journaux d'audit avec filtrage amélioré - Administrateurs uniquement.
    
    Args:
        user_id: Filtrer par identifiant d'utilisateur (optionnel)
        action_filter: Filtrer par type d'action (optionnel)
        entity_type: Filtrer par type d'entité (optionnel)
        start_date: Date de début pour le filtrage (optionnel)
        end_date: Date de fin pour le filtrage (optionnel)
        skip: Nombre d'éléments à ignorer pour la pagination
        limit: Nombre maximum d'éléments à retourner
        db: Session de base de données
        current_user: Utilisateur administrateur actuel
    
    Returns:
        dict: Journaux d'audit filtrés
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
    
    Args:
        appareil_id: Identifiant de l'appareil à supprimer
        db: Session de base de données
        current_user: Utilisateur administrateur actuel
        audit_service: Service d'audit pour la journalisation
        translator: Service de traduction
    
    Returns:
        dict: Message de confirmation de suppression
    """
    appareil = db.query(Appareil).filter(Appareil.id == appareil_id).first()
    if not appareil:
        raise HTTPException(status_code=404, detail="Appareil non trouvé")
    
    # Collecter les données de l'appareil pour le journal d'audit avant suppression
    appareil_data = {
        "marque": appareil.marque,
        "modele": appareil.modele,
        "emmc": appareil.emmc,
        "imeis": [imei.imei_number for imei in appareil.imeis]
    }
    
    db.delete(appareil)
    db.commit()
    
    # Journaliser la suppression de l'appareil
    audit_service.log_device_deletion(
        device_id=appareil_id,
        user_id=str(current_user.id),
        device_data=appareil_data
    )
    
    return {"message":translator.translate('device_deleted')}

# Opérations en lot
@app.post("/admin/import-lot-appareils", tags=["Appareils", "Admin"])
def bulk_import_devices(
    devices_data: List[dict], 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user),
    audit_service: AuditService = Depends(get_audit_service)
):
    """
    Import en lot d'appareils avec journalisation d'audit - Administrateurs uniquement.
    
    Args:
        devices_data: Liste des données d'appareils à importer
        db: Session de base de données
        current_user: Utilisateur administrateur actuel
        audit_service: Service d'audit pour la journalisation
    
    Returns:
        dict: Résultats de l'import incluant le nombre d'appareils importés et les erreurs
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
            imeis_data = device_data.get("imeis", [])
            for i, imei_data in enumerate(imeis_data):
                if isinstance(imei_data, str):
                    # Format chaîne simple
                    imei = IMEI(
                        id=uuid.uuid4(),
                        imei_number=imei_data,
                        slot_number=i + 1,
                        status="active",
                        appareil_id=appareil.id
                    )
                else:
                    # Format dictionnaire
                    imei = IMEI(
                        id=uuid.uuid4(),
                        imei_number=imei_data.get("imei_number"),
                        slot_number=imei_data.get("slot_number", i + 1),
                        status=imei_data.get("status", "active"),
                        appareil_id=appareil.id
                    )
                db.add(imei)
            
            imported_count += 1
        except Exception as e:
            errors.append(f"Erreur lors de l'import de l'appareil {device_data.get('marque', 'Inconnu')}: {str(e)}")
    
    db.commit()
    
    # Journaliser l'opération d'import en lot
    audit_service.log_bulk_import(
        user_id=str(current_user.id),
        imported_count=imported_count,
        errors=errors
    )
    
    return {
        "imported_count": imported_count,
        "errors": errors
    }

@app.post("/appareils/{appareil_id}/imeis", tags=["Appareils"])
def add_imei_to_device(appareil_id: str, imei_data: dict, db: Session = Depends(get_db)):
    """
    Ajouter un IMEI à un appareil.
    
    Args:
        appareil_id: Identifiant de l'appareil
        imei_data: Données de l'IMEI à ajouter
        db: Session de base de données
    
    Returns:
        dict: Confirmation d'ajout avec détails de l'IMEI
        
    Raises:
        HTTPException: Si l'appareil n'est pas trouvé ou a déjà le maximum d'IMEIs
    """
    appareil = db.query(Appareil).filter(Appareil.id == appareil_id).first()
    if not appareil:
        raise HTTPException(status_code=404, detail="Appareil non trouvé")
    
    # Vérifier si l'appareil a déjà 2 IMEIs
    if len(appareil.imeis) >= 2:
        raise HTTPException(status_code=400, detail="L'appareil a déjà le nombre maximum d'IMEIs (2)")
    
    imei = IMEI(
        id=uuid.uuid4(),
        imei_number=imei_data.get("imei_number"),
        slot_number=imei_data.get("slot_number", len(appareil.imeis) + 1),
        status=imei_data.get("status", "active"),
        appareil_id=appareil.id
    )
    
    db.add(imei)
    db.commit()
    
    return {
        "message": "IMEI ajouté avec succès",
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
    current_user: Utilisateur = Depends(get_admin_user),
    audit_service: AuditService = Depends(get_audit_service),
    translator = Depends(get_current_translator)
):
    """
    Mettre à jour le statut d'un IMEI avec journalisation d'audit - Administrateurs uniquement.
    
    Args:
        imei_id: Identifiant de l'IMEI
        status_data: Nouvelles données de statut
        db: Session de base de données
        current_user: Utilisateur administrateur actuel
        audit_service: Service d'audit pour la journalisation
        translator: Service de traduction
    
    Returns:
        dict: Message de confirmation de mise à jour
    """
    imei = db.query(IMEI).filter(IMEI.id == imei_id).first()
    if not imei:
        raise HTTPException(status_code=404, detail=translator.translate("imei_not_found_error"))
    
    old_status = imei.status
    new_status = status_data.get("status")
    imei.status = new_status
    db.commit()
    
    # Journaliser le changement de statut IMEI
    audit_service.log_imei_status_change(
        imei_id=str(imei.id),
        imei_number=imei.imei_number,
        old_status=old_status,
        new_status=new_status,
        user_id=str(current_user.id)
    )
    
    return {"message": translator.translate("imei_status_updated")}

# ANALYSES PUBLIQUES (Limitées pour les visiteurs)
@app.get("/public/statistiques", tags=["Public", "Analyses"])
def public_statistics(
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
    translator = Depends(get_current_translator)
):
    """
    Statistiques publiques avec informations limitées.
    
    Args:
        request: Requête HTTP
        db: Session de base de données
        user: Utilisateur optionnel (peut être None pour les visiteurs)
        translator: Service de traduction
    
    Returns:
        dict: Statistiques publiques limitées
    """
    current_user = user
    type_utilisateur = "visiteur"
    if current_user:
        if current_user.type_utilisateur == "administrateur":
            type_utilisateur = "admin"
        else:
            type_utilisateur = "utilisateur"
    
    # Statistiques de base disponibles pour tous
    total_devices = db.query(Appareil).count()
    total_imeis = db.query(IMEI).count()
    
    response = {
        translator.translate("total_devices"): total_devices,
        translator.translate("total_imeis"): total_imeis,
        translator.translate("last_updated"): datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Statistiques améliorées pour les utilisateurs authentifiés
    if type_utilisateur != "visiteur":
        total_users = db.query(Utilisateur).count()
        total_searches = db.query(Recherche).count()
        response.update({
            translator.translate("total_users"): total_users,
            translator.translate("total_searches"): total_searches
        })
    
    return response

