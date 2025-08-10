"""
Service d'envoi de SMS pour le système de notifications EIR Project
Supporte mode simulation (console/log) et APIs réelles (Twilio, AWS SNS)
Compatible Docker et async pour FastAPI
"""

import asyncio
import logging
import yaml
import os
import re
import json
from typing import Dict, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class SMSService:
    """
    Service d'envoi de SMS avec support de multiple providers
    Mode simulation pour développement et APIs réelles pour production
    """
    
    def __init__(self, config_file: str = "config/notifications.yml"):
        """
        Initialise le service SMS avec la configuration
        
        Args:
            config_file: Chemin vers le fichier de configuration YAML
        """
        self.config = self._load_config(config_file)
        self.sms_config = self.config.get('notifications', {}).get('sms', {})
        self.enabled = self.sms_config.get('enabled', False)
        self.provider = self.sms_config.get('provider', 'console')
        
        # Configuration du provider sélectionné
        self.provider_config = self.sms_config.get(self.provider, {})
        
        # Configuration des retry
        self.retry_config = self.sms_config.get('retry', {})
        self.max_attempts = self.retry_config.get('max_attempts', 3)
        self.retry_delay = self.retry_config.get('retry_delay_seconds', 180)
        self.exponential_backoff = self.retry_config.get('exponential_backoff', True)
        
        # Configuration de validation
        self.validation_config = self.sms_config.get('validation', {})
        self.validation_enabled = self.validation_config.get('enabled', True)
        self.min_length = self.validation_config.get('min_length', 8)
        self.max_length = self.validation_config.get('max_length', 15)
        self.international_format = self.validation_config.get('international_format', True)
        
        # Initialiser le provider
        self._init_provider()
        
        logger.info(f"SMSService initialisé - Provider: {self.provider}, Enabled: {self.enabled}")
    
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
                'sms': {
                    'enabled': False,
                    'provider': 'console',
                    'console': {
                        'enabled': True,
                        'log_to_file': True,
                        'log_file': 'logs/sms_simulation.log'
                    },
                    'retry': {
                        'max_attempts': 3,
                        'retry_delay_seconds': 180,
                        'exponential_backoff': True
                    },
                    'validation': {
                        'enabled': True,
                        'min_length': 8,
                        'max_length': 15,
                        'international_format': True
                    }
                }
            }
        }
    
    def _init_provider(self):
        """
        Initialise le provider SMS sélectionné
        """
        if self.provider == 'console':
            self._init_console_provider()
        elif self.provider == 'twilio':
            self._init_twilio_provider()
        elif self.provider == 'aws_sns':
            self._init_aws_sns_provider()
        else:
            logger.warning(f"Provider SMS inconnu: {self.provider}")
    
    def _init_console_provider(self):
        """
        Initialise le provider console (simulation)
        """
        self.log_to_file = self.provider_config.get('log_to_file', True)
        self.log_file = self.provider_config.get('log_file', 'logs/sms_simulation.log')
        
        # Créer le répertoire de logs si nécessaire
        if self.log_to_file:
            log_path = Path(self.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def _init_twilio_provider(self):
        """
        Initialise le provider Twilio
        """
        self.twilio_account_sid = self.provider_config.get('account_sid', '')
        self.twilio_auth_token = self.provider_config.get('auth_token', '')
        self.twilio_from_number = self.provider_config.get('from_number', '')
        
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_from_number]):
            logger.warning("Configuration Twilio incomplète")
            self.enabled = False
    
    def _init_aws_sns_provider(self):
        """
        Initialise le provider AWS SNS
        """
        self.aws_region = self.provider_config.get('region', 'eu-west-1')
        self.aws_access_key_id = self.provider_config.get('access_key_id', '')
        self.aws_secret_access_key = self.provider_config.get('secret_access_key', '')
        
        if not all([self.aws_access_key_id, self.aws_secret_access_key]):
            logger.warning("Configuration AWS SNS incomplète")
            self.enabled = False
    
    def _validate_phone_number(self, phone_number: str) -> Tuple[bool, str, Optional[str]]:
        """
        Valide un numéro de téléphone
        
        Args:
            phone_number: Numéro de téléphone à valider
            
        Returns:
            Tuple (valide, numéro_formaté, message_erreur)
        """
        if not self.validation_enabled:
            return True, phone_number, None
        
        # Nettoyer le numéro (supprimer espaces, tirets, points)
        cleaned = re.sub(r'[\s\-\.\(\)]', '', phone_number)
        
        # Vérifier la longueur
        if len(cleaned) < self.min_length:
            return False, cleaned, f"Numéro trop court (minimum {self.min_length} chiffres)"
        
        if len(cleaned) > self.max_length:
            return False, cleaned, f"Numéro trop long (maximum {self.max_length} chiffres)"
        
        # Vérifier le format international si requis
        if self.international_format and not cleaned.startswith('+'):
            return False, cleaned, "Format international requis (commencer par +)"
        
        # Vérifier que c'est uniquement des chiffres (après le +)
        digits_only = cleaned[1:] if cleaned.startswith('+') else cleaned
        if not digits_only.isdigit():
            return False, cleaned, "Le numéro ne doit contenir que des chiffres"
        
        return True, cleaned, None
    
    async def send_sms_async(self, to_phone: str, message: str) -> Tuple[bool, Optional[str]]:
        """
        Envoie un SMS de manière asynchrone
        
        Args:
            to_phone: Numéro de téléphone destinataire
            message: Contenu du message
            
        Returns:
            Tuple (succès, message_erreur)
        """
        if not self.enabled:
            logger.warning("Service SMS désactivé")
            return False, "Service SMS désactivé dans la configuration"
        
        # Validation du numéro
        valid, formatted_phone, error_msg = self._validate_phone_number(to_phone)
        if not valid:
            logger.error(f"Numéro de téléphone invalide: {error_msg}")
            return False, error_msg
        
        # Validation du message
        if not message or len(message.strip()) == 0:
            error_msg = "Message SMS vide"
            logger.error(error_msg)
            return False, error_msg
        
        if len(message) > 1600:  # Limite standard SMS
            error_msg = f"Message trop long ({len(message)} caractères, max 1600)"
            logger.error(error_msg)
            return False, error_msg
        
        # Exécuter l'envoi selon le provider
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._send_sms_sync, formatted_phone, message)
    
    def _send_sms_sync(self, to_phone: str, message: str) -> Tuple[bool, Optional[str]]:
        """
        Envoie un SMS de manière synchrone avec retry automatique
        
        Args:
            to_phone: Numéro de téléphone destinataire
            message: Contenu du message
            
        Returns:
            Tuple (succès, message_erreur)
        """
        for attempt in range(1, self.max_attempts + 1):
            try:
                if self.provider == 'console':
                    return self._send_sms_console(to_phone, message, attempt)
                elif self.provider == 'twilio':
                    return self._send_sms_twilio(to_phone, message, attempt)
                elif self.provider == 'aws_sns':
                    return self._send_sms_aws_sns(to_phone, message, attempt)
                else:
                    return False, f"Provider SMS non supporté: {self.provider}"
                    
            except Exception as e:
                error_msg = f"Erreur inattendue lors de l'envoi SMS: {str(e)}"
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
    
    def _send_sms_console(self, to_phone: str, message: str, attempt: int) -> Tuple[bool, Optional[str]]:
        """
        Simule l'envoi SMS via la console (mode développement)
        
        Args:
            to_phone: Numéro de téléphone destinataire
            message: Contenu du message
            attempt: Numéro de tentative
            
        Returns:
            Tuple (succès, message_erreur)
        """
        timestamp = datetime.now().isoformat()
        
        # Log dans la console
        console_msg = f"""
====== SMS SIMULATION ======
Timestamp: {timestamp}
To: {to_phone}
Message: {message}
Attempt: {attempt}
Provider: Console Simulation
Status: SUCCESS
============================
"""
        print(console_msg)
        
        # Log dans un fichier si configuré
        if self.log_to_file:
            try:
                log_entry = {
                    'timestamp': timestamp,
                    'to_phone': to_phone,
                    'message': message,
                    'attempt': attempt,
                    'provider': 'console',
                    'status': 'success'
                }
                
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                    
            except Exception as e:
                logger.warning(f"Impossible d'écrire dans le fichier de log SMS: {e}")
        
        logger.info(f"SMS simulé envoyé à {to_phone} (tentative {attempt})")
        return True, None
    
    def _send_sms_twilio(self, to_phone: str, message: str, attempt: int) -> Tuple[bool, Optional[str]]:
        """
        Envoie un SMS via Twilio
        
        Args:
            to_phone: Numéro de téléphone destinataire
            message: Contenu du message
            attempt: Numéro de tentative
            
        Returns:
            Tuple (succès, message_erreur)
        """
        try:
            # Import Twilio (optionnel, ne pas faire planter si pas installé)
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message = client.messages.create(
                body=message,
                from_=self.twilio_from_number,
                to=to_phone
            )
            
            logger.info(f"SMS Twilio envoyé à {to_phone} (tentative {attempt}), SID: {message.sid}")
            return True, None
            
        except ImportError:
            error_msg = "Twilio SDK non installé (pip install twilio)"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Erreur Twilio: {str(e)}"
            logger.error(f"{error_msg} (tentative {attempt})")
            return False, error_msg
    
    def _send_sms_aws_sns(self, to_phone: str, message: str, attempt: int) -> Tuple[bool, Optional[str]]:
        """
        Envoie un SMS via AWS SNS
        
        Args:
            to_phone: Numéro de téléphone destinataire
            message: Contenu du message
            attempt: Numéro de tentative
            
        Returns:
            Tuple (succès, message_erreur)
        """
        try:
            # Import boto3 (optionnel, ne pas faire planter si pas installé)
            import boto3
            
            client = boto3.client(
                'sns',
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            
            response = client.publish(
                PhoneNumber=to_phone,
                Message=message
            )
            
            message_id = response.get('MessageId', 'unknown')
            logger.info(f"SMS AWS SNS envoyé à {to_phone} (tentative {attempt}), MessageId: {message_id}")
            return True, None
            
        except ImportError:
            error_msg = "AWS boto3 SDK non installé (pip install boto3)"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Erreur AWS SNS: {str(e)}"
            logger.error(f"{error_msg} (tentative {attempt})")
            return False, error_msg
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Teste la connexion du provider SMS
        
        Returns:
            Tuple (succès, message)
        """
        if not self.enabled:
            return False, "Service SMS désactivé"
        
        if self.provider == 'console':
            return True, "Provider console - simulation activée"
        elif self.provider == 'twilio':
            return self._test_twilio_connection()
        elif self.provider == 'aws_sns':
            return self._test_aws_sns_connection()
        else:
            return False, f"Provider non supporté: {self.provider}"
    
    def _test_twilio_connection(self) -> Tuple[bool, str]:
        """
        Teste la connexion Twilio
        
        Returns:
            Tuple (succès, message)
        """
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            account = client.api.accounts(self.twilio_account_sid).fetch()
            
            return True, f"Connexion Twilio réussie - Account: {account.friendly_name}"
            
        except ImportError:
            return False, "Twilio SDK non installé"
        except Exception as e:
            return False, f"Erreur connexion Twilio: {str(e)}"
    
    def _test_aws_sns_connection(self) -> Tuple[bool, str]:
        """
        Teste la connexion AWS SNS
        
        Returns:
            Tuple (succès, message)
        """
        try:
            import boto3
            
            client = boto3.client(
                'sns',
                region_name=self.aws_region,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )
            
            # Test de base - lister les topics
            response = client.list_topics()
            
            return True, f"Connexion AWS SNS réussie - Region: {self.aws_region}"
            
        except ImportError:
            return False, "AWS boto3 SDK non installé"
        except Exception as e:
            return False, f"Erreur connexion AWS SNS: {str(e)}"
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Retourne les informations de configuration (sans les secrets)
        
        Returns:
            Informations de configuration
        """
        info = {
            'enabled': self.enabled,
            'provider': self.provider,
            'max_attempts': self.max_attempts,
            'retry_delay_seconds': self.retry_delay,
            'exponential_backoff': self.exponential_backoff,
            'validation_enabled': self.validation_enabled,
            'min_length': self.min_length,
            'max_length': self.max_length,
            'international_format': self.international_format
        }
        
        if self.provider == 'console':
            info.update({
                'log_to_file': self.log_to_file,
                'log_file': self.log_file
            })
        elif self.provider == 'twilio':
            info.update({
                'account_sid': self.twilio_account_sid[:8] + '***' if self.twilio_account_sid else 'Non configuré',
                'auth_token_configured': bool(self.twilio_auth_token),
                'from_number': self.twilio_from_number
            })
        elif self.provider == 'aws_sns':
            info.update({
                'region': self.aws_region,
                'access_key_id': self.aws_access_key_id[:8] + '***' if self.aws_access_key_id else 'Non configuré',
                'secret_access_key_configured': bool(self.aws_secret_access_key)
            })
        
        return info

# Instance globale pour utilisation dans l'application
sms_service = SMSService()

# Fonction utilitaire pour FastAPI
async def send_sms(to_phone: str, message: str) -> Tuple[bool, Optional[str]]:
    """
    Fonction utilitaire pour envoyer un SMS
    
    Args:
        to_phone: Numéro de téléphone destinataire
        message: Contenu du message
        
    Returns:
        Tuple (succès, message_erreur)
    """
    return await sms_service.send_sms_async(to_phone, message)
