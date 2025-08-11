#!/bin/bash
# scripts/reset-database.sh
# Script pour réinitialiser rapidement la base de données EIR

set -e

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

echo "🔄 Réinitialisation rapide de la base de données EIR"
echo "=================================================="
echo "Début de la réinitialisation rapide..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    log_error "Docker n'est pas en cours d'exécution. Veuillez démarrer Docker."
    exit 1
fi

log_success "Docker est opérationnel"

# Check if containers are running
if ! docker compose ps | grep -q "Up"; then
    log_warning "Les conteneurs ne sont pas démarrés. Démarrage..."
    docker compose up -d
    sleep 10
fi

# Wait for database to be ready
log_info "Vérification de l'accès à la base de données..."
for i in {1..30}; do
    if docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 1
done

if ! docker compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    log_error "Impossible de se connecter à la base de données"
    exit 1
fi

log_success "Base de données accessible"

# Create clear data script
log_info "Suppression des données existantes..."
cat > /tmp/clear_data.sql << 'EOF'
-- Disable triggers temporarily to avoid constraint issues
SET session_replication_role = replica;

-- Clear all data from tables (order matters due to foreign keys)
TRUNCATE TABLE importexport RESTART IDENTITY CASCADE;
TRUNCATE TABLE journal_audit RESTART IDENTITY CASCADE;
TRUNCATE TABLE notification RESTART IDENTITY CASCADE;
TRUNCATE TABLE recherche RESTART IDENTITY CASCADE;
TRUNCATE TABLE sim RESTART IDENTITY CASCADE;
TRUNCATE TABLE imei RESTART IDENTITY CASCADE;
TRUNCATE TABLE appareil RESTART IDENTITY CASCADE;
TRUNCATE TABLE tac_database RESTART IDENTITY CASCADE;
TRUNCATE TABLE utilisateur RESTART IDENTITY CASCADE;

-- Re-enable triggers
SET session_replication_role = DEFAULT;

SELECT 'Données supprimées avec succès!' as status;
EOF

# Copy and execute clear script
docker compose cp /tmp/clear_data.sql db:/tmp/clear_data.sql
docker compose exec -T db psql -U postgres -d eir_project -f /tmp/clear_data.sql

log_success "Données supprimées"

# Create test data if it doesn't exist
if [[ ! -f "backend/test_data.sql" ]]; then
    log_info "Création du fichier de données de test..."
    mkdir -p backend
    cat > backend/test_data.sql << 'EOF'
-- Test data for EIR system
-- Insert test users
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, organisation, est_actif) VALUES
('00000000-0000-0000-0000-000000000001', 'Admin System', 'admin@eir.ma', '$2b$12$LQv3c1yqBwEHFwyDOSjR5.3yxSC..u3YGRKr5QOOXzKH8nYXn6mhO', 'administrateur', 'admin', 'tout', 'ANRT', true),
('00000000-0000-0000-0000-000000000002', 'Operateur Orange', 'devvmrr@gmail.com', '$2b$12$LQv3c1yqBwEHFwyDOSjR5.3yxSC..u3YGRKr5QOOXzKH8nYXn6mhO', 'operateur', 'standard', 'organisation', 'Orange Maroc', true),
('00000000-0000-0000-0000-000000000003', 'Operateur Inwi', 'inwi@eir.ma', '$2b$12$LQv3c1yqBwEHFwyDOSjR5.3yxSC..u3YGRKr5QOOXzKH8nYXn6mhO', 'operateur', 'standard', 'organisation', 'Inwi', true),
('00000000-0000-0000-0000-000000000004', 'Utilisateur Test', 'sidis9828@gmail.com', '$2b$12$LQv3c1yqBwEHFwyDOSjR5.3yxSC..u3YGRKr5QOOXzKH8nYXn6mhO', 'utilisateur_authentifie', 'basique', 'personnel', 'Test Corp', true);

-- Insert test TAC data
INSERT INTO tac_database (tac, marque, modele, type_appareil, statut) VALUES
('35326005', 'Samsung', 'Galaxy S23', 'smartphone', 'valide'),
('35692005', 'Apple', 'iPhone 14', 'smartphone', 'valide'),
('86234567', 'Huawei', 'P50 Pro', 'smartphone', 'valide'),
('35847200', 'Xiaomi', 'Mi 12', 'smartphone', 'valide'),
('35404806', 'OnePlus', '10 Pro', 'smartphone', 'valide'),
('35404807', 'OnePlus', 'Nord 2', 'smartphone', 'valide'),
('99000000', 'TestDevice', 'Test Model', 'test_device', 'test'),
('01194800', 'Apple', 'iPhone 3GS', 'smartphone', 'obsolete'),
('35060680', 'Nokia', '3310', 'feature_phone', 'obsolete');

