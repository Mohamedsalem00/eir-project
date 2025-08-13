#!/bin/bash

# 🚀 Script de démarrage rapide EIR Frontend avec Docker
# Usage: ./quick-start-docker.sh [dev|prod|stop|logs|clean]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}"
    echo "🌐====================================🌐"
    echo "    EIR Frontend Docker Manager"
    echo "======================================"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    print_success "Docker et Docker Compose sont disponibles"
}

start_development() {
    print_header
    echo "🛠️  Démarrage de l'environnement de développement..."
    
    # Vérifier si le fichier .env.local existe
    if [ ! -f "./frontend/.env.local" ]; then
        print_warning "Création du fichier .env.local à partir de l'exemple"
        cp ./frontend/.env.example ./frontend/.env.local
    fi
    
    # Démarrer les services
    docker-compose up -d
    
    # Attendre que les services soient prêts
    echo "⏳ Attente du démarrage des services..."
    sleep 10
    
    # Vérifier le statut
    if docker-compose ps | grep -q "Up"; then
        print_success "Services démarrés avec succès !"
        echo ""
        echo "🌐 URLs disponibles:"
        echo "   Frontend:  http://localhost:3000"
        echo "   Backend:   http://localhost:8000"
        echo "   API Docs:  http://localhost:8000/docs"
        echo "   Database:  localhost:5432"
        echo ""
        echo "📋 Commandes utiles:"
        echo "   Logs frontend: docker-compose logs -f frontend"
        echo "   Logs backend:  docker-compose logs -f web"
        echo "   Arrêter:       docker-compose down"
    else
        print_error "Erreur lors du démarrage des services"
        docker-compose logs
        exit 1
    fi
}

start_production() {
    print_header
    echo "🚀 Démarrage de l'environnement de production..."
    
    # Construction des images
    print_warning "Construction des images de production..."
    docker-compose -f docker-compose.prod.yml build
    
    # Démarrage
    docker-compose -f docker-compose.prod.yml up -d
    
    # Vérification
    sleep 15
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        print_success "Environnement de production démarré !"
        echo ""
        echo "🌐 URLs de production:"
        echo "   Frontend:  http://localhost:3000"
        echo "   Backend:   http://localhost:8000"
    else
        print_error "Erreur lors du démarrage de la production"
        exit 1
    fi
}

stop_services() {
    print_header
    echo "🛑 Arrêt des services..."
    
    docker-compose down
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    
    print_success "Services arrêtés"
}

show_logs() {
    print_header
    echo "📋 Logs des services..."
    echo ""
    echo "Logs du frontend (Ctrl+C pour quitter):"
    docker-compose logs -f frontend
}

clean_environment() {
    print_header
    print_warning "🧹 Nettoyage de l'environnement Docker..."
    
    # Arrêter tous les services
    docker-compose down -v 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
    
    # Supprimer les images EIR
    docker images | grep eir | awk '{print $3}' | xargs docker rmi -f 2>/dev/null || true
    
    # Nettoyer les ressources inutilisées
    docker system prune -f
    
    print_success "Nettoyage terminé"
}

install_dependencies() {
    print_header
    echo "📦 Installation des dépendances frontend..."
    
    if [ ! -f "./frontend/package.json" ]; then
        print_error "Le fichier package.json n'existe pas dans ./frontend/"
        exit 1
    fi
    
    # Créer le conteneur temporaire pour installer les dépendances
    docker run --rm -v $(pwd)/frontend:/app -w /app node:18-alpine npm install
    
    print_success "Dépendances installées"
}

show_status() {
    print_header
    echo "📊 Statut des services Docker EIR:"
    echo ""
    
    if docker-compose ps 2>/dev/null | grep -q "Up"; then
        echo "🟢 Services de développement:"
        docker-compose ps
    else
        echo "🔴 Aucun service de développement en cours"
    fi
    
    echo ""
    
    if docker-compose -f docker-compose.prod.yml ps 2>/dev/null | grep -q "Up"; then
        echo "🟢 Services de production:"
        docker-compose -f docker-compose.prod.yml ps
    else
        echo "🔴 Aucun service de production en cours"
    fi
    
    echo ""
    echo "💾 Utilisation de l'espace Docker:"
    docker system df
}

# Menu principal
case "$1" in
    "dev"|"development"|"")
        check_docker
        start_development
        ;;
    "prod"|"production")
        check_docker
        start_production
        ;;
    "stop")
        stop_services
        ;;
    "logs")
        show_logs
        ;;
    "clean")
        clean_environment
        ;;
    "install")
        install_dependencies
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        print_header
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  dev, development    Démarrer l'environnement de développement (défaut)"
        echo "  prod, production    Démarrer l'environnement de production"
        echo "  stop                Arrêter tous les services"
        echo "  logs                Afficher les logs du frontend"
        echo "  clean               Nettoyer l'environnement Docker"
        echo "  install             Installer les dépendances npm"
        echo "  status              Afficher le statut des services"
        echo "  help                Afficher cette aide"
        echo ""
        echo "Exemples:"
        echo "  $0                  # Démarrer en développement"
        echo "  $0 dev              # Démarrer en développement"
        echo "  $0 prod             # Démarrer en production"
        echo "  $0 logs             # Voir les logs"
        echo "  $0 clean            # Nettoyer tout"
        ;;
    *)
        print_error "Commande inconnue: $1"
        echo "Utilisez '$0 help' pour voir les commandes disponibles"
        exit 1
        ;;
esac
