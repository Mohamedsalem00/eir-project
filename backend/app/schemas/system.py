from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, List, Any, Optional
from datetime import datetime

class MetadonneesAPI(BaseModel):
    """Informations de métadonnées de l'API"""
    nom: str = Field(..., description="Nom du service API")
    version: str = Field(..., description="Version de l'API")
    build: str = Field(..., description="Version de construction")
    environnement: str = Field(..., description="Environnement de déploiement")
    statut_disponibilite: str = Field(..., description="Statut de disponibilité du service")

class InfosContact(BaseModel):
    """Informations de contact"""
    organisation: str = Field(..., description="Nom de l'organisation")
    email: str = Field(..., description="Email de contact")
    email_support: str = Field(..., description="Email de support")
    url_documentation: str = Field(..., description="URL de documentation")

class InfosSecurite(BaseModel):
    """Informations de sécurité et conformité"""
    methodes_authentification: List[str] = Field(..., description="Méthodes d'authentification supportées")
    limitation_taux: str = Field(..., description="Politique de limitation du taux")
    normes_conformite: List[str] = Field(..., description="Normes de conformité")
    chiffrement_donnees: str = Field(..., description="Statut du chiffrement des données")

class CapacitesService(BaseModel):
    """Capacités et fonctionnalités du service"""
    validation_imei: Dict[str, Any] = Field(..., description="Capacités de validation IMEI")
    gestion_appareils: Dict[str, Any] = Field(..., description="Fonctionnalités de gestion d'appareils")
    gestion_utilisateurs: Dict[str, Any] = Field(..., description="Fonctionnalités de gestion d'utilisateurs")
    analyses: Dict[str, Any] = Field(..., description="Capacités d'analyse")
    operations_lot: Dict[str, Any] = Field(..., description="Support des opérations en lot")

class PointsTerminaisonAPI(BaseModel):
    """Points de terminaison API disponibles"""
    publics: Dict[str, str] = Field(..., description="Points de terminaison publics")
    authentifies: Dict[str, str] = Field(..., description="Points de terminaison pour utilisateurs authentifiés")
    admin: Dict[str, str] = Field(..., description="Points de terminaison admin uniquement")

class SpecificationsTechniques(BaseModel):
    """Spécifications techniques"""
    formats_supportes: List[str] = Field(..., description="Formats de données supportés")
    taille_max_requete: str = Field(..., description="Taille maximale de requête")
    sla_temps_reponse: str = Field(..., description="SLA du temps de réponse")
    sla_disponibilite: str = Field(..., description="SLA de disponibilité")
    support_sdk: List[str] = Field(..., description="SDKs disponibles")

class ReponseBienvenue(BaseModel):
    """Réponse de bienvenue professionnelle de l'API"""
    titre: str = Field(..., description="Titre de l'API")
    description: str = Field(..., description="Description de l'API")
    slogan: str = Field(..., description="Slogan de l'API")
    statut: str = Field(..., description="Statut actuel de l'API")
    horodatage: str = Field(..., description="Horodatage de la réponse")
    langue: str = Field(..., description="Langue de la réponse")
    
    # Informations principales
    api: MetadonneesAPI
    contact: InfosContact
    securite: InfosSecurite
    
    # Détails du service
    capacites: CapacitesService
    points_terminaison: PointsTerminaisonAPI
    specifications_techniques: SpecificationsTechniques
    
    # Démarrage rapide
    demarrage_rapide: Dict[str, str] = Field(..., description="Informations de démarrage rapide")
    
    # Légal
    legal: Dict[str, str] = Field(..., description="Informations légales")

class ReponseControleEtat(BaseModel):
    """Réponse du contrôle d'état de santé"""
    statut: str
    horodatage: str
    service: str
    version: str
    duree_fonctionnement: str
    base_donnees: Dict[str, str]
    infos_systeme: Dict[str, str]
    statut_points_terminaison: Dict[str, str]
    statut_securite: Dict[str, str]

class ReponseInfosAPI(BaseModel):
    """Réponse des informations API"""
    nom_api: str
    version: str
    description: str
    objectif: str
    capacites: Dict[str, Dict[str, Any]]
    specifications_techniques: Dict[str, str]
    fonctionnalites_conformite: Dict[str, str]
    formats_supportes: Dict[str, List[str]]
    pret_integration: Dict[str, str]