#!/bin/bash
# Script pour tester tous les endpoints de l'API EIR

set -e

# Couleurs pour la sortie
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Script de Test API EIR${NC}"
echo -e "${BLUE}=========================${NC}"

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    exit 1
fi

# Vérifier si les dépendances sont installées
python3 -c "import requests" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  Installation de la dépendance requests...${NC}"
    pip3 install requests
}

# URL de base de l'API
API_URL="${1:-http://localhost:8000}"

echo -e "${BLUE}🔍 Test de l'API sur: ${API_URL}${NC}"

# Vérifier si l'API est accessible
echo -e "${YELLOW}⏳ Vérification de la connectivité API...${NC}"
if curl -s -f "${API_URL}/verification-etat" > /dev/null; then
    echo -e "${GREEN}✅ API accessible${NC}"
else
    echo -e "${RED}❌ API non accessible sur ${API_URL}${NC}"
    echo -e "${YELLOW}💡 Assurez-vous que les conteneurs Docker sont en cours d'exécution:${NC}"
    echo -e "   sudo docker-compose ps"
    echo -e "   sudo docker-compose up -d"
    exit 1
fi

# Exécuter le script de test Python
echo -e "${BLUE}🧪 Exécution des tests...${NC}"
echo ""

cd "$(dirname "$0")"
python3 test_api_endpoints.py "${API_URL}"

echo ""
echo -e "${GREEN}✅ Tests terminés!${NC}"

# Afficher les fichiers de rapport générés
echo -e "${BLUE}📄 Fichiers de rapport générés:${NC}"
ls -la api_test_report_*.json 2>/dev/null || echo "Aucun fichier de rapport trouvé"
