#!/usr/bin/env python3
"""
🧪 Test API EIR - Version 2.0 avec Configuration Centralisée JSON
Tests automatisés utilisant la configuration JSON centralisée des endpoints
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Importer la nouvelle configuration JSON
try:
    from api_endpoints_config_v2 import (
        ENDPOINTS, TEST_CONFIG, TEST_GROUPS, 
        get_endpoint, get_all_endpoints, get_test_group,
        get_endpoints_by_tag, API_CONFIG, APIEndpointsConfig
    )
    print("✅ Configuration JSON chargée avec succès")
except ImportError:
    # Fallback vers l'ancienne configuration Python
    from api_endpoints_config import (
        ENDPOINTS, TEST_CONFIG, TEST_GROUPS, 
        get_endpoint, get_all_endpoints, get_test_group,
        get_endpoints_by_tag, API_CONFIG
    )
    print("⚠️  Utilisation de la configuration Python (fallback)")

class APITesterV2:
    def __init__(self, base_url: str = None, test_group: str = "core"):
        self.base_url = base_url or TEST_CONFIG["base_url"]
        self.session = requests.Session()
        self.token = None
        self.test_results = []
        self.test_group = test_group
        self.summary = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "skipped": 0,
            "start_time": None,
            "end_time": None,
            "duration": None,
            "test_group": test_group,
            "api_info": API_CONFIG["info"]
        }

    def log_test(self, endpoint_info: dict, status: str, response_code: int = None, 
                 response_time: float = None, error: str = None, response_data: Any = None):
        """Enregistrer le résultat d'un test avec informations d'endpoint"""
        result = {
            "name": endpoint_info.get("summary", "Unknown"),
            "category": endpoint_info.get("category", "Unknown"),
            "endpoint_key": endpoint_info.get("endpoint_key", "Unknown"),
            "method": endpoint_info.get("method", "GET"),
            "path": endpoint_info.get("path", ""),
            "tags": endpoint_info.get("tags", []),
            "auth_required": endpoint_info.get("auth_required", False),
            "test_priority": endpoint_info.get("test_priority", "medium"),
            "status": status,
            "response_code": response_code,
            "response_time": response_time,
            "error": error,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        self.summary["total_tests"] += 1
        
        status_icon = {
            "PASS": "✅",
            "FAIL": "❌", 
            "WARN": "⚠️",
            "SKIP": "⏭️"
        }.get(status, "❓")
        
        if status == "PASS":
            self.summary["passed"] += 1
        elif status == "FAIL":
            self.summary["failed"] += 1
        elif status == "WARN":
            self.summary["warnings"] += 1
        elif status == "SKIP":
            self.summary["skipped"] += 1
            
        # Affichage avec plus d'informations
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
            endpoint_info.get("test_priority", "medium"), "⚪"
        )
        
        print(f"{status_icon} {priority_icon} {endpoint_info.get('summary', 'Unknown')} - {status}")
        if error and status in ["FAIL", "WARN"]:
            print(f"    💬 {error}")
        if response_time:
            print(f"    ⏱️  {response_time:.3f}s")

    def make_request(self, endpoint_config: dict, path_params: dict = None) -> requests.Response:
        """Faire une requête HTTP basée sur la configuration d'endpoint"""
        path = endpoint_config["path"]
        method = endpoint_config.get("method", "GET").upper()
        
        # Remplacer les paramètres de chemin
        if path_params:
            for param, value in path_params.items():
                path = path.replace(f"{{{param}}}", str(value))
        
        url = f"{self.base_url}{path}"
        
        # Préparer les headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Ajouter l'authentification si nécessaire
        if endpoint_config.get("auth_required", False) and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        # Préparer les données de test
        test_data = endpoint_config.get("test_data")
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=TEST_CONFIG["default_timeout"])
            elif method == "POST":
                response = self.session.post(url, json=test_data, headers=headers, timeout=TEST_CONFIG["default_timeout"])
            elif method == "PUT":
                response = self.session.put(url, json=test_data, headers=headers, timeout=TEST_CONFIG["default_timeout"])
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=TEST_CONFIG["default_timeout"])
            else:
                raise ValueError(f"Méthode HTTP non supportée: {method}")
                
            return response
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur de requête: {str(e)}")

    def authenticate(self) -> bool:
        """S'authentifier avec les credentials par défaut"""
        login_config = get_endpoint("auth", "login")
        if not login_config:
            print("❌ Configuration de login non trouvée")
            return False
            
        try:
            auth_data = TEST_CONFIG["test_users"]["admin"]
            login_config["test_data"] = auth_data
            
            print("🔐 Authentification en cours...")
            start_time = time.time()
            response = self.make_request(login_config)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.token = data["access_token"]
                    print(f"✅ Authentification réussie ({response_time:.3f}s)")
                    return True
                else:
                    print("❌ Token non trouvé dans la réponse")
                    return False
            else:
                print(f"❌ Échec authentification: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur d'authentification: {str(e)}")
            return False

    def test_endpoint(self, category: str, endpoint_key: str, endpoint_config: dict):
        """Tester un endpoint spécifique"""
        endpoint_info = {
            "category": category,
            "endpoint_key": endpoint_key,
            **endpoint_config
        }
        
        try:
            # Vérifier si l'authentification est requise
            if endpoint_config.get("auth_required", False) and not self.token:
                self.log_test(
                    endpoint_info, "SKIP", None, None,
                    "Authentification requise mais non disponible"
                )
                return
            
            # Préparer les paramètres de chemin si nécessaire
            path_params = endpoint_config.get("path_params", {})
            if path_params:
                # Utiliser les données de test par défaut si nécessaire
                for param, default_value in path_params.items():
                    if param in TEST_CONFIG["test_data"]:
                        path_params[param] = TEST_CONFIG["test_data"][param]
            
            # Exécuter la requête
            start_time = time.time()
            response = self.make_request(endpoint_config, path_params)
            response_time = time.time() - start_time
            
            # Analyser la réponse
            self.analyze_response(endpoint_info, response, response_time)
            
        except Exception as e:
            self.log_test(endpoint_info, "FAIL", None, None, str(e))

    def analyze_response(self, endpoint_info: dict, response: requests.Response, response_time: float):
        """Analyser la réponse d'un endpoint"""
        endpoint_config = endpoint_info
        
        # Codes de statut attendus selon le contexte
        if response.status_code == 200:
            # Succès - vérifier le contenu
            try:
                data = response.json()
                expected_fields = endpoint_config.get("expected_fields", [])
                
                if expected_fields:
                    missing_fields = [field for field in expected_fields if field not in data]
                    if missing_fields:
                        self.log_test(
                            endpoint_info, "WARN", response.status_code, response_time,
                            f"Champs manquants: {missing_fields}", data
                        )
                    else:
                        self.log_test(
                            endpoint_info, "PASS", response.status_code, response_time,
                            None, {"validated_fields": expected_fields}
                        )
                else:
                    self.log_test(
                        endpoint_info, "PASS", response.status_code, response_time,
                        None, {"response_size": len(str(data))}
                    )
                    
            except json.JSONDecodeError:
                self.log_test(
                    endpoint_info, "WARN", response.status_code, response_time,
                    "Réponse non-JSON", {"content_type": response.headers.get("content-type")}
                )
                
        elif response.status_code == 401:
            # Non autorisé - normal pour certains endpoints
            if endpoint_config.get("auth_required", False):
                self.log_test(
                    endpoint_info, "WARN", response.status_code, response_time,
                    "Authentification requise (attendu)"
                )
            else:
                self.log_test(
                    endpoint_info, "FAIL", response.status_code, response_time,
                    "Authentification inattendue"
                )
                
        elif response.status_code == 403:
            # Interdit - peut être normal selon les permissions
            self.log_test(
                endpoint_info, "WARN", response.status_code, response_time,
                "Accès interdit (permissions insuffisantes)"
            )
            
        elif response.status_code == 404:
            # Non trouvé
            self.log_test(
                endpoint_info, "FAIL", response.status_code, response_time,
                "Endpoint non trouvé"
            )
            
        elif response.status_code >= 500:
            # Erreur serveur
            self.log_test(
                endpoint_info, "FAIL", response.status_code, response_time,
                f"Erreur serveur: {response.status_code}"
            )
            
        else:
            # Autres codes de statut
            self.log_test(
                endpoint_info, "WARN", response.status_code, response_time,
                f"Code de statut inattendu: {response.status_code}"
            )

    def run_tests(self):
        """Exécuter tous les tests du groupe sélectionné"""
        print(f"\n🚀 Démarrage des tests API EIR - Groupe: {self.test_group}")
        print(f"📍 URL de base: {self.base_url}")
        print(f"📋 API: {API_CONFIG['info']['title']} v{API_CONFIG['info']['version']}")
        print("=" * 60)
        
        self.summary["start_time"] = datetime.now().isoformat()
        
        # Obtenir les endpoints à tester
        if self.test_group == "all":
            endpoints_to_test = []
            for category_name, category in get_all_endpoints().items():
                for endpoint_key, endpoint_config in category.items():
                    endpoints_to_test.append((category_name, endpoint_key, endpoint_config))
        else:
            endpoint_keys = get_test_group(self.test_group)
            endpoints_to_test = []
            
            for endpoint_ref in endpoint_keys:
                if "." in endpoint_ref:
                    category_name, endpoint_key = endpoint_ref.split(".", 1)
                    endpoint_config = get_endpoint(category_name, endpoint_key)
                    if endpoint_config:
                        endpoints_to_test.append((category_name, endpoint_key, endpoint_config))
        
        print(f"📊 Nombre d'endpoints à tester: {len(endpoints_to_test)}")
        
        # Authentification si nécessaire
        auth_needed = any(ep[2].get("auth_required", False) for ep in endpoints_to_test)
        if auth_needed:
            if not self.authenticate():
                print("❌ Impossible de continuer sans authentification")
                return
        
        print("\n🧪 Exécution des tests...")
        print("-" * 40)
        
        # Exécuter les tests par priorité
        priorities = ["high", "medium", "low"]
        for priority in priorities:
            priority_tests = [ep for ep in endpoints_to_test if ep[2].get("test_priority") == priority]
            
            if priority_tests:
                priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                print(f"\n{priority_icons[priority]} Tests priorité {priority.upper()} ({len(priority_tests)} endpoints)")
                
                for category_name, endpoint_key, endpoint_config in priority_tests:
                    self.test_endpoint(category_name, endpoint_key, endpoint_config)
                    time.sleep(0.1)  # Petite pause entre les tests
        
        self.summary["end_time"] = datetime.now().isoformat()
        start_dt = datetime.fromisoformat(self.summary["start_time"])
        end_dt = datetime.fromisoformat(self.summary["end_time"])
        self.summary["duration"] = (end_dt - start_dt).total_seconds()
        
        self.print_summary()
        self.save_report()

    def print_summary(self):
        """Afficher le résumé des tests"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        print(f"🎯 Groupe de test: {self.test_group}")
        print(f"⏱️  Durée totale: {self.summary['duration']:.2f}s")
        print(f"📊 Tests exécutés: {self.summary['total_tests']}")
        print(f"✅ Réussites: {self.summary['passed']}")
        print(f"❌ Échecs: {self.summary['failed']}")
        print(f"⚠️  Avertissements: {self.summary['warnings']}")
        print(f"⏭️  Ignorés: {self.summary['skipped']}")
        
        if self.summary['total_tests'] > 0:
            success_rate = (self.summary['passed'] / self.summary['total_tests']) * 100
            print(f"📈 Taux de réussite: {success_rate:.1f}%")
            
            # Temps de réponse moyen
            response_times = [r['response_time'] for r in self.test_results if r['response_time']]
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                max_time = max(response_times)
                min_time = min(response_times)
                print(f"⚡ Temps de réponse moyen: {avg_time:.3f}s")
                print(f"🐌 Plus lent: {max_time:.3f}s")
                print(f"🚀 Plus rapide: {min_time:.3f}s")
        
        # Recommandations
        print("\n💡 RECOMMANDATIONS:")
        if self.summary['failed'] > 0:
            print("  🔧 Corriger les endpoints en échec")
            failed_endpoints = [r['name'] for r in self.test_results if r['status'] == 'FAIL']
            print(f"     Endpoints échoués: {', '.join(failed_endpoints[:3])}...")
        
        if self.summary['warnings'] > 0:
            print("  ⚠️  Vérifier les avertissements")
        
        if self.summary['passed'] == self.summary['total_tests']:
            print("  🎉 Excellent! Tous les tests passent!")

    def save_report(self):
        """Sauvegarder le rapport détaillé"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_test_report_v2_{timestamp}.json"
        
        report = {
            "summary": self.summary,
            "results": self.test_results,
            "config": {
                "test_group": self.test_group,
                "base_url": self.base_url,
                "api_info": API_CONFIG["info"]
            }
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Rapport sauvegardé: {filename}")
        except Exception as e:
            print(f"\n❌ Erreur sauvegarde rapport: {str(e)}")

def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test API EIR v2.0 avec configuration centralisée")
    parser.add_argument("--url", default=TEST_CONFIG["base_url"], help="URL de base de l'API")
    parser.add_argument("--group", default="core", choices=list(TEST_GROUPS.keys()) + ["all"], 
                       help="Groupe de tests à exécuter")
    parser.add_argument("--list-groups", action="store_true", help="Lister les groupes disponibles")
    parser.add_argument("--list-endpoints", action="store_true", help="Lister tous les endpoints")
    parser.add_argument("--tag", help="Tester uniquement les endpoints avec ce tag")
    
    args = parser.parse_args()
    
    if args.list_groups:
        print("📋 Groupes de test disponibles:")
        for group_name, endpoints in TEST_GROUPS.items():
            count = len(endpoints) if isinstance(endpoints, list) else "tous"
            print(f"  🎯 {group_name}: {count} endpoints")
        return
    
    if args.list_endpoints:
        print("📋 Tous les endpoints disponibles:")
        for category_name, category in get_all_endpoints().items():
            print(f"\n📂 {category_name}:")
            for endpoint_key, endpoint in category.items():
                auth_icon = "🔐" if endpoint.get("auth_required") else "🌐"
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                    endpoint.get("test_priority", "medium"), "⚪"
                )
                print(f"  {auth_icon} {priority_icon} {endpoint_key}: {endpoint.get('method', 'GET')} {endpoint.get('path', '')}")
        return
    
    if args.tag:
        # Tester uniquement les endpoints avec un tag spécifique
        matching_endpoints = get_endpoints_by_tag(args.tag)
        print(f"🏷️  Endpoints avec tag '{args.tag}': {len(matching_endpoints)}")
        if not matching_endpoints:
            print("❌ Aucun endpoint trouvé avec ce tag")
            return
        
        # Créer un groupe temporaire
        temp_group = [f"{ep['category']}.{ep['name']}" for ep in matching_endpoints]
        TEST_GROUPS[f"tag_{args.tag}"] = temp_group
        test_group = f"tag_{args.tag}"
    else:
        test_group = args.group
    
    # Créer et exécuter le testeur
    tester = APITesterV2(args.url, test_group)
    
    try:
        tester.run_tests()
        
        # Code de sortie basé sur les résultats
        if tester.summary["failed"] > 0:
            sys.exit(1)
        elif tester.summary["warnings"] > 0:
            sys.exit(2)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrompus par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erreur critique: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
