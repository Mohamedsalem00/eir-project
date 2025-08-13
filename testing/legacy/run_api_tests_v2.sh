#!/bin/bash

# 🧪 Test Complet API EIR v2.0 avec Configuration Centralisée
# Exécuteur de tests utilisant la configuration centralisée des endpoints

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration par défaut
API_URL="${1:-http://localhost:8000}"
TEST_GROUP="${2:-core}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_usage() {
    echo -e "${BLUE}📋 Utilisation: $0 [URL_API] [GROUPE_TEST]${NC}"
    echo ""
    echo -e "${YELLOW}Paramètres:${NC}"
    echo "  URL_API      URL de base de l'API (défaut: http://localhost:8000)"
    echo "  GROUPE_TEST  Groupe de tests à exécuter (défaut: core)"
    echo ""
    echo -e "${YELLOW}Groupes disponibles:${NC}"
    echo "  🚀 smoke    - Tests critiques rapides (4 endpoints)"
    echo "  🎯 core     - Tests essentiels (9 endpoints)"
    echo "  🔐 authenticated - Tous les endpoints nécessitant auth"
    echo "  🌐 public   - Tous les endpoints publics"
    echo "  👑 admin    - Endpoints administratifs"
    echo "  🌍 all      - Tous les endpoints"
    echo ""
    echo -e "${YELLOW}Exemples:${NC}"
    echo "  $0                                    # Tests core sur localhost"
    echo "  $0 http://localhost:8000 smoke        # Tests smoke"
    echo "  $0 https://api.example.com all        # Tous les tests sur serveur distant"
}

print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║              🧪 TESTS API EIR v2.0 - CENTRALISÉ             ║"
    echo "║         Tests automatisés avec configuration unifiée        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Afficher l'aide si demandée
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_usage
    exit 0
fi

print_header

echo -e "${BLUE}🌐 URL de l'API: ${YELLOW}$API_URL${NC}"
echo -e "${BLUE}🎯 Groupe de test: ${YELLOW}$TEST_GROUP${NC}"
echo -e "${BLUE}📅 Date: ${YELLOW}$(date)${NC}"
echo ""

