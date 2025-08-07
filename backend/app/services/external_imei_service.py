"""
Service d'intégration avec les APIs externes IMEI
Fournit un système de fallback avec cache pour les vérifications IMEI
"""

import aiohttp
import asyncio
import json
import yaml
import hashlib
import logging
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class ExternalIMEIService:
    def __init__(self, config_file: str = "config/external_apis.yml"):
        self.config_file = config_file
        self.config = self.load_config()
        self.cache = {}  # En production: utiliser Redis
        self.daily_usage = {}
        self.tac_database = self.load_tac_database()
        
    def load_config(self) -> Dict:
        """Charge la configuration des APIs externes"""
        try:
            config_path = Path(self.config_file)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Fichier de configuration non trouvé: {self.config_file}")
                return self.get_default_config()
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la configuration: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Configuration par défaut si le fichier n'existe pas"""
        return {
            'external_apis': {
                'enabled': False,
                'providers': {},
                'cache': {'enabled': False}
            }
        }
    
    def load_tac_database(self) -> Dict:
        """Charge la base de données TAC locale"""
        try:
            tac_file = Path("data/tac_database.json")
            if tac_file.exists():
                with open(tac_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('tac_entries', {})
            else:
                logger.warning("Base de données TAC non trouvée")
                return {}
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la base TAC: {e}")
            return {}
    
    async def check_imei_external(self, imei: str) -> Dict:
        """
        Vérifie un IMEI via les APIs externes avec système de fallback
        
        Args:
            imei: Numéro IMEI à vérifier
            
        Returns:
            Dict contenant les informations trouvées
        """
        if not self.config.get('external_apis', {}).get('enabled', False):
            return self.create_not_found_response(imei, "APIs externes désactivées")
        
        # 1. Vérifier le cache d'abord
        cached_result = self.get_from_cache(imei)
        if cached_result:
            logger.info(f"IMEI {imei} trouvé en cache")
            cached_result['cache_hit'] = True
            return cached_result
        
        # 2. Essayer les providers par ordre de priorité
        providers = self.get_sorted_providers()
        
        for provider_name, provider_config in providers:
            if not provider_config.get('enabled', False):
                continue
                
            if self.is_rate_limited(provider_name):
                logger.warning(f"Provider {provider_name} rate limited")
                continue
            
            try:
                result = await self.query_provider(provider_name, provider_config, imei)
                if result and result.get('status') != 'not_found':
                    # Succès - mettre en cache et retourner
                    result['provider_used'] = provider_name
                    result['cache_hit'] = False
                    self.cache_result(imei, result)
                    self.update_usage(provider_name)
                    
                    logger.info(f"IMEI {imei} trouvé via {provider_name}")
                    return result
                    
            except Exception as e:
                logger.error(f"Erreur avec provider {provider_name}: {e}")
                continue
        
        # 3. Aucun provider n'a trouvé l'IMEI
        not_found_result = self.create_not_found_response(imei, "Non trouvé dans toutes les sources")
        self.cache_result(imei, not_found_result)  # Cache aussi les "non trouvé"
        return not_found_result
    
    def get_sorted_providers(self) -> List[Tuple[str, Dict]]:
        """Retourne les providers triés par priorité"""
        providers = self.config.get('external_apis', {}).get('providers', {})
        return sorted(
            providers.items(),
            key=lambda x: x[1].get('priority', 999)
        )
    
    async def query_provider(self, name: str, config: Dict, imei: str) -> Optional[Dict]:
        """Query un provider spécifique"""
        
        if config.get('type') == 'local_database':
            return self.query_local_tac_db(imei)
        
        # APIs HTTP externes
        if 'imei.info' in config.get('url', ''):
            return await self.query_imei_info(config['url'], imei)
        elif 'checkimei.com' in config.get('url', ''):
            return await self.query_checkimei_com(config['url'], imei, config.get('api_key'))
        elif 'imeicheck.com' in config.get('url', ''):
            return await self.query_imeicheck_com(config['url'], imei)
        
        return None
    
    def query_local_tac_db(self, imei: str) -> Optional[Dict]:
        """Query la base de données TAC locale"""
        if len(imei) < 8:
            return None
            
        tac = imei[:8]
        tac_info = self.tac_database.get(tac)
        
        if tac_info:
            return {
                "imei": imei,
                "status": "found",
                "brand": tac_info.get("brand", "Unknown"),
                "model": tac_info.get("model", "Unknown"),
                "device_status": tac_info.get("status", "valid"),
                "device_type": tac_info.get("type", "smartphone"),
                "source": "local_tac_database",
                "timestamp": datetime.now().isoformat(),
                "tac": tac
            }
        
        return None
    
    async def query_imei_info(self, base_url: str, imei: str) -> Optional[Dict]:
        """Query IMEI.info API (gratuite)"""
        try:
            timeout = aiohttp.ClientTimeout(
                total=self.config.get('external_apis', {}).get('timeouts', {}).get('total_timeout', 15)
            )
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"{base_url}?imei={imei}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        # API imei.info retourne souvent du HTML, pas du JSON
                        text = await response.text()
                        
                        # Parse basique du contenu HTML
                        if "valid" in text.lower() or "samsung" in text.lower() or "apple" in text.lower():
                            # Extraction basique des informations
                            brand = "Unknown"
                            model = "Unknown"
                            
                            # Logique d'extraction simplifiée
                            if "samsung" in text.lower():
                                brand = "Samsung"
                            elif "apple" in text.lower() or "iphone" in text.lower():
                                brand = "Apple"
                            elif "huawei" in text.lower():
                                brand = "Huawei"
                            
                            return {
                                "imei": imei,
                                "status": "found",
                                "brand": brand,
                                "model": model,
                                "source": "imei_info_api",
                                "timestamp": datetime.now().isoformat(),
                                "raw_response": text[:200]  # Premiers 200 caractères pour debug
                            }
                        
        except Exception as e:
            logger.error(f"Erreur IMEI.info API: {e}")
        
        return None
    
    async def query_checkimei_com(self, base_url: str, imei: str, api_key: str) -> Optional[Dict]:
        """Query CheckIMEI.com API (freemium)"""
        try:
            timeout = aiohttp.ClientTimeout(
                total=self.config.get('external_apis', {}).get('timeouts', {}).get('total_timeout', 15)
            )
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {}
                if api_key:
                    headers['Authorization'] = f"Bearer {api_key}"
                
                url = f"{base_url}/{imei}"
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            "imei": imei,
                            "status": "found" if data.get('valid') else "invalid",
                            "brand": data.get('manufacturer', 'Unknown'),
                            "model": data.get('model', 'Unknown'),
                            "device_status": data.get('status', 'unknown'),
                            "source": "checkimei_com_api",
                            "timestamp": datetime.now().isoformat()
                        }
                        
        except Exception as e:
            logger.error(f"Erreur CheckIMEI.com API: {e}")
        
        return None
    
    async def query_imeicheck_com(self, base_url: str, imei: str) -> Optional[Dict]:
        """Query IMEICheck.com API (gratuite)"""
        try:
            timeout = aiohttp.ClientTimeout(
                total=self.config.get('external_apis', {}).get('timeouts', {}).get('total_timeout', 15)
            )
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"{base_url}/{imei}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            "imei": imei,
                            "status": "found" if data.get('found') else "not_found",
                            "brand": data.get('brand', 'Unknown'),
                            "model": data.get('model', 'Unknown'),
                            "source": "imeicheck_com_api",
                            "timestamp": datetime.now().isoformat()
                        }
                        
        except Exception as e:
            logger.error(f"Erreur IMEICheck.com API: {e}")
        
        return None
    
    def create_not_found_response(self, imei: str, reason: str = "Non trouvé") -> Dict:
        """Crée une réponse pour un IMEI non trouvé"""
        return {
            "imei": imei,
            "status": "not_found",
            "brand": "Unknown",
            "model": "Unknown",
            "source": "external_apis",
            "message": reason,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_from_cache(self, imei: str) -> Optional[Dict]:
        """Récupère un résultat du cache"""
        if not self.config.get('external_apis', {}).get('cache', {}).get('enabled', False):
            return None
            
        cache_key = f"imei_{hashlib.md5(imei.encode()).hexdigest()}"
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            # Vérifier expiration
            if datetime.now() < entry['expires_at']:
                return entry['data']
            else:
                del self.cache[cache_key]
        
        return None
    
    def cache_result(self, imei: str, result: Dict):
        """Met un résultat en cache"""
        if not self.config.get('external_apis', {}).get('cache', {}).get('enabled', False):
            return
            
        cache_key = f"imei_{hashlib.md5(imei.encode()).hexdigest()}"
        ttl_seconds = self.config.get('external_apis', {}).get('cache', {}).get('default_ttl', 86400)
        
        self.cache[cache_key] = {
            'data': result,
            'expires_at': datetime.now() + timedelta(seconds=ttl_seconds),
            'cached_at': datetime.now()
        }
        
        # Cleanup cache si trop grand
        max_size = self.config.get('external_apis', {}).get('cache', {}).get('max_cache_size', 10000)
        if len(self.cache) > max_size:
            # Supprimer les plus anciens
            oldest_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k]['cached_at']
            )[:len(self.cache) - max_size + 100]  # Garder un peu de marge
            
            for key in oldest_keys:
                del self.cache[key]
    
    def is_rate_limited(self, provider_name: str) -> bool:
        """Vérifie si un provider est rate limited"""
        today = datetime.now().date()
        usage_key = f"{provider_name}_{today}"
        
        provider_config = self.config.get('external_apis', {}).get('providers', {}).get(provider_name, {})
        daily_limit = provider_config.get('daily_limit', 1000)
        
        current_usage = self.daily_usage.get(usage_key, 0)
        return current_usage >= daily_limit
    
    def update_usage(self, provider_name: str):
        """Met à jour l'usage d'un provider"""
        today = datetime.now().date()
        usage_key = f"{provider_name}_{today}"
        
        self.daily_usage[usage_key] = self.daily_usage.get(usage_key, 0) + 1
    
    def get_cache_stats(self) -> Dict:
        """Retourne des statistiques du cache"""
        total_entries = len(self.cache)
        expired_entries = 0
        
        now = datetime.now()
        for entry in self.cache.values():
            if now >= entry['expires_at']:
                expired_entries += 1
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "valid_entries": total_entries - expired_entries,
            "cache_enabled": self.config.get('external_apis', {}).get('cache', {}).get('enabled', False)
        }
    
    def get_usage_stats(self) -> Dict:
        """Retourne des statistiques d'usage"""
        today = datetime.now().date()
        stats = {}
        
        for provider_name in self.config.get('external_apis', {}).get('providers', {}):
            usage_key = f"{provider_name}_{today}"
            stats[provider_name] = {
                "usage_today": self.daily_usage.get(usage_key, 0),
                "daily_limit": self.config.get('external_apis', {}).get('providers', {}).get(provider_name, {}).get('daily_limit', 0),
                "rate_limited": self.is_rate_limited(provider_name)
            }
        
        return stats

# Instance globale du service
external_imei_service = ExternalIMEIService()
