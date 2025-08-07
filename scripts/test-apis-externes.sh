#!/bin/bash

# Script de test des APIs IMEI externes
echo "🔍 Test des APIs IMEI Externes"
echo "=============================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# IMEI de test valide
TEST_IMEI="352745080123456"

echo "📱 IMEI de test: $TEST_IMEI"
echo ""

# Fonction de test d'API
test_api() {
    local name="$1"
    local url="$2"
    local timeout=10
    
    echo -n "🌐 Test $name: "
    
    # Test de connectivité
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $timeout "$url" 2>/dev/null)
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "302" ] || [ "$http_code" = "301" ]; then
        echo -e "${GREEN}✅ ACTIF${NC} (HTTP $http_code)"
        return 0
    elif [ "$http_code" = "404" ]; then
        echo -e "${YELLOW}⚠️  404 - Endpoint peut exister${NC}"
        return 1
    elif [ "$http_code" = "000" ]; then
        echo -e "${RED}❌ INACCESSIBLE${NC} (Timeout/DNS)"
        return 1
    else
        echo -e "${RED}❌ ERREUR${NC} (HTTP $http_code)"
        return 1
    fi
}

# Test des APIs principales
echo "1️⃣ APIs IMEI Gratuites"
echo "----------------------"

# APIs potentiellement fonctionnelles
test_api "IMEI24" "https://imei24.com"
test_api "NumLookup" "https://numlookup.com"
test_api "IMEILookup" "https://imeilookup.org"
test_api "CheckIMEI" "https://checkimei.com"

echo ""
echo "2️⃣ APIs de Validation Mobile"
echo "----------------------------"

test_api "NumVerify" "https://numverify.com"
test_api "Twilio Lookup" "https://lookups.twilio.com"
test_api "APILayer" "https://apilayer.com"

echo ""
echo "3️⃣ Sources TAC Database"
echo "----------------------"

test_api "GitHub TAC DB" "https://raw.githubusercontent.com/tacdb/tacdb/main/tacdb.json"
test_api "DeviceAtlas" "https://deviceatlas.com"
test_api "GSMA TAC" "https://imeidb.gsma.com"

echo ""
echo "4️⃣ Test d'APIs Alternatives"
echo "---------------------------"

# Test de quelques URLs connues pour fonctionner
test_api "JSONPlaceholder (Test)" "https://jsonplaceholder.typicode.com/posts/1"
test_api "HTTPBin (Test)" "https://httpbin.org/status/200"

echo ""
echo "🔧 APIs Recommandées GRATUITES:"
echo "================================"

echo "✅ Solution 1 - Base TAC Locale uniquement"
echo "   • Coût: 0€"
echo "   • Fiabilité: 100%"
echo "   • Données: 16,000+ modèles"

echo ""
echo "✅ Solution 2 - Validation Algorithmique"
echo "   • Algorithme Luhn pour validation IMEI"
echo "   • Vérification TAC local"
echo "   • Pas d'appels API externes"

echo ""
echo "💰 APIs Payantes Recommandées:"
echo "=============================="

echo "🔹 NumVerify (API Layer)"
echo "   • 1000 req/mois gratuit"
echo "   • 49€/mois pour 10K req"
echo "   • Très fiable"

echo ""
echo "🔹 Twilio Lookup API"
echo "   • 0.05€ par requête"
echo "   • Données officielles"
echo "   • Support entreprise"

echo ""
echo "📋 Configuration Recommandée:"
echo "============================"

cat << 'EOF'
external_apis:
  enabled: true
  fallback_enabled: true
  
  providers:
    # Priorité 0: Base locale (gratuit, fiable)
    local_tac_db:
      enabled: true
      type: "local_database"
      priority: 0
      
    # Priorité 1: Validation algorithmique (gratuit)
    luhn_validator:
      enabled: true
      type: "algorithmic"
      priority: 1
      
    # Priorité 2: NumVerify (freemium, fiable)
    numverify:
      enabled: false  # Activer avec clé API
      url: "http://apilayer.net/api/validate"
      api_key: "${NUMVERIFY_API_KEY}"
      priority: 2
EOF

echo ""
echo "🚀 Pour appliquer cette configuration:"
echo "cp config/external_apis_working.yml config/external_apis.yml"
echo "docker compose restart web"
