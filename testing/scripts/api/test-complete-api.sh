#!/bin/bash

# Script de test complet pour l'API EIR avec nouvelles fonctionnalités
echo "🔍 Test Complet de l'API EIR"
echo "============================"

BASE_URL="http://localhost:8000"

# Test 1: Vérification de santé
echo ""
echo "1️⃣ Test de santé de l'API"
echo "----------------------------"
curl -s "$BASE_URL/verification-etat" | jq '.'

# Test 2: Informations de l'API
echo ""
echo "2️⃣ Informations de l'API"
echo "-------------------------"
curl -s "$BASE_URL/" | jq '.api'

# Test 3: Recherche IMEI simple
echo ""
echo "3️⃣ Recherche IMEI Simple"
echo "-------------------------"
curl -s "$BASE_URL/imei/123456789012345" | jq '.'

# Test 4: Recherche IMEI avec un IMEI de test valide
echo ""
echo "4️⃣ Recherche IMEI avec IMEI de test"
echo "------------------------------------"
curl -s "$BASE_URL/imei/350123456789012" | jq '.'

# Test 5: Test avec un IMEI Samsung connu
echo ""
echo "5️⃣ Test avec IMEI Samsung (TAC: 35294406)"
echo "------------------------------------------"
curl -s "$BASE_URL/imei/352944060000001" | jq '.'

# Test 6: Vérification des statistiques publiques
echo ""
echo "6️⃣ Statistiques publiques"
echo "--------------------------"
curl -s "$BASE_URL/public/statistiques" | jq '.'

# Test 7: Test des langues supportées
echo ""
echo "7️⃣ Langues supportées"
echo "----------------------"
curl -s "$BASE_URL/languages" | jq '.'

# Test 8: Documentation interactive
echo ""
echo "8️⃣ Documentation (vérification d'accès)"
echo "----------------------------------------"
curl -s -I "$BASE_URL/docs" | head -1

echo ""
echo "✅ Tests terminés!"
echo ""
echo "💡 Pour tester les APIs externes:"
echo "   - Modifiez les clés API dans config/external_apis.yml"
echo "   - Testez avec: docker exec -it eir_web python -m pytest tests/"
echo ""
echo "🌐 Pour la documentation complète:"
echo "   - Ouvrez: http://localhost:8000/docs"
echo ""
