# Tasks package
"""
Package pour les tâches en arrière-plan du système EIR Project
Inclut le dispatcher de notifications et le planificateur APScheduler
"""

from .notification_dispatcher import (
    notification_dispatcher,
    send_notification_now,
    process_notifications_background
)

from .notification_scheduler import (
    notification_scheduler,
    start_notification_scheduler,
    stop_notification_scheduler,
    get_scheduler_status,
    trigger_notification_job
)

__all__ = [
    'notification_dispatcher',
    'send_notification_now', 
    'process_notifications_background',
    'notification_scheduler',
    'start_notification_scheduler',
    'stop_notification_scheduler',
    'get_scheduler_status',
    'trigger_notification_job'
]