-- Insert test devices
INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id) VALUES
('10000000-0000-0000-0000-000000000001', 'Samsung', 'Galaxy S23', '256GB', '00000000-0000-0000-0000-000000000002'),
('10000000-0000-0000-0000-000000000002', 'Apple', 'iPhone 14', '128GB', '00000000-0000-0000-0000-000000000003'),
('10000000-0000-0000-0000-000000000003', 'Huawei', 'P50 Pro', '512GB', '00000000-0000-0000-0000-000000000004'),
('10000000-0000-0000-0000-000000000004', 'Xiaomi', 'Mi 12', '256GB', '00000000-0000-0000-0000-000000000002'),
('10000000-0000-0000-0000-000000000005', 'OnePlus', '10 Pro', '128GB', '00000000-0000-0000-0000-000000000003');

-- Insert test IMEIs
INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id) VALUES
('20000000-0000-0000-0000-000000000001', '353260051234567', 1, 'active', '10000000-0000-0000-0000-000000000001'),
('20000000-0000-0000-0000-000000000002', '353260051234568', 2, 'active', '10000000-0000-0000-0000-000000000001'),
('20000000-0000-0000-0000-000000000003', '356920051234567', 1, 'active', '10000000-0000-0000-0000-000000000002'),
('20000000-0000-0000-0000-000000000004', '862345671234567', 1, 'active', '10000000-0000-0000-0000-000000000003'),
('20000000-0000-0000-0000-000000000005', '358472001234567', 1, 'active', '10000000-0000-0000-0000-000000000004'),
('20000000-0000-0000-0000-000000000006', '354048061234567', 1, 'active', '10000000-0000-0000-0000-000000000005'),
('20000000-0000-0000-0000-000000000007', '990000001234567', 1, 'suspect', '10000000-0000-0000-0000-000000000005'),
('20000000-0000-0000-0000-000000000008', '011948001234567', 1, 'bloque', '10000000-0000-0000-0000-000000000004');

-- Insert test SIM cards
INSERT INTO sim (id, iccid, operateur, utilisateur_id) VALUES
('30000000-0000-0000-0000-000000000001', '89212070000000001234', 'Orange', '00000000-0000-0000-0000-000000000002'),
('30000000-0000-0000-0000-000000000002', '89212040000000001234', 'Inwi', '00000000-0000-0000-0000-000000000003'),
('30000000-0000-0000-0000-000000000003', '89212010000000001234', 'Maroc Telecom', '00000000-0000-0000-0000-000000000004'),
('30000000-0000-0000-0000-000000000004', '89212070000000005678', 'Orange', '00000000-0000-0000-0000-000000000002'),
('30000000-0000-0000-0000-000000000005', '89212040000000005678', 'Inwi', '00000000-0000-0000-0000-000000000003');

-- Insert test searches
INSERT INTO recherche (id, date_recherche, imei_recherche, utilisateur_id) VALUES
('40000000-0000-0000-0000-000000000001', NOW() - INTERVAL '1 day', '353260051234567', '00000000-0000-0000-0000-000000000002'),
('40000000-0000-0000-0000-000000000002', NOW() - INTERVAL '2 hours', '356920051234567', '00000000-0000-0000-0000-000000000003'),
('40000000-0000-0000-0000-000000000003', NOW() - INTERVAL '30 minutes', '862345671234567', '00000000-0000-0000-0000-000000000004'),
('40000000-0000-0000-0000-000000000004', NOW() - INTERVAL '5 minutes', '990000001234567', '00000000-0000-0000-0000-000000000001'),
('40000000-0000-0000-0000-000000000005', NOW(), '011948001234567', '00000000-0000-0000-0000-000000000001');

-- Insert test notifications
INSERT INTO notification (id, type, contenu, statut, utilisateur_id) VALUES
('50000000-0000-0000-0000-000000000001', 'alerte', 'IMEI suspect détecté: 990000001234567', 'non_lu', '00000000-0000-0000-0000-000000000001'),
('50000000-0000-0000-0000-000000000002', 'info', 'Nouveau dispositif enregistré: Samsung Galaxy S23', 'lu', '00000000-0000-0000-0000-000000000002'),
('50000000-0000-0000-0000-000000000003', 'alerte', 'IMEI bloqué utilisé: 011948001234567', 'non_lu', '00000000-0000-0000-0000-000000000001'),
('50000000-0000-0000-0000-000000000004', 'info', 'Recherche effectuée pour IMEI: 356920051234567', 'lu', '00000000-0000-0000-0000-000000000003');

