"""
Router FastAPI pour la gestion des notifications EIR Project
Fournit les endpoints pour créer, lister, envoyer et gérer les notifications
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
import logging
import time

from ..core.dependencies import get_db, get_current_user, get_admin_user
from ..services.email_service import send_email
from ..services.sms_service import send_sms
from ..models.notification import Notification
from ..models.utilisateur import Utilisateur

# Import essential schemas with fallback
try:
    from ..schemas.notifications import (
        CreationNotification, ReponseNotification, ReponseListeNotifications,
        StatistiquesNotifications, ReponseEnvoiImmediat,
        EnvoiNotificationAdmin, EnvoiNotificationLotAdmin, ReponseEnvoiLotAdmin,
        EnvoiNotificationLotAdminParEmail, EnvoiNotificationAdminParId
    )
except ImportError:
    # Fallback minimal schemas
    from pydantic import BaseModel
    from enum import Enum
    
    class NotificationType(str, Enum):
        EMAIL = "email"
        SMS = "sms"
    
    class CreationNotification(BaseModel):
        type: str
        destinataire: str
        sujet: Optional[str] = None
        contenu: str
        utilisateur_id: Optional[str] = None
        envoyer_immediatement: bool = False
    
    class ReponseNotification(BaseModel):
        id: str
        type: str
        destinataire: str
        sujet: Optional[str]
        contenu: str
        statut: str
        tentative: int
        erreur: Optional[str]
        date_creation: datetime
        date_envoi: Optional[datetime]
        utilisateur_id: str
    
    class ReponseListeNotifications(BaseModel):
        notifications: List[ReponseNotification]
        total: int
        page: int
        taille_page: int
        total_pages: int
    
    class StatistiquesNotifications(BaseModel):
        total_notifications: int
        en_attente: int
        envoyes: int
        echecs: int
        emails_total: int
        sms_total: int
        derniere_24h: Dict[str, int]
        taux_succes: float
    
    class ReponseEnvoiImmediat(BaseModel):
        success: bool
        message: str
        notification_id: str
        destinataire: str
        type: str
    
    class EnvoiNotificationAdmin(BaseModel):
        utilisateur_id: str
        type: str
        destinataire: Optional[str] = None
        sujet: str
        contenu: str
        priorite: str = "normale"
    
    class EnvoiNotificationLotAdmin(BaseModel):
        utilisateurs_ids: List[str]
        type: str
        sujet: str
        contenu: str
        priorite: str = "normale"
        filtre_utilisateurs_actifs: bool = True
    
    class ReponseEnvoiLotAdmin(BaseModel):
        total_utilisateurs: int
        envoyes_succes: int
        envoyes_echec: int
        utilisateurs_introuvables: List[str]
        utilisateurs_inactifs: List[str]
        details_envois: List[Dict[str, Any]]
        duree_traitement_secondes: float

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=Dict[str, str])
async def test_notifications():
    """Test endpoint pour vérifier que le router fonctionne"""
    return {"message": "Router notifications opérationnel", "status": "OK"}

@router.get("/statistiques/globales", response_model=StatistiquesNotifications)
async def obtenir_statistiques_notifications(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
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

@router.post("/admin/envoyer-a-utilisateur", response_model=ReponseEnvoiImmediat)
async def admin_envoyer_notification_utilisateur(
    notification_data: EnvoiNotificationAdmin,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """
    Permet à un administrateur d'envoyer une notification à un utilisateur spécifique via son email
    
    **Réservé aux administrateurs**
    **Pratique: Utilisez l'email de l'utilisateur au lieu de son ID**
    """
    try:
        # Vérifier que l'utilisateur destinataire existe par email
        utilisateur_cible = db.query(Utilisateur).filter(
            Utilisateur.email == notification_data.email_utilisateur
        ).first()
        
        if not utilisateur_cible:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Utilisateur avec l'email {notification_data.email_utilisateur} introuvable"
            )
        
        # Pour les emails, utiliser automatiquement l'email de l'utilisateur
        destinataire_effectif = utilisateur_cible.email
        
        if not destinataire_effectif:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"L'utilisateur {notification_data.email_utilisateur} n'a pas d'adresse email valide"
            )
        
        # Valider le type de notification (maintenant seulement email)
        if notification_data.type != "email":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce endpoint ne supporte que les emails (type='email')"
            )
        
        # Envoyer l'email (type vérifié par le validateur Pydantic)
        envoi_reussi = False
        erreur_envoi = None
        
        try:
            if not notification_data.sujet:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Le sujet est requis pour les emails"
                )
            
            envoi_reussi, erreur_envoi = await send_email(
                to_email=destinataire_effectif,
                subject=notification_data.sujet,
                content=notification_data.contenu
            )
            
            if not envoi_reussi:
                raise Exception(f"Échec de l'envoi: {erreur_envoi}")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification: {e}")
            # Créer la notification avec statut d'échec
            notification = Notification(
                id=uuid.uuid4(),
                type=notification_data.type,
                destinataire=destinataire_effectif,
                sujet=notification_data.sujet,
                contenu=notification_data.contenu,
                statut='échoué',
                tentative=1,
                erreur=str(e),
                source='admin',  # Notification envoyée par admin
                utilisateur_id=str(utilisateur_cible.id),  # Utiliser l'ID trouvé par email
                date_creation=datetime.now()
            )
            
            db.add(notification)
            db.commit()
            
            return ReponseEnvoiImmediat(
                success=False,
                message=f"Échec de l'envoi de la notification: {erreur_envoi or str(e)}",
                notification_id=str(notification.id),
                destinataire=destinataire_effectif,
                type=notification_data.type,
                error=erreur_envoi or str(e)
            )
        
        # Créer la notification avec statut de succès
        notification = Notification(
            id=uuid.uuid4(),
            type=notification_data.type,
            destinataire=destinataire_effectif,
            sujet=notification_data.sujet,
            contenu=notification_data.contenu,
            statut='envoyé',
            tentative=1,
            source='admin',  # Notification envoyée par admin
            utilisateur_id=str(utilisateur_cible.id),  # Utiliser l'ID trouvé par email
            date_creation=datetime.now(),
            date_envoi=datetime.now()
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        logger.info(f"Notification administrative envoyée via email {notification_data.email_utilisateur}: {notification.id}")
        
        return ReponseEnvoiImmediat(
            success=True,
            message=f"Notification administrative envoyée avec succès à {utilisateur_cible.nom} ({notification_data.email_utilisateur})",
            notification_id=str(notification.id),
            destinataire=destinataire_effectif,
            type=notification_data.type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi administrateur par ID (legacy): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'envoi de la notification administrative par ID"
        )

@router.post("/admin/envoyer-lot-utilisateurs", response_model=ReponseEnvoiLotAdmin)
async def admin_envoyer_notifications_lot(
    notification_data: EnvoiNotificationLotAdmin,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """
    Permet à un administrateur d'envoyer des notifications en lot à plusieurs utilisateurs
    
    **Réservé aux administrateurs**
    """
    import time
    debut_traitement = time.time()
    
    try:
        # Récupérer les utilisateurs ciblés
        query = db.query(Utilisateur).filter(Utilisateur.id.in_(notification_data.utilisateurs_ids))
        
        if notification_data.filtre_utilisateurs_actifs:
            query = query.filter(Utilisateur.est_actif == True)
        
        utilisateurs_valides = query.all()
        
        # Préparer les listes de tracking
        utilisateurs_introuvables = []
        envoyes_succes = 0
        envoyes_echec = 0
        details_envois = []
        
        # Identifier les utilisateurs introuvables
        ids_trouves = {str(u.id) for u in utilisateurs_valides}
        utilisateurs_introuvables = [uid for uid in notification_data.utilisateurs_ids if uid not in ids_trouves]
        
        # Traiter chaque utilisateur valide
        for utilisateur in utilisateurs_valides:
            try:
                # Déterminer le destinataire selon le type de notification
                destinataire_effectif = None
                
                if notification_data.type == "email":
                    if not utilisateur.email:
                        details_envois.append({
                            "utilisateur_id": str(utilisateur.id),
                            "nom": utilisateur.nom,
                            "statut": "échec",
                            "erreur": "Utilisateur sans adresse email"
                        })
                        envoyes_echec += 1
                        continue
                    destinataire_effectif = utilisateur.email
                    
                elif notification_data.type == "sms":
                    if not hasattr(utilisateur, 'telephone') or not utilisateur.telephone:
                        details_envois.append({
                            "utilisateur_id": str(utilisateur.id),
                            "nom": utilisateur.nom,
                            "statut": "échec",
                            "erreur": "Utilisateur sans numéro de téléphone"
                        })
                        envoyes_echec += 1
                        continue
                    destinataire_effectif = utilisateur.telephone
                else:
                    details_envois.append({
                        "utilisateur_id": str(utilisateur.id),
                        "nom": utilisateur.nom,
                        "statut": "échec",
                        "erreur": "Type de notification invalide"
                    })
                    envoyes_echec += 1
                    continue
                
                # Envoyer la notification
                envoi_reussi = False
                erreur_envoi = None
                
                try:
                    if notification_data.type == "email":
                        if not notification_data.sujet:
                            raise Exception("Le sujet est requis pour les emails")
                        
                        envoi_reussi, erreur_envoi = await send_email(
                            to_email=destinataire_effectif,
                            subject=notification_data.sujet,
                            content=notification_data.contenu
                        )
                        
                    elif notification_data.type == "sms":
                        envoi_reussi, erreur_envoi = await send_sms(
                            to_phone=destinataire_effectif,
                            message=notification_data.contenu
                        )
                    
                    if not envoi_reussi:
                        raise Exception(f"Échec de l'envoi: {erreur_envoi}")
                        
                except Exception as e_envoi:
                    # Créer la notification avec statut d'échec
                    notification = Notification(
                        id=uuid.uuid4(),
                        type=notification_data.type,
                        destinataire=destinataire_effectif,
                        sujet=notification_data.sujet,
                        contenu=notification_data.contenu,
                        statut='échoué',
                        tentative=1,
                        erreur=str(e_envoi),
                    source='admin',  # Notification lot admin
                    utilisateur_id=str(utilisateur.id),
                    date_creation=datetime.now()
                )
                
                db.add(notification)
                db.commit()
                
                envoyes_echec += 1
                details_envois.append({
                    "utilisateur_id": str(utilisateur.id),
                    "nom": utilisateur.nom,
                    "destinataire": destinataire_effectif,
                    "statut": "échec",
                    "erreur": str(e_envoi),
                    "notification_id": str(notification.id)
                })
                continue
                
                # Créer la notification avec statut de succès
                notification = Notification(
                    id=uuid.uuid4(),
                    type=notification_data.type,
                    destinataire=destinataire_effectif,
                    sujet=notification_data.sujet,
                    contenu=notification_data.contenu,
                    statut='envoyé',
                    tentative=1,
                    source='admin',  # Notification lot admin
                    utilisateur_id=str(utilisateur.id),
                    date_creation=datetime.now(),
                    date_envoi=datetime.now()
                )
                
                db.add(notification)
                db.commit()
                
                envoyes_succes += 1
                details_envois.append({
                    "utilisateur_id": str(utilisateur.id),
                    "nom": utilisateur.nom,
                    "destinataire": destinataire_effectif,
                    "statut": "succès",
                    "notification_id": str(notification.id)
                })
                    
            except Exception as e:
                envoyes_echec += 1
                details_envois.append({
                    "utilisateur_id": str(utilisateur.id),
                    "nom": utilisateur.nom,
                    "statut": "échec",
                    "erreur": str(e)
                })
        
        duree_traitement = time.time() - debut_traitement
        
        logger.info(f"Envoi lot administrateur terminé: {envoyes_succes} succès, {envoyes_echec} échecs")
        
        return ReponseEnvoiLotAdmin(
            total_utilisateurs=len(notification_data.utilisateurs_ids),
            envoyes_succes=envoyes_succes,
            envoyes_echec=envoyes_echec,
            utilisateurs_introuvables=utilisateurs_introuvables,
            utilisateurs_inactifs=[],
            details_envois=details_envois,
            duree_traitement_secondes=round(duree_traitement, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi en lot administrateur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'envoi en lot de notifications administratives"
        )

@router.post("/admin/envoyer-lot-emails", response_model=ReponseEnvoiLotAdmin)
async def admin_envoyer_notifications_lot_par_emails(
    notification_data: EnvoiNotificationLotAdminParEmail,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """
    Permet à un administrateur d'envoyer des notifications en lot en utilisant les adresses email
    
    **Réservé aux administrateurs**
    **Pratique: Utilisez les emails directement au lieu des UUIDs**
    """
    debut_traitement = time.time()
    
    try:
        # Récupérer les utilisateurs par email
        query = db.query(Utilisateur).filter(Utilisateur.email.in_(notification_data.emails))
        
        if notification_data.filtre_utilisateurs_actifs:
            query = query.filter(Utilisateur.est_actif == True)
        
        utilisateurs_valides = query.all()
        
        # Préparer les listes de tracking
        emails_introuvables = []
        envoyes_succes = 0
        envoyes_echec = 0
        details_envois = []
        
        # Identifier les emails introuvables
        emails_trouves = {u.email for u in utilisateurs_valides}
        emails_introuvables = [email for email in notification_data.emails if email not in emails_trouves]
        
        # Traiter chaque utilisateur valide
        for utilisateur in utilisateurs_valides:
            try:
                # Pour les notifications par email, on utilise toujours l'email de l'utilisateur
                if notification_data.type != "email":
                    details_envois.append({
                        "utilisateur_id": str(utilisateur.id),
                        "nom": utilisateur.nom,
                        "email": utilisateur.email,
                        "statut": "échec",
                        "erreur": "Ce endpoint ne supporte que les emails (type=email)"
                    })
                    envoyes_echec += 1
                    continue
                
                if not notification_data.sujet:
                    details_envois.append({
                        "utilisateur_id": str(utilisateur.id),
                        "nom": utilisateur.nom,
                        "email": utilisateur.email,
                        "statut": "échec",
                        "erreur": "Le sujet est requis pour les emails"
                    })
                    envoyes_echec += 1
                    continue
                
                # Envoyer l'email
                envoi_reussi = False
                erreur_envoi = None
                
                try:
                    envoi_reussi, erreur_envoi = await send_email(
                        to_email=utilisateur.email,
                        subject=notification_data.sujet,
                        content=notification_data.contenu
                    )
                    
                    if not envoi_reussi:
                        raise Exception(f"Échec de l'envoi: {erreur_envoi}")
                        
                except Exception as e_envoi:
                    # Créer la notification avec statut d'échec
                    notification = Notification(
                        id=uuid.uuid4(),
                        type="email",
                        destinataire=utilisateur.email,
                        sujet=notification_data.sujet,
                        contenu=notification_data.contenu,
                        statut='échoué',
                        tentative=1,
                        erreur=str(e_envoi),
                        source='admin',  # Notification admin par email
                        utilisateur_id=str(utilisateur.id),
                        date_creation=datetime.now()
                    )
                    
                    db.add(notification)
                    db.commit()
                    
                    envoyes_echec += 1
                    details_envois.append({
                        "utilisateur_id": str(utilisateur.id),
                        "nom": utilisateur.nom,
                        "email": utilisateur.email,
                        "statut": "échec",
                        "erreur": str(e_envoi),
                        "notification_id": str(notification.id)
                    })
                    continue
                
                # Créer la notification avec statut de succès
                notification = Notification(
                    id=uuid.uuid4(),
                    type="email",
                    destinataire=utilisateur.email,
                    sujet=notification_data.sujet,
                    contenu=notification_data.contenu,
                    statut='envoyé',
                    tentative=1,
                    source='admin',  # Notification admin par email
                    utilisateur_id=str(utilisateur.id),
                    date_creation=datetime.now(),
                    date_envoi=datetime.now()
                )
                
                db.add(notification)
                db.commit()
                
                envoyes_succes += 1
                details_envois.append({
                    "utilisateur_id": str(utilisateur.id),
                    "nom": utilisateur.nom,
                    "email": utilisateur.email,
                    "statut": "succès",
                    "notification_id": str(notification.id)
                })
                    
            except Exception as e:
                envoyes_echec += 1
                details_envois.append({
                    "utilisateur_id": str(utilisateur.id),
                    "nom": utilisateur.nom,
                    "email": utilisateur.email,
                    "statut": "échec",
                    "erreur": str(e)
                })
        
        duree_traitement = time.time() - debut_traitement
        
        logger.info(f"Envoi lot admin par emails terminé: {envoyes_succes} succès, {envoyes_echec} échecs")
        
        return ReponseEnvoiLotAdmin(
            total_utilisateurs=len(notification_data.emails),
            envoyes_succes=envoyes_succes,
            envoyes_echec=envoyes_echec,
            utilisateurs_introuvables=emails_introuvables,  # Ici ce sont les emails introuvables
            utilisateurs_inactifs=[],
            details_envois=details_envois,
            duree_traitement_secondes=round(duree_traitement, 2)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi en lot par emails: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'envoi en lot de notifications par email"
        )

@router.get("/admin/liste-utilisateurs", response_model=List[Dict[str, Any]])
async def admin_lister_utilisateurs_pour_notifications(
    actifs_seulement: bool = Query(True, description="Lister seulement les utilisateurs actifs"),
    avec_email: bool = Query(True, description="Lister seulement les utilisateurs avec email"),
    recherche: Optional[str] = Query(None, description="Rechercher par nom ou email"),
    limite: int = Query(50, le=100, description="Limite du nombre de résultats"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """
    Liste les utilisateurs disponibles pour l'envoi de notifications administratives
    
    **Réservé aux administrateurs**
    """
    try:
        # Construire la requête de base
        query = db.query(Utilisateur)
        
        # Appliquer les filtres
        if actifs_seulement:
            query = query.filter(Utilisateur.est_actif == True)
        
        if avec_email:
            query = query.filter(Utilisateur.email.isnot(None), Utilisateur.email != '')
        
        if recherche:
            terme_recherche = f"%{recherche}%"
            query = query.filter(
                or_(
                    Utilisateur.nom.ilike(terme_recherche),
                    Utilisateur.email.ilike(terme_recherche)
                )
            )
        
        # Limiter les résultats et ordonner
        utilisateurs = query.order_by(Utilisateur.nom).limit(limite).all()
        
        # Formater la réponse
        utilisateurs_formated = [
            {
                "id": str(utilisateur.id),
                "nom": utilisateur.nom,
                "email": utilisateur.email,
                "type_utilisateur": utilisateur.type_utilisateur,
                "niveau_acces": getattr(utilisateur, 'niveau_acces', None),
                "organisation": getattr(utilisateur, 'organisation', None),
                "est_actif": getattr(utilisateur, 'est_actif', True),
                "date_creation": utilisateur.date_creation.isoformat() if hasattr(utilisateur, 'date_creation') and utilisateur.date_creation else None
            }
            for utilisateur in utilisateurs
        ]
        
        logger.info(f"Admin consultation liste utilisateurs: {len(utilisateurs_formated)} résultats")
        
        return utilisateurs_formated
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des utilisateurs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération de la liste des utilisateurs"
        )

# Endpoints de test pour les administrateurs

@router.post("/admin/test-email", response_model=Dict[str, Any])
async def admin_test_email(
    email_test: str = Query(..., description="Adresse email de test"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """
    Teste l'envoi d'email pour les administrateurs
    
    **Réservé aux administrateurs**
    """
    try:
        sujet = "Test d'envoi d'email - EIR Project"
        contenu = f"""
        Bonjour,
        
        Ceci est un email de test envoyé depuis le système de notifications EIR Project.
        
        Détails du test:
        - Date: {datetime.now().strftime('%d/%m/%Y à %H:%M')}
        - Envoyé par: {current_user.nom} (Admin)
        - Système: EIR Notification System
        
        Si vous recevez cet email, la configuration email fonctionne correctement.
        
        Cordialement,
        L'équipe EIR Project
        """
        
        envoi_reussi, erreur_envoi = await send_email(
            to_email=email_test,
            subject=sujet,
            content=contenu
        )
        
        if envoi_reussi:
            logger.info(f"Test email réussi vers {email_test} par admin {current_user.id}")
            return {
                "success": True,
                "message": f"Email de test envoyé avec succès à {email_test}",
                "timestamp": datetime.now().isoformat(),
                "admin": current_user.nom
            }
        else:
            logger.error(f"Test email échoué vers {email_test}: {erreur_envoi}")
            return {
                "success": False,
                "message": f"Échec de l'envoi de l'email de test: {erreur_envoi}",
                "timestamp": datetime.now().isoformat(),
                "error": erreur_envoi
            }
            
    except Exception as e:
        logger.error(f"Erreur lors du test email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors du test email: {str(e)}"
        )

@router.post("/admin/test-sms", response_model=Dict[str, Any])
async def admin_test_sms(
    numero_test: str = Query(..., description="Numéro de téléphone de test"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """
    Teste l'envoi de SMS pour les administrateurs
    
    **Réservé aux administrateurs**
    """
    try:
        contenu = f"Test SMS EIR Project - {datetime.now().strftime('%d/%m/%Y %H:%M')} - Envoyé par: {current_user.nom} (Admin)"
        
        envoi_reussi, erreur_envoi = await send_sms(
            to_phone=numero_test,
            message=contenu
        )
        
        if envoi_reussi:
            logger.info(f"Test SMS réussi vers {numero_test} par admin {current_user.id}")
            return {
                "success": True,
                "message": f"SMS de test envoyé avec succès au {numero_test}",
                "timestamp": datetime.now().isoformat(),
                "admin": current_user.nom
            }
        else:
            logger.error(f"Test SMS échoué vers {numero_test}: {erreur_envoi}")
            return {
                "success": False,
                "message": f"Échec de l'envoi du SMS de test: {erreur_envoi}",
                "timestamp": datetime.now().isoformat(),
                "error": erreur_envoi
            }
            
    except Exception as e:
        logger.error(f"Erreur lors du test SMS: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne lors du test SMS: {str(e)}"
        )
