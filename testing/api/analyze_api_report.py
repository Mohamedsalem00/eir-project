#!/usr/bin/env python3
"""
Script d'analyse du rapport de test API EIR v2.0
Analyse les échecs, avertissements et performances
"""

import json
import sys
from collections import defaultdict

def analyze_api_report(report_file):
    """Analyse complète du rapport de test API"""
    
    with open(report_file, 'r', encoding='utf-8') as f:
        rapport = json.load(f)
    
    print("🔍 ANALYSE COMPLÈTE DU RAPPORT API EIR v2.0")
    print("=" * 60)
    
    # 1. RÉSUMÉ GLOBAL
    summary = rapport['summary']
    total = summary['total_tests']
    passed = summary['passed']
    failed = summary['failed']
    warnings = summary['warnings']
    
    print(f"📊 RÉSUMÉ GLOBAL:")
    print(f"   📝 Total des tests: {total}")
    print(f"   ✅ Réussites: {passed} ({passed/total*100:.1f}%)")
    print(f"   ❌ Échecs: {failed} ({failed/total*100:.1f}%)")
    print(f"   ⚠️  Avertissements: {warnings} ({warnings/total*100:.1f}%)")
    print(f"   ⏱️  Durée totale: {summary['duration']:.2f}s")
    print(f"   🚀 Temps moyen par test: {summary['duration']/total:.3f}s")
    print()
    
    # 2. ANALYSE DES ÉCHECS
    failed_tests = [r for r in rapport['results'] if r['status'] == 'FAIL']
    if failed_tests:
        print(f"❌ ENDPOINTS EN ÉCHEC ({len(failed_tests)} endpoints):")
        print("-" * 50)
        
        # Grouper par code d'erreur
        errors_by_code = defaultdict(list)
        for test in failed_tests:
            code = test['response_code']
            errors_by_code[code].append(test)
        
        for code, tests in errors_by_code.items():
            print(f"   🔴 Erreur {code} ({len(tests)} endpoints):")
            for test in tests:
                print(f"      • {test['name']}")
                print(f"        📍 {test['method']} {test['path']}")
                print(f"        📂 Catégorie: {test['category']}")
                print(f"        🔑 Priorité: {test['test_priority']}")
                print(f"        🔒 Auth requis: {'Oui' if test['auth_required'] else 'Non'}")
                print(f"        ⏱️  Temps: {test['response_time']:.3f}s")
                print()
        print()
    
    # 3. ANALYSE DES AVERTISSEMENTS
    warning_tests = [r for r in rapport['results'] if r['status'] == 'WARN']
    if warning_tests:
        print(f"⚠️  ENDPOINTS AVEC AVERTISSEMENTS ({len(warning_tests)} endpoints):")
        print("-" * 50)
        
        # Grouper par type d'avertissement
        warnings_by_type = defaultdict(list)
        for test in warning_tests:
            error_msg = test['error']
            if 'Champs manquants' in error_msg:
                warnings_by_type['Champs manquants'].append(test)
            elif 'Code de statut' in error_msg:
                warnings_by_type['Code de statut inattendu'].append(test)
            else:
                warnings_by_type['Autre'].append(test)
        
        for warn_type, tests in warnings_by_type.items():
            print(f"   🟡 {warn_type} ({len(tests)} endpoints):")
            for test in tests:
                print(f"      • {test['name']}")
                print(f"        📍 {test['method']} {test['path']}")
                print(f"        📂 Catégorie: {test['category']}")
                print(f"        ⚠️  Détail: {test['error']}")
                print()
        print()
    
    # 4. ANALYSE PAR CATÉGORIE
    print("📂 ANALYSE PAR CATÉGORIE:")
    print("-" * 50)
    
    categories = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0, 'warnings': 0})
    
    for test in rapport['results']:
        cat = test['category']
        categories[cat]['total'] += 1
        if test['status'] == 'PASS':
            categories[cat]['passed'] += 1
        elif test['status'] == 'FAIL':
            categories[cat]['failed'] += 1
        elif test['status'] == 'WARN':
            categories[cat]['warnings'] += 1
    
    for cat, stats in sorted(categories.items()):
        total_cat = stats['total']
        success_rate = (stats['passed'] + stats['warnings']) / total_cat * 100
        print(f"   📁 {cat.upper()}")
        print(f"      Total: {total_cat} | ✅ {stats['passed']} | ❌ {stats['failed']} | ⚠️  {stats['warnings']}")
        print(f"      Taux de fonctionnalité: {success_rate:.1f}%")
        print()
    
    # 5. ANALYSE DES PERFORMANCES
    print("⚡ ANALYSE DES PERFORMANCES:")
    print("-" * 50)
    
    response_times = [r['response_time'] for r in rapport['results']]
    avg_time = sum(response_times) / len(response_times)
    max_time = max(response_times)
    min_time = min(response_times)
    
    slow_tests = [r for r in rapport['results'] if r['response_time'] > avg_time * 2]
    
    print(f"   ⏱️  Temps de réponse moyen: {avg_time:.3f}s")
    print(f"   🐌 Plus lent: {max_time:.3f}s")
    print(f"   🚀 Plus rapide: {min_time:.3f}s")
    
    if slow_tests:
        print(f"   🐢 Tests lents (>{avg_time*2:.3f}s): {len(slow_tests)}")
        for test in slow_tests:
            print(f"      • {test['name']}: {test['response_time']:.3f}s")
    print()
    
    # 6. RECOMMANDATIONS PRIORITAIRES
    print("💡 RECOMMANDATIONS PRIORITAIRES:")
    print("-" * 50)
    
    # Échecs critiques (priorité haute)
    critical_failures = [t for t in failed_tests if t['test_priority'] == 'high']
    if critical_failures:
        print(f"   🚨 URGENT - Corriger les {len(critical_failures)} échecs critiques:")
        for test in critical_failures:
            print(f"      • {test['name']} (Code: {test['response_code']})")
    
    # Erreurs 500 (problèmes serveur)
    server_errors = [t for t in failed_tests if t['response_code'] == 500]
    if server_errors:
        print(f"   🔧 SERVEUR - Corriger les {len(server_errors)} erreurs serveur (500):")
        for test in server_errors:
            print(f"      • {test['name']} - {test['path']}")
    
    # Problèmes d'authentification
    auth_issues = [t for t in failed_tests if t['auth_required']]
    if auth_issues:
        print(f"   🔐 AUTH - Vérifier les {len(auth_issues)} problèmes d'authentification")
    
    # Champs manquants
    missing_fields = [t for t in warning_tests if 'Champs manquants' in t['error']]
    if missing_fields:
        print(f"   📝 SCHEMA - Standardiser les {len(missing_fields)} réponses avec champs manquants")
    
    print()
    print("🎯 PRIORITÉ D'ACTION:")
    print("   1. Corriger les erreurs 500 (problèmes serveur)")
    print("   2. Résoudre les échecs d'authentification")
    print("   3. Standardiser les schémas de réponse")
    print("   4. Optimiser les performances des tests lents")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_api_report.py <rapport.json>")
        sys.exit(1)
    
    analyze_api_report(sys.argv[1])
