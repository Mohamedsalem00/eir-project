"""
Service d'envoi d'emails pour le système de notifications EIR Project
Supporte SMTP générique et Gmail avec configuration via variables d'environnement
Compatible Docker et async pour FastAPI
"""

import smtplib
import asyncio
import logging
import ssl
import yaml
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from typing import Dict, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class EmailService:
    """
    Service d'envoi d'emails avec support SMTP et Gmail
    Gestion des erreurs, retry automatique et configuration flexible
    """
    
    def __init__(self, config_file: str = None):
        """
        Initialise le service d'email avec la configuration
        Args:
            config_file: Chemin vers le fichier de configuration YAML
        """
        if config_file is None:
            config_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config",
                "notifications.yml"
            )
        self.config = self._load_config(config_file)
        self.email_config = self.config.get('notifications', {}).get('email', {})
        self.enabled = self.email_config.get('enabled', False)
        self.provider = self.email_config.get('provider', 'smtp')

        # Configuration du provider sélectionné
        if self.provider == 'gmail':
            self.smtp_config = self.email_config.get('gmail', {})
        else:
            self.smtp_config = self.email_config.get('smtp', {})

        # Configuration des retry
        self.retry_config = self.email_config.get('retry', {})
        self.max_attempts = self.retry_config.get('max_attempts', 3)
        self.retry_delay = self.retry_config.get('retry_delay_seconds', 300)
        self.exponential_backoff = self.retry_config.get('exponential_backoff', True)

        # Templates
        self.templates = self.email_config.get('templates', {})

        logger.info(f"EmailService initialisé - Provider: {self.provider}, Enabled: {self.enabled}, Config path: {config_file}")
    
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
                    content = f.read()
                    # Remplacer les variables d'environnement
                    content = self._replace_env_vars(content)
                    return yaml.safe_load(content)
            else:
                logger.warning(f"Fichier de configuration non trouvé: {config_file}")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            return self._get_default_config()
    
    def _replace_env_vars(self, content: str) -> str:
        """
        Remplace les variables d'environnement dans le contenu YAML
        Format: ${VAR_NAME:default_value}
        
        Args:
            content: Contenu YAML avec variables d'environnement
            
        Returns:
            Contenu avec variables remplacées
        """
        import re
        
        def replace_var(match):
            var_expr = match.group(1)
            if ':' in var_expr:
                var_name, default_value = var_expr.split(':', 1)
                return os.getenv(var_name, default_value)
            else:
                return os.getenv(var_expr, '')
        
        return re.sub(r'\$\{([^}]+)\}', replace_var, content)
    
    def _get_default_config(self) -> Dict:
        """
        Configuration par défaut en cas d'erreur de chargement
        
        Returns:
            Configuration par défaut
        """
        return {
            'notifications': {
                'email': {
                    'enabled': False,
                    'provider': 'smtp',
                    'smtp': {
                        'host': 'localhost',
                        'port': 587,
                        'use_tls': True,
                        'username': '',
                        'password': '',
                        'from_email': 'noreply@localhost',
                        'from_name': 'EIR Project'
                    },
                    'retry': {
                        'max_attempts': 3,
                        'retry_delay_seconds': 300,
                        'exponential_backoff': True
                    }
                }
            }
        }
    
    def _get_smtp_config(self) -> Tuple[str, int, bool, str, str, str, str]:
        """
        Extrait la configuration SMTP selon le provider
        
        Returns:
            Tuple (host, port, use_tls, username, password, from_email, from_name)
        """
        if self.provider == 'gmail':
            return (
                'smtp.gmail.com',
                587,
                True,
                self.smtp_config.get('username', ''),
                self.smtp_config.get('password', ''),
                self.smtp_config.get('from_email', ''),
                self.smtp_config.get('from_name', 'EIR Project')
            )
        else:
            return (
                self.smtp_config.get('host', 'localhost'),
                int(self.smtp_config.get('port', 587)),
                self.smtp_config.get('use_tls', True),
                self.smtp_config.get('username', ''),
                self.smtp_config.get('password', ''),
                self.smtp_config.get('from_email', 'noreply@localhost'),
                self.smtp_config.get('from_name', 'EIR Project')
            )
    
    def _create_message(self, to_email: str, subject: str, content: str, 
                       from_email: str, from_name: str) -> MIMEMultipart:
        """
        Crée un message email formaté
        
        Args:
            to_email: Adresse email destinataire
            subject: Sujet de l'email
            content: Contenu du message
            from_email: Adresse email expéditeur
            from_name: Nom de l'expéditeur
            
        Returns:
            Message email formaté
        """
        message = MIMEMultipart()
        message['From'] = formataddr((from_name, from_email))
        message['To'] = to_email
        message['Subject'] = subject or self.templates.get('default_subject', 'Notification EIR Project')
        
        # Ajouter le footer si configuré
        footer = self.templates.get('footer', '')
        full_content = content + footer
        
        # Attacher le contenu
        message.attach(MIMEText(full_content, 'plain', 'utf-8'))
        
        return message
    
    async def send_email_async(self, to_email: str, subject: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Envoie un email de manière asynchrone
        
        Args:
            to_email: Adresse email destinataire
            subject: Sujet de l'email
            content: Contenu du message
            
        Returns:
            Tuple (succès, message_erreur)
        """
        if not self.enabled:
            logger.warning("Service d'email désactivé")
            return False, "Service d'email désactivé dans la configuration"
        
        # Validation de base
        if not to_email or '@' not in to_email:
            error_msg = f"Adresse email invalide: {to_email}"
            logger.error(error_msg)
            return False, error_msg
        
        # Exécuter l'envoi dans un thread pour éviter de bloquer l'event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._send_email_sync, to_email, subject, content)
    
    def _send_email_sync(self, to_email: str, subject: str, content: str) -> Tuple[bool, Optional[str]]:
        """
        Envoie un email de manière synchrone avec retry automatique
        
        Args:
            to_email: Adresse email destinataire
            subject: Sujet de l'email
            content: Contenu du message
            
        Returns:
            Tuple (succès, message_erreur)
        """
        host, port, use_tls, username, password, from_email, from_name = self._get_smtp_config()
        
        if not username or not password:
            error_msg = "Configuration SMTP incomplète (username/password manquants)"
            logger.error(error_msg)
            return False, error_msg
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                # Créer le message
                message = self._create_message(to_email, subject, content, from_email, from_name)
                
                # Établir la connexion SMTP
                if use_tls:
                    context = ssl.create_default_context()
                    server = smtplib.SMTP(host, port)
                    server.starttls(context=context)
                else:
                    server = smtplib.SMTP(host, port)
                
                # Authentification
                if username and password:
                    server.login(username, password)
                
                # Envoyer l'email
                server.send_message(message)
                server.quit()
                
                logger.info(f"Email envoyé avec succès à {to_email} (tentative {attempt})")
                return True, None
                
            except smtplib.SMTPAuthenticationError as e:
                error_msg = f"Erreur d'authentification SMTP: {str(e)}"
                logger.error(f"{error_msg} (tentative {attempt}/{self.max_attempts})")
                if attempt == self.max_attempts:
                    return False, error_msg
                
            except smtplib.SMTPRecipientsRefused as e:
                error_msg = f"Destinataire refusé: {str(e)}"
                logger.error(f"{error_msg} (tentative {attempt}/{self.max_attempts})")
                if attempt == self.max_attempts:
                    return False, error_msg
                
            except smtplib.SMTPServerDisconnected as e:
                error_msg = f"Connexion SMTP fermée: {str(e)}"
                logger.error(f"{error_msg} (tentative {attempt}/{self.max_attempts})")
                if attempt == self.max_attempts:
                    return False, error_msg
                
            except Exception as e:
                error_msg = f"Erreur inattendue lors de l'envoi d'email: {str(e)}"
                logger.error(f"{error_msg} (tentative {attempt}/{self.max_attempts})")
                if attempt == self.max_attempts:
                    return False, error_msg
            
            # Attendre avant la prochaine tentative (avec backoff exponentiel si activé)
            if attempt < self.max_attempts:
                delay = self.retry_delay
                if self.exponential_backoff:
                    delay = self.retry_delay * (2 ** (attempt - 1))
                
                logger.info(f"Attente de {delay} secondes avant la prochaine tentative...")
                import time
                time.sleep(delay)
        
        return False, f"Échec après {self.max_attempts} tentatives"
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Teste la connexion SMTP
        
        Returns:
            Tuple (succès, message)
        """
        if not self.enabled:
            return False, "Service d'email désactivé"
        
        try:
            host, port, use_tls, username, password, from_email, from_name = self._get_smtp_config()
            
            if use_tls:
                context = ssl.create_default_context()
                server = smtplib.SMTP(host, port)
                server.starttls(context=context)
            else:
                server = smtplib.SMTP(host, port)
            
            if username and password:
                server.login(username, password)
            
            server.quit()
            return True, f"Connexion réussie au serveur SMTP {host}:{port}"
            
        except Exception as e:
            return False, f"Erreur de connexion SMTP: {str(e)}"
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Retourne les informations de configuration (sans les mots de passe)
        
        Returns:
            Informations de configuration
        """
        host, port, use_tls, username, password, from_email, from_name = self._get_smtp_config()
        
        return {
            'enabled': self.enabled,
            'provider': self.provider,
            'host': host,
            'port': port,
            'use_tls': use_tls,
            'username': username[:3] + '***' if username else 'Non configuré',
            'password_configured': bool(password),
            'from_email': from_email,
            'from_name': from_name,
            'max_attempts': self.max_attempts,
            'retry_delay_seconds': self.retry_delay,
            'exponential_backoff': self.exponential_backoff
        }

# Instance globale pour utilisation dans l'application
email_service = EmailService()

# Fonction utilitaire pour FastAPI
async def send_email(to_email: str, subject: str, content: str) -> Tuple[bool, Optional[str]]:
    """
    Fonction utilitaire pour envoyer un email
    
    Args:
        to_email: Adresse email destinataire
        subject: Sujet de l'email
        content: Contenu du message
        
    Returns:
        Tuple (succès, message_erreur)
    """
    return await email_service.send_email_async(to_email, subject, content)
