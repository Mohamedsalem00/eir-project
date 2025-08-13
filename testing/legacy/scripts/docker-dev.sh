#!/bin/bash

# Script pour démarrage rapide de l'environnement de développement

echo "⚡ Démarrage rapide de l'environnement EIR Project..."

# Vérifier si les conteneurs existent déjà
if docker compose ps -q | grep -q .; then
    echo "📋 Conteneurs existants détectés"
    
    # Redémarrer seulement les services arrêtés
    echo "🔄 Redémarrage des services..."
    docker compose up -d
else
    echo "🏗️  Première construction nécessaire..."
    docker compose build
    docker compose up -d
fi

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 5

# Vérifier l'état des services
echo "📊 État des services:"
docker compose ps

echo ""
echo "✅ Services démarrés!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo ""
echo "Pour voir les logs:"
echo "  docker compose logs -f"
