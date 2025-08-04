#!/bin/bash
# scripts/reset-database.sh
# Quick database reset script (keeps structure, reloads data)

set -e

echo "🔄 Réinitialisation rapide de la base de données EIR"
echo "=================================================="

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

# Function to check if database is accessible
check_database() {
    log_info "Vérification de l'accès à la base de données..."
    
    if ! docker compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
        log_error "Base de données non accessible. Utilisez rebuild-database.sh pour une reconstruction complète."
        exit 1
    fi
    
    log_success "Base de données accessible"
}

# Function to clear existing data
clear_data() {
    log_info "Suppression des données existantes..."
    
    # Clear tables in proper order (respecting foreign keys)
    docker compose exec -T db psql -U postgres -d imei_db << 'EOF'
-- Disable foreign key checks temporarily
SET session_replication_role = replica;

-- Clear data from all tables
TRUNCATE TABLE Journal_Audit CASCADE;
TRUNCATE TABLE Notification CASCADE;
TRUNCATE TABLE Recherche CASCADE;
TRUNCATE TABLE IMEI CASCADE;
TRUNCATE TABLE SIM CASCADE;
TRUNCATE TABLE Appareil CASCADE;
TRUNCATE TABLE ImportExport CASCADE;
TRUNCATE TABLE Utilisateur CASCADE;

-- Re-enable foreign key checks
SET session_replication_role = DEFAULT;

-- Reset sequences
ALTER SEQUENCE IF EXISTS utilisateur_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS appareil_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS imei_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS sim_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS recherche_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS notification_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS journal_audit_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS importexport_id_seq RESTART WITH 1;
EOF

    if [[ $? -eq 0 ]]; then
        log_success "Données supprimées"
    else
        log_error "Échec de la suppression des données"
        exit 1
    fi
}

# Function to reload test data
reload_test_data() {
    log_info "Rechargement des données de test..."
    
    # Check if test data file exists
    if [[ ! -f "backend/test_data.sql" ]]; then
        log_error "Fichier de données de test non trouvé : backend/test_data.sql"
        exit 1
    fi
    
    # Load test data
    if docker compose exec -T db psql -U postgres -d imei_db -f /docker-entrypoint-initdb.d/03-test-data.sql; then
        log_success "Données de test rechargées"
    else
        log_error "Échec du rechargement des données de test"
        exit 1
    fi
}

# Function to create custom test data
create_custom_data() {
    log_info "Création de données personnalisées..."
    
    docker compose exec -T db psql -U postgres -d imei_db << 'EOF'
-- Insert additional test users
INSERT INTO Utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, est_actif)
VALUES 
    (gen_random_uuid(), 'Testeur API', 'tester@eir-project.com', '$2b$12$LQv3c7yD8ED8YzLwq2T7vu7C6YXCX3STj6yzGHdRLgIZDQzjfHI8C', 'utilisateur_authentifie', 'standard', 'own', true),
    (gen_random_uuid(), 'Support Technique', 'support@eir-project.com', '$2b$12$LQv3c7yD8ED8YzLwq2T7vu7C6YXCX3STj6yzGHdRLgIZDQzjfHI8C', 'utilisateur_authentifie', 'limited', 'tout', true);

-- Insert some additional test devices
WITH new_user AS (
    SELECT id FROM Utilisateur WHERE email = 'tester@eir-project.com'
)
INSERT INTO Appareil (id, marque, modele, emmc, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'Xiaomi',
    'Mi 11',
    '128GB',
    new_user.id
FROM new_user;

-- Insert corresponding IMEI
WITH device_info AS (
    SELECT a.id as device_id 
    FROM Appareil a 
    JOIN Utilisateur u ON a.utilisateur_id = u.id 
    WHERE u.email = 'tester@eir-project.com' AND a.marque = 'Xiaomi'
)
INSERT INTO IMEI (id, imei_number, slot_number, status, appareil_id)
SELECT 
    gen_random_uuid(),
    '351234567890123',
    1,
    'active',
    device_info.device_id
FROM device_info;

EOF

    if [[ $? -eq 0 ]]; then
        log_success "Données personnalisées créées"
    else
        log_warning "Problème avec la création des données personnalisées"
    fi
}

