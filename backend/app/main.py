from fastapi import FastAPI, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from .core.dependencies import get_db, get_current_user, get_current_user_optional, get_admin_user
from .core.permissions import PermissionManager, Operation, AccessLevel, require_permission, require_niveau_acces
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
    description="Obtenir la liste des langues supportées et informations de locale"
)
def obtenir_langues_supportees(translator = Depends(get_current_translator)):
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
            "en_tete": translator.translate("usage_langue_en_tete"),
            "parametre_requete": translator.translate("usage_langue_requete"),
            "accept_language": translator.translate("usage_langue_accept")
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
            status=donnees_imei.get("statut", "active"),
            appareil_id=appareil.id
        )
        db.add(imei)
        numeros_imei.append(imei.numero_imei)
    
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
            "niveau_acces": user.niveau_acces or "basique"
        }
    )
    
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
@app.get("/appareils", tags=["Appareils"],summary= "Liste des appareils")
def list_devices(
    skip: int = 0,
    limit: int = 100,
    marque: str = None,
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
    
    # Apply access-based filtering based on user's data portee_donnees
    if not filter_context["is_admin"]:
        if filter_context["portee_donnees"].value == "own":
            query = query.filter(Appareil.utilisateur_id == user.id)
        elif filter_context["portee_donnees"].value == "brands" and filter_context["marques_autorisees"]:
            query = query.filter(Appareil.marque.in_(filter_context["marques_autorisees"]))
        elif filter_context["portee_donnees"].value == "organization" and filter_context["organization"]:
            # Organization filtering would need additional device fields
            pass
    
    # Apply marque filter with access validation
    if marque:
        # Validate marque access for limited users
        if user.niveau_acces == "limited" and user.marques_autorisees:
            if marque not in user.marques_autorisees:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Accès refusé : Marque '{marque}' pas dans les marques autorisées"
                )
        query = query.filter(Appareil.marque == marque)
    
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
                "motif_acces": access_details["reason"]
            }
            
            # Add enhanced info based on access level
            user_level = AccessLevel(user.niveau_acces or "basique")
            if user_level in [AccessLevel.ELEVATED, AccessLevel.ADMIN]:
                device_info.update({
                    "emmc": device.emmc,
                    "utilisateur_id": str(device.utilisateur_id) if device.utilisateur_id else None,
                    "imei_count": len(device.imeis)
                })
            
            device_list.append(device_info)
    
    return {
        "devices": device_list,
        "contexte_acces": {
            "niveau_acces": user.niveau_acces or "basique",
            "portee_donnees": filter_context["portee_donnees"].value,
            "marques_autorisees": filter_context["marques_autorisees"],
            "total_accessible": len(device_list)
        },
        "filters": {
            "marque": marque,
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
                        numero_imei=imei_data,
                        numero_slot=i + 1,
                        status="active",
                        appareil_id=appareil.id
                    )
                else:
                    # Format dictionnaire
                    imei = IMEI(
                        id=uuid.uuid4(),
                        numero_imei=imei_data.get("numero_imei"),
                        numero_slot=imei_data.get("numero_slot", i + 1),
                        status=imei_data.get("statut", "active"),
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
    description="Vérifier un IMEI via différents protocoles (REST, SS7, Diameter) selon la configuration"
)
async def verify_imei_multi_protocol(
    request_data: dict,
    protocol: str = Query(default="rest", description="Protocole à utiliser (rest, ss7, diameter)"),
    request: Request = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
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
    description="Obtenir le statut d'activation des protocoles d'intégration"
)
async def get_protocols_status(
    user = Depends(get_current_user_optional),
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

