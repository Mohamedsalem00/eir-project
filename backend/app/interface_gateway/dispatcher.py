"""
Dispatcher pour les requêtes multi-protocoles
Gère le routage des requêtes vers les handlers appropriés
"""
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime

from ..config_loader import is_protocol_enabled, get_protocol_timeout, get_protocol_logging_config
from .handlers import rest_handler, ss7_handler, diameter_handler

logger = logging.getLogger(__name__)

class ProtocolNotEnabledException(Exception):
    """Exception levée quand un protocole n'est pas activé"""
    pass

class UnsupportedProtocolException(Exception):
    """Exception levée pour un protocole non supporté"""
    pass

def setup_protocol_logger(protocol: str) -> logging.Logger:
    """
    Configure un logger spécifique pour un protocole
    
    Args:
        protocol: Nom du protocole
        
    Returns:
        Logger configuré pour le protocole
    """
    protocol_logger = logging.getLogger(f"protocol.{protocol}")
    
    # Obtenir la configuration de logging pour ce protocole
    log_config = get_protocol_logging_config(protocol)
    
    if log_config.get("enabled", True):
        level = getattr(logging, log_config.get("level", "INFO").upper())
        protocol_logger.setLevel(level)
        
        # Créer un handler si pas déjà existant
        if not protocol_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'%(asctime)s - {protocol.upper()} - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            protocol_logger.addHandler(handler)
    
    return protocol_logger

def handle_incoming_request(protocol: str, payload: Dict[str, Any]) -> Union[Dict[str, Any], None]:
    """
    Dispatche une requête entrante vers le handler approprié
    
    Args:
        protocol: Type de protocole (rest, ss7, diameter)
        payload: Données de la requête
        
    Returns:
        Réponse du handler ou None pour les protocoles fire-and-forget
        
    Raises:
        ProtocolNotEnabledException: Si le protocole n'est pas activé
        UnsupportedProtocolException: Si le protocole n'est pas supporté
    """
    # Vérifier si le protocole est activé
    if not is_protocol_enabled(protocol):
        logger.warning(f"Tentative d'utilisation du protocole désactivé: {protocol}")
        raise ProtocolNotEnabledException(f"Le protocole {protocol} n'est pas activé")
    
    # Configurer le logger pour ce protocole
    protocol_logger = setup_protocol_logger(protocol)
    
    # Ajouter des métadonnées à la payload
    enhanced_payload = {
        **payload,
        "request_timestamp": datetime.now().isoformat(),
        "protocol": protocol,
        "timeout": get_protocol_timeout(protocol)
    }
    
    protocol_logger.info(f"Traitement de la requête {protocol.upper()}: {payload}")
    
    try:
        # Dispatcher vers le handler approprié
        if protocol == "rest":
            response = rest_handler.process_rest(enhanced_payload)
            protocol_logger.info(f"Réponse REST: {response}")
            return response
            
        elif protocol == "ss7":
            # SS7 est fire-and-forget, pas de réponse
            ss7_handler.process_ss7(enhanced_payload)
            protocol_logger.info("Requête SS7 traitée (fire-and-forget)")
            return None
            
        elif protocol == "diameter":
            response = diameter_handler.process_diameter(enhanced_payload)
            protocol_logger.info(f"Réponse Diameter: {response}")
            return response
            
        else:
            logger.error(f"Protocole non supporté: {protocol}")
            raise UnsupportedProtocolException(f"Le protocole {protocol} n'est pas supporté")
            
    except Exception as e:
        protocol_logger.error(f"Erreur lors du traitement de la requête {protocol}: {str(e)}")
        # Re-lever l'exception pour que l'appelant puisse la gérer
        raise

def get_supported_protocols() -> Dict[str, bool]:
    """
    Retourne la liste des protocoles supportés et leur statut d'activation
    
    Returns:
        Dict avec les protocoles et leur statut
    """
    protocols = ["rest", "ss7", "diameter"]
    return {
        protocol: is_protocol_enabled(protocol) 
        for protocol in protocols
    }

def validate_payload(protocol: str, payload: Dict[str, Any]) -> bool:
    """
    Valide la payload pour un protocole donné
    
    Args:
        protocol: Type de protocole
        payload: Données à valider
        
    Returns:
        True si la payload est valide
    """
    # Validation de base - l'IMEI doit être présent
    if "imei" not in payload:
        return False
    
    imei = payload["imei"]
    
    # Validation de base de l'IMEI (14 ou 15 chiffres)
    if not isinstance(imei, str) or not imei.isdigit():
        return False
    
    if len(imei) not in [14, 15]:
        return False
    
    # Validations spécifiques par protocole
    if protocol == "ss7":
        # Pour SS7, on pourrait vérifier des champs supplémentaires
        # comme MSISDN, IMSI, etc.
        pass
    elif protocol == "diameter":
        # Pour Diameter, on pourrait vérifier des AVPs spécifiques
        pass
    
    return True
