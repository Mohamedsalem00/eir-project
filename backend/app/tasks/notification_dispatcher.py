"""
Dispatcher de notifications pour le système EIR Project
Gestion automatique des notifications en attente avec retry et planification
Compatible avec APScheduler et BackgroundTasks de FastAPI
"""

import asyncio
import logging
import yaml
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pathlib import Path

from ..core.database import get_db_session
from ..models.notification import Notification
from ..models.utilisateur import Utilisateur
from ..services.email_service import email_service
from ..services.sms_service import sms_service

logger = logging.getLogger(__name__)

class NotificationDispatcher:
    """
    Dispatcher pour traiter automatiquement les notifications en attente
    Supporte les retry automatiques et la planification avec APScheduler
    """
    
    def __init__(self, config_file: str = "config/notifications.yml"):
        """
        Initialise le dispatcher avec la configuration
        
        Args:
            config_file: Chemin vers le fichier de configuration YAML
        """
        self.config = self._load_config(config_file)
        self.scheduler_config = self.config.get('notifications', {}).get('scheduler', {})
        self.rate_limiting_config = self.config.get('notifications', {}).get('rate_limiting', {})
        
        # Configuration du scheduler
        self.enabled = self.scheduler_config.get('enabled', True)
        self.check_interval = self.scheduler_config.get('check_interval_seconds', 60)
        self.batch_size = self.scheduler_config.get('batch_size', 50)
        self.max_execution_time = self.scheduler_config.get('max_execution_time_seconds', 300)
        
        # Configuration des heures de fonctionnement
        self.working_hours_config = self.scheduler_config.get('working_hours', {})
        self.working_hours_enabled = self.working_hours_config.get('enabled', False)
        self.start_time = self.working_hours_config.get('start_time', '08:00')
        self.end_time = self.working_hours_config.get('end_time', '20:00')
        self.timezone = self.working_hours_config.get('timezone', 'Europe/Paris')
        
        # Configuration du rate limiting
        self.rate_limiting_enabled = self.rate_limiting_config.get('enabled', True)
        
        # Tracking des statistiques
        self.stats = {
            'total_processed': 0,
            'emails_sent': 0,
            'sms_sent': 0,
            'errors': 0,
            'last_run': None,
            'is_running': False
        }
        
        logger.info(f"NotificationDispatcher initialisé - Enabled: {self.enabled}, Interval: {self.check_interval}s")
    
    def _load_config(self, config_file: str) -> Dict:
        """
        Charge la configuration depuis le fichier YAML
        
        Args:
            config_file: Chemin vers le fichier de configuration
            
        Returns:
            Configuration chargée
        """
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Fichier de configuration non trouvé: {config_file}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """
        Configuration par défaut en cas d'erreur de chargement
        
        Returns:
            Configuration par défaut
        """
        return {
            'notifications': {
                'scheduler': {
                    'enabled': True,
                    'check_interval_seconds': 60,
                    'batch_size': 50,
                    'max_execution_time_seconds': 300
                },
                'rate_limiting': {
                    'enabled': True,
                    'email': {
                        'per_user_per_hour': 10,
                        'per_user_per_day': 50,
                        'global_per_minute': 100
                    },
                    'sms': {
                        'per_user_per_hour': 5,
                        'per_user_per_day': 20,
                        'global_per_minute': 50
                    }
                }
            }
        }
    
    def _is_working_hours(self) -> bool:
        """
        Vérifie si nous sommes dans les heures de fonctionnement configurées
        
        Returns:
            True si nous sommes dans les heures de travail
        """
        if not self.working_hours_enabled:
            return True
        
        try:
            from datetime import time
            import pytz
            
            # Obtenir l'heure actuelle dans le timezone configuré
            tz = pytz.timezone(self.timezone)
            current_time = datetime.now(tz).time()
            
            # Parser les heures de début et fin
            start_hour, start_minute = map(int, self.start_time.split(':'))
            end_hour, end_minute = map(int, self.end_time.split(':'))
            
            start_time = time(start_hour, start_minute)
            end_time = time(end_hour, end_minute)
            
            return start_time <= current_time <= end_time
            
        except Exception as e:
            logger.warning(f"Erreur lors de la vérification des heures de travail: {e}")
            return True  # Par défaut, autoriser l'envoi
    
    async def _check_rate_limit(self, user_id: str, notification_type: str, db: Session) -> bool:
        """
        Vérifie les limites de débit pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            notification_type: Type de notification (email, sms)
            db: Session de base de données
            
        Returns:
            True si la limite n'est pas dépassée
        """
        if not self.rate_limiting_enabled:
            return True
        
        try:
            type_config = self.rate_limiting_config.get(notification_type, {})
            per_hour_limit = type_config.get('per_user_per_hour', 10)
            per_day_limit = type_config.get('per_user_per_day', 50)
            global_per_minute = type_config.get('global_per_minute', 100)
            
            now = datetime.now()
            one_hour_ago = now - timedelta(hours=1)
            one_day_ago = now - timedelta(days=1)
            one_minute_ago = now - timedelta(minutes=1)
            
            # Vérifier la limite par utilisateur par heure
            hourly_count = db.query(Notification).filter(
                and_(
                    Notification.utilisateur_id == user_id,
                    Notification.type == notification_type,
                    Notification.statut == 'envoyé',
                    Notification.date_envoi >= one_hour_ago
                )
            ).count()
            
            if hourly_count >= per_hour_limit:
                logger.warning(f"Limite horaire dépassée pour utilisateur {user_id}: {hourly_count}/{per_hour_limit}")
                return False
            
            # Vérifier la limite par utilisateur par jour
            daily_count = db.query(Notification).filter(
                and_(
                    Notification.utilisateur_id == user_id,
                    Notification.type == notification_type,
                    Notification.statut == 'envoyé',
                    Notification.date_envoi >= one_day_ago
                )
            ).count()
            
            if daily_count >= per_day_limit:
                logger.warning(f"Limite quotidienne dépassée pour utilisateur {user_id}: {daily_count}/{per_day_limit}")
                return False
            
            # Vérifier la limite globale par minute
            global_count = db.query(Notification).filter(
                and_(
                    Notification.type == notification_type,
                    Notification.statut == 'envoyé',
                    Notification.date_envoi >= one_minute_ago
                )
            ).count()
            
            if global_count >= global_per_minute:
                logger.warning(f"Limite globale par minute dépassée: {global_count}/{global_per_minute}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du rate limiting: {e}")
            return True  # En cas d'erreur, autoriser l'envoi
    
    async def _get_pending_notifications(self, db: Session) -> List[Notification]:
        """
        Récupère les notifications en attente à traiter
        
        Args:
            db: Session de base de données
            
        Returns:
            Liste des notifications en attente
        """
        try:
            # Récupérer les notifications en attente, limitées par batch_size
            notifications = db.query(Notification).filter(
                and_(
                    Notification.statut == 'en_attente',
                    or_(
                        Notification.tentative < 3,  # Limite de tentatives
                        Notification.tentative.is_(None)
                    )
                )
            ).order_by(Notification.date_creation).limit(self.batch_size).all()
            
            return notifications
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des notifications: {e}")
            return []
    
    async def _send_notification(self, notification: Notification, db: Session) -> bool:
        """
        Envoie une notification individuelle
        
        Args:
            notification: Notification à envoyer
            db: Session de base de données
            
        Returns:
            True si l'envoi a réussi
        """
        try:
            # Incrémenter le nombre de tentatives
            notification.tentative = (notification.tentative or 0) + 1
            
            # Vérifier les limites de débit
            rate_limit_ok = await self._check_rate_limit(
                str(notification.utilisateur_id), 
                notification.type, 
                db
            )
            
            if not rate_limit_ok:
                notification.erreur = "Limite de débit dépassée"
                db.commit()
                return False
            
            success = False
            error_message = None
            
            # Envoyer selon le type
            if notification.type == 'email':
                success, error_message = await email_service.send_email_async(
                    notification.destinataire,
                    notification.sujet or "Notification EIR Project",
                    notification.contenu
                )
                if success:
                    self.stats['emails_sent'] += 1
                    
            elif notification.type == 'sms':
                success, error_message = await sms_service.send_sms_async(
                    notification.destinataire,
                    notification.contenu
                )
                if success:
                    self.stats['sms_sent'] += 1
                    
            else:
                error_message = f"Type de notification non supporté: {notification.type}"
            
            # Mettre à jour le statut de la notification
            if success:
                notification.statut = 'envoyé'
                notification.date_envoi = datetime.now()
                notification.erreur = None
                logger.info(f"Notification {notification.id} envoyée avec succès ({notification.type})")
            else:
                notification.statut = 'échoué' if notification.tentative >= 3 else 'en_attente'
                notification.erreur = error_message
                logger.error(f"Échec envoi notification {notification.id}: {error_message}")
                self.stats['errors'] += 1
            
            db.commit()
            return success
            
        except Exception as e:
            error_msg = f"Erreur lors de l'envoi de la notification {notification.id}: {str(e)}"
            logger.error(error_msg)
            
            try:
                notification.statut = 'échoué' if notification.tentative >= 3 else 'en_attente'
                notification.erreur = error_msg
                db.commit()
            except Exception as commit_error:
                logger.error(f"Erreur lors de la sauvegarde de l'erreur: {commit_error}")
            
            self.stats['errors'] += 1
            return False
    
    async def process_pending_notifications(self) -> Dict[str, Any]:
        """
        Traite toutes les notifications en attente
        
        Returns:
            Statistiques du traitement
        """
        if not self.enabled:
            return {'message': 'Dispatcher désactivé', 'processed': 0}
        
        if self.stats['is_running']:
            return {'message': 'Traitement déjà en cours', 'processed': 0}
        
        if not self._is_working_hours():
            return {'message': 'Hors heures de fonctionnement', 'processed': 0}
        
        self.stats['is_running'] = True
        start_time = datetime.now()
        processed_count = 0
        
        try:
            db = next(get_db_session())
            
            # Récupérer les notifications en attente
            notifications = await self._get_pending_notifications(db)
            
            if not notifications:
                logger.debug("Aucune notification en attente")
                return {'message': 'Aucune notification en attente', 'processed': 0}
            
            logger.info(f"Traitement de {len(notifications)} notifications en attente")
            
            # Traiter chaque notification
            for notification in notifications:
                # Vérifier le temps d'exécution maximum
                if (datetime.now() - start_time).seconds > self.max_execution_time:
                    logger.warning("Temps d'exécution maximum atteint, arrêt du traitement")
                    break
                
                success = await self._send_notification(notification, db)
                processed_count += 1
                self.stats['total_processed'] += 1
                
                # Petite pause entre les envois pour éviter la surcharge
                await asyncio.sleep(0.1)
            
            self.stats['last_run'] = datetime.now()
            
            logger.info(f"Traitement terminé: {processed_count} notifications traitées")
            
            return {
                'message': 'Traitement terminé',
                'processed': processed_count,
                'total_notifications': len(notifications),
                'execution_time_seconds': (datetime.now() - start_time).seconds,
                'stats': self.get_stats()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement des notifications: {e}")
            return {
                'error': str(e),
                'processed': processed_count,
                'execution_time_seconds': (datetime.now() - start_time).seconds
            }
        
        finally:
            self.stats['is_running'] = False
    
    async def send_immediate_notification(self, user_id: str, notification_type: str, 
                                        destinataire: str, sujet: Optional[str], 
                                        contenu: str) -> Dict[str, Any]:
        """
        Envoie une notification immédiatement (bypass de la queue)
        
        Args:
            user_id: ID de l'utilisateur
            notification_type: Type de notification (email, sms)
            destinataire: Destinataire (email ou téléphone)
            sujet: Sujet (pour email uniquement)
            contenu: Contenu du message
            
        Returns:
            Résultat de l'envoi
        """
        try:
            db = next(get_db_session())
            
            # Créer une notification temporaire
            notification = Notification(
                type=notification_type,
                destinataire=destinataire,
                sujet=sujet,
                contenu=contenu,
                statut='en_attente',
                utilisateur_id=user_id
            )
            
            # Tenter l'envoi immédiat
            success = await self._send_notification(notification, db)
            
            if success:
                # Sauvegarder la notification si l'envoi a réussi
                db.add(notification)
                db.commit()
                
                return {
                    'success': True,
                    'message': 'Notification envoyée immédiatement',
                    'notification_id': str(notification.id)
                }
            else:
                # Sauvegarder la notification avec l'erreur pour retry ultérieur
                db.add(notification)
                db.commit()
                
                return {
                    'success': False,
                    'message': 'Échec envoi immédiat, notification ajoutée à la queue',
                    'notification_id': str(notification.id),
                    'error': notification.erreur
                }
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi immédiat: {e}")
            return {
                'success': False,
                'message': f'Erreur lors de l\'envoi immédiat: {str(e)}'
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du dispatcher
        
        Returns:
            Statistiques actuelles
        """
        return {
            **self.stats,
            'enabled': self.enabled,
            'check_interval_seconds': self.check_interval,
            'batch_size': self.batch_size,
            'working_hours_enabled': self.working_hours_enabled,
            'rate_limiting_enabled': self.rate_limiting_enabled,
            'is_working_hours': self._is_working_hours()
        }
    
    def reset_stats(self):
        """
        Remet à zéro les statistiques
        """
        self.stats = {
            'total_processed': 0,
            'emails_sent': 0,
            'sms_sent': 0,
            'errors': 0,
            'last_run': None,
            'is_running': False
        }
        logger.info("Statistiques du dispatcher remises à zéro")

# Instance globale pour utilisation dans l'application
notification_dispatcher = NotificationDispatcher()

# Fonction utilitaire pour FastAPI BackgroundTasks
async def process_notifications_background():
    """
    Fonction à utiliser avec FastAPI BackgroundTasks
    """
    return await notification_dispatcher.process_pending_notifications()

# Fonction utilitaire pour envoi immédiat
async def send_notification_now(user_id: str, notification_type: str, 
                               destinataire: str, sujet: Optional[str], 
                               contenu: str) -> Dict[str, Any]:
    """
    Envoie une notification immédiatement
    
    Args:
        user_id: ID de l'utilisateur
        notification_type: Type de notification (email, sms)
        destinataire: Destinataire (email ou téléphone)
        sujet: Sujet (pour email uniquement)
        contenu: Contenu du message
        
    Returns:
        Résultat de l'envoi
    """
    return await notification_dispatcher.send_immediate_notification(
        user_id, notification_type, destinataire, sujet, contenu
    )
