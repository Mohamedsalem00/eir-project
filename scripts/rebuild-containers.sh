#!/bin/bash
# scripts/rebuild-containers.sh
# Complete container rebuild script with francized output

set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Load Docker utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../docker-utils.sh"

echo "🔄 Reconstruction complète des conteneurs EIR"
echo "============================================="

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Setup Docker commands
setup_docker_commands

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if Docker is running (handled by setup_docker_commands)
check_docker() {
    log_success "Docker configuré avec les permissions appropriées"
}

# Function to stop containers
stop_containers() {
    log_info "Arrêt des conteneurs existants..."
    if docker compose ps -q | grep -q .; then
        docker compose down -v --remove-orphans
        log_success "Conteneurs arrêtés avec succès"
    else
        log_info "Aucun conteneur en cours d'exécution"
    fi
}

# Function to clean up Docker resources
cleanup_docker() {
    log_info "Nettoyage des ressources Docker..."
    
    # Remove old images
    if docker images -q eir-project* | grep -q .; then
        docker compose down --rmi all 2>/dev/null || true
        log_success "Images supprimées"
    fi
    
    # Clean volumes
    docker volume prune -f
    log_success "Volumes nettoyés"
    
    # Clean system
    docker system prune -f
    log_success "Système Docker nettoyé"
}

# Function to build containers
build_containers() {
    log_info "Construction des nouveaux conteneurs..."
    
    # Check if Dockerfile exists
    if [[ ! -f "backend/Dockerfile" ]]; then
        log_error "Dockerfile non trouvé dans backend/"
        exit 1
    fi
    
    # Build with no cache
    if docker compose build --no-cache; then
        log_success "Conteneurs construits avec succès"
    else
        log_error "Échec de la construction des conteneurs"
        exit 1
    fi
}

# Function to start containers
start_containers() {
    log_info "Démarrage des conteneurs..."
    
    if docker compose up -d; then
        log_success "Conteneurs démarrés"
    else
        log_error "Échec du démarrage des conteneurs"
        exit 1
    fi
}

# Function to wait for database
wait_for_database() {
    log_info "Attente de l'initialisation de la base de données..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
            log_success "Base de données prête !"
            return 0
        fi
        
        log_info "Tentative $attempt/$max_attempts - Base de données non prête"
        sleep 2
        ((attempt++))
    done
    
    log_error "Timeout - Base de données non accessible"
    return 1
}

# Function to initialize database
initialize_database() {
    log_info "Vérification de l'initialisation de la base de données..."
    
    # Check if tables exist
    local table_count
    table_count=$(docker compose exec -T db psql -U postgres -d imei_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' \n' || echo "0")
    
    if [[ "$table_count" -eq "0" ]]; then
        log_warning "Base de données vide, initialisation manuelle..."
        if docker compose exec -T web bash /app/scripts/init-db.sh; then
            log_success "Base de données initialisée"
        else
            log_error "Échec de l'initialisation de la base de données"
            return 1
        fi
    else
        log_success "Base de données déjà initialisée avec $table_count tables"
    fi
}

# Function to test API
test_api() {
    log_info "Test de connectivité API..."
    
    local max_attempts=12
    local attempt=1
    
    sleep 5  # Initial wait
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:8000/verification-etat > /dev/null 2>&1; then
            log_success "API répond correctement !"
            return 0
        fi
        
        log_info "Tentative $attempt/$max_attempts - API non prête"
        sleep 5
        ((attempt++))
    done
    
    log_warning "API ne répond pas encore. Vérifiez les logs :"
    echo "   docker compose logs web"
    return 1
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Statut des conteneurs :"
    docker compose ps
    
    echo ""
    echo "🎉 Reconstruction complète terminée !"
    echo ""
    echo "📍 Points d'accès :"
    echo "   🌐 Documentation API : http://localhost:8000/docs"
    echo "   🔍 Vérification santé : http://localhost:8000/verification-etat"
    echo "   🏠 Accueil API : http://localhost:8000/"
    echo "   🗄️  Base de données : localhost:5432 (postgres/postgres)"
    echo ""
    echo "🔑 Utilisateurs de test (mot de passe: admin123) :"
    echo "   👑 admin@eir-project.com (Administrateur)"
    echo "   👤 user@example.com (Utilisateur Standard)"
    echo "   🏢 insurance@company.com (Assurance)"
    echo "   👮 police@agency.gov (Police)"
    echo "   🏭 manufacturer@techcorp.com (Fabricant)"
    echo ""
    echo "📱 IMEIs de test :"
    echo "   Samsung : 352745080123456"
    echo "   Apple : 354123456789012"
    echo "   TechCorp : 352745080987654"
    echo ""
    echo "🧪 Commandes de test rapide :"
    echo "   curl http://localhost:8000/"
    echo "   curl http://localhost:8000/verification-etat"
    echo "   curl http://localhost:8000/imei/352745080123456"
    echo ""
    echo "🔧 Dépannage :"
    echo "   docker compose logs web    # Logs du service web"
    echo "   docker compose logs db     # Logs de la base de données"
    echo "   docker compose ps          # Statut des services"
    echo "   ./scripts/restart-containers.sh  # Redémarrage simple"
}

# Main execution
main() {
    echo "Début de la reconstruction complète..."
    
    check_docker
    stop_containers
    cleanup_docker
    build_containers
    start_containers
    
    if wait_for_database; then
        initialize_database
        test_api
    fi
    
    show_status
}

# Handle interruption
trap 'log_error "Processus interrompu"; exit 130' INT

# Run main function
main
