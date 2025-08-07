#!/bin/bash
# scripts/configurer-apis-externes.sh
# Script pour configurer les APIs externes IMEI

set -e

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🌐 Configuration des APIs Externes IMEI"
echo "======================================"

# Navigate to project root
cd "$(dirname "$0")/.."

# Function to create external APIs configuration
create_external_apis_config() {
    log_info "Création de la configuration des APIs externes..."
    
    # Create config directory if it doesn't exist
    mkdir -p config
    
    cat > "config/external_apis.yml" << 'EOF'
# Configuration des APIs externes pour vérification IMEI
external_apis:
  enabled: true
  fallback_enabled: true
  cache_duration_hours: 24
  
  providers:
    # Base de données TAC locale (priorité 0 - toujours en premier)
    local_tac_db:
      enabled: true
      type: "local_database"
      priority: 0
      description: "Base de données TAC locale gratuite"
      
    # IMEI.info - API gratuite (1000 req/jour)
    imei_info:
      enabled: true
      url: "https://imei.info/api/check.php"
      api_key: null
      daily_limit: 1000
      priority: 1
      description: "API publique gratuite"
      
    # CheckIMEI.com - API freemium (100 req/jour gratuit)
    checkimei_com:
      enabled: false  # Nécessite clé API
      url: "https://api.checkimei.com/v1/imei/"
      api_key: "${CHECKIMEI_API_KEY}"
      daily_limit: 100
      priority: 2
      description: "API freemium avec clé requise"
      
    # IMEICheck.com - API basique gratuite
    imeicheck_com:
      enabled: true
      url: "https://imeicheck.com/api/check/"
      api_key: null
      daily_limit: 500
      priority: 3
      description: "API basique gratuite"
      
  rate_limiting:
    max_requests_per_minute: 10
    max_requests_per_hour: 100
    burst_limit: 20
    
  cache:
    enabled: true
    redis_url: "${REDIS_URL:-redis://localhost:6379}"
    default_ttl: 86400  # 24 heures
    max_cache_size: 10000  # Nombre maximum d'entrées en cache
    
  timeouts:
    connection_timeout: 5
    read_timeout: 10
    total_timeout: 15
    
  logging:
    level: "INFO"
    log_requests: true
    log_cache_hits: true
    log_external_calls: true

# Configuration de la base de données TAC locale
tac_database:
  enabled: true
  update_frequency: "weekly"
  sources:
    - name: "gsma_public"
      url: "https://example.com/tac-database.json"
      format: "json"
    - name: "manual_updates"
      file: "data/manual_tac_updates.json"
      format: "json"
EOF

    log_success "Configuration des APIs externes créée: config/external_apis.yml"
}

