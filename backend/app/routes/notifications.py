"""
Router FastAPI pour la gestion des notifications EIR Project
Fournit les endpoints pour créer, lister, envoyer et gérer les notifications
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging

from ..core.dependencies import get_db, get_current_user, get_admin_user
from ..core.permissions import require_niveau_acces, AccessLevel
from ..models.notification import Notification
from ..models.utilisateur import Utilisateur
from ..schemas.notifications import (
    CreationNotification, ReponseNotification, ReponseListeNotifications,
    FiltresNotifications, EnvoiNotificationImmediat, ReponseEnvoiImmediat,
    StatistiquesNotifications, StatistiquesDispatcher, TestConnexionEmail,
    TestConnexionSMS, MiseAJourNotification, ReponseProcessingNotifications,
    HistoriqueNotification, ConfigurationService
)
from ..services.email_service import email_service
from ..services.sms_service import sms_service
from ..tasks.notification_dispatcher import (
    notification_dispatcher, send_notification_now, process_notifications_background
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/", response_model=ReponseNotification, status_code=status.HTTP_201_CREATED)
async def creer_notification(
    notification_data: CreationNotification,
    db: Session = Depends(get_db),
    current_user: Optional[Utilisateur] = Depends(get_current_user)
):
    """
    Crée une nouvelle notification
    
    - **type**: Type de notification (email ou sms)
    - **destinataire**: Adresse email ou numéro de téléphone
    - **sujet**: Sujet du message (requis pour email)
    - **contenu**: Contenu du message
    - **envoyer_immediatement**: Si true, envoie immédiatement
    """
    try:
        # Utiliser l'utilisateur connecté si pas d'ID spécifié
        user_id = notification_data.utilisateur_id or str(current_user.id)
        
        # Vérifier que l'utilisateur peut créer pour cet ID
        if str(current_user.id) != user_id and current_user.type_utilisateur != "administrateur":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez créer des notifications que pour vous-même"
            )
        
        # Créer la notification
        notification = Notification(
            id=uuid.uuid4(),
            type=notification_data.type.value,
            destinataire=notification_data.destinataire,
            sujet=notification_data.sujet,
            contenu=notification_data.contenu,
            statut='en_attente',
            tentative=0,
            utilisateur_id=user_id,
            date_creation=datetime.now()
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Envoyer immédiatement si demandé
        if notification_data.envoyer_immediatement:
            result = await send_notification_now(
                user_id,
                notification_data.type.value,
                notification_data.destinataire,
                notification_data.sujet,
                notification_data.contenu
            )
            
            # Mettre à jour le statut selon le résultat
            if result.get('success'):
                notification.statut = 'envoyé'
                notification.date_envoi = datetime.now()
            else:
                notification.statut = 'échoué'
                notification.erreur = result.get('error', 'Erreur inconnue')
            
            db.commit()
            db.refresh(notification)
        
        logger.info(f"Notification créée: {notification.id} ({notification.type})")
        
        return ReponseNotification(
            id=str(notification.id),
            type=notification.type,
            destinataire=notification.destinataire,
            sujet=notification.sujet,
            contenu=notification.contenu,
            statut=notification.statut,
            tentative=notification.tentative,
            erreur=notification.erreur,
            date_creation=notification.date_creation,
            date_envoi=notification.date_envoi,
            utilisateur_id=str(notification.utilisateur_id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la création de notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la création de la notification"
        )

@router.get("/", response_model=ReponseListeNotifications)
async def lister_notifications(
    page: int = Query(1, ge=1, description="Numéro de page"),
    taille_page: int = Query(20, ge=1, le=100, description="Taille de la page"),
    type_notification: Optional[str] = Query(None, description="Filtrer par type"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    destinataire: Optional[str] = Query(None, description="Filtrer par destinataire"),
    db: Session = Depends(get_db),
    current_user: Optional[Utilisateur] = Depends(get_current_user)
):
    """
    Liste les notifications de l'utilisateur connecté
    
    Paramètres de filtrage et pagination disponibles
    """
    try:
        # Construire la requête de base
        query = db.query(Notification).filter(
            Notification.utilisateur_id == current_user.id
        )
        
        # Appliquer les filtres
        if type_notification:
            query = query.filter(Notification.type == type_notification)
        
        if statut:
            query = query.filter(Notification.statut == statut)
        
        if destinataire:
            query = query.filter(Notification.destinataire.ilike(f"%{destinataire}%"))
        
        # Compter le total
        total = query.count()
        
        # Appliquer la pagination
        offset = (page - 1) * taille_page
        notifications = query.order_by(desc(Notification.date_creation)).offset(offset).limit(taille_page).all()
        
        # Calculer le nombre total de pages
        total_pages = (total + taille_page - 1) // taille_page
        
        # Convertir en schéma de réponse
        notifications_response = [
            ReponseNotification(
                id=str(notif.id),
                type=notif.type,
                destinataire=notif.destinataire,
                sujet=notif.sujet,
                contenu=notif.contenu,
                statut=notif.statut,
                tentative=notif.tentative,
                erreur=notif.erreur,
                date_creation=notif.date_creation,
                date_envoi=notif.date_envoi,
                utilisateur_id=str(notif.utilisateur_id)
            )
            for notif in notifications
        ]
        
        return ReponseListeNotifications(
            notifications=notifications_response,
            total=total,
            page=page,
            taille_page=taille_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération des notifications"
        )

@router.get("/{notification_id}", response_model=HistoriqueNotification)
async def obtenir_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[Utilisateur] = Depends(get_current_user)
):
    """
    Obtient les détails d'une notification spécifique avec son historique
    """
    try:
        # Récupérer la notification
        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                or_(
                    Notification.utilisateur_id == current_user.id,
                    current_user.type_utilisateur == "administrateur"
                )
            )
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification non trouvée"
            )
        
        # Récupérer les informations utilisateur
        utilisateur = db.query(Utilisateur).filter(
            Utilisateur.id == notification.utilisateur_id
        ).first()
        
        # Créer l'historique des tentatives (simulation)
        tentatives = []
        for i in range(notification.tentative):
            tentatives.append({
                'numero_tentative': i + 1,
                'date_tentative': notification.date_creation,  # Simulation
                'statut': 'échoué' if i < notification.tentative - 1 else notification.statut,
                'erreur': notification.erreur if i == notification.tentative - 1 else None
            })
        
        response = HistoriqueNotification(
            notification=ReponseNotification(
                id=str(notification.id),
                type=notification.type,
                destinataire=notification.destinataire,
                sujet=notification.sujet,
                contenu=notification.contenu,
                statut=notification.statut,
                tentative=notification.tentative,
                erreur=notification.erreur,
                date_creation=notification.date_creation,
                date_envoi=notification.date_envoi,
                utilisateur_id=str(notification.utilisateur_id)
            ),
            tentatives=tentatives,
            utilisateur_nom=utilisateur.nom if utilisateur else None,
            utilisateur_email=utilisateur.email if utilisateur else None
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération de la notification"
        )

@router.post("/envoyer-immediatement", response_model=ReponseEnvoiImmediat)
async def envoyer_notification_immediatement(
    notification_data: EnvoiNotificationImmediat,
    db: Session = Depends(get_db),
    current_user: Optional[Utilisateur] = Depends(get_current_user)
):
    """
    Envoie une notification immédiatement (bypass de la queue)
    
    Utile pour les notifications urgentes ou les tests
    """
    try:
        result = await send_notification_now(
            str(current_user.id),
            notification_data.type.value,
            notification_data.destinataire,
            notification_data.sujet,
            notification_data.contenu
        )
        
        return ReponseEnvoiImmediat(**result)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi immédiat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'envoi immédiat"
        )

@router.put("/{notification_id}", response_model=ReponseNotification)
async def mettre_a_jour_notification(
    notification_id: str,
    update_data: MiseAJourNotification,
    db: Session = Depends(get_db),
    current_user: Optional[Utilisateur] = Depends(get_current_user)
):
    """
    Met à jour une notification (statut, erreur, tentatives)
    
    Seuls les administrateurs peuvent modifier les notifications
    """
    if current_user.type_utilisateur != "administrateur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les administrateurs peuvent modifier les notifications"
        )
    
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification non trouvée"
            )
        
        # Mettre à jour les champs spécifiés
        if update_data.statut is not None:
            notification.statut = update_data.statut.value
            
            # Si le statut devient "envoyé", mettre à jour la date d'envoi
            if update_data.statut.value == "envoyé" and not notification.date_envoi:
                notification.date_envoi = datetime.now()
        
        if update_data.erreur is not None:
            notification.erreur = update_data.erreur
        
        if update_data.tentative is not None:
            notification.tentative = update_data.tentative
        
        db.commit()
        db.refresh(notification)
        
        return ReponseNotification(
            id=str(notification.id),
            type=notification.type,
            destinataire=notification.destinataire,
            sujet=notification.sujet,
            contenu=notification.contenu,
            statut=notification.statut,
            tentative=notification.tentative,
            erreur=notification.erreur,
            date_creation=notification.date_creation,
            date_envoi=notification.date_envoi,
            utilisateur_id=str(notification.utilisateur_id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la mise à jour"
        )

@router.delete("/{notification_id}", response_model=None)
async def supprimer_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[Utilisateur] = Depends(get_current_user)
):
    """
    Supprime une notification
    
    Les utilisateurs peuvent supprimer leurs propres notifications
    Les administrateurs peuvent supprimer toutes les notifications
    """
    try:
        query = db.query(Notification).filter(Notification.id == notification_id)
        
        # Les utilisateurs normaux ne peuvent supprimer que leurs notifications
        if current_user.type_utilisateur != "administrateur":
            query = query.filter(Notification.utilisateur_id == current_user.id)
        
        notification = query.first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification non trouvée"
            )
        
        db.delete(notification)
        db.commit()
        
        logger.info(f"Notification supprimée: {notification_id}")
        
        return {"message": "Notification supprimée avec succès"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la suppression"
        )

@router.get("/statistiques/globales", response_model=StatistiquesNotifications)
async def obtenir_statistiques_notifications(
    db: Session = Depends(get_db),
    current_user: Optional[Utilisateur] = Depends(get_current_user)
):
    """
    Obtient les statistiques des notifications pour l'utilisateur connecté
    """
    try:
        # Filtrer par utilisateur sauf pour les admins
        base_query = db.query(Notification)
        if current_user.type_utilisateur != "administrateur":
            base_query = base_query.filter(Notification.utilisateur_id == current_user.id)
        
        # Statistiques générales
        total_notifications = base_query.count()
        en_attente = base_query.filter(Notification.statut == 'en_attente').count()
        envoyes = base_query.filter(Notification.statut == 'envoyé').count()
        echecs = base_query.filter(Notification.statut == 'échoué').count()
        
        # Statistiques par type
        emails_total = base_query.filter(Notification.type == 'email').count()
        sms_total = base_query.filter(Notification.type == 'sms').count()
        
        # Statistiques des dernières 24h
        since_24h = datetime.now() - timedelta(hours=24)
        derniere_24h_query = base_query.filter(Notification.date_creation >= since_24h)
        
        derniere_24h = {
            'total': derniere_24h_query.count(),
            'envoyes': derniere_24h_query.filter(Notification.statut == 'envoyé').count(),
            'echecs': derniere_24h_query.filter(Notification.statut == 'échoué').count(),
            'emails': derniere_24h_query.filter(Notification.type == 'email').count(),
            'sms': derniere_24h_query.filter(Notification.type == 'sms').count()
        }
        
        # Calcul du taux de succès
        taux_succes = 0.0
        if total_notifications > 0:
            taux_succes = (envoyes / total_notifications) * 100
        
        return StatistiquesNotifications(
            total_notifications=total_notifications,
            en_attente=en_attente,
            envoyes=envoyes,
            echecs=echecs,
            emails_total=emails_total,
            sms_total=sms_total,
            derniere_24h=derniere_24h,
            taux_succes=round(taux_succes, 2)
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors du calcul des statistiques"
        )

# Endpoints administratifs

@router.post("/admin/traiter-en-attente", response_model=ReponseProcessingNotifications)
async def traiter_notifications_en_attente(
    background_tasks: BackgroundTasks,
    executer_en_arriere_plan: bool = Query(True, description="Exécuter en arrière-plan"),
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN))
):
    """
    Déclenche le traitement des notifications en attente
    
    **Réservé aux administrateurs**
    """
    try:
        if executer_en_arriere_plan:
            background_tasks.add_task(process_notifications_background)
            return ReponseProcessingNotifications(
                message="Traitement des notifications démarré en arrière-plan",
                processed=0
            )
        else:
            result = await notification_dispatcher.process_pending_notifications()
            return ReponseProcessingNotifications(**result)
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement des notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors du traitement des notifications"
        )

@router.get("/admin/statistiques-dispatcher", response_model=StatistiquesDispatcher)
async def obtenir_statistiques_dispatcher(
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN))
):
    """
    Obtient les statistiques du dispatcher de notifications
    
    **Réservé aux administrateurs**
    """
    try:
        stats = notification_dispatcher.get_stats()
        
        return StatistiquesDispatcher(
            total_processed=stats['total_processed'],
            emails_sent=stats['emails_sent'],
            sms_sent=stats['sms_sent'],
            errors=stats['errors'],
            last_run=stats['last_run'],
            configuration={
                'enabled': stats['enabled'],
                'check_interval_seconds': stats['check_interval_seconds'],
                'batch_size': stats['batch_size'],
                'working_hours_enabled': stats['working_hours_enabled'],
                'rate_limiting_enabled': stats['rate_limiting_enabled'],
                'is_working_hours': stats['is_working_hours'],
                'is_running': stats['is_running']
            }
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération des statistiques"
        )

@router.post("/admin/reset-statistiques", response_model=None)
async def reset_statistiques_dispatcher(
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN))
):
    """
    Remet à zéro les statistiques du dispatcher
    
    **Réservé aux administrateurs**
    """
    try:
        notification_dispatcher.reset_stats()
        return {"message": "Statistiques remises à zéro avec succès"}
        
    except Exception as e:
        logger.error(f"Erreur lors de la remise à zéro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la remise à zéro"
        )

@router.get("/admin/test-connexions", response_model=Dict[str, Any])
async def tester_connexions_services(
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN))
):
    """
    Teste les connexions des services email et SMS
    
    **Réservé aux administrateurs**
    """
    try:
        # Test connexion email
        email_success, email_message = email_service.test_connection()
        email_config = email_service.get_config_info()
        
        # Test connexion SMS
        sms_success, sms_message = sms_service.test_connection()
        sms_config = sms_service.get_config_info()
        
        return {
            "email": {
                "success": email_success,
                "message": email_message,
                "configuration": email_config
            },
            "sms": {
                "success": sms_success,
                "message": sms_message,
                "configuration": sms_config
            },
            "test_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erreur lors du test des connexions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors du test des connexions"
        )

@router.get("/admin/configuration", response_model=ConfigurationService)
async def obtenir_configuration_services(
    contexte_acces: Dict[str, Any] = Depends(require_niveau_acces(AccessLevel.ADMIN))
):
    """
    Obtient la configuration complète des services de notification
    
    **Réservé aux administrateurs**
    """
    try:
        return ConfigurationService(
            email_service=email_service.get_config_info(),
            sms_service=sms_service.get_config_info(),
            dispatcher=notification_dispatcher.get_stats(),
            rate_limiting=notification_dispatcher.rate_limiting_config
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération de la configuration"
        )
