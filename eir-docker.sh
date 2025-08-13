#!/bin/bash

# Script d'utilitaires EIR Docker

show_help() {
    echo "🛠️  Utilitaires Docker pour le projet EIR"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commandes disponibles:"
    echo "  start      - Démarrer tous les services"
    echo "  stop       - Arrêter tous les services"
    echo "  restart    - Redémarrer tous les services"
    echo "  rebuild    - Reconstruire et redémarrer tous les services"
    echo "  logs       - Afficher les logs de tous les services"
    echo "  status     - Afficher l'état des services"
    echo "  clean      - Nettoyer les conteneurs et images"
    echo "  shell-web  - Ouvrir un shell dans le conteneur backend"
    echo "  shell-frontend - Ouvrir un shell dans le conteneur frontend"
    echo "  test       - Tester la connectivité des services"
    echo ""
}

case "$1" in
    start)
        echo "🚀 Démarrage des services..."
        docker compose up -d
        echo "✅ Services démarrés!"
        echo "🌐 Frontend: http://localhost:3000"
        echo "🔗 Backend API: http://localhost:8000"
        ;;
    
    stop)
        echo "🛑 Arrêt des services..."
        docker compose down
        echo "✅ Services arrêtés!"
        ;;
    
    restart)
        echo "🔄 Redémarrage des services..."
        docker compose down
        docker compose up -d
        echo "✅ Services redémarrés!"
        ;;
    
    rebuild)
        echo "🏗️  Reconstruction des services..."
        docker compose down
        docker compose build --no-cache
        docker compose up -d
        echo "✅ Services reconstruits et démarrés!"
        ;;
    
    logs)
        if [ -n "$2" ]; then
            docker compose logs -f "$2"
        else
            docker compose logs -f
        fi
        ;;
    
    status)
        echo "📊 État des services:"
        docker compose ps
        echo ""
        echo "🔗 URLs disponibles:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend API: http://localhost:8000"
        echo "  Base de données: localhost:5432"
        ;;
    
    clean)
        echo "🧹 Nettoyage..."
        docker compose down --remove-orphans
        docker system prune -f
        echo "✅ Nettoyage terminé!"
        ;;
    
    shell-web)
        echo "🐚 Ouverture du shell backend..."
        docker compose exec web bash
        ;;
    
    shell-frontend)
        echo "🐚 Ouverture du shell frontend..."
        docker compose exec frontend sh
        ;;
    
    test)
        echo "🧪 Test de connectivité..."
        echo "Backend API:"
        curl -s http://localhost:8000/health || echo "❌ Backend non accessible"
        echo ""
        echo "Frontend:"
        curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend accessible" || echo "❌ Frontend non accessible"
        echo ""
        echo "Base de données:"
        docker compose exec db pg_isready -U postgres && echo "✅ Base de données accessible" || echo "❌ Base de données non accessible"
        ;;
    
    *)
        show_help
        ;;
esac
