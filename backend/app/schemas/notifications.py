"""
Schémas Pydantic pour le système de notifications EIR Project
Définit les modèles de validation pour les APIs de notifications
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    """Types de notifications supportés"""
    EMAIL = "email"
    SMS = "sms"

class NotificationStatus(str, Enum):
    """Statuts des notifications"""
    EN_ATTENTE = "en_attente"
    ENVOYE = "envoyé"
    ECHEC = "échoué"

class CreationNotification(BaseModel):
    """Schéma pour créer une nouvelle notification"""
    type: NotificationType = Field(..., description="Type de notification (email ou sms)")
    destinataire: str = Field(..., min_length=1, max_length=255, description="Adresse email ou numéro de téléphone du destinataire")
    sujet: Optional[str] = Field(None, max_length=255, description="Sujet du message (requis pour email)")
    contenu: str = Field(..., min_length=1, description="Contenu du message à envoyer")
    utilisateur_id: Optional[str] = Field(None, description="ID de l'utilisateur (optionnel si utilisateur connecté)")
    envoyer_immediatement: bool = Field(False, description="Envoyer immédiatement ou ajouter à la queue")
    
    @validator('destinataire')
    def valider_destinataire(cls, v, values):
        """Valide le format du destinataire selon le type"""
        notification_type = values.get('type')
        
        if notification_type == NotificationType.EMAIL:
            # Validation email basique
            if '@' not in v or '.' not in v:
                raise ValueError('Format email invalide')
        elif notification_type == NotificationType.SMS:
            # Validation téléphone basique
            import re
            # Supprimer les espaces et caractères spéciaux
            cleaned = re.sub(r'[\s\-\.\(\)]', '', v)
            if not cleaned.startswith('+') and len(cleaned) < 8:
                raise ValueError('Numéro de téléphone invalide (doit commencer par + ou avoir au moins 8 chiffres)')
        
        return v
    
    @validator('sujet')
    def valider_sujet_email(cls, v, values):
        """Valide que le sujet est présent pour les emails"""
        notification_type = values.get('type')
        
        if notification_type == NotificationType.EMAIL and not v:
            raise ValueError('Sujet requis pour les emails')
        
        return v

class ReponseNotification(BaseModel):
    """Schéma de réponse pour une notification"""
    id: str = Field(..., description="ID unique de la notification")
    type: str = Field(..., description="Type de notification")
    destinataire: str = Field(..., description="Destinataire de la notification")
    sujet: Optional[str] = Field(None, description="Sujet du message")
    contenu: str = Field(..., description="Contenu du message")
    statut: str = Field(..., description="Statut actuel de la notification")
    tentative: int = Field(..., description="Nombre de tentatives d'envoi")
    erreur: Optional[str] = Field(None, description="Message d'erreur si échec")
    date_creation: datetime = Field(..., description="Date de création de la notification")
    date_envoi: Optional[datetime] = Field(None, description="Date d'envoi réussie")
    utilisateur_id: str = Field(..., description="ID de l'utilisateur propriétaire")
    
    class Config:
        from_attributes = True

class ReponseListeNotifications(BaseModel):
    """Schéma de réponse pour une liste de notifications"""
    notifications: List[ReponseNotification] = Field(..., description="Liste des notifications")
    total: int = Field(..., description="Nombre total de notifications")
    page: int = Field(..., description="Page actuelle")
    taille_page: int = Field(..., description="Taille de la page")
    total_pages: int = Field(..., description="Nombre total de pages")

class FiltresNotifications(BaseModel):
    """Schéma pour filtrer les notifications"""
    type: Optional[NotificationType] = Field(None, description="Filtrer par type de notification")
    statut: Optional[NotificationStatus] = Field(None, description="Filtrer par statut")
    destinataire: Optional[str] = Field(None, description="Filtrer par destinataire")
    date_debut: Optional[datetime] = Field(None, description="Date de début pour filtrer")
    date_fin: Optional[datetime] = Field(None, description="Date de fin pour filtrer")

class EnvoiNotificationImmediat(BaseModel):
    """Schéma pour envoyer une notification immédiatement"""
    type: NotificationType = Field(..., description="Type de notification")
    destinataire: str = Field(..., description="Destinataire")
    sujet: Optional[str] = Field(None, description="Sujet (requis pour email)")
    contenu: str = Field(..., min_length=1, description="Contenu du message")
    
    @validator('destinataire')
    def valider_destinataire(cls, v, values):
        """Valide le format du destinataire selon le type"""
        notification_type = values.get('type')
        
        if notification_type == NotificationType.EMAIL:
            if '@' not in v or '.' not in v:
                raise ValueError('Format email invalide')
        elif notification_type == NotificationType.SMS:
            import re
            cleaned = re.sub(r'[\s\-\.\(\)]', '', v)
            if not cleaned.startswith('+') and len(cleaned) < 8:
                raise ValueError('Numéro de téléphone invalide')
        
        return v

class ReponseEnvoiImmediat(BaseModel):
    """Schéma de réponse pour un envoi immédiat"""
    success: bool = Field(..., description="Succès de l'envoi")
    message: str = Field(..., description="Message de résultat")
    notification_id: Optional[str] = Field(None, description="ID de la notification créée")
    error: Optional[str] = Field(None, description="Message d'erreur si échec")

class StatistiquesNotifications(BaseModel):
    """Schéma pour les statistiques des notifications"""
    total_notifications: int = Field(..., description="Nombre total de notifications")
    en_attente: int = Field(..., description="Notifications en attente")
    envoyes: int = Field(..., description="Notifications envoyées")
    echecs: int = Field(..., description="Notifications échouées")
    emails_total: int = Field(..., description="Total d'emails")
    sms_total: int = Field(..., description="Total de SMS")
    derniere_24h: Dict[str, int] = Field(..., description="Statistiques des dernières 24h")
    taux_succes: float = Field(..., description="Taux de succès en pourcentage")

class ConfigurationDispatcher(BaseModel):
    """Schéma pour la configuration du dispatcher"""
    enabled: bool = Field(..., description="Dispatcher activé")
    check_interval_seconds: int = Field(..., description="Intervalle de vérification en secondes")
    batch_size: int = Field(..., description="Taille des lots de traitement")
    working_hours_enabled: bool = Field(..., description="Heures de travail activées")
    rate_limiting_enabled: bool = Field(..., description="Limitation de débit activée")
    is_working_hours: bool = Field(..., description="Dans les heures de travail actuellement")
    is_running: bool = Field(..., description="Traitement en cours")

class StatistiquesDispatcher(BaseModel):
    """Schéma pour les statistiques du dispatcher"""
    total_processed: int = Field(..., description="Total de notifications traitées")
    emails_sent: int = Field(..., description="Emails envoyés")
    sms_sent: int = Field(..., description="SMS envoyés")
    errors: int = Field(..., description="Nombre d'erreurs")
    last_run: Optional[datetime] = Field(None, description="Dernière exécution")
    configuration: ConfigurationDispatcher = Field(..., description="Configuration actuelle")

class TestConnexionEmail(BaseModel):
    """Schéma pour tester la connexion email"""
    success: bool = Field(..., description="Test réussi")
    message: str = Field(..., description="Message du test")
    configuration: Dict[str, Any] = Field(..., description="Configuration utilisée (sans secrets)")

class TestConnexionSMS(BaseModel):
    """Schéma pour tester la connexion SMS"""
    success: bool = Field(..., description="Test réussi")
    message: str = Field(..., description="Message du test")
    configuration: Dict[str, Any] = Field(..., description="Configuration utilisée (sans secrets)")

class MiseAJourNotification(BaseModel):
    """Schéma pour mettre à jour une notification"""
    statut: Optional[NotificationStatus] = Field(None, description="Nouveau statut")
    erreur: Optional[str] = Field(None, description="Message d'erreur")
    tentative: Optional[int] = Field(None, ge=0, description="Nombre de tentatives")

class NotificationTemplate(BaseModel):
    """Schéma pour un template de notification"""
    nom: str = Field(..., description="Nom du template")
    type: NotificationType = Field(..., description="Type de notification")
    sujet_template: Optional[str] = Field(None, description="Template du sujet")
    contenu_template: str = Field(..., description="Template du contenu")
    variables: List[str] = Field(..., description="Variables utilisables dans le template")
    description: str = Field(..., description="Description du template")

class EnvoiNotificationTemplate(BaseModel):
    """Schéma pour envoyer une notification avec template"""
    template_nom: str = Field(..., description="Nom du template à utiliser")
    destinataire: str = Field(..., description="Destinataire")
    variables: Dict[str, str] = Field(default_factory=dict, description="Variables pour le template")
    envoyer_immediatement: bool = Field(False, description="Envoyer immédiatement")

class ReponseProcessingNotifications(BaseModel):
    """Schéma de réponse pour le traitement des notifications"""
    message: str = Field(..., description="Message de résultat")
    processed: int = Field(..., description="Nombre de notifications traitées")
    total_notifications: Optional[int] = Field(None, description="Total de notifications dans le lot")
    execution_time_seconds: Optional[int] = Field(None, description="Temps d'exécution en secondes")
    stats: Optional[StatistiquesDispatcher] = Field(None, description="Statistiques mises à jour")
    error: Optional[str] = Field(None, description="Message d'erreur si échec")

class HistoriqueNotification(BaseModel):
    """Schéma pour l'historique d'une notification"""
    notification: ReponseNotification = Field(..., description="Données de la notification")
    tentatives: List[Dict[str, Any]] = Field(..., description="Historique des tentatives")
    utilisateur_nom: Optional[str] = Field(None, description="Nom de l'utilisateur")
    utilisateur_email: Optional[str] = Field(None, description="Email de l'utilisateur")

class ConfigurationService(BaseModel):
    """Schéma pour la configuration des services de notification"""
    email_service: Dict[str, Any] = Field(..., description="Configuration du service email")
    sms_service: Dict[str, Any] = Field(..., description="Configuration du service SMS")
    dispatcher: Dict[str, Any] = Field(..., description="Configuration du dispatcher")
    rate_limiting: Dict[str, Any] = Field(..., description="Configuration du rate limiting")
