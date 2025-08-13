#!/bin/bash

# Script pour construire et démarrer l'environnement Docker complet

echo "🚀 Construction et démarrage de l'environnement EIR Project..."

# Arrêter les conteneurs existants
echo "🛑 Arrêt des conteneurs existants..."
docker compose down --remove-orphans

# Nettoyer les images orphelines
echo "🧹 Nettoyage des images orphelines..."
docker system prune -f

# Construire les images
echo "🔧 Construction des images Docker..."
docker compose build --no-cache

# Démarrer les services
echo "🌟 Démarrage des services..."
docker compose up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 10

# Vérifier l'état des services
echo "📊 État des services:"
docker compose ps

# Afficher les logs du frontend
echo "📜 Logs du frontend (les 20 dernières lignes):"
docker compose logs --tail=20 frontend

echo ""
echo "✅ Environnement prêt!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "🗄️  Base de données: localhost:5432"
echo ""
echo "Pour voir les logs en temps réel:"
echo "  docker compose logs -f frontend"
echo "  docker compose logs -f web"
echo "  docker compose logs -f db"
echo ""
echo "Pour arrêter les services:"
echo "  docker compose down"
