"""
Handler Diameter pour la vérification IMEI
Traite les requêtes Diameter et retourne des réponses AVP
"""
import logging
from typing import Dict, Any
from datetime import datetime
import time
import random

logger = logging.getLogger("protocol.diameter")

def process_diameter(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Traite une requête Diameter de vérification IMEI
    
    Args:
        payload: Dictionnaire contenant les données de la requête
                 - imei (str): Numéro IMEI à vérifier
                 - session_id (str, optional): ID de session Diameter
                 - origin_host (str, optional): Hôte d'origine
                 - origin_realm (str, optional): Realm d'origine
                 - request_timestamp (str): Timestamp de la requête
                 
    Returns:
        Dict avec la réponse Diameter incluant les AVPs
    """
    logger.info(f"Traitement requête Diameter - IMEI: {payload.get('imei')}")
    
    start_time = time.time()
    imei = payload.get("imei")
    session_id = payload.get("session_id", generate_session_id())
    origin_host = payload.get("origin_host", "unknown.host")
    origin_realm = payload.get("origin_realm", "unknown.realm")
    
    try:
        # Simulation d'une vérification IMEI via Diameter
        time.sleep(random.uniform(0.2, 0.8))
        
        # Déterminer le statut de l'IMEI
        imei_status = determine_diameter_imei_status(imei)
        
        processing_time = time.time() - start_time
        
        # Construire la réponse Diameter avec AVPs
        response = build_diameter_response(
            imei=imei,
            imei_status=imei_status,
            session_id=session_id,
            origin_host=origin_host,
            origin_realm=origin_realm,
            processing_time=processing_time
        )
        
        logger.info(f"Réponse Diameter générée - Session: {session_id}, Statut: {imei_status}")
        return response
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement Diameter pour IMEI {imei}: {str(e)}")
        
        # Retourner une réponse d'erreur Diameter
        return build_diameter_error_response(
            imei=imei,
            session_id=session_id,
            origin_host=origin_host,
            origin_realm=origin_realm,
            error_message=str(e)
        )

def build_diameter_response(imei: str, imei_status: str, session_id: str, 
                          origin_host: str, origin_realm: str, processing_time: float) -> Dict[str, Any]:
    """
    Construit une réponse Diameter avec les AVPs appropriés
    
    Args:
        imei: Numéro IMEI
        imei_status: Statut déterminé de l'IMEI
        session_id: ID de session Diameter
        origin_host: Hôte d'origine
        origin_realm: Realm d'origine
        processing_time: Temps de traitement
        
    Returns:
        Réponse Diameter formatée
    """
    # Mapper le statut IMEI vers les codes Diameter
    result_code = map_imei_status_to_diameter_code(imei_status)
    
    response = {
        "message_type": "Equipment-Status-Answer",
        "application_id": 16777252,  # 3GPP S6a/S6d Application
        "command_code": 319,  # Check-IMEI-Answer
        "request_type": "answer",
        "avps": {
            "Session-Id": session_id,
            "Result-Code": result_code,
            "Origin-Host": "eir.local.realm",
            "Origin-Realm": "local.realm",
            "Auth-Application-Id": 16777252,
            "Equipment-Status": map_status_to_equipment_status(imei_status),
            "User-Name": imei,  # IMEI dans le champ User-Name
        },
        "metadata": {
            "imei": imei,
            "imei_status": imei_status,
            "processing_time_ms": round(processing_time * 1000, 2),
            "timestamp": datetime.now().isoformat(),
            "protocol": "Diameter"
        }
    }
    
    # Ajouter des AVPs conditionnels selon le statut
    if imei_status == "blacklisted":
        response["avps"]["Equipment-Status-raison"] = "STOLEN_OR_LOST"
    elif imei_status == "unknown":
        response["avps"]["Equipment-Status-raison"] = "UNKNOWN_EQUIPMENT"
    
    return response

def build_diameter_error_response(imei: str, session_id: str, origin_host: str, 
                                origin_realm: str, error_message: str) -> Dict[str, Any]:
    """
    Construit une réponse d'erreur Diameter
    
    Args:
        imei: Numéro IMEI
        session_id: ID de session
        origin_host: Hôte d'origine
        origin_realm: Realm d'origine
        error_message: Message d'erreur
        
    Returns:
        Réponse d'erreur Diameter
    """
    return {
        "message_type": "Equipment-Status-Answer",
        "application_id": 16777252,
        "command_code": 319,
        "request_type": "answer",
        "avps": {
            "Session-Id": session_id,
            "Result-Code": 5012,  # DIAMETER_UNABLE_TO_COMPLY
            "Origin-Host": "eir.local.realm", 
            "Origin-Realm": "local.realm",
            "Error-Message": error_message,
            "User-Name": imei
        },
        "metadata": {
            "imei": imei,
            "error": True,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat(),
            "protocol": "Diameter"
        }
    }

def determine_diameter_imei_status(imei: str) -> str:
    """
    Détermine le statut d'un IMEI pour Diameter
    
    Args:
        imei: Numéro IMEI
        
    Returns:
        Statut de l'IMEI
    """
    if not imei:
        return "unknown"
    
    # Logique similaire aux autres handlers mais avec des spécificités Diameter
    last_digit = int(imei[-1]) if imei[-1].isdigit() else 0
    
    if last_digit in [0, 1, 2, 3, 4, 5, 6]:
        return "whitelisted"
    elif last_digit in [7, 8]:
        return "blacklisted"
    else:
        return "unknown"

def map_imei_status_to_diameter_code(status: str) -> int:
    """
    Mappe le statut IMEI vers les codes de résultat Diameter
    
    Args:
        status: Statut de l'IMEI
        
    Returns:
        Code de résultat Diameter
    """
    status_mapping = {
        "whitelisted": 2001,  # DIAMETER_SUCCESS
        "blacklisted": 2001,  # DIAMETER_SUCCESS (mais avec Equipment-Status différent)
        "unknown": 2001,      # DIAMETER_SUCCESS (mais avec Equipment-Status différent)
    }
    
    return status_mapping.get(status, 5012)  # DIAMETER_UNABLE_TO_COMPLY par défaut

def map_status_to_equipment_status(status: str) -> int:
    """
    Mappe le statut IMEI vers l'AVP Equipment-Status
    
    Args:
        status: Statut de l'IMEI
        
    Returns:
        Valeur Equipment-Status
    """
    equipment_status_mapping = {
        "whitelisted": 0,  # WHITELISTED
        "blacklisted": 1,  # BLACKLISTED  
        "unknown": 2       # UNKNOWN
    }
    
    return equipment_status_mapping.get(status, 2)

def generate_session_id() -> str:
    """
    Génère un ID de session Diameter unique
    
    Returns:
        ID de session formaté selon les standards Diameter
    """
    import uuid
    timestamp = int(time.time())
    unique_id = str(uuid.uuid4())[:8]
    return f"eir.local.realm;{timestamp};{unique_id}"

def validate_diameter_payload(payload: Dict[str, Any]) -> tuple[bool, str]:
    """
    Valide la payload pour une requête Diameter
    
    Args:
        payload: Données à valider
        
    Returns:
        Tuple (is_valid, error_message)
    """
    # Vérifications de base
    if "imei" not in payload:
        return False, "IMEI manquant dans la payload Diameter"
    
    imei = payload["imei"]
    
    if not isinstance(imei, str):
        return False, "IMEI doit être une chaîne de caractères"
    
    if not imei.isdigit():
        return False, "IMEI doit contenir uniquement des chiffres"
    
    if len(imei) not in [14, 15]:
        return False, "IMEI doit contenir 14 ou 15 chiffres"
    
    # Vérifications spécifiques à Diameter
    if "session_id" in payload and not payload["session_id"]:
        return False, "Session-Id ne peut pas être vide"
    
    return True, ""

def get_diameter_statistics() -> Dict[str, Any]:
    """
    Retourne des statistiques sur les requêtes Diameter traitées
    
    Returns:
        Dictionnaire avec les statistiques
    """
    return {
        "total_diameter_requests": 0,
        "successful_responses": 0,
        "error_responses": 0,
        "average_response_time_ms": 0,
        "active_sessions": 0,
        "last_request_timestamp": None,
        "result_codes": {
            "2001": 0,  # DIAMETER_SUCCESS
            "5012": 0   # DIAMETER_UNABLE_TO_COMPLY
        }
    }