# Function to create TAC database
create_tac_database() {
    log_info "Création de la base de données TAC locale..."
    
    # Create data directory
    mkdir -p data
    
    cat > "data/tac_database.json" << 'EOF'
{
  "metadata": {
    "last_updated": "2025-08-04",
    "version": "1.0",
    "total_entries": 15,
    "source": "Manual compilation"
  },
  "tac_entries": {
    "35274508": {
      "brand": "Samsung",
      "model": "Galaxy S21",
      "status": "valid",
      "type": "smartphone",
      "release_year": 2021
    },
    "35412345": {
      "brand": "Apple", 
      "model": "iPhone 13",
      "status": "valid",
      "type": "smartphone",
      "release_year": 2021
    },
    "86753090": {
      "brand": "Huawei",
      "model": "P50 Pro", 
      "status": "valid",
      "type": "smartphone",
      "release_year": 2021
    },
    "35123456": {
      "brand": "Xiaomi",
      "model": "Mi 11",
      "status": "valid",
      "type": "smartphone", 
      "release_year": 2021
    },
    "35987654": {
      "brand": "OnePlus",
      "model": "9 Pro",
      "status": "valid",
      "type": "smartphone",
      "release_year": 2021
    },
    "35456789": {
      "brand": "Google",
      "model": "Pixel 6",
      "status": "valid",
      "type": "smartphone",
      "release_year": 2021
    },
    "35789012": {
      "brand": "Sony",
      "model": "Xperia 1 III",
      "status": "valid",
      "type": "smartphone",
      "release_year": 2021
    },
    "35234567": {
      "brand": "Nokia",
      "model": "X20",
      "status": "valid",
      "type": "smartphone",
      "release_year": 2021
    },
    "35876543": {
      "brand": "Motorola",
      "model": "Edge 20",
      "status": "valid", 
      "type": "smartphone",
      "release_year": 2021
    },
    "35345678": {
      "brand": "Oppo",
      "model": "Find X3",
      "status": "valid",
      "type": "smartphone",
      "release_year": 2021
    },
    "35654321": {
      "brand": "Vivo",
      "model": "X70 Pro",
      "status": "valid",
      "type": "smartphone",
      "release_year": 2021
    },
    "35111111": {
      "brand": "Unknown",
      "model": "Unknown Model",
      "status": "blacklisted",
      "type": "smartphone",
      "reason": "Reported stolen"
    },
    "35999999": {
      "brand": "Fake Brand",
      "model": "Counterfeit Device",
      "status": "invalid",
      "type": "smartphone",
      "reason": "Counterfeit device"
    },
    "35000000": {
      "brand": "Test Brand",
      "model": "Test Model",
      "status": "test",
      "type": "test_device",
      "reason": "Test TAC for development"
    },
    "35888888": {
      "brand": "Legacy Brand",
      "model": "Old Model",
      "status": "deprecated",
      "type": "feature_phone",
      "reason": "Obsolete model"
    }
  }
}
EOF

    log_success "Base de données TAC créée: data/tac_database.json"
}

# Function to create external IMEI service
create_external_imei_service() {
    log_info "Création du service d'APIs externes..."
    
    # Create services directory
    mkdir -p backend/app/services
    
    cat > "backend/app/services/external_imei_service.py" << 'EOF'
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
EOF

    log_success "Service d'APIs externes créé: backend/app/services/external_imei_service.py"
}

