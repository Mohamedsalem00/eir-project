#!/bin/bash
# scripts/manage-eir.sh
# Main management script for EIR project

set -e

# Navigate to project root
cd "$(dirname "$0")/.."

# Source Docker utilities
source scripts/docker-utils.sh

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${CYAN}${BOLD}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    🏗️  GESTIONNAIRE EIR 🏗️                    ║"
    echo "║              Système de Gestion des Conteneurs              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_menu() {
    echo -e "${BOLD}📋 Options disponibles :${NC}"
    echo ""
    echo -e "${GREEN}🔄 CONTENEURS :${NC}"
    echo "  1) Reconstruire complètement les conteneurs"
    echo "  2) Redémarrer les conteneurs existants"
    echo "  3) Redémarrer un service spécifique (web/db)"
    echo ""
    echo -e "${BLUE}🗄️  BASE DE DONNÉES :${NC}"
    echo "  4) Reconstruire complètement la base de données"
    echo "  5) Réinitialiser rapidement la base de données"
    echo ""
    echo -e "${YELLOW}📊 STATUT & TESTS :${NC}"
    echo "  6) Afficher le statut des services"
    echo "  7) Tester l'API francisée"
    echo "  8) Voir les logs des services"
    echo "  9) Lancer les tests complets du système"
    echo ""
    echo -e "${CYAN}🛠️  UTILITAIRES :${NC}"
    echo " 10) Nettoyer les ressources Docker"
    echo " 11) Sauvegarder la base de données"
    echo " 12) Restaurer une sauvegarde"
    echo ""
    echo -e "${RED}❌ SORTIE :${NC}"
    echo "  0) Quitter"
    echo ""
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

# Function to check Docker status and permissions
check_docker_status() {
    echo "🔍 Vérification de Docker et configuration des permissions..."
    setup_docker_commands
    echo -e "${GREEN}✅ Docker configuré et prêt${NC}"
}

# Function to show service status
show_status() {
    echo -e "${BOLD}📊 Statut des services EIR :${NC}"
    echo ""
    
    # Check Docker
    if run_docker info > /dev/null 2>&1; then
        log_success "Docker : Opérationnel"
    else
        log_error "Docker : Non disponible"
        return 1
    fi
    
    # Check containers
    if run_docker_compose ps -q | grep -q .; then
        echo ""
        echo "📦 Conteneurs :"
        run_docker_compose ps
        
        # Check database
        echo ""
        if run_docker_compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
            log_success "Base de données : Accessible"
            
            # Count tables and data
            local table_count user_count
            table_count=$(run_docker_compose exec -T db psql -U postgres -d imei_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' \n' || echo "0")
            user_count=$(run_docker_compose exec -T db psql -U postgres -d imei_db -t -c "SELECT COUNT(*) FROM Utilisateur;" 2>/dev/null | tr -d ' \n' || echo "0")
            
            echo "  └─ Tables : $table_count"
            echo "  └─ Utilisateurs : $user_count"
        else
            log_error "Base de données : Non accessible"
        fi
        
        # Check API
        echo ""
        if curl -s -f http://localhost:8000/verification-etat > /dev/null 2>&1; then
            log_success "API : Opérationnelle (http://localhost:8000)"
        else
            log_warning "API : Non accessible"
        fi
        
    else
        log_warning "Aucun conteneur en cours d'exécution"
    fi
    
    echo ""
    echo "📍 Points d'accès :"
    echo "  🌐 Documentation : http://localhost:8000/docs"
    echo "  🔍 Santé API : http://localhost:8000/verification-etat"
    echo "  🏠 Accueil : http://localhost:8000/"
}

# Function to test francized API
test_francized_api() {
    echo -e "${BOLD}🧪 Test de l'API francisée :${NC}"
    echo ""
    
    if ! curl -s -f http://localhost:8000/verification-etat > /dev/null 2>&1; then
        log_error "API non accessible. Démarrez les conteneurs d'abord."
        return 1
    fi
    
    echo "1. Test endpoint de santé francisé :"
    curl -s http://localhost:8000/verification-etat | jq '.' 2>/dev/null || curl -s http://localhost:8000/verification-etat
    
    echo ""
    echo "2. Test langues supportées :"
    curl -s http://localhost:8000/langues | jq '.langues_supportees' 2>/dev/null || curl -s http://localhost:8000/langues
    
    echo ""
    echo "3. Test recherche IMEI (si données présentes) :"
    curl -s http://localhost:8000/imei/352745080123456 | jq '.' 2>/dev/null || curl -s http://localhost:8000/imei/352745080123456
    
    echo ""
    log_success "Test de l'API francisée terminé"
}

# Function to show logs
show_logs() {
    echo -e "${BOLD}📝 Logs des services :${NC}"
    echo ""
    echo "Quel service voulez-vous consulter ?"
    echo "1) Web (API)"
    echo "2) Base de données"
    echo "3) Tous les services"
    echo "4) Retour au menu principal"
    echo ""
    read -p "Votre choix (1-4) : " log_choice
    
    case $log_choice in
        1)
            echo ""
            log_info "Logs du service web (dernières 50 lignes) :"
            run_docker_compose logs --tail=50 web
            ;;
        2)
            echo ""
            log_info "Logs de la base de données (dernières 50 lignes) :"
            run_docker_compose logs --tail=50 db
            ;;
        3)
            echo ""
            log_info "Logs de tous les services (dernières 30 lignes) :"
            run_docker_compose logs --tail=30
            ;;
        4)
            return 0
            ;;
        *)
            log_error "Choix invalide"
            ;;
    esac
}

