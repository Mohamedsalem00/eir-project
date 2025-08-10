"""
Planificateur APScheduler pour le traitement automatique des notifications
Démarre avec l'application FastAPI et traite les notifications en arrière-plan
"""

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from typing import Optional

from .notification_dispatcher import notification_dispatcher

logger = logging.getLogger(__name__)

class NotificationScheduler:
    """
    Planificateur pour le traitement automatique des notifications
    Utilise APScheduler pour exécuter le dispatcher périodiquement
    """
    
    def __init__(self):
        """
        Initialise le planificateur APScheduler
        """
        # Configuration du scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': AsyncIOExecutor()
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 1  # Une seule instance à la fois
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Europe/Paris'
        )
        
        self.is_running = False
        
        logger.info("NotificationScheduler initialisé")
    
    async def start(self):
        """
        Démarre le planificateur avec les tâches configurées
        """
        if self.is_running:
            logger.warning("Le planificateur est déjà en cours d'exécution")
            return
        
        try:
            # Ajouter la tâche principale de traitement des notifications
            self.scheduler.add_job(
                func=self._process_notifications_job,
                trigger=IntervalTrigger(
                    seconds=notification_dispatcher.check_interval
                ),
                id='process_notifications',
                name='Traitement des notifications en attente',
                replace_existing=True,
                misfire_grace_time=30  # 30 secondes de grâce si le job est en retard
            )
            
            # Ajouter une tâche de nettoyage quotidienne (à 2h du matin)
            self.scheduler.add_job(
                func=self._cleanup_notifications_job,
                trigger=CronTrigger(hour=2, minute=0),
                id='cleanup_notifications',
                name='Nettoyage des anciennes notifications',
                replace_existing=True
            )
            
            # Ajouter une tâche de statistiques (toutes les heures)
            self.scheduler.add_job(
                func=self._log_statistics_job,
                trigger=CronTrigger(minute=0),  # Chaque heure à la minute 0
                id='log_statistics',
                name='Log des statistiques de notifications',
                replace_existing=True
            )
            
            # Démarrer le scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info("NotificationScheduler démarré avec succès")
            logger.info(f"Tâche principale: toutes les {notification_dispatcher.check_interval} secondes")
            logger.info("Tâche de nettoyage: quotidienne à 2h00")
            logger.info("Tâche de statistiques: toutes les heures")
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage du planificateur: {e}")
            raise
    
    async def stop(self):
        """
        Arrête le planificateur proprement
        """
        if not self.is_running:
            logger.warning("Le planificateur n'est pas en cours d'exécution")
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("NotificationScheduler arrêté")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du planificateur: {e}")
    
    async def _process_notifications_job(self):
        """
        Tâche principale: traitement des notifications en attente
        """
        try:
            if not notification_dispatcher.enabled:
                logger.debug("Dispatcher de notifications désactivé")
                return
            
            # Vérifier les heures de fonctionnement
            if not notification_dispatcher._is_working_hours():
                logger.debug("Hors heures de fonctionnement")
                return
            
            # Éviter les exécutions simultanées
            if notification_dispatcher.stats['is_running']:
                logger.debug("Traitement déjà en cours, passage ignoré")
                return
            
            logger.debug("Démarrage du traitement planifié des notifications")
            
            # Exécuter le traitement
            result = await notification_dispatcher.process_pending_notifications()
            
            # Log du résultat
            if result.get('processed', 0) > 0:
                logger.info(f"Traitement planifié terminé: {result.get('processed')} notifications traitées")
            else:
                logger.debug(f"Traitement planifié: {result.get('message', 'Aucune notification')}")
                
        except Exception as e:
            logger.error(f"Erreur dans la tâche de traitement des notifications: {e}")
    
    async def _cleanup_notifications_job(self):
        """
        Tâche de nettoyage: supprime les anciennes notifications selon la configuration
        """
        try:
            from ..core.database import get_db_session
            from ..models.notification import Notification
            from datetime import timedelta
            from sqlalchemy import and_
            
            # Configuration de nettoyage
            cleanup_config = notification_dispatcher.config.get('notifications', {}).get('cleanup', {})
            
            if not cleanup_config.get('enabled', True):
                logger.debug("Nettoyage automatique désactivé")
                return
            
            delete_sent_after_days = cleanup_config.get('delete_sent_after_days', 30)
            delete_failed_after_days = cleanup_config.get('delete_failed_after_days', 7)
            
            db = next(get_db_session())
            
            current_time = datetime.now()
            
            # Supprimer les notifications envoyées anciennes
            sent_cutoff = current_time - timedelta(days=delete_sent_after_days)
            sent_deleted = db.query(Notification).filter(
                and_(
                    Notification.statut == 'envoyé',
                    Notification.date_envoi < sent_cutoff
                )
            ).delete(synchronize_session=False)
            
            # Supprimer les notifications échouées anciennes
            failed_cutoff = current_time - timedelta(days=delete_failed_after_days)
            failed_deleted = db.query(Notification).filter(
                and_(
                    Notification.statut == 'échoué',
                    Notification.date_creation < failed_cutoff
                )
            ).delete(synchronize_session=False)
            
            db.commit()
            
            if sent_deleted > 0 or failed_deleted > 0:
                logger.info(f"Nettoyage effectué: {sent_deleted} notifications envoyées supprimées, {failed_deleted} notifications échouées supprimées")
            else:
                logger.debug("Nettoyage effectué: aucune notification à supprimer")
                
        except Exception as e:
            logger.error(f"Erreur dans la tâche de nettoyage: {e}")
    
    async def _log_statistics_job(self):
        """
        Tâche de statistiques: log périodique des statistiques du système
        """
        try:
            stats = notification_dispatcher.get_stats()
            
            logger.info(f"[STATS] Total traité: {stats['total_processed']}, "
                       f"Emails: {stats['emails_sent']}, "
                       f"SMS: {stats['sms_sent']}, "
                       f"Erreurs: {stats['errors']}, "
                       f"Dernière exécution: {stats['last_run']}")
            
        except Exception as e:
            logger.error(f"Erreur dans la tâche de statistiques: {e}")
    
    def get_job_status(self) -> dict:
        """
        Retourne le statut des tâches planifiées
        
        Returns:
            Informations sur les tâches
        """
        if not self.is_running:
            return {'scheduler_running': False, 'jobs': []}
        
        jobs_info = []
        
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'next_run': next_run.isoformat() if next_run else None,
                'trigger': str(job.trigger)
            })
        
        return {
            'scheduler_running': self.is_running,
            'jobs': jobs_info,
            'scheduler_state': 'running' if self.scheduler.running else 'stopped'
        }
    
    async def trigger_job_now(self, job_id: str) -> dict:
        """
        Déclenche une tâche immédiatement
        
        Args:
            job_id: ID de la tâche à déclencher
            
        Returns:
            Résultat de l'exécution
        """
        try:
            if not self.is_running:
                return {'success': False, 'message': 'Planificateur non démarré'}
            
            job = self.scheduler.get_job(job_id)
            if not job:
                return {'success': False, 'message': f'Tâche {job_id} non trouvée'}
            
            # Déclencher la tâche
            if job_id == 'process_notifications':
                result = await self._process_notifications_job()
                return {'success': True, 'message': 'Tâche de traitement exécutée', 'result': result}
            elif job_id == 'cleanup_notifications':
                await self._cleanup_notifications_job()
                return {'success': True, 'message': 'Tâche de nettoyage exécutée'}
            elif job_id == 'log_statistics':
                await self._log_statistics_job()
                return {'success': True, 'message': 'Tâche de statistiques exécutée'}
            else:
                return {'success': False, 'message': f'Tâche {job_id} non supportée pour exécution manuelle'}
                
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution manuelle de la tâche {job_id}: {e}")
            return {'success': False, 'message': f'Erreur: {str(e)}'}

# Instance globale
notification_scheduler = NotificationScheduler()

# Fonctions utilitaires pour l'intégration FastAPI
async def start_notification_scheduler():
    """
    Démarre le planificateur de notifications
    À appeler au démarrage de l'application FastAPI
    """
    await notification_scheduler.start()

async def stop_notification_scheduler():
    """
    Arrête le planificateur de notifications
    À appeler à l'arrêt de l'application FastAPI
    """
    await notification_scheduler.stop()

def get_scheduler_status() -> dict:
    """
    Retourne le statut du planificateur
    """
    return notification_scheduler.get_job_status()

async def trigger_notification_job(job_id: str) -> dict:
    """
    Déclenche une tâche de notification manuellement
    """
    return await notification_scheduler.trigger_job_now(job_id)
