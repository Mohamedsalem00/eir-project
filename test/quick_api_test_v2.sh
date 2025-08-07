#!/bin/bash

# 🚀 Test Rapide API EIR v2.0 avec Configuration Centralisée
# Test rapide des endpoints critiques utilisant la nouvelle configuration

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_URL="${1:-http://localhost:8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 Test Rapide API EIR v2.0${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "🌐 URL: ${YELLOW}$API_URL${NC}"
echo -e "📅 $(date)"
echo ""

# Vérifier que Python est disponible
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 requis mais non trouvé${NC}"
    exit 1
fi

# Vérifier que le fichier de configuration existe
if [[ ! -f "$SCRIPT_DIR/api_endpoints_config.py" ]]; then
    echo -e "${RED}❌ Fichier de configuration api_endpoints_config.py non trouvé${NC}"
    exit 1
fi

# Vérifier que le script de test v2 existe
if [[ ! -f "$SCRIPT_DIR/test_api_v2.py" ]]; then
    echo -e "${RED}❌ Script test_api_v2.py non trouvé${NC}"
    exit 1
fi

echo -e "${BLUE}🧪 Exécution des tests critiques (groupe: smoke)...${NC}"
echo ""

# Exécuter les tests avec le groupe "smoke" pour un test rapide
cd "$SCRIPT_DIR"
if python3 test_api_v2.py --url "$API_URL" --group smoke; then
    echo ""
    echo -e "${GREEN}✅ Tests rapides réussis !${NC}"
    echo -e "${GREEN}🎉 L'API EIR fonctionne correctement${NC}"
    exit 0
else
    exit_code=$?
    echo ""
    if [[ $exit_code -eq 1 ]]; then
        echo -e "${RED}❌ Des tests critiques ont échoué${NC}"
        echo -e "${YELLOW}💡 Utilisez './run_api_tests_v2.sh' pour plus de détails${NC}"
    elif [[ $exit_code -eq 2 ]]; then
        echo -e "${YELLOW}⚠️  Tests avec avertissements${NC}"
        echo -e "${YELLOW}💡 Vérifiez les détails du rapport${NC}"
    else
        echo -e "${RED}❌ Erreur inattendue lors des tests${NC}"
    fi
    exit $exit_code
fi
