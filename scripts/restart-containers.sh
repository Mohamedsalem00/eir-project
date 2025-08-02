#!/bin/bash
# scripts/restart-containers.sh
# Simple container restart script

set -e

echo "🔄 Redémarrage des conteneurs EIR"
echo "================================="

# Navigate to project root
cd "$(dirname "$0")/.."

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker n'est pas en cours d'exécution. Veuillez démarrer Docker."
        exit 1
    fi
    log_success "Docker est opérationnel"
}

# Function to restart containers
restart_containers() {
    log_info "Redémarrage des conteneurs..."
    
    # Stop containers gracefully
    if docker-compose ps -q | grep -q .; then
        log_info "Arrêt des conteneurs existants..."
        docker-compose down
        log_success "Conteneurs arrêtés"
    else
        log_info "Aucun conteneur en cours d'exécution"
    fi
    
    # Start containers
    log_info "Démarrage des conteneurs..."
    if docker-compose up -d; then
        log_success "Conteneurs démarrés"
    else
        log_error "Échec du démarrage des conteneurs"
        exit 1
    fi
}

# Function to wait for services
wait_for_services() {
    log_info "Attente des services..."
    
    # Wait for database
    local db_attempts=20
    local db_attempt=1
    
    while [ $db_attempt -le $db_attempts ]; do
        if docker-compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
            log_success "Base de données prête !"
            break
        fi
        
        log_info "Tentative $db_attempt/$db_attempts - Base de données non prête"
        sleep 2
        ((db_attempt++))
    done
    
    if [ $db_attempt -gt $db_attempts ]; then
        log_warning "Base de données prend plus de temps que prévu"
    fi
    
    # Wait for API
    log_info "Test de l'API..."
    local api_attempts=10
    local api_attempt=1
    
    sleep 3  # Initial wait
    
    while [ $api_attempt -le $api_attempts ]; do
        if curl -s -f http://localhost:8000/verification-etat > /dev/null 2>&1; then
            log_success "API opérationnelle !"
            return 0
        fi
        
        log_info "Tentative $api_attempt/$api_attempts - API non prête"
        sleep 3
        ((api_attempt++))
    done
    
    if [ $api_attempt -gt $api_attempts ]; then
        log_warning "API prend plus de temps que prévu à démarrer"
    fi
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Statut des conteneurs :"
    docker-compose ps
    
    echo ""
    echo "🎉 Redémarrage terminé !"
    echo ""
    echo "📍 Points d'accès :"
    echo "   🌐 Documentation API : http://localhost:8000/docs"
    echo "   🔍 Vérification santé : http://localhost:8000/verification-etat"
    echo "   🏠 Accueil API : http://localhost:8000/"
    echo ""
    echo "🧪 Test rapide :"
    echo "   curl http://localhost:8000/verification-etat"
    echo ""
    echo "🔧 Si problèmes :"
    echo "   docker-compose logs web    # Logs du service web"
    echo "   docker-compose logs db     # Logs de la base de données"
    echo "   ./scripts/rebuild-containers.sh  # Reconstruction complète"
}

# Function to handle service-specific restart
restart_service() {
    local service=$1
    
    if [[ -z "$service" ]]; then
        restart_containers
    else
        log_info "Redémarrage du service : $service"
        
        if docker-compose restart "$service"; then
            log_success "Service $service redémarré"
        else
            log_error "Échec du redémarrage du service $service"
            exit 1
        fi
        
        # Wait a bit for service to stabilize
        sleep 5
        
        # Check service status
        if docker-compose ps "$service" | grep -q "Up"; then
            log_success "Service $service opérationnel"
        else
            log_warning "Service $service pourrait avoir des problèmes"
        fi
    fi
}

# Main execution
main() {
    local service_name=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --service|-s)
                service_name="$2"
                shift 2
                ;;
            --help|-h)
                echo "Usage: $0 [--service|-s SERVICE_NAME]"
                echo "Redémarre tous les conteneurs ou un service spécifique"
                echo ""
                echo "Services disponibles : web, db"
                echo ""
                echo "Exemples :"
                echo "  $0                    # Redémarre tous les conteneurs"
                echo "  $0 --service web      # Redémarre seulement le service web"
                echo "  $0 -s db             # Redémarre seulement la base de données"
                exit 0
                ;;
            *)
                log_error "Option inconnue : $1"
                echo "Utilisez --help pour voir l'aide"
                exit 1
                ;;
        esac
    done
    
    echo "Début du redémarrage..."
    
    check_docker
    
    if [[ -n "$service_name" ]]; then
        restart_service "$service_name"
    else
        restart_containers
        wait_for_services
        show_status
    fi
}

# Handle interruption
trap 'log_error "Processus interrompu"; exit 130' INT

# Run main function
main "$@"
