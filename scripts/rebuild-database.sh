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
    
    # Create backup directory with proper permissions (use sudo if needed)
    if ! mkdir -p "$backup_dir" 2>/dev/null; then
        log_warning "Impossible de créer le répertoire de sauvegarde (permissions)"
        return 1
    fi
    
    # Try to set permissions, ignore if it fails
    chmod 755 "$backup_dir" 2>/dev/null || true
    
    # Check if database exists and is accessible
    if docker compose ps | grep -q "db.*Up"; then
        if docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
            if docker compose exec -T db pg_dump -U postgres eir_project > "$backup_dir/$backup_file" 2>/dev/null; then
                log_success "Sauvegarde créée : $backup_dir/$backup_file"
                return 0
            else
                log_warning "Impossible de créer une sauvegarde (base de données vide ou inaccessible)"
                return 1
            fi
        else
            log_warning "Base de données non accessible pour la sauvegarde"
            return 1
        fi
    else
        log_warning "Service de base de données non démarré"
        return 1
    fi
}

# Function to stop and remove database
remove_database() {
    log_info "Suppression de la base de données existante..."
    
    # Stop containers
    docker compose down -v
    log_success "Conteneurs arrêtés"
    
    # Remove database volume if it exists
    if docker volume ls -q | grep -q "eir-project_postgres_data"; then
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
    if docker compose up -d db; then
        log_success "Service de base de données démarré"
    else
        log_error "Échec du démarrage de la base de données"
        exit 1
    fi
    
    # Wait for database to be ready with better timing
    local max_attempts=60  # Increased from 30
    local attempt=1
    
    log_info "Attente de la disponibilité de la base de données..."
    
    # Initial wait for container to fully start
    sleep 5
    
    while [ $attempt -le $max_attempts ]; do
        if docker compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
            log_success "Base de données disponible !"
            # Additional wait to ensure full initialization
            sleep 3
            break
        fi
        
        if [ $((attempt % 10)) -eq 0 ]; then
            log_info "Tentative $attempt/$max_attempts - Base de données en cours d'initialisation..."
            # Check container logs for debugging
            if [ $attempt -eq 20 ]; then
                log_info "Vérification des logs de la base de données..."
                docker compose logs --tail=10 db
            fi
        fi
        
        sleep 3  # Increased from 2
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "Timeout - Base de données non accessible"
        log_info "Logs de la base de données :"
        docker compose logs db
        exit 1
    fi
}

# Function to create database
create_database() {
    log_info "Création de la base de données..."
    
    # The database should already be created by the Docker init process
    # But let's ensure it exists
    if docker compose exec -T db psql -U postgres -lqt | cut -d \| -f 1 | grep -qw eir_project; then
        log_success "Base de données 'eir_project' existe déjà"
    else
        # Create database if it doesn't exist
        if docker compose exec -T db psql -U postgres -c "CREATE DATABASE eir_project;" 2>/dev/null; then
            log_success "Base de données 'eir_project' créée"
        else
            log_error "Échec de la création de la base de données"
            exit 1
        fi
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
    
    # Copy schema file to container and apply it
    docker compose cp backend/schema_postgres.sql db:/tmp/schema.sql
    
    if docker compose exec -T db psql -U postgres -d eir_project -f /tmp/schema.sql; then
        log_success "Schéma appliqué avec succès"
    else
        log_error "Échec de l'application du schéma"
        exit 1
    fi
}

# Function to load test data
load_test_data() {
    local load_data=${1:-"yes"}
    
    if [[ "$load_data" == "yes" ]]; then
        log_info "Chargement des données de test..."
        
        # Check if test data file exists
        if [[ -f "backend/test_data.sql" ]]; then
            # Copy test data file to container and apply it
            docker compose cp backend/test_data.sql db:/tmp/test_data.sql
            
            if docker compose exec -T db psql -U postgres -d eir_project -f /tmp/test_data.sql; then
                log_success "Données de test chargées"
            else
                log_error "Échec du chargement des données de test"
                return 1
            fi
        else
            log_warning "Fichier de données de test non trouvé"
            # Create basic test data
            create_basic_test_data
        fi
    else
        log_info "Chargement des données de test ignoré"
    fi
}

# Function to create basic test data if file doesn't exist
create_basic_test_data() {
    log_info "Création de données de test de base..."
    
    docker compose exec -T db psql -U postgres -d eir_project << 'EOF'
-- Create basic admin user
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, est_actif)
VALUES (
    gen_random_uuid(),
    'System Administrator',
    'admin@eir.ma',
    '$2b$12$LQv3c1yqBwEHFwyDOSjR5.3yxSC..u3YGRKr5QOOXzKH8nYXn6mhO',
    'administrateur',
    'admin',
    'tout',
    true
);

-- Create basic test user
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, est_actif)
VALUES (
    gen_random_uuid(),
    'Test User',
    'sidis9828@gmail.com',
    '$2b$12$LQv3c1yqBwEHFwyDOSjR5.3yxSC..u3YGRKr5QOOXzKH8nYXn6mhO',
    'utilisateur_authentifie',
    'standard',
    'personnel',
    true
);

