#!/bin/bash
# scripts/test-system.sh
# Test automatisé du système EIR francisé

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Navigate to project root
cd "$(dirname "$0")/.."

print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🧪 TESTS SYSTÈME EIR 🧪                   ║"
    echo "║              Validation complète du projet francisé         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

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

test_counter=0
passed_tests=0
failed_tests=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((test_counter++))
    echo ""
    echo -e "${BOLD}Test $test_counter: $test_name${NC}"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        log_success "$test_name : RÉUSSI"
        ((passed_tests++))
        return 0
    else
        log_error "$test_name : ÉCHEC"
        ((failed_tests++))
        return 1
    fi
}

# Test 1: Docker availability
test_docker() {
    if docker info > /dev/null 2>&1; then
        log_info "Docker est disponible et en cours d'exécution"
        return 0
    else
        log_error "Docker n'est pas disponible"
        return 1
    fi
}

# Test 2: Docker Compose file validation
test_docker_compose() {
    if docker-compose config > /dev/null 2>&1; then
        log_info "Configuration docker-compose.yml valide"
        return 0
    else
        log_error "Configuration docker-compose.yml invalide"
        return 1
    fi
}

# Test 3: Scripts availability
test_scripts_available() {
    local scripts=("manage-eir.sh" "rebuild-containers.sh" "restart-containers.sh" "rebuild-database.sh" "reset-database.sh")
    local missing_scripts=()
    
    for script in "${scripts[@]}"; do
        if [[ ! -f "scripts/$script" ]]; then
            missing_scripts+=("$script")
        elif [[ ! -x "scripts/$script" ]]; then
            log_warning "Script scripts/$script n'est pas exécutable"
            chmod +x "scripts/$script"
        fi
    done
    
    if [[ ${#missing_scripts[@]} -eq 0 ]]; then
        log_info "Tous les scripts de gestion sont présents et exécutables"
        return 0
    else
        log_error "Scripts manquants: ${missing_scripts[*]}"
        return 1
    fi
}

# Test 4: Backend structure
test_backend_structure() {
    local required_files=(
        "backend/app/main.py"
        "backend/app/api/imei.py"
        "backend/app/api/user.py"
        "backend/app/core/database.py"
        "backend/app/core/auth.py"
        "backend/app/i18n/translator.py"
        "backend/requirements.txt"
        "backend/Dockerfile"
    )
    
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -eq 0 ]]; then
        log_info "Structure du backend complète"
        return 0
    else
        log_error "Fichiers backend manquants: ${missing_files[*]}"
        return 1
    fi
}

# Test 5: Translation files
test_translation_files() {
    local translation_files=(
        "backend/app/i18n/translations/fr.json"
        "backend/app/i18n/translations/en.json"
        "backend/app/i18n/translations/ar.json"
    )
    
    local missing_translations=()
    
    for file in "${translation_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            missing_translations+=("$file")
        else
            # Test if file contains valid JSON
            if ! python3 -m json.tool "$file" > /dev/null 2>&1; then
                log_error "Fichier de traduction invalide: $file"
                return 1
            fi
        fi
    done
    
    if [[ ${#missing_translations[@]} -eq 0 ]]; then
        log_info "Tous les fichiers de traduction sont présents et valides"
        return 0
    else
        log_error "Fichiers de traduction manquants: ${missing_translations[*]}"
        return 1
    fi
}

# Test 6: French translation keys
test_french_keys() {
    local fr_file="backend/app/i18n/translations/fr.json"
    
    if [[ ! -f "$fr_file" ]]; then
        log_error "Fichier de traduction français manquant"
        return 1
    fi
    
    # Check for some key French translation keys
    local french_keys=("service_en_cours" "appareil_non_trouve" "utilisateur_cree" "erreur_interne")
    local missing_keys=()
    
    for key in "${french_keys[@]}"; do
        if ! grep -q "\"$key\"" "$fr_file"; then
            missing_keys+=("$key")
        fi
    done
    
    if [[ ${#missing_keys[@]} -eq 0 ]]; then
        log_info "Clés de traduction françaises présentes"
        return 0
    else
        log_error "Clés françaises manquantes: ${missing_keys[*]}"
        return 1
    fi
}

# Test 7: Database schema files
test_database_files() {
    local db_files=(
        "backend/schema_postgres.sql"
        "backend/test_data.sql"
        "backend/init-db.sh"
    )
    
    local missing_db_files=()
    
    for file in "${db_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            missing_db_files+=("$file")
        fi
    done
    
    if [[ ${#missing_db_files[@]} -eq 0 ]]; then
        log_info "Fichiers de base de données présents"
        return 0
    else
        log_error "Fichiers de base de données manquants: ${missing_db_files[*]}"
        return 1
    fi
}

# Test 8: Container build test
test_container_build() {
    log_info "Test de construction des conteneurs (peut prendre quelques minutes)..."
    
    if docker-compose build --no-cache > /dev/null 2>&1; then
        log_info "Construction des conteneurs réussie"
        return 0
    else
        log_error "Échec de la construction des conteneurs"
        return 1
    fi
}

# Test 9: Container startup test
test_container_startup() {
    log_info "Test de démarrage des conteneurs..."
    
    # Start containers
    if docker-compose up -d > /dev/null 2>&1; then
        log_info "Conteneurs démarrés"
        
        # Wait for services to be ready
        log_info "Attente du démarrage des services (30 secondes)..."
        sleep 30
        
        # Check if API is responding
        if curl -s -f http://localhost:8000/verification-etat > /dev/null 2>&1; then
            log_info "API accessible et répond"
            return 0
        else
            log_error "API non accessible"
            return 1
        fi
    else
        log_error "Échec du démarrage des conteneurs"
        return 1
    fi
}

# Test 10: French API endpoints test
test_french_api() {
    log_info "Test des endpoints API francisés..."
    
    # Test health endpoint
    local health_response
    health_response=$(curl -s http://localhost:8000/verification-etat 2>/dev/null || echo "")
    
    if [[ -n "$health_response" ]] && echo "$health_response" | grep -q "service_en_cours"; then
        log_info "Endpoint de santé francisé fonctionne"
    else
        log_error "Endpoint de santé francisé ne fonctionne pas correctement"
        return 1
    fi
    
    # Test languages endpoint
    local languages_response
    languages_response=$(curl -s http://localhost:8000/langues 2>/dev/null || echo "")
    
    if [[ -n "$languages_response" ]] && echo "$languages_response" | grep -q "langues_supportees"; then
        log_info "Endpoint des langues francisé fonctionne"
    else
        log_error "Endpoint des langues francisé ne fonctionne pas correctement"
        return 1
    fi
    
    return 0
}

# Test 11: Database connectivity
test_database_connectivity() {
    log_info "Test de connectivité à la base de données..."
    
    if docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
        log_info "Base de données accessible"
        
        # Test database content
        local table_count
        table_count=$(docker-compose exec -T db psql -U postgres -d imei_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' \n' || echo "0")
        
        if [[ "$table_count" -gt 0 ]]; then
            log_info "Base de données contient $table_count tables"
            return 0
        else
            log_error "Base de données vide ou inaccessible"
            return 1
        fi
    else
        log_error "Base de données non accessible"
        return 1
    fi
}

# Test 12: Documentation accessibility
test_documentation() {
    log_info "Test d'accessibilité de la documentation..."
    
    if curl -s -f http://localhost:8000/docs > /dev/null 2>&1; then
        log_info "Documentation Swagger accessible"
        return 0
    else
        log_error "Documentation Swagger non accessible"
        return 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Nettoyage après tests..."
    docker-compose down > /dev/null 2>&1 || true
}

# Main test execution
main() {
    print_header
    
    echo "🚀 Démarrage des tests du système EIR francisé..."
    echo ""
    
    # Run all tests
    run_test "Disponibilité Docker" "test_docker"
    run_test "Validation docker-compose.yml" "test_docker_compose"
    run_test "Scripts de gestion disponibles" "test_scripts_available"
    run_test "Structure du backend" "test_backend_structure"
    run_test "Fichiers de traduction" "test_translation_files"
    run_test "Clés de traduction françaises" "test_french_keys"
    run_test "Fichiers de base de données" "test_database_files"
    run_test "Construction des conteneurs" "test_container_build"
    run_test "Démarrage des conteneurs" "test_container_startup"
    run_test "API francisée" "test_french_api"
    run_test "Connectivité base de données" "test_database_connectivity"
    run_test "Documentation accessible" "test_documentation"
    
    # Test summary
    echo ""
    echo -e "${BOLD}📊 RÉSUMÉ DES TESTS${NC}"
    echo "=================================="
    echo -e "Total des tests : ${BOLD}$test_counter${NC}"
    echo -e "Tests réussis : ${GREEN}$passed_tests${NC}"
    echo -e "Tests échoués : ${RED}$failed_tests${NC}"
    echo ""
    
    if [[ $failed_tests -eq 0 ]]; then
        log_success "🎉 Tous les tests sont passés ! Le système EIR francisé est opérationnel."
        echo ""
        echo "🌐 Accès à l'application :"
        echo "  📖 Documentation : http://localhost:8000/docs"
        echo "  🔍 Santé API : http://localhost:8000/verification-etat"
        echo "  🏠 Accueil : http://localhost:8000/"
    else
        log_error "❌ $failed_tests test(s) ont échoué. Veuillez vérifier les erreurs ci-dessus."
        cleanup
        exit 1
    fi
}

# Handle interruption
trap 'echo ""; log_error "Tests interrompus"; cleanup; exit 130' INT

# Run main function
main