# Vérifications préliminaires
echo -e "${BLUE}🔍 Vérifications préliminaires...${NC}"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 requis mais non trouvé${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python 3 disponible${NC}"

# Vérifier les dépendances
if ! python3 -c "import requests" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Module 'requests' manquant, tentative d'installation...${NC}"
    if pip3 install requests; then
        echo -e "${GREEN}✅ Module 'requests' installé${NC}"
    else
        echo -e "${RED}❌ Impossible d'installer 'requests'${NC}"
        echo -e "${YELLOW}💡 Installez manuellement: pip3 install requests${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Module 'requests' disponible${NC}"
fi

# Vérifier les fichiers requis
REQUIRED_FILES=(
    "$SCRIPT_DIR/test/api_endpoints_config_v2.py"
    "$SCRIPT_DIR/test_api_v2.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}❌ Fichier requis manquant: $(basename "$file")${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ Tous les fichiers requis présents${NC}"

# Test de connectivité API
echo -e "${BLUE}🌐 Test de connectivité...${NC}"
if curl -s --max-time 10 "$API_URL/" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API accessible${NC}"
else
    echo -e "${RED}❌ API non accessible${NC}"
    echo -e "${YELLOW}💡 Vérifiez que l'API est démarrée et l'URL correcte${NC}"
    exit 1
fi

echo ""

# Afficher les informations du groupe de test
echo -e "${BLUE}📊 Informations sur le groupe de test...${NC}"
cd "$SCRIPT_DIR"

# Utiliser Python pour obtenir les infos du groupe
python3 -c "
from api_endpoints_config import TEST_GROUPS, get_test_group, get_all_endpoints
import sys

group = '$TEST_GROUP'
if group in TEST_GROUPS:
    endpoints = get_test_group(group)
    if isinstance(endpoints, list):
        print(f'📋 Nombre d\'endpoints à tester: {len(endpoints)}')
        
        # Compter par priorité
        from api_endpoints_config import ENDPOINTS
        priorities = {'high': 0, 'medium': 0, 'low': 0}
        auth_required = 0
        
        for endpoint_ref in endpoints:
            if '.' in endpoint_ref:
                cat, key = endpoint_ref.split('.', 1)
                if cat in ENDPOINTS and key in ENDPOINTS[cat]:
                    ep = ENDPOINTS[cat][key]
                    priority = ep.get('test_priority', 'medium')
                    if priority in priorities:
                        priorities[priority] += 1
                    if ep.get('auth_required', False):
                        auth_required += 1
        
        print(f'🔴 Haute priorité: {priorities[\"high\"]}')
        print(f'🟡 Priorité moyenne: {priorities[\"medium\"]}')
        print(f'🟢 Basse priorité: {priorities[\"low\"]}')
        print(f'🔐 Nécessitent auth: {auth_required}')
    else:
        # Groupe 'all'
        total = sum(len(cat) for cat in get_all_endpoints().values())
        print(f'📋 Tous les endpoints: {total}')
else:
    print(f'❌ Groupe inconnu: {group}')
    sys.exit(1)
"

if [[ $? -ne 0 ]]; then
    echo -e "${RED}❌ Groupe de test invalide: $TEST_GROUP${NC}"
    echo ""
    show_usage
    exit 1
fi

echo ""

# Exécuter les tests
echo -e "${BOLD}🧪 EXÉCUTION DES TESTS${NC}"
echo "=" * 60

# Démarrer le chronomètre
START_TIME=$(date +%s)

# Exécuter le script de test principal
if python3 test_api_v2.py --url "$API_URL" --group "$TEST_GROUP"; then
    TEST_EXIT_CODE=0
    TEST_STATUS="SUCCESS"
else
    TEST_EXIT_CODE=$?
    if [[ $TEST_EXIT_CODE -eq 1 ]]; then
        TEST_STATUS="FAILED"
    elif [[ $TEST_EXIT_CODE -eq 2 ]]; then
        TEST_STATUS="WARNING"
    else
        TEST_STATUS="ERROR"
    fi
fi

# Calculer la durée
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=" * 60
echo -e "${BOLD}📊 RÉSULTATS FINAUX${NC}"
echo "=" * 60

echo -e "⏱️  Durée totale: ${BOLD}${DURATION}s${NC}"
echo -e "🎯 Groupe testé: ${BOLD}$TEST_GROUP${NC}"
echo -e "🌐 URL testée: ${BOLD}$API_URL${NC}"

case $TEST_STATUS in
    "SUCCESS")
        echo -e "✅ Statut: ${GREEN}${BOLD}SUCCÈS${NC}"
        echo -e "${GREEN}🎉 Tous les tests sont passés avec succès !${NC}"
        ;;
    "WARNING")
        echo -e "⚠️  Statut: ${YELLOW}${BOLD}AVERTISSEMENTS${NC}"
        echo -e "${YELLOW}💡 Certains tests ont des avertissements${NC}"
        ;;
    "FAILED")
        echo -e "❌ Statut: ${RED}${BOLD}ÉCHEC${NC}"
        echo -e "${RED}🔧 Des tests ont échoué - action requise${NC}"
        ;;
    "ERROR")
        echo -e "💥 Statut: ${RED}${BOLD}ERREUR${NC}"
        echo -e "${RED}🚨 Erreur critique lors de l'exécution${NC}"
        ;;
esac

echo ""

# Suggestions post-test
echo -e "${BLUE}💡 ACTIONS SUGGÉRÉES:${NC}"

if [[ $TEST_STATUS == "SUCCESS" ]]; then
    echo "  🎯 API fonctionnelle - prête pour utilisation"
    echo "  📊 Consultez le rapport détaillé pour les métriques"
elif [[ $TEST_STATUS == "WARNING" ]]; then
    echo "  📋 Examinez les avertissements dans le rapport"
    echo "  🔍 Vérifiez les permissions et l'authentification"
elif [[ $TEST_STATUS == "FAILED" ]]; then
    echo "  🔧 Corrigez les endpoints en échec"
    echo "  📝 Vérifiez les logs serveur: sudo docker logs eir_web"
    echo "  🔄 Redémarrez l'API si nécessaire"
else
    echo "  🚨 Vérifiez la configuration et les dépendances"
    echo "  🔄 Redémarrez complètement le système"
fi

echo ""
echo -e "${BLUE}📄 Fichiers générés:${NC}"
echo "  📊 Rapport JSON: api_test_report_v2_*.json"
echo "  📋 Analysez avec: python3 analyze_test_results.py <rapport>"

echo ""

# Proposer des actions selon le résultat
if [[ $TEST_STATUS == "FAILED" || $TEST_STATUS == "ERROR" ]]; then
    echo -e "${YELLOW}🔧 Besoin d'aide pour déboguer ?${NC}"
    echo "  1. Voir les logs: sudo docker logs eir_web --tail 50"
    echo "  2. Redémarrer l'API: sudo docker-compose restart"
    echo "  3. Test rapide: ./quick_api_test_v2.sh"
    echo "  4. Dashboard interactif: ./test_dashboard.sh"
fi

# Code de sortie
exit $TEST_EXIT_CODE
