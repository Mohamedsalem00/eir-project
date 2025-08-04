"""
Module de chargement de configuration pour les protocoles d'intégration
"""
import yaml
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Cache pour éviter de lire le fichier à chaque fois en production
_config_cache = None
_cache_timestamp = None

def load_protocol_config(force_reload: bool = False) -> Dict[str, Any]:
    """
    Charge la configuration des protocoles depuis le fichier YAML
    
    Args:
        force_reload: Si True, force le rechargement même si en cache
    
    Returns:
        Dict contenant la configuration des protocoles
    """
    global _config_cache, _cache_timestamp
    
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        "config", 
        "protocols.yml"
    )
    
    # Vérifier si on doit recharger (force ou fichier modifié)
    should_reload = force_reload or _config_cache is None
    
    if not should_reload and _cache_timestamp is not None:
        try:
            file_mtime = os.path.getmtime(config_path)
            if file_mtime > _cache_timestamp:
                should_reload = True
        except OSError:
            should_reload = True
    
    if should_reload:
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                _config_cache = yaml.safe_load(file)
                _cache_timestamp = os.path.getmtime(config_path)
                logger.info(f"Configuration des protocoles rechargée depuis {config_path}")
        except FileNotFoundError:
            logger.error(f"Fichier de configuration non trouvé: {config_path}")
            # Configuration par défaut si le fichier n'existe pas
            _config_cache = {
                "enabled_protocols": {
                    "rest": True,
                    "ss7": False,
                    "diameter": False
                },
                "timeouts": {
                    "rest": 30,
                    "ss7": 10,
                    "diameter": 60
                },
                "logging": {
                    "rest": {"level": "INFO", "enabled": True},
                    "ss7": {"level": "DEBUG", "enabled": True},
                    "diameter": {"level": "INFO", "enabled": True}
                }
            }
            _cache_timestamp = 0
        except yaml.YAMLError as e:
            logger.error(f"Erreur lors du parsing du fichier YAML: {e}")
            raise ValueError(f"Configuration YAML invalide: {e}")
    
    return _config_cache

def is_protocol_enabled(protocol: str) -> bool:
    """
    Vérifie si un protocole est activé dans la configuration
    
    Args:
        protocol: Nom du protocole (rest, ss7, diameter)
        
    Returns:
        True si le protocole est activé, False sinon
    """
    config = load_protocol_config(force_reload=True)  # Force reload pour les changements de config
    enabled_protocols = config.get("enabled_protocols", {})
    return enabled_protocols.get(protocol, False)

def get_protocol_timeout(protocol: str) -> int:
    """
    Obtient le timeout configuré pour un protocole
    
    Args:
        protocol: Nom du protocole
        
    Returns:
        Timeout en secondes
    """
    config = load_protocol_config(force_reload=True)
    timeouts = config.get("timeouts", {})
    default_timeout = 30
    return timeouts.get(protocol, default_timeout)

def get_protocol_logging_config(protocol: str) -> Dict[str, Any]:
    """
    Obtient la configuration de logging pour un protocole
    
    Args:
        protocol: Nom du protocole
        
    Returns:
        Configuration de logging
    """
    config = load_protocol_config(force_reload=True)
    logging_config = config.get("logging", {})
    default_config = {"level": "INFO", "enabled": True}
    return logging_config.get(protocol, default_config)
