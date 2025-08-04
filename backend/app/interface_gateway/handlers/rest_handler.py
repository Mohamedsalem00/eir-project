"""
Handler REST pour la vérification IMEI
Traite les requêtes REST et retourne des réponses JSON
"""
import logging
from typing import Dict, Any
from datetime import datetime
import random
import time

logger = logging.getLogger("protocol.rest")

def process_rest(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Traite une requête REST de vérification IMEI
    
    Args:
        payload: Dictionnaire contenant les données de la requête
                 - imei (str): Numéro IMEI à vérifier
                 - request_timestamp (str): Timestamp de la requête
                 - timeout (int): Timeout configuré
                 
    Returns:
        Dict avec la réponse JSON incluant le statut de l'IMEI
    """
    logger.info(f"Traitement requête REST - IMEI: {payload.get('imei')}")
    
    start_time = time.time()
    imei = payload.get("imei")
    
    # Simulation d'une vérification IMEI
    # Dans un vrai système, ceci ferait appel à une base de données EIR
    try:
        # Simuler un délai de traitement
        time.sleep(random.uniform(0.1, 0.5))
        
        # Logique de simulation basée sur l'IMEI
        imei_status = determine_imei_status(imei)
        
        processing_time = time.time() - start_time
        
        response = {
            "status": "success",
            "imei": imei,
            "imei_status": imei_status,
            "timestamp": datetime.now().isoformat(),
            "processing_time_ms": round(processing_time * 1000, 2),
            "protocol": "REST",
            "response_code": "OK"
        }
        
        # Ajouter des informations supplémentaires selon le statut
        if imei_status == "whitelisted":
            response["message"] = "IMEI autorisé - Appareil légitime"
            response["action"] = "allow"
        elif imei_status == "blacklisted":
            response["message"] = "IMEI bloqué - Appareil signalé"
            response["action"] = "block"
            response["reason"] = "Appareil déclaré volé ou perdu"
        elif imei_status == "unknown":
            response["message"] = "IMEI inconnu - Statut indéterminé"
            response["action"] = "monitor"
        
        logger.info(f"Réponse REST générée - Statut: {imei_status}, Temps: {processing_time:.3f}s")
        return response
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement REST pour IMEI {imei}: {str(e)}")
        
        # Retourner une réponse d'erreur
        return {
            "status": "error",
            "imei": imei,
            "error_message": str(e),
            "timestamp": datetime.now().isoformat(),
            "protocol": "REST",
            "response_code": "ERROR"
        }

def determine_imei_status(imei: str) -> str:
    """
    Détermine le statut d'un IMEI basé sur une logique de simulation
    
    Args:
        imei: Numéro IMEI à vérifier
        
    Returns:
        Statut de l'IMEI: 'whitelisted', 'blacklisted', ou 'unknown'
    """
    if not imei:
        return "unknown"
    
    # Logique de simulation basée sur les derniers chiffres de l'IMEI
    last_digit = int(imei[-1]) if imei[-1].isdigit() else 0
    
    if last_digit in [0, 1, 2, 3, 4, 5, 6]:
        return "whitelisted"
    elif last_digit in [7, 8]:
        return "blacklisted"
    else:
        return "unknown"

def validate_rest_payload(payload: Dict[str, Any]) -> tuple[bool, str]:
    """
    Valide la payload pour une requête REST
    
    Args:
        payload: Données à valider
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if "imei" not in payload:
        return False, "IMEI manquant dans la payload"
    
    imei = payload["imei"]
    
    if not isinstance(imei, str):
        return False, "IMEI doit être une chaîne de caractères"
    
    if not imei.isdigit():
        return False, "IMEI doit contenir uniquement des chiffres"
    
    if len(imei) not in [14, 15]:
        return False, "IMEI doit contenir 14 ou 15 chiffres"
    
    return True, ""

def get_rest_statistics() -> Dict[str, Any]:
    """
    Retourne des statistiques sur les requêtes REST traitées
    
    Returns:
        Dictionnaire avec les statistiques
    """
    # Dans un vrai système, ces statistiques seraient stockées en base
    return {
        "total_requests": 0,
        "successful_requests": 0,
        "failed_requests": 0,
        "average_response_time_ms": 0,
        "last_request_timestamp": None
    }