# Function to test APIs configuration
test_apis_configuration() {
    log_info "Test de la configuration des APIs externes..."
    
    # Create a simple test script
    cat > "test_external_apis.py" << 'EOF'
#!/usr/bin/env python3
"""
Script de test pour les APIs externes IMEI
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('backend')

try:
    from app.services.external_imei_service import external_imei_service
    
    async def test_apis():
        print("🧪 Test des APIs externes IMEI")
        print("=" * 40)
        
        # IMEIs de test
        test_imeis = [
            "352745080123456",  # TAC Samsung dans notre base
            "354123456789012",  # TAC Apple dans notre base  
            "999999999999999",  # IMEI inexistant
        ]
        
        for imei in test_imeis:
            print(f"\n🔍 Test IMEI: {imei}")
            try:
                result = await external_imei_service.check_imei_external(imei)
                print(f"   Statut: {result.get('status')}")
                print(f"   Marque: {result.get('brand')}")
                print(f"   Modèle: {result.get('model')}")
                print(f"   Source: {result.get('source')}")
                print(f"   Cache hit: {result.get('cache_hit', False)}")
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
        
        # Statistiques
        print(f"\n📊 Statistiques du cache:")
        cache_stats = external_imei_service.get_cache_stats()
        for key, value in cache_stats.items():
            print(f"   {key}: {value}")
        
        print(f"\n📈 Statistiques d'usage:")
        usage_stats = external_imei_service.get_usage_stats()
        for provider, stats in usage_stats.items():
            print(f"   {provider}: {stats['usage_today']}/{stats['daily_limit']} requêtes")
    
    if __name__ == "__main__":
        asyncio.run(test_apis())
        
except ImportError as e:
    print(f"❌ Erreur d'importation: {e}")
    print("Assurez-vous que les dépendances sont installées:")
    print("   pip install aiohttp pyyaml")
EOF

    # Make executable
    chmod +x test_external_apis.py
    
    log_success "Script de test créé: test_external_apis.py"
    log_info "Pour tester: python test_external_apis.py"
}

# Function to install dependencies
install_dependencies() {
    log_info "Installation des dépendances Python..."
    
    # Add to requirements.txt if it doesn't exist
    if [[ ! -f "backend/requirements.txt" ]] || ! grep -q "aiohttp" backend/requirements.txt; then
        echo "" >> backend/requirements.txt
        echo "# APIs externes" >> backend/requirements.txt
        echo "aiohttp>=3.8.0" >> backend/requirements.txt
        echo "pyyaml>=6.0" >> backend/requirements.txt
        
        log_success "Dépendances ajoutées à requirements.txt"
    fi
    
    # Install in container if running
    if docker compose ps | grep -q "Up"; then
        log_info "Installation des dépendances dans le conteneur..."
        docker compose exec web pip install aiohttp pyyaml
        log_success "Dépendances installées dans le conteneur"
    else
        log_warning "Conteneurs non démarrés. Installez manuellement: pip install aiohttp pyyaml"
    fi
}

# Function to create endpoint integration
create_endpoint_integration() {
    log_info "Création de l'intégration avec l'endpoint principal..."
    
    cat > "backend/app/external_integration_example.py" << 'EOF'
"""
Exemple d'intégration des APIs externes dans main.py
Copiez ce code dans votre endpoint /imei/{imei}
"""

# Import à ajouter en haut de main.py
# from .services.external_imei_service import external_imei_service

# Modification de l'endpoint /imei/{imei}
@app.get("/imei/{imei}")
async def verifier_imei(
    imei: str,
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
    translator = Depends(get_current_translator),
    audit_service: AuditService = Depends(get_audit_service)
):
    # ... code existant pour vérifications d'accès ...
    
    # Search for IMEI in local database first
    imei_record = db.query(IMEI).filter(IMEI.numero_imei == imei).first()
    found = imei_record is not None
    
    # Log the search in Recherche table
    recherche = Recherche(
        id=uuid.uuid4(),
        date_recherche=datetime.now(),
        imei_recherche=imei,
        utilisateur_id=user.id if user else None
    )
    db.add(recherche)
    
    if imei_record:
        # IMEI trouvé localement - code existant
        appareil = imei_record.appareil
        
        response_data = {
            "id": str(imei_record.id),
            "imei": imei,
            "trouve": True,
            "statut": imei_record.statut,
            "source": "local_database",
            "appareil": {
                "marque": appareil.marque,
                "modele": appareil.modele
            },
            "recherche_enregistree": True,
            "id_recherche": str(recherche.id)
        }
        
        db.commit()
        return response_data
    
    else:
        # IMEI non trouvé localement - chercher via APIs externes
        try:
            external_result = await external_imei_service.check_imei_external(imei)
            
            if external_result.get('status') == 'found':
                # IMEI trouvé via API externe
                
                # Optionnel: sauvegarder en base locale pour cache permanent
                if external_result.get('source') != 'local_tac_database':
                    # Créer un nouvel appareil en base
                    new_appareil = Appareil(
                        id=uuid.uuid4(),
                        marque=external_result.get('brand', 'Unknown'),
                        modele=external_result.get('model', 'Unknown'),
                        emmc=None,
                        utilisateur_id=None
                    )
                    db.add(new_appareil)
                    db.flush()
                    
                    # Créer l'IMEI associé
                    new_imei = IMEI(
                        id=uuid.uuid4(),
                        numero_imei=imei,
                        numero_slot=1,
                        statut='active',
                        appareil_id=new_appareil.id
                    )
                    db.add(new_imei)
                
                db.commit()
                
                return {
                    "id": str(new_imei.id) if 'new_imei' in locals() else None,
                    "imei": imei,
                    "trouve": True,
                    "statut": external_result.get('device_status', 'active'),
                    "source": "external_api",
                    "provider_used": external_result.get('provider_used'),
                    "cache_hit": external_result.get('cache_hit', False),
                    "appareil": {
                        "marque": external_result.get('brand', 'Unknown'),
                        "modele": external_result.get('model', 'Unknown')
                    },
                    "external_data": external_result,
                    "recherche_enregistree": True,
                    "id_recherche": str(recherche.id)
                }
            
        except Exception as e:
            logger.error(f"Erreur APIs externes pour IMEI {imei}: {e}")
        
        # IMEI non trouvé nulle part
        db.commit()
        
        return {
            "imei": imei,
            "trouve": False,
            "source": "not_found",
            "message": translator.translate("erreur_imei_non_trouve"),
            "recherche_enregistree": True,
            "id_recherche": str(recherche.id)
        }
EOF

    log_success "Exemple d'intégration créé: backend/app/external_integration_example.py"
}

# Main menu
show_menu() {
    echo ""
    echo "🔢 Options disponibles:"
    echo "  1) Créer la configuration des APIs externes"
    echo "  2) Créer la base de données TAC locale"
    echo "  3) Créer le service d'APIs externes"
    echo "  4) Installer les dépendances"
    echo "  5) Créer le script de test"
    echo "  6) Créer l'exemple d'intégration"
    echo "  7) Configuration complète (toutes les étapes)"
    echo "  8) Tester la configuration"
    echo "  9) Quitter"
    echo ""
}

# Function to do complete setup
complete_setup() {
    log_info "Configuration complète des APIs externes..."
    
    create_external_apis_config
    create_tac_database
    create_external_imei_service
    install_dependencies
    test_apis_configuration
    create_endpoint_integration
    
    log_success "Configuration complète terminée!"
    
    echo ""
    echo "📋 Prochaines étapes:"
    echo "1. Vérifiez la configuration: config/external_apis.yml"
    echo "2. Testez: python test_external_apis.py"
    echo "3. Intégrez le code d'exemple dans main.py"
    echo "4. Redémarrez l'application: docker compose restart web"
    echo ""
    echo "💡 Pour activer CheckIMEI.com:"
    echo "   - Obtenez une clé API sur checkimei.com"
    echo "   - Ajoutez CHECKIMEI_API_KEY=votre_cle dans .env"
    echo "   - Activez le provider dans config/external_apis.yml"
}

# Parse command line arguments
case "${1:-}" in
    --config)
        create_external_apis_config
        ;;
    --tac-db)
        create_tac_database
        ;;
    --service)
        create_external_imei_service
        ;;
    --deps)
        install_dependencies
        ;;
    --test)
        test_apis_configuration
        ;;
    --integration)
        create_endpoint_integration
        ;;
    --complete)
        complete_setup
        ;;
    --help)
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  --config       Créer configuration APIs"
        echo "  --tac-db       Créer base TAC locale"
        echo "  --service      Créer service d'APIs"
        echo "  --deps         Installer dépendances"
        echo "  --test         Créer script de test"
        echo "  --integration  Créer exemple d'intégration"
        echo "  --complete     Configuration complète"
        echo "  --help         Afficher cette aide"
        ;;
    *)
        # Interactive mode
        while true; do
            show_menu
            read -p "Choisissez une option (1-9): " choice
            
            case $choice in
                1)
                    create_external_apis_config
                    ;;
                2)
                    create_tac_database
                    ;;
                3)
                    create_external_imei_service
                    ;;
                4)
                    install_dependencies
                    ;;
                5)
                    test_apis_configuration
                    ;;
                6)
                    create_endpoint_integration
                    ;;
                7)
                    complete_setup
                    ;;
                8)
                    if [[ -f "test_external_apis.py" ]]; then
                        log_info "Exécution des tests..."
                        python test_external_apis.py
                    else
                        log_error "Script de test non trouvé. Créez-le d'abord (option 5)"
                    fi
                    ;;
                9)
                    log_info "Au revoir!"
                    exit 0
                    ;;
                *)
                    log_warning "Option invalide. Veuillez choisir entre 1 et 9."
                    ;;
            esac
            
            echo ""
            read -p "Appuyez sur Entrée pour continuer..."
        done
        ;;
esac

log_success "Opération terminée"
