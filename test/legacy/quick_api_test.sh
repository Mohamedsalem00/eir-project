#!/bin/bash
# Test rapide des endpoints critiques de l'API EIR

API_URL="${1:-http://localhost:8000}"

echo "🚀 Test rapide des endpoints API EIR"
echo "===================================="
echo "API URL: $API_URL"
echo ""

# Fonction pour tester un endpoint
test_endpoint() {
    local method="$1"
    local endpoint="$2"
    local description="$3"
    local expected_code="${4:-200}"
    local data="$5"
    
    echo -n "📍 $description... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json "$API_URL$endpoint")
    elif [ "$method" = "POST" ] && [ -n "$data" ]; then
        response=$(curl -s -w "%{http_code}" -o /tmp/response.json \
                   -X POST \
                   -H "Content-Type: application/json" \
                   -d "$data" \
                   "$API_URL$endpoint")
    fi
    
    if [ "$response" = "$expected_code" ]; then
        echo "✅ ($response)"
    else
        echo "❌ ($response)"
    fi
}

echo "🔧 Endpoints Système:"
test_endpoint "GET" "/" "Page d'accueil"
test_endpoint "GET" "/verification-etat" "Vérification d'état"
test_endpoint "GET" "/languages" "Langues supportées"

echo ""
echo "📱 Endpoints IMEI:"
test_endpoint "GET" "/imei/352745080123456" "Recherche IMEI"
test_endpoint "GET" "/imei/352745080123456/historique" "Historique IMEI"

echo ""
echo "🔐 Endpoints Authentification:"
test_endpoint "POST" "/authentification/connexion" "Connexion admin" "200" '{"email":"admin@eir-project.com","mot_de_passe":"admin123"}'

echo ""
echo "📊 Endpoints Analyses:"
test_endpoint "GET" "/public/statistiques" "Statistiques publiques"
test_endpoint "GET" "/analyses/appareils" "Analyses appareils" "401"

echo ""
echo "✅ Test rapide terminé!"
echo ""
echo "💡 Pour des tests complets, utilisez:"
echo "   ./run_api_tests.sh"