-- Insert test audit logs
INSERT INTO journal_audit (id, action, date, utilisateur_id) VALUES
('60000000-0000-0000-0000-000000000001', 'LOGIN: Connexion utilisateur admin@eir.ma', NOW() - INTERVAL '1 hour', '00000000-0000-0000-0000-000000000001'),
('60000000-0000-0000-0000-000000000002', 'SEARCH: Recherche IMEI 353260051234567', NOW() - INTERVAL '45 minutes', '00000000-0000-0000-0000-000000000002'),
('60000000-0000-0000-0000-000000000003', 'CREATE: Nouveau dispositif ajouté', NOW() - INTERVAL '30 minutes', '00000000-0000-0000-0000-000000000003'),
('60000000-0000-0000-0000-000000000004', 'UPDATE: Statut IMEI modifié', NOW() - INTERVAL '15 minutes', '00000000-0000-0000-0000-000000000001'),
('60000000-0000-0000-0000-000000000005', 'EXPORT: Export de données effectué', NOW() - INTERVAL '5 minutes', '00000000-0000-0000-0000-000000000001');

-- Insert test import/export records
INSERT INTO importexport (id, type_operation, fichier, date, utilisateur_id) VALUES
('70000000-0000-0000-0000-000000000001', 'import', 'devices_batch_001.csv', NOW() - INTERVAL '2 days', '00000000-0000-0000-0000-000000000001'),
('70000000-0000-0000-0000-000000000002', 'export', 'imei_report_2024.csv', NOW() - INTERVAL '1 day', '00000000-0000-0000-0000-000000000002'),
('70000000-0000-0000-0000-000000000003', 'import', 'tac_database_update.csv', NOW() - INTERVAL '6 hours', '00000000-0000-0000-0000-000000000001'),
('70000000-0000-0000-0000-000000000004', 'export', 'monthly_stats.xlsx', NOW() - INTERVAL '1 hour', '00000000-0000-0000-0000-000000000003');

-- Display summary
SELECT 'Données de test insérées avec succès!' as message;
SELECT 
    'Utilisateurs: ' || (SELECT COUNT(*) FROM utilisateur) ||
    ', Appareils: ' || (SELECT COUNT(*) FROM appareil) ||
    ', IMEIs: ' || (SELECT COUNT(*) FROM imei) ||
    ', TACs: ' || (SELECT COUNT(*) FROM tac_database) as resume;
EOF
fi

# Load test data
log_info "Rechargement des données de test..."
docker compose cp backend/test_data.sql db:/tmp/test_data.sql
if docker compose exec -T db psql -U postgres -d eir_project -f /tmp/test_data.sql; then
    log_success "Données de test chargées"
else
    log_error "Échec du rechargement des données de test"
    exit 1
fi

# Display statistics
log_info "Affichage des statistiques..."
docker compose exec -T db psql -U postgres -d eir_project -c "
SELECT 'Base de données réinitialisée avec succès!' as status;
SELECT 
    'Statistiques' as info,
    (SELECT COUNT(*) FROM utilisateur) as utilisateurs,
    (SELECT COUNT(*) FROM appareil) as appareils,
    (SELECT COUNT(*) FROM imei) as imeis,
    (SELECT COUNT(*) FROM sim) as cartes_sim,
    (SELECT COUNT(*) FROM recherche) as recherches,
    (SELECT COUNT(*) FROM tac_database) as tac_entries;
"

# Clean up temporary files
rm -f /tmp/clear_data.sql

log_success "Réinitialisation terminée avec succès!"
echo ""
echo "📊 Comptes de test disponibles:"
echo "   Admin: admin@eir.ma / password123"
echo "   Orange: devvmrr@gmail.com / password123"
echo "   Inwi: inwi@eir.ma / password123"
echo "   User: sidis9828@gmail.com / password123"
echo ""
echo "🌐 Interface web: http://localhost:8000"
echo "🔧 Admin: http://localhost:8000/admin"
echo ""
echo "🔧 Pour importer votre base TAC Osmocom:"
echo "   ./scripts/alimenter-base-donnees.sh --osmocom-tac data/tacdb.csv"
echo ""
echo "🧪 Test TAC validation:"
echo "   curl http://localhost:8000/imei/353260051234567/validate"
    echo "🔑 Utilisateurs de test disponibles (mot de passe: admin123) :"
    echo "   👑 eirrproject@gmail.com (Administrateur)"
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
