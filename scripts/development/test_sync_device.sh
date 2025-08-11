#!/bin/bash

echo "🧪 Test de l'endpoint /sync-device"
echo "=================================="

# Test 1: Synchronisation basique
echo ""
echo "📱 Test 1: Création d'un nouvel appareil"
response1=$(curl -s -X POST "http://localhost:8000/sync-device" \
     -H "Content-Type: application/json" \
     -d '{
       "appareils": [
         {
           "imei": "111222333444555",
           "marque": "Xiaomi",
           "modele": "Mi 11",
           "statut": "active",
           "emmc": "128GB"
         }
       ],
       "sync_mode": "upsert",
       "source_system": "DMS_Test"
     }')

echo "Réponse: $response1"
echo ""

# Test 2: Mise à jour existant
echo "📱 Test 2: Mise à jour du même appareil"
response2=$(curl -s -X POST "http://localhost:8000/sync-device" \
     -H "Content-Type: application/json" \
     -d '{
       "appareils": [
         {
           "imei": "111222333444555",
           "marque": "Xiaomi",
           "modele": "Mi 11 Pro",
           "statut": "active",
           "emmc": "256GB"
         }
       ],
       "sync_mode": "upsert",
       "source_system": "DMS_Test"
     }')

echo "Réponse: $response2"
echo ""

# Test 3: Plusieurs appareils
echo "📱 Test 3: Synchronisation de plusieurs appareils"
response3=$(curl -s -X POST "http://localhost:8000/sync-device" \
     -H "Content-Type: application/json" \
     -d '{
       "appareils": [
         {
           "imei": "666777888999000",
           "marque": "OnePlus",
           "modele": "Nord 3",
           "statut": "active"
         },
         {
           "imei": "555444333222111",
           "marque": "Google",
           "modele": "Pixel 7",
           "statut": "active"
         }
       ],
       "sync_mode": "upsert",
       "source_system": "DMS_Bulk"
     }')

echo "Réponse: $response3"
echo ""

# Test 4: Erreur validation
echo "❌ Test 4: Test d'erreur (IMEI invalide)"
response4=$(curl -s -X POST "http://localhost:8000/sync-device" \
     -H "Content-Type: application/json" \
     -d '{
       "appareils": [
         {
           "imei": "123",
           "marque": "InvalidBrand",
           "modele": "Test"
         }
       ],
       "sync_mode": "upsert",
       "source_system": "DMS_Error_Test"
     }')

echo "Réponse: $response4"
echo ""

echo "✅ Tests terminés!"
