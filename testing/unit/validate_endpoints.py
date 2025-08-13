#!/usr/bin/env python3
"""
Validation des endpoints API - Compare les endpoints définis dans la configuration
avec les endpoints réellement implémentés dans l'application FastAPI
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import ast

class EndpointValidator:
    def __init__(self, config_file: str = "test/api_endpoints.json", app_dir: str = "backend/app"):
        self.config_file = config_file
        self.app_dir = app_dir
        self.config_endpoints = set()
        self.app_endpoints = set()
        
    def load_config_endpoints(self) -> Set[str]:
        """Charger les endpoints du fichier de configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            endpoints = set()
            for category, category_endpoints in config.get("endpoints", {}).items():
                for endpoint_name, endpoint_config in category_endpoints.items():
                    method = endpoint_config["method"].upper()
                    path = endpoint_config["path"]
                    endpoints.add(f"{method} {path}")
            
            return endpoints
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement de la configuration: {e}")
            return set()
    
    def extract_fastapi_endpoints(self) -> Set[str]:
        """Extraire les endpoints des fichiers Python FastAPI"""
        endpoints = set()
        
        # Parcourir tous les fichiers Python dans le répertoire app
        for py_file in Path(self.app_dir).rglob("*.py"):
            endpoints.update(self.parse_python_file(py_file))
        
        return endpoints
    
    def parse_python_file(self, file_path: Path) -> Set[str]:
        """Parser un fichier Python pour extraire les endpoints FastAPI"""
        endpoints = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Rechercher les décorateurs de routes FastAPI
            route_patterns = [
                r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
                r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
                r'router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
                r'app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in route_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    method = match.group(1).upper()
                    path = match.group(2)
                    
                    # Nettoyer le chemin
                    path = self.normalize_path(path)
                    endpoints.add(f"{method} {path}")
            
            # Rechercher aussi les routes définies via APIRouter.include_router
            include_patterns = [
                r'app\.include_router\s*\(\s*\w+\s*,\s*prefix\s*=\s*["\']([^"\']+)["\']',
                r'router\.include_router\s*\(\s*\w+\s*,\s*prefix\s*=\s*["\']([^"\']+)["\']'
            ]
            
            # Cette partie nécessiterait une analyse plus complexe pour les sous-routes
            
        except Exception as e:
            print(f"⚠️  Erreur lors du parsing de {file_path}: {e}")
        
        return endpoints
    
    def normalize_path(self, path: str) -> str:
        """Normaliser un chemin d'endpoint"""
        # Supprimer les espaces
        path = path.strip()
        
        # S'assurer que le chemin commence par /
        if not path.startswith('/'):
            path = '/' + path
        
        # Normaliser les paramètres de chemin FastAPI {param} 
        # vs les paramètres de test génériques
        path = re.sub(r'\{(\w+)\}', r'{\1}', path)
        
        return path
    
    def find_missing_endpoints(self) -> Tuple[Set[str], Set[str]]:
        """Trouver les endpoints manquants"""
        self.config_endpoints = self.load_config_endpoints()
        self.app_endpoints = self.extract_fastapi_endpoints()
        
        # Endpoints dans la config mais pas dans l'app
        missing_in_app = self.config_endpoints - self.app_endpoints
        
        # Endpoints dans l'app mais pas dans la config
        missing_in_config = self.app_endpoints - self.config_endpoints
        
        return missing_in_app, missing_in_config
    
    def generate_report(self) -> None:
        """Générer un rapport de validation"""
        print("🔍 VALIDATION DES ENDPOINTS API")
        print("=" * 80)
        
        missing_in_app, missing_in_config = self.find_missing_endpoints()
        
        print(f"📊 Statistiques:")
        print(f"   • Endpoints dans la configuration: {len(self.config_endpoints)}")
        print(f"   • Endpoints dans l'application: {len(self.app_endpoints)}")
        print(f"   • Endpoints manquants dans l'app: {len(missing_in_app)}")
        print(f"   • Endpoints manquants dans la config: {len(missing_in_config)}")
        
        # Endpoints communs
        common_endpoints = self.config_endpoints & self.app_endpoints
        if common_endpoints:
            coverage_rate = len(common_endpoints) / len(self.app_endpoints) * 100
            print(f"   • Taux de couverture: {coverage_rate:.1f}%")
        
        # Endpoints manquants dans l'application
        if missing_in_app:
            print(f"\n❌ Endpoints définis dans la config mais introuvables dans l'app ({len(missing_in_app)}):")
            for endpoint in sorted(missing_in_app):
                print(f"   • {endpoint}")
        
        # Endpoints manquants dans la configuration
        if missing_in_config:
            print(f"\n⚠️  Endpoints dans l'app mais non testés dans la config ({len(missing_in_config)}):")
            for endpoint in sorted(missing_in_config):
                print(f"   • {endpoint}")
        
        # Endpoints bien couverts
        if common_endpoints and len(missing_in_app) == 0 and len(missing_in_config) == 0:
            print(f"\n✅ Tous les endpoints sont correctement couverts!")
        elif common_endpoints:
            print(f"\n✅ Endpoints correctement couverts ({len(common_endpoints)}):")
            # Afficher seulement les premiers pour éviter un output trop long
            for endpoint in sorted(list(common_endpoints)[:10]):
                print(f"   • {endpoint}")
            if len(common_endpoints) > 10:
                print(f"   ... et {len(common_endpoints) - 10} autres")
    
    def suggest_missing_configs(self, missing_endpoints: Set[str]) -> Dict[str, Dict]:
        """Suggérer des configurations pour les endpoints manquants"""
        suggestions = {}
        
        for endpoint in missing_endpoints:
            method, path = endpoint.split(' ', 1)
            
            # Deviner la catégorie basée sur le chemin
            category = self.guess_category(path)
            
            # Générer une configuration de base
            endpoint_name = self.generate_endpoint_name(path, method)
            
            config = {
                "method": method.lower(),
                "path": path,
                "description": f"Auto-generated config for {endpoint}",
                "test_data": self.generate_test_data(method, path),
                "expected_fields": self.guess_expected_fields(path)
            }
            
            if category not in suggestions:
                suggestions[category] = {}
            suggestions[category][endpoint_name] = config
        
        return suggestions
    
    def guess_category(self, path: str) -> str:
        """Deviner la catégorie d'un endpoint basé sur son chemin"""
        path_lower = path.lower()
        
        if '/auth' in path_lower or '/login' in path_lower or '/register' in path_lower:
            return 'auth'
        elif '/user' in path_lower:
            return 'users'
        elif '/device' in path_lower or '/imei' in path_lower:
            return 'devices'
        elif '/notification' in path_lower:
            return 'notifications'
        elif '/admin' in path_lower:
            return 'admin'
        elif '/import' in path_lower or '/export' in path_lower:
            return 'import'
        elif '/protocol' in path_lower:
            return 'protocols'
        elif '/health' in path_lower or '/info' in path_lower:
            return 'system'
        else:
            return 'misc'
    
    def generate_endpoint_name(self, path: str, method: str) -> str:
        """Générer un nom d'endpoint basé sur le chemin et la méthode"""
        # Supprimer les paramètres et nettoyer
        clean_path = re.sub(r'\{[^}]+\}', '', path)
        clean_path = re.sub(r'[^a-zA-Z0-9/]', '', clean_path)
        
        # Extraire les segments significatifs
        segments = [s for s in clean_path.split('/') if s and s != 'api']
        
        # Construire le nom
        if segments:
            name = '_'.join(segments)
            if method.lower() != 'get':
                name = f"{method.lower()}_{name}"
        else:
            name = f"{method.lower()}_root"
        
        return name
    
    def generate_test_data(self, method: str, path: str) -> Dict:
        """Générer des données de test basiques"""
        if method.upper() in ['POST', 'PUT']:
            if 'device' in path.lower():
                return {"imei": "123456789012345", "status": "test"}
            elif 'user' in path.lower():
                return {"username": "test_user", "email": "test@example.com"}
            elif 'notification' in path.lower():
                return {"message": "Test notification", "type": "info"}
            else:
                return {"test": "data"}
        return {}
    
    def guess_expected_fields(self, path: str) -> List[str]:
        """Deviner les champs attendus dans la réponse"""
        if 'device' in path.lower():
            return ["imei", "status", "id"]
        elif 'user' in path.lower():
            return ["id", "username", "email"]
        elif 'notification' in path.lower():
            return ["id", "message", "created_at"]
        elif 'auth' in path.lower():
            return ["access_token", "token_type"]
        else:
            return ["id", "status"]

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
🔍 Validateur d'Endpoints API EIR Project

Usage: python3 validate_endpoints.py [OPTIONS]

OPTIONS:
    -h, --help      Afficher cette aide
    --suggest       Générer des suggestions pour les endpoints manquants
    --config FILE   Fichier de configuration (défaut: test/api_endpoints.json)
    --app-dir DIR   Répertoire de l'application (défaut: backend/app)

EXEMPLES:
    python3 validate_endpoints.py
    python3 validate_endpoints.py --suggest
    python3 validate_endpoints.py --config custom_endpoints.json
""")
        return
    
    # Parser les arguments basiques
    config_file = "test/api_endpoints.json"
    app_dir = "backend/app"
    suggest_mode = False
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--suggest":
            suggest_mode = True
        elif arg == "--config" and i + 1 < len(sys.argv):
            config_file = sys.argv[i + 1]
        elif arg == "--app-dir" and i + 1 < len(sys.argv):
            app_dir = sys.argv[i + 1]
    
    # Créer le validateur
    validator = EndpointValidator(config_file, app_dir)
    
    # Générer le rapport
    validator.generate_report()
    
    # Mode suggestion
    if suggest_mode:
        _, missing_in_config = validator.find_missing_endpoints()
        if missing_in_config:
            suggestions = validator.suggest_missing_configs(missing_in_config)
            
            print(f"\n💡 SUGGESTIONS DE CONFIGURATION")
            print("=" * 80)
            print("Ajoutez ces configurations à votre fichier JSON:")
            print()
            print(json.dumps(suggestions, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