# Function to verify reset
verify_reset() {
    log_info "Vérification de la réinitialisation..."
    
    # Count records
    local counts
    counts=$(docker compose exec -T db psql -U postgres -d imei_db -t << 'EOF'
SELECT 
    'Utilisateurs: ' || COUNT(*) FROM Utilisateur
UNION ALL
SELECT 
    'Appareils: ' || COUNT(*) FROM Appareil
UNION ALL
SELECT 
    'IMEIs: ' || COUNT(*) FROM IMEI
UNION ALL
SELECT 
    'SIMs: ' || COUNT(*) FROM SIM;
EOF
)

    echo "$counts" | while read -r line; do
        log_success "$line"
    done
}

# Function to restart web service if needed
restart_web_if_needed() {
    log_info "Vérification du service web..."
    
    if curl -s -f http://localhost:8000/verification-etat > /dev/null 2>&1; then
        log_success "Service web opérationnel"
    else
        log_info "Redémarrage du service web..."
        docker compose restart web
        
        # Wait for API
        local max_attempts=10
        local attempt=1
        
        sleep 3
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s -f http://localhost:8000/verification-etat > /dev/null 2>&1; then
                log_success "Service web redémarré avec succès"
                break
            fi
            
            log_info "Tentative $attempt/$max_attempts - Service web non prêt"
            sleep 2
            ((attempt++))
        done
        
        if [ $attempt -gt $max_attempts ]; then
            log_warning "Service web prend plus de temps que prévu"
        fi
    fi
}

# Function to show final status
show_status() {
    echo ""
    echo "🎉 Réinitialisation de la base de données terminée !"
    echo ""
    echo "📊 Statut :"
    docker compose ps
    echo ""
    echo "🔑 Utilisateurs de test disponibles (mot de passe: admin123) :"
    echo "   👑 admin@eir-project.com (Administrateur)"
    echo "   👤 user@example.com (Utilisateur Standard)"
    echo "   🏢 insurance@company.com (Assurance)"
    echo "   👮 police@agency.gov (Police)"
    echo "   🏭 manufacturer@techcorp.com (Fabricant)"
    echo "   🧪 tester@eir-project.com (Testeur)"
    echo "   🛠️  support@eir-project.com (Support)"
    echo ""
    echo "📱 IMEIs de test :"
    echo "   Samsung : 352745080123456"
    echo "   Apple : 354123456789012"
    echo "   TechCorp : 352745080987654"
    echo "   Xiaomi : 351234567890123"
    echo ""
    echo "🧪 Test rapide :"
    echo "   curl http://localhost:8000/verification-etat"
    echo "   curl http://localhost:8000/imei/352745080123456"
    echo ""
    echo "🔧 Autres scripts utiles :"
    echo "   ./scripts/rebuild-database.sh    # Reconstruction complète"
    echo "   ./scripts/restart-containers.sh  # Redémarrage simple"
}

# Main execution
main() {
    local skip_custom_data="no"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-custom-data)
                skip_custom_data="yes"
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [--no-custom-data]"
                echo "Réinitialise rapidement la base de données EIR"
                echo ""
                echo "Options :"
                echo "  --no-custom-data   Ne crée pas de données personnalisées additionnelles"
                echo ""
                echo "Note: Ce script conserve la structure de la base de données"
                echo "      et ne fait que recharger les données."
                exit 0
                ;;
            *)
                log_error "Option inconnue : $1"
                echo "Utilisez --help pour voir l'aide"
                exit 1
                ;;
        esac
    done
    
    echo "Début de la réinitialisation rapide..."
    
    check_docker
    check_database
    clear_data
    reload_test_data
    
    if [[ "$skip_custom_data" == "no" ]]; then
        create_custom_data
    fi
    
    verify_reset
    restart_web_if_needed
    show_status
}

# Handle interruption
trap 'log_error "Processus interrompu"; exit 130' INT

# Run main function
main "$@"
