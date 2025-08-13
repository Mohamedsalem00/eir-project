#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📋 Configuration des Endpoints API EIR - Wrapper JSON
Fichier de chargement et gestion de la configuration JSON des endpoints
Version: 2.0.0 - Basé sur JSON avec wrapper Python
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

# Chemin vers le fichier de configuration JSON
CONFIG_FILE = Path(__file__).parent / "api_endpoints.json"

class APIEndpointsConfig:
    """Gestionnaire de configuration des endpoints API basé sur JSON"""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialiser avec le fichier de configuration JSON"""
        self.config_file = config_file or CONFIG_FILE
        self._config = None
        self.load_config()
    
    def load_config(self):
        """Charger la configuration depuis le fichier JSON"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Fichier de configuration non trouvé: {self.config_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erreur de parsing JSON: {e}")
    
    @property
    def api_config(self) -> Dict[str, Any]:
        """Obtenir la configuration API"""
        return self._config.get("api_config", {})
    
    @property
    def endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Obtenir tous les endpoints"""
        return self._config.get("endpoints", {})
    
    @property
    def test_groups(self) -> Dict[str, List[str]]:
        """Obtenir les groupes de test"""
        return self._config.get("test_groups", {})
    
    @property
    def test_config(self) -> Dict[str, Any]:
        """Obtenir la configuration de test"""
        return self._config.get("test_config", {})
    
    def get_endpoint(self, category: str, name: str) -> Dict[str, Any]:
        """Récupérer la configuration d'un endpoint spécifique"""
        return self.endpoints.get(category, {}).get(name, {})
    
    def get_all_endpoints(self) -> Dict[str, Dict[str, Any]]:
        """Récupérer tous les endpoints organisés par catégorie"""
        return self.endpoints
    
    def get_endpoints_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Récupérer tous les endpoints avec un tag spécifique"""
        matching_endpoints = []
        for category_name, category in self.endpoints.items():
            for endpoint_name, endpoint in category.items():
                if tag in endpoint.get("tags", []):
                    matching_endpoints.append({
                        "category": category_name,
                        "name": endpoint_name,
                        "config": endpoint
                    })
        return matching_endpoints
    
    def get_test_group(self, group_name: str) -> List[str]:
        """Récupérer les endpoints d'un groupe de test"""
        if group_name not in self.test_groups:
            return []
        
        group = self.test_groups[group_name]
        
        if group == "all":
            # Retourner tous les endpoints
            all_endpoints = []
            for category_name, category in self.endpoints.items():
                for endpoint_name in category.keys():
                    all_endpoints.append(f"{category_name}.{endpoint_name}")
            return all_endpoints
        
        return group
    
    def get_endpoint_by_path(self, path: str, method: str = "GET") -> Dict[str, Any]:
        """Trouver un endpoint par son chemin et méthode"""
        for category in self.endpoints.values():
            for endpoint in category.values():
                if (endpoint.get("path") == path and 
                    endpoint.get("method", "GET").upper() == method.upper()):
                    return endpoint
        return {}
    
    def get_authenticated_endpoints(self) -> List[str]:
        """Obtenir tous les endpoints nécessitant une authentification"""
        authenticated = []
        for category_name, category in self.endpoints.items():
            for endpoint_name, endpoint in category.items():
                if endpoint.get("auth_required", False):
                    authenticated.append(f"{category_name}.{endpoint_name}")
        return authenticated
    
    def get_public_endpoints(self) -> List[str]:
        """Obtenir tous les endpoints publics"""
        public = []
        for category_name, category in self.endpoints.items():
            for endpoint_name, endpoint in category.items():
                if not endpoint.get("auth_required", False):
                    public.append(f"{category_name}.{endpoint_name}")
        return public
    
    def get_admin_endpoints(self) -> List[str]:
        """Obtenir tous les endpoints administratifs"""
        admin = []
        for category_name, category in self.endpoints.items():
            for endpoint_name, endpoint in category.items():
                if "Admin" in endpoint.get("tags", []):
                    admin.append(f"{category_name}.{endpoint_name}")
        return admin
    
    def add_endpoint(self, category: str, name: str, config: Dict[str, Any]):
        """Ajouter un nouvel endpoint à la configuration"""
        if category not in self.endpoints:
            self.endpoints[category] = {}
        self.endpoints[category][name] = config
    
    def save_config(self):
        """Sauvegarder la configuration modifiée dans le fichier JSON"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2, ensure_ascii=False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtenir des statistiques sur la configuration"""
        total_endpoints = sum(len(cat) for cat in self.endpoints.values())
        auth_required = len(self.get_authenticated_endpoints())
        admin_endpoints = len(self.get_admin_endpoints())
        
        priorities = {"high": 0, "medium": 0, "low": 0}
        for category in self.endpoints.values():
            for endpoint in category.values():
                priority = endpoint.get("test_priority", "medium")
                if priority in priorities:
                    priorities[priority] += 1
        
        return {
            "total_endpoints": total_endpoints,
            "categories": list(self.endpoints.keys()),
            "test_groups": list(self.test_groups.keys()),
            "auth_required": auth_required,
            "admin_endpoints": admin_endpoints,
            "public_endpoints": total_endpoints - auth_required,
            "priorities": priorities
        }


# Créer une instance globale pour compatibilité avec l'ancienne interface
_config_instance = APIEndpointsConfig()

# Exporter les variables pour compatibilité avec l'ancien code
API_CONFIG = _config_instance.api_config
ENDPOINTS = _config_instance.endpoints
TEST_GROUPS = _config_instance.test_groups
TEST_CONFIG = _config_instance.test_config

# Exporter les fonctions pour compatibilité
get_endpoint = _config_instance.get_endpoint
get_all_endpoints = _config_instance.get_all_endpoints
get_endpoints_by_tag = _config_instance.get_endpoints_by_tag
get_test_group = _config_instance.get_test_group
get_endpoint_by_path = _config_instance.get_endpoint_by_path

# Nouvelles fonctions basées sur la configuration JSON
def get_authenticated_endpoints() -> List[str]:
    """Obtenir tous les endpoints nécessitant une authentification"""
    return _config_instance.get_authenticated_endpoints()

def get_public_endpoints() -> List[str]:
    """Obtenir tous les endpoints publics"""
    return _config_instance.get_public_endpoints()

def get_admin_endpoints() -> List[str]:
    """Obtenir tous les endpoints administratifs"""
    return _config_instance.get_admin_endpoints()


if __name__ == "__main__":
    # Test de la configuration
    config = APIEndpointsConfig()
    stats = config.get_statistics()
    
    print("🧪 Configuration des Endpoints API EIR - Version JSON")
    print(f"📊 Nombre total d'endpoints: {stats['total_endpoints']}")
    print(f"📂 Catégories: {stats['categories']}")
    print(f"🎯 Groupes de test: {stats['test_groups']}")
    print(f"🔐 Endpoints nécessitant auth: {stats['auth_required']}")
    print(f"👑 Endpoints admin: {stats['admin_endpoints']}")
    print(f"🌐 Endpoints publics: {stats['public_endpoints']}")
    print(f"⚡ Priorités: {stats['priorities']}")
    
    # Test des nouvelles fonctionnalités TAC
    tac_endpoints = config.get_endpoints_by_tag("TAC")
    print(f"📱 Endpoints TAC: {len(tac_endpoints)}")
    
    tac_group = config.get_test_group("tac")
    print(f"🧪 Groupe TAC: {len(tac_group)} endpoints")
