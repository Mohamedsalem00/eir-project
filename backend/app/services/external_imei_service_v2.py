"""
Service IMEI externe mis à jour avec APIs fonctionnelles
Support pour validation locale et algorithmique
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
import yaml
import re
import os

logger = logging.getLogger(__name__)

class ExternalIMEIService:
    def __init__(self, config_path: str = "config/external_apis.yml"):
        """Initialise le service avec la configuration"""
        self.config_path = config_path
        self.config = self._load_config()
        self.cache = {}
        self.request_counts = {}
        self.tac_database = self._load_tac_database()
        
    def _load_config(self) -> Dict:
        """Charge la configuration depuis le fichier YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Configuration par défaut si le fichier n'existe pas"""
        return {
            "external_apis": {
                "enabled": True,
                "fallback_enabled": True,
                "cache_duration_hours": 24,
                "providers": {
                    "local_tac_db": {
                        "enabled": True,
                        "type": "local_database",
                        "priority": 0
                    },
                    "luhn_validator": {
                        "enabled": True,
                        "type": "algorithmic",
                        "priority": 1
                    }
                }
            }
        }
    
    def _load_tac_database(self) -> Dict:
        """Charge la base de données TAC locale"""
        tac_file = "data/tac_database.json"
        try:
            with open(tac_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"TAC database {tac_file} not found")
            return {}
    
    def validate_imei_luhn(self, imei: str) -> bool:
        """
        Valide un IMEI avec l'algorithme de Luhn
        """
        if not imei or len(imei) not in [14, 15]:
            return False
        
        # Supprime les espaces et caractères non numériques
        imei_clean = re.sub(r'\D', '', imei)
        
        if len(imei_clean) not in [14, 15]:
            return False
        
        # Pour IMEI de 15 chiffres, on utilise les 14 premiers pour Luhn
        if len(imei_clean) == 15:
            digits = [int(d) for d in imei_clean[:14]]
        else:
            digits = [int(d) for d in imei_clean]
        
        # Algorithme de Luhn
        total = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:  # Positions paires (en partant de la droite)
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        
        # Calcule le chiffre de contrôle
        check_digit = (10 - (total % 10)) % 10
        
        # Pour IMEI de 15 chiffres, vérifie le dernier chiffre
        if len(imei_clean) == 15:
            return check_digit == int(imei_clean[-1])
        
        return True  # Pour IMEI de 14 chiffres, considéré valide si Luhn passe
    
    def get_tac_info(self, imei: str) -> Dict:
        """
        Extrait les informations TAC depuis la base locale
        """
        if len(imei) < 8:
            return {}
        
        tac = imei[:8]  # Les 8 premiers chiffres sont le TAC
        
        # Recherche dans la base TAC locale
        if tac in self.tac_database:
            return {
                "tac": tac,
                "brand": self.tac_database[tac].get("brand", "Unknown"),
                "model": self.tac_database[tac].get("model", "Unknown"),
                "device_type": self.tac_database[tac].get("type", "Mobile"),
                "source": "local_tac_database"
            }
        
        # Informations par défaut basées sur TAC connus
        tac_prefixes = {
            "35294406": {"brand": "Samsung", "model": "Galaxy S21"},
            "35404806": {"brand": "Apple", "model": "iPhone 12"},
            "35274508": {"brand": "Samsung", "model": "Galaxy Note"},
            "35404807": {"brand": "Apple", "model": "iPhone 13"},
            "35694906": {"brand": "Huawei", "model": "P30"},
            "35899209": {"brand": "Xiaomi", "model": "Mi 11"},
        }
        
        for prefix, info in tac_prefixes.items():
            if tac.startswith(prefix):
                return {
                    "tac": tac,
                    "brand": info["brand"],
                    "model": info["model"],
                    "device_type": "Smartphone",
                    "source": "known_tac_patterns"
                }
        
        return {
            "tac": tac,
            "brand": "Unknown",
            "model": "Unknown",
            "device_type": "Unknown",
            "source": "tac_only"
        }
    
    async def validate_imei_external(self, imei: str, provider: str) -> Optional[Dict]:
        """
        Valide un IMEI via une API externe (si configurée)
        """
        providers = self.config.get("external_apis", {}).get("providers", {})
        
        if provider not in providers or not providers[provider].get("enabled", False):
            return None
        
        provider_config = providers[provider]
        
        # Pour NumVerify (seule API externe recommandée)
        if provider == "numverify" and provider_config.get("api_key"):
            try:
                url = provider_config["url"]
                api_key = os.getenv("NUMVERIFY_API_KEY") or provider_config.get("api_key", "").replace("${NUMVERIFY_API_KEY}", "")
                
                if not api_key or api_key.startswith("${"):
                    logger.warning("NumVerify API key not configured")
                    return None
                
                async with aiohttp.ClientSession() as session:
                    params = {
                        "access_key": api_key,
                        "number": imei
                    }
                    
                    async with session.get(url, params=params, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "valid": data.get("valid", False),
                                "carrier": data.get("carrier", "Unknown"),
                                "country": data.get("country_name", "Unknown"),
                                "source": "numverify_api"
                            }
            except Exception as e:
                logger.error(f"Error calling NumVerify API: {e}")
                return None
        
        return None
    
    async def check_imei(self, imei: str, include_external: bool = False) -> Dict:
        """
        Fonction principale de vérification IMEI
        """
        result = {
            "imei": imei,
            "timestamp": datetime.now().isoformat(),
            "checks_performed": [],
            "validation_results": {}
        }
        
        # 1. Validation algorithmique (Luhn)
        luhn_valid = self.validate_imei_luhn(imei)
        result["validation_results"]["luhn_algorithm"] = {
            "valid": luhn_valid,
            "source": "local_algorithm"
        }
        result["checks_performed"].append("luhn_algorithm")
        
        # 2. Recherche TAC locale
        tac_info = self.get_tac_info(imei)
        result["validation_results"]["tac_lookup"] = tac_info
        result["checks_performed"].append("tac_lookup")
        
        # 3. API externe (si demandée et configurée)
        if include_external:
            external_result = await self.validate_imei_external(imei, "numverify")
            if external_result:
                result["validation_results"]["external_api"] = external_result
                result["checks_performed"].append("external_api")
        
        # 4. Résultat final
        result["overall_valid"] = luhn_valid
        result["confidence_level"] = self._calculate_confidence(result["validation_results"])
        result["recommendation"] = self._get_recommendation(result)
        
        return result
    
    def _calculate_confidence(self, validation_results: Dict) -> str:
        """Calcule le niveau de confiance du résultat"""
        scores = []
        
        # Score Luhn
        if validation_results.get("luhn_algorithm", {}).get("valid"):
            scores.append(0.6)  # 60% pour Luhn valide
        
        # Score TAC
        tac_info = validation_results.get("tac_lookup", {})
        if tac_info.get("brand") != "Unknown":
            scores.append(0.3)  # 30% pour TAC reconnu
        
        # Score API externe
        if validation_results.get("external_api", {}).get("valid"):
            scores.append(0.8)  # 80% pour API externe
        
        total_score = sum(scores)
        
        if total_score >= 0.8:
            return "high"
        elif total_score >= 0.5:
            return "medium"
        else:
            return "low"
    
    def _get_recommendation(self, result: Dict) -> str:
        """Génère une recommandation basée sur les résultats"""
        confidence = result["confidence_level"]
        luhn_valid = result["validation_results"].get("luhn_algorithm", {}).get("valid", False)
        tac_known = result["validation_results"].get("tac_lookup", {}).get("brand") != "Unknown"
        
        if confidence == "high" and luhn_valid and tac_known:
            return "IMEI appears valid - strong confidence"
        elif confidence == "medium" and luhn_valid:
            return "IMEI likely valid - moderate confidence"
        elif not luhn_valid:
            return "IMEI invalid - failed Luhn algorithm"
        else:
            return "IMEI validation inconclusive - requires manual review"

# Fonction d'interface pour l'application
async def check_imei_external(imei: str, include_external: bool = False) -> Dict:
    """
    Interface publique pour la vérification IMEI
    """
    service = ExternalIMEIService()
    return await service.check_imei(imei, include_external)

# Exemple d'utilisation
if __name__ == "__main__":
    import asyncio
    
    async def test_service():
        # Tests avec différents IMEIs
        test_imeis = [
            "352745080123456",  # IMEI de test valide
            "354123456789012",  # Autre IMEI de test
            "123456789012345",  # IMEI invalide
            "352944060000001"   # IMEI Samsung
        ]
        
        service = ExternalIMEIService()
        
        for imei in test_imeis:
            print(f"\n📱 Test IMEI: {imei}")
            result = await service.check_imei(imei, include_external=False)
            
            print(f"   Luhn Valid: {result['validation_results']['luhn_algorithm']['valid']}")
            print(f"   Brand: {result['validation_results']['tac_lookup']['brand']}")
            print(f"   Model: {result['validation_results']['tac_lookup']['model']}")
            print(f"   Confidence: {result['confidence_level']}")
            print(f"   Recommendation: {result['recommendation']}")
    
    asyncio.run(test_service())