# Function to clean Docker resources
clean_docker() {
    echo -e "${BOLD}🧹 Nettoyage des ressources Docker :${NC}"
    echo ""
    log_warning "Cette opération va supprimer :"
    echo "  - Les conteneurs arrêtés"
    echo "  - Les images non utilisées"
    echo "  - Les volumes non utilisés"
    echo "  - Les réseaux non utilisés"
    echo ""
    read -p "Continuer ? (o/N) : " confirm
    
    if [[ "$confirm" =~ ^[Oo]$ ]]; then
        log_info "Nettoyage en cours..."
        run_docker system prune -f
        run_docker volume prune -f
        log_success "Nettoyage terminé"
    else
        log_info "Nettoyage annulé"
    fi
}

# Function to backup database
backup_database() {
    echo -e "${BOLD}💾 Sauvegarde de la base de données :${NC}"
    echo ""
    
    if ! run_docker_compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
        log_error "Base de données non accessible"
        return 1
    fi
    
    local backup_dir="backups"
    local backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    mkdir -p "$backup_dir"
    
    log_info "Création de la sauvegarde..."
    if run_docker_compose exec -T db pg_dump -U postgres imei_db > "$backup_dir/$backup_file"; then
        log_success "Sauvegarde créée : $backup_dir/$backup_file"
        echo "Taille : $(du -h "$backup_dir/$backup_file" | cut -f1)"
    else
        log_error "Échec de la sauvegarde"
        return 1
    fi
}

# Function to restore database
restore_database() {
    echo -e "${BOLD}📥 Restauration de la base de données :${NC}"
    echo ""
    
    local backup_dir="backups"
    
    if [[ ! -d "$backup_dir" ]]; then
        log_error "Aucun dossier de sauvegarde trouvé"
        return 1
    fi
    
    echo "Sauvegardes disponibles :"
    local backups=($(ls -1t "$backup_dir"/*.sql 2>/dev/null || true))
    
    if [[ ${#backups[@]} -eq 0 ]]; then
        log_error "Aucune sauvegarde trouvée"
        return 1
    fi
    
    for i in "${!backups[@]}"; do
        echo "$((i+1))) $(basename "${backups[$i]}")"
    done
    
    echo ""
    read -p "Choisir une sauvegarde (numéro) : " backup_choice
    
    if [[ "$backup_choice" =~ ^[0-9]+$ ]] && [[ "$backup_choice" -ge 1 ]] && [[ "$backup_choice" -le ${#backups[@]} ]]; then
        local selected_backup="${backups[$((backup_choice-1))]}"
        
        log_warning "Cette opération va remplacer toutes les données actuelles"
        read -p "Continuer ? (o/N) : " confirm
        
        if [[ "$confirm" =~ ^[Oo]$ ]]; then
            log_info "Restauration en cours..."
            if run_docker_compose exec -T db psql -U postgres -d imei_db < "$selected_backup"; then
                log_success "Restauration terminée"
            else
                log_error "Échec de la restauration"
                return 1
            fi
        else
            log_info "Restauration annulée"
        fi
    else
        log_error "Choix invalide"
    fi
}

# Function to handle service-specific restart
restart_specific_service() {
    echo -e "${BOLD}🔄 Redémarrage d'un service spécifique :${NC}"
    echo ""
    echo "Quel service voulez-vous redémarrer ?"
    echo "1) Service web (API)"
    echo "2) Base de données"
    echo "3) Retour au menu principal"
    echo ""
    read -p "Votre choix (1-3) : " service_choice
    
    case $service_choice in
        1)
            log_info "Redémarrage du service web..."
            ./scripts/restart-containers.sh --service web
            ;;
        2)
            log_info "Redémarrage de la base de données..."
            ./scripts/restart-containers.sh --service db
            ;;
        3)
            return 0
            ;;
        *)
            log_error "Choix invalide"
            ;;
    esac
}

# Main menu loop
main() {
    print_header
    
    # Check Docker availability
    check_docker_status
    
    while true; do
        echo ""
        print_menu
        read -p "Votre choix (0-12) : " choice
        echo ""
        
        case $choice in
            1)
                log_info "Lancement de la reconstruction complète des conteneurs..."
                ./scripts/rebuild-containers.sh
                ;;
            2)
                log_info "Redémarrage des conteneurs..."
                ./scripts/restart-containers.sh
                ;;
            3)
                restart_specific_service
                ;;
            4)
                log_info "Lancement de la reconstruction de la base de données..."
                ./scripts/rebuild-database.sh
                ;;
            5)
                log_info "Réinitialisation rapide de la base de données..."
                ./scripts/reset-database.sh
                ;;
            6)
                show_status
                ;;
            7)
                test_francized_api
                ;;
            8)
                show_logs
                ;;
            9)
                log_info "Lancement des tests complets du système..."
                ./scripts/test-system.sh
                ;;
            10)
                clean_docker
                ;;
            11)
                backup_database
                ;;
            12)
                restore_database
                ;;
            0)
                echo -e "${GREEN}👋 Au revoir !${NC}"
                exit 0
                ;;
            *)
                log_error "Choix invalide. Veuillez choisir entre 0 et 12."
                ;;
        esac
        
        echo ""
        read -p "Appuyez sur Entrée pour continuer..."
    done
}

# Handle interruption
trap 'echo ""; log_error "Processus interrompu"; exit 130' INT

# Run main function
main