-- Create basic test device and IMEI for testing TAC validation
DO $$
DECLARE
    user_id UUID;
    device_id UUID := gen_random_uuid();
BEGIN
    -- Get a user ID for the device
    SELECT id INTO user_id FROM utilisateur WHERE email = 'sidis9828@gmail.com' LIMIT 1;
    
    -- Create test device
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'Samsung', 'Galaxy Test', '128GB', user_id);
    
    -- Create test IMEI
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES (gen_random_uuid(), '353260051234567', 1, 'active', device_id);
    
    -- Create basic TAC entry for testing
    INSERT INTO tac_database (tac, marque, modele, type_appareil, statut)
    VALUES ('35326005', 'Samsung', 'Galaxy S23', 'smartphone', 'valide')
    ON CONFLICT (tac) DO NOTHING;
END $$;

SELECT 'Données de test de base créées' as status;
EOF
    
    log_success "Données de test de base créées"
}

# Function to verify database
verify_database() {
    log_info "Vérification de la base de données..."
    
    # Count tables
    local table_count
    table_count=$(docker compose exec -T db psql -U postgres -d eir_project -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' \n')
    
    log_success "Tables créées : $table_count"
    
    # Count users
    local user_count
    user_count=$(docker compose exec -T db psql -U postgres -d eir_project -t -c "SELECT COUNT(*) FROM utilisateur;" 2>/dev/null | tr -d ' \n' || echo "0")
    
    if [[ "$user_count" -gt "0" ]]; then
        log_success "Utilisateurs de test : $user_count"
    else
        log_info "Aucun utilisateur de test chargé"
    fi
    
    # Count devices
    local device_count
    device_count=$(docker compose exec -T db psql -U postgres -d eir_project -t -c "SELECT COUNT(*) FROM appareil;" 2>/dev/null | tr -d ' \n' || echo "0")
    
    if [[ "$device_count" -gt "0" ]]; then
        log_success "Appareils de test : $device_count"
    else
        log_info "Aucun appareil de test chargé"
    fi
    
    # Check TAC database
    local tac_count
    tac_count=$(docker compose exec -T db psql -U postgres -d eir_project -t -c "SELECT COUNT(*) FROM tac_database;" 2>/dev/null | tr -d ' \n' || echo "0")
    
    if [[ "$tac_count" -gt "0" ]]; then
        log_success "Entrées TAC : $tac_count"
    else
        log_info "Base TAC vide (utilisez ./scripts/alimenter-base-donnees.sh --osmocom-tac pour l'importer)"
    fi
}

# Function to start web service
start_web_service() {
    log_info "Démarrage du service web..."
    
    if docker compose up -d web; then
        log_success "Service web démarré"
        
        # Wait for API with better error handling
        local max_attempts=20
        local attempt=1
        
        sleep 8  # Initial wait for API startup
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s -f http://localhost:8000/verification-etat > /dev/null 2>&1; then
                log_success "API opérationnelle !"
                break
            fi
            
            if [ $((attempt % 5)) -eq 0 ]; then
                log_info "Tentative $attempt/$max_attempts - API en cours de démarrage..."
            fi
            
            sleep 3
            ((attempt++))
        done
        
        if [ $attempt -gt $max_attempts ]; then
            log_warning "API prend plus de temps que prévu - vérifiez http://localhost:8000/docs"
            log_info "Logs du service web :"
            docker compose logs --tail=20 web
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
    docker compose ps
    
    echo ""
    echo "🎉 Reconstruction de la base de données terminée !"
    echo ""
    echo "📍 Points d'accès :"
    echo "   🌐 Documentation API : http://localhost:8000/docs"
    echo "   🔍 Vérification santé : http://localhost:8000/verification-etat"
    echo "   🗄️  Base de données : localhost:5432 (postgres/postgres)"
    echo ""
    echo "🔑 Utilisateurs de test (mot de passe: password123) :"
    echo "   👑 admin@eir.ma (Administrateur)"
    echo "   👤 sidis9828@gmail.com (Utilisateur Standard)"
    echo ""
    echo "🧪 Test rapide de la base de données :"
    echo "   curl http://localhost:8000/verification-etat"
    echo "   curl http://localhost:8000/imei/353260051234567/validate"
    echo ""
    echo "📱 Import de la base TAC :"
    echo "   ./scripts/alimenter-base-donnees.sh --osmocom-tac data/tacdb.csv"
    echo ""
    echo "🔧 Si problèmes :"
    echo "   docker compose logs db     # Logs de la base de données"
    echo "   docker compose logs web    # Logs du service web"
    echo "   ./scripts/reset-database.sh  # Réinitialisation rapide"
    echo ""
    echo "🗃️ Administration de la base :"
    echo "   docker compose exec db psql -U postgres -d eir_project -c \"\\dt\""
    echo "   docker compose exec db psql -U postgres -d eir_project -c \"SELECT COUNT(*) FROM utilisateur;\""
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
                echo "Note: Ce script détruit complètement la base de données existante"
                echo "      et la recrée depuis zéro."
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
