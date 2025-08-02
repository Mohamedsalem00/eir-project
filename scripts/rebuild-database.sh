#!/bin/bash
# scripts/rebuild-database.sh
# Complete database rebuild script

set -e

echo "🗄️  Reconstruction complète de la base de données EIR"
echo "===================================================="

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

# Function to backup existing data (optional)
backup_database() {
    log_info "Création d'une sauvegarde de sécurité..."
    
    local backup_dir="backups"
    local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    mkdir -p "$backup_dir"
    
    if docker-compose exec -T db pg_dump -U postgres imei_db > "$backup_dir/$backup_file" 2>/dev/null; then
        log_success "Sauvegarde créée : $backup_dir/$backup_file"
        return 0
    else
        log_warning "Impossible de créer une sauvegarde (base de données peut-être inexistante)"
        return 1
    fi
}

# Function to stop and remove database
remove_database() {
    log_info "Suppression de la base de données existante..."
    
    # Stop containers
    docker-compose down -v
    log_success "Conteneurs arrêtés"
    
    # Remove database volume
    if docker volume ls | grep -q "eir-project_postgres_data"; then
        docker volume rm eir-project_postgres_data 2>/dev/null || true
        log_success "Volume de base de données supprimé"
    else
        log_info "Aucun volume de base de données existant"
    fi
}

# Function to start database service
start_database() {
    log_info "Démarrage du service de base de données..."
    
    # Start only database service
    if docker-compose up -d db; then
        log_success "Service de base de données démarré"
    else
        log_error "Échec du démarrage de la base de données"
        exit 1
    fi
    
    # Wait for database to be ready
    local max_attempts=30
    local attempt=1
    
    log_info "Attente de la disponibilité de la base de données..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
            log_success "Base de données disponible !"
            break
        fi
        
        log_info "Tentative $attempt/$max_attempts - Base de données non prête"
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "Timeout - Base de données non accessible"
        exit 1
    fi
}

# Function to create database
create_database() {
    log_info "Création de la base de données..."
    
    # Create database
    if docker-compose exec -T db psql -U postgres -c "CREATE DATABASE imei_db;" 2>/dev/null; then
        log_success "Base de données 'imei_db' créée"
    else
        log_warning "Base de données 'imei_db' existe déjà ou erreur de création"
        # Drop and recreate if exists
        docker-compose exec -T db psql -U postgres -c "DROP DATABASE IF EXISTS imei_db;"
        docker-compose exec -T db psql -U postgres -c "CREATE DATABASE imei_db;"
        log_success "Base de données 'imei_db' recréée"
    fi
}

# Function to apply schema
apply_schema() {
    log_info "Application du schéma de base de données..."
    
    # Check if schema file exists
    if [[ ! -f "backend/schema_postgres.sql" ]]; then
        log_error "Fichier de schéma non trouvé : backend/schema_postgres.sql"
        exit 1
    fi
    
    # Apply schema
    if docker-compose exec -T db psql -U postgres -d imei_db -f /docker-entrypoint-initdb.d/01-schema.sql; then
        log_success "Schéma appliqué avec succès"
    else
        log_error "Échec de l'application du schéma"
        exit 1
    fi
}

# Function to apply migrations
apply_migrations() {
    log_info "Application des migrations..."
    
    # Check if migration file exists
    if [[ -f "backend/migrations/access_control_migration.sql" ]]; then
        if docker-compose exec -T db psql -U postgres -d imei_db -f /docker-entrypoint-initdb.d/02-migrate.sql; then
            log_success "Migrations appliquées"
        else
            log_warning "Problème avec les migrations"
        fi
    else
        log_info "Aucun fichier de migration trouvé"
    fi
}

# Function to load test data
load_test_data() {
    local load_data=${1:-"yes"}
    
    if [[ "$load_data" == "yes" ]]; then
        log_info "Chargement des données de test..."
        
        # Check if test data file exists
        if [[ -f "backend/test_data.sql" ]]; then
            if docker-compose exec -T db psql -U postgres -d imei_db -f /docker-entrypoint-initdb.d/03-test-data.sql; then
                log_success "Données de test chargées"
            else
                log_error "Échec du chargement des données de test"
                return 1
            fi
        else
            log_warning "Fichier de données de test non trouvé"
        fi
    else
        log_info "Chargement des données de test ignoré"
    fi
}

