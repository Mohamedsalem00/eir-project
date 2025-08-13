#!/bin/bash

# 🧪 Script de Test de l'Interface EIR
# Test de l'intégration frontend-backend

echo "🔍 === TEST D'INTÉGRATION EIR ==="
echo ""

# Configuration
FRONTEND_URL="http://localhost:3001"
BACKEND_URL="http://localhost:8000"

# Couleurs pour la sortie
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de test avec couleurs
test_endpoint() {
    local url=$1
    local description=$2
    
    echo -n "🚀 Test: $description... "
    
    if curl -s -f "$url" > /dev/null; then
        echo -e "${GREEN}✅ SUCCÈS${NC}"
        return 0
    else
        echo -e "${RED}❌ ÉCHEC${NC}"
        return 1
    fi
}

# Tests de base
echo -e "${BLUE}📡 Tests de Connectivité${NC}"
echo "================================="

test_endpoint "$FRONTEND_URL" "Frontend Next.js"
test_endpoint "$BACKEND_URL/health" "Backend API Health"
test_endpoint "$BACKEND_URL" "Backend API Root"

echo ""
echo -e "${BLUE}🔍 Tests d'Endpoints IMEI${NC}"
echo "================================="

# Test avec IMEI valide
echo -n "🔍 Test IMEI valide (123456789012345)... "
response=$(curl -s -w "%{http_code}" "$BACKEND_URL/imei/123456789012345" -o /dev/null)
if [ "$response" == "200" ]; then
    echo -e "${GREEN}✅ SUCCÈS (200)${NC}"
elif [ "$response" == "404" ]; then
    echo -e "${YELLOW}⚠️  IMEI NON TROUVÉ (404) - Normal${NC}"
else
    echo -e "${RED}❌ ERREUR ($response)${NC}"
fi

# Test avec IMEI invalide
echo -n "🚫 Test IMEI invalide (12345)... "
response=$(curl -s -w "%{http_code}" "$BACKEND_URL/imei/12345" -o /dev/null)
if [ "$response" == "422" ]; then
    echo -e "${GREEN}✅ VALIDATION OK (422)${NC}"
else
    echo -e "${RED}❌ ERREUR ($response)${NC}"
fi

echo ""
echo -e "${BLUE}📊 Tests de Rate Limiting${NC}"
echo "================================="

# Test de rate limiting (faire plusieurs requêtes rapidement)
echo "🏃 Test de 5 requêtes rapides..."
for i in {1..5}; do
    echo -n "  Requête $i: "
    response=$(curl -s -w "%{http_code}" "$BACKEND_URL/imei/123456789012345" -o /dev/null)
    
    if [ "$response" == "200" ] || [ "$response" == "404" ]; then
        echo -e "${GREEN}✅ OK ($response)${NC}"
    elif [ "$response" == "429" ]; then
        echo -e "${YELLOW}⚠️  RATE LIMITED (429)${NC}"
    else
        echo -e "${RED}❌ ERREUR ($response)${NC}"
    fi
    
    sleep 0.5
done

echo ""
echo -e "${BLUE}🌐 Tests Frontend${NC}"
echo "================================="

# Test des pages frontend
test_endpoint "$FRONTEND_URL" "Page d'accueil"
test_endpoint "$FRONTEND_URL/test" "Page de test API"

echo ""
echo -e "${BLUE}📈 Informations Système${NC}"
echo "================================="

echo "🖥️  Frontend: $FRONTEND_URL"
echo "🔧 Backend:  $BACKEND_URL"
echo "📅 Date:     $(date)"

# Vérifier les ports occupés
echo ""
echo "🔌 Ports utilisés:"
if command -v lsof &> /dev/null; then
    echo "  Port 3001 (Frontend): $(lsof -ti:3001 | wc -l) processus"
    echo "  Port 8000 (Backend):  $(lsof -ti:8000 | wc -l) processus"
else
    echo "  (lsof non disponible pour vérifier les ports)"
fi

echo ""
echo -e "${GREEN}🎉 Tests terminés !${NC}"
echo ""
echo "💡 Pour utiliser l'interface:"
echo "   Frontend: $FRONTEND_URL"
echo "   Test API: $FRONTEND_URL/test"
echo "   Backend:  $BACKEND_URL/docs"
echo ""
echo "🔧 Pour redémarrer les services:"
echo "   Frontend: cd frontend && npm run dev"
echo "   Backend:  cd backend && uvicorn app.main:app --reload"