# Function to verify database
verify_database() {
    log_info "Vérification de la base de données..."
    
    # Count tables
    local table_count
    table_count=$(docker-compose exec -T db psql -U postgres -d imei_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' \n')
    
    log_success "Tables créées : $table_count"
    
    # Count users
    local user_count
    user_count=$(docker-compose exec -T db psql -U postgres -d imei_db -t -c "SELECT COUNT(*) FROM Utilisateur;" 2>/dev/null | tr -d ' \n' || echo "0")
    
    if [[ "$user_count" -gt "0" ]]; then
        log_success "Utilisateurs de test : $user_count"
    else
        log_info "Aucun utilisateur de test chargé"
    fi
    
    # Count devices
    local device_count
    device_count=$(docker-compose exec -T db psql -U postgres -d imei_db -t -c "SELECT COUNT(*) FROM Appareil;" 2>/dev/null | tr -d ' \n' || echo "0")
    
    if [[ "$device_count" -gt "0" ]]; then
        log_success "Appareils de test : $device_count"
    else
        log_info "Aucun appareil de test chargé"
    fi
}

# Function to start web service
start_web_service() {
    log_info "Démarrage du service web..."
    
    if docker-compose up -d web; then
        log_success "Service web démarré"
        
        # Wait for API
        local max_attempts=15
        local attempt=1
        
        sleep 5  # Initial wait
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s -f http://localhost:8000/verification-etat > /dev/null 2>&1; then
                log_success "API opérationnelle !"
                break
            fi
            
            log_info "Tentative $attempt/$max_attempts - API non prête"
            sleep 3
            ((attempt++))
        done
        
        if [ $attempt -gt $max_attempts ]; then
            log_warning "API prend plus de temps que prévu"
        fi
    else
        log_error "Échec du démarrage du service web"
        exit 1
    fi
}

# Function to show final status
show_status() {
    echo ""
    echo "📊 Statut final :"
    docker-compose ps
    
    echo ""
    echo "🎉 Reconstruction de la base de données terminée !"
    echo ""
    echo "📍 Points d'accès :"
    echo "   🌐 Documentation API : http://localhost:8000/docs"
    echo "   🔍 Vérification santé : http://localhost:8000/verification-etat"
    echo "   🗄️  Base de données : localhost:5432 (postgres/postgres)"
    echo ""
    echo "🔑 Utilisateurs de test (mot de passe: admin123) :"
    echo "   👑 admin@eir-project.com (Administrateur)"
    echo "   👤 user@example.com (Utilisateur Standard)"
    echo "   🏢 insurance@company.com (Assurance)"
    echo "   👮 police@agency.gov (Police)"
    echo "   🏭 manufacturer@techcorp.com (Fabricant)"
    echo ""
    echo "🧪 Test de la base de données :"
    echo "   docker-compose exec db psql -U postgres -d imei_db -c \"\\dt\""
    echo ""
    echo "🔧 Si problèmes :"
    echo "   docker-compose logs db     # Logs de la base de données"
    echo "   ./scripts/reset-database.sh  # Réinitialisation rapide"
}

# Main execution
main() {
    local skip_backup="no"
    local skip_test_data="no"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-backup)
                skip_backup="yes"
                shift
                ;;
            --no-test-data)
                skip_test_data="yes"
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [--no-backup] [--no-test-data]"
                echo "Reconstruit complètement la base de données EIR"
                echo ""
                echo "Options :"
                echo "  --no-backup      Ne crée pas de sauvegarde avant reconstruction"
                echo "  --no-test-data   Ne charge pas les données de test"
                echo ""
                exit 0
                ;;
            *)
                log_error "Option inconnue : $1"
                echo "Utilisez --help pour voir l'aide"
                exit 1
                ;;
        esac
    done
    
    echo "Début de la reconstruction de la base de données..."
    
    check_docker
    
    if [[ "$skip_backup" == "no" ]]; then
        backup_database || true  # Continue even if backup fails
    fi
    
    remove_database
    start_database
    create_database
    apply_schema
    apply_migrations
    
    if [[ "$skip_test_data" == "no" ]]; then
        load_test_data "yes"
    fi
    
    verify_database
    start_web_service
    show_status
}

# Handle interruption
trap 'log_error "Processus interrompu"; exit 130' INT

# Run main function
main "$@"
