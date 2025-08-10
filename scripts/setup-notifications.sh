#!/bin/bash

# Script de configuration automatique du système de notifications EIR
# Usage: ./setup-notifications.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔔 Configuration du système de notifications EIR${NC}"
echo "=================================================="

# Fonction pour afficher les messages
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Vérifier les prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 n'est pas installé"
        exit 1
    fi
    log_success "Python 3 trouvé : $(python3 --version)"
    
    # pip
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        log_error "pip n'est pas installé"
        exit 1
    fi
    log_success "pip trouvé"
    
    # PostgreSQL (optionnel)
    if command -v psql &> /dev/null; then
        log_success "PostgreSQL trouvé"
    else
        log_warning "PostgreSQL non trouvé - vous devrez le configurer manuellement"
    fi
    
    # curl (pour les tests)
    if ! command -v curl &> /dev/null; then
        log_warning "curl non trouvé - les tests automatiques ne fonctionneront pas"
    else
        log_success "curl trouvé"
    fi
    
    echo ""
}

# Configuration de l'environnement
setup_environment() {
    log_info "Configuration de l'environnement..."
    
    # Créer le répertoire backend s'il n'existe pas
    if [ ! -d "$BACKEND_DIR" ]; then
        log_error "Répertoire backend non trouvé : $BACKEND_DIR"
        exit 1
    fi
    
    # Créer le fichier .env s'il n'existe pas
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        if [ -f "$BACKEND_DIR/.env.example" ]; then
            log_info "Copie du fichier .env.example vers .env..."
            cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
            log_success "Fichier .env créé"
        else
            log_warning "Fichier .env.example non trouvé - création d'un .env basique..."
            create_basic_env
        fi
    else
        log_success "Fichier .env existe déjà"
    fi
    
    # Créer le répertoire des logs
    if [ ! -d "$BACKEND_DIR/logs" ]; then
        mkdir -p "$BACKEND_DIR/logs"
        log_success "Répertoire logs créé"
    fi
    
    echo ""
}

# Créer un fichier .env basique
create_basic_env() {
    cat > "$BACKEND_DIR/.env" << 'EOF'
# Configuration de base pour les notifications EIR
DATABASE_URL=postgresql://user:password@localhost:5432/eir_project

# Configuration email (Gmail - à personnaliser)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_USER=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe-app

# Mode développement
EMAIL_TEST_MODE=true
SMS_TEST_MODE=true
NOTIFICATIONS_MODE=development
SMS_PROVIDER=console

# Scheduler
SCHEDULER_ENABLED=true
SCHEDULER_INTERVAL_MINUTES=5

# Logs
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/notifications.log
EOF
    log_success "Fichier .env basique créé"
}

# Installation des dépendances Python
install_dependencies() {
    log_info "Installation des dépendances Python..."
    
    cd "$BACKEND_DIR"
    
    if [ -f "requirements.txt" ]; then
        # Vérifier si APScheduler est déjà dans requirements.txt
        if ! grep -q "APScheduler" requirements.txt; then
            log_info "Ajout des nouvelles dépendances à requirements.txt..."
            # Sauvegarder l'original
            cp requirements.txt requirements.txt.bak
            
            # Ajouter les nouvelles dépendances
            cat >> requirements.txt << 'EOF'

# Nouvelles dépendances pour les notifications
APScheduler>=3.10.0
PyYAML>=6.0
aiofiles>=23.0.0
python-multipart>=0.0.6

# Dépendances optionnelles pour SMS
# twilio>=8.0.0  # Décommentez pour Twilio
# boto3>=1.26.0  # Décommentez pour AWS SNS
EOF
            log_success "Dépendances ajoutées à requirements.txt"
        fi
        
        # Installer les dépendances
        log_info "Installation en cours..."
        if pip3 install -r requirements.txt; then
            log_success "Dépendances installées avec succès"
        else
            log_error "Erreur lors de l'installation des dépendances"
            exit 1
        fi
    else
        log_error "Fichier requirements.txt non trouvé"
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    echo ""
}

# Configuration de la base de données
setup_database() {
    log_info "Configuration de la base de données..."
    
    if [ -f "$BACKEND_DIR/schema_postgres.sql" ]; then
        log_info "Schéma de base de données trouvé"
        
        # Demander si l'utilisateur veut appliquer le schéma
        read -p "Voulez-vous appliquer le schéma de base de données maintenant ? [y/N] " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # Essayer d'appliquer le schéma
            if command -v psql &> /dev/null; then
                read -p "Nom de la base de données [eir_project]: " db_name
                db_name=${db_name:-eir_project}
                
                if psql -d "$db_name" -f "$BACKEND_DIR/schema_postgres.sql" 2>/dev/null; then
                    log_success "Schéma appliqué avec succès"
                else
                    log_warning "Impossible d'appliquer le schéma automatiquement"
                    log_info "Appliquez-le manuellement avec : psql -d $db_name -f $BACKEND_DIR/schema_postgres.sql"
                fi
            else
                log_warning "psql non trouvé - appliquez le schéma manuellement"
            fi
        else
            log_info "Schéma non appliqué - appliquez-le manuellement plus tard"
        fi
    else
        log_warning "Schéma de base de données non trouvé"
    fi
    
    echo ""
}

# Configuration email interactive
configure_email() {
    log_info "Configuration de l'email..."
    
    echo "Choisissez votre provider email :"
    echo "1) Gmail (recommandé pour débuter)"
    echo "2) Outlook/Hotmail"
    echo "3) SendGrid (production)"
    echo "4) Configuration personnalisée"
    echo "5) Ignorer pour l'instant"
    
    read -p "Votre choix [1]: " email_choice
    email_choice=${email_choice:-1}
    
    case $email_choice in
        1)
            configure_gmail
            ;;
        2)
            configure_outlook
            ;;
        3)
            configure_sendgrid
            ;;
        4)
            configure_custom_email
            ;;
        5)
            log_info "Configuration email ignorée"
            ;;
        *)
            log_warning "Choix invalide - configuration email ignorée"
            ;;
    esac
    
    echo ""
}

# Configuration Gmail
configure_gmail() {
    log_info "Configuration Gmail..."
    
    read -p "Votre adresse Gmail : " gmail_user
    if [ -n "$gmail_user" ]; then
        # Mettre à jour le fichier .env
        sed -i "s/EMAIL_USER=.*/EMAIL_USER=$gmail_user/" "$BACKEND_DIR/.env"
        
        log_success "Adresse Gmail configurée"
        log_warning "IMPORTANT : Vous devez :"
        echo "  1. Activer l'authentification à 2 facteurs sur votre compte Gmail"
        echo "  2. Générer un mot de passe d'application : https://myaccount.google.com/security"
        echo "  3. Mettre à jour EMAIL_PASSWORD dans $BACKEND_DIR/.env"
    fi
}

# Configuration Outlook
configure_outlook() {
    log_info "Configuration Outlook..."
    
    read -p "Votre adresse Outlook/Hotmail : " outlook_user
    if [ -n "$outlook_user" ]; then
        # Mettre à jour le fichier .env
        sed -i "s/SMTP_SERVER=.*/SMTP_SERVER=smtp-mail.outlook.com/" "$BACKEND_DIR/.env"
        sed -i "s/EMAIL_USER=.*/EMAIL_USER=$outlook_user/" "$BACKEND_DIR/.env"
        
        log_success "Configuration Outlook mise à jour"
        log_warning "Mettez à jour EMAIL_PASSWORD dans $BACKEND_DIR/.env"
    fi
}

# Configuration SendGrid
configure_sendgrid() {
    log_info "Configuration SendGrid..."
    
    read -p "Votre clé API SendGrid : " sendgrid_key
    if [ -n "$sendgrid_key" ]; then
        # Mettre à jour le fichier .env
        sed -i "s/SMTP_SERVER=.*/SMTP_SERVER=smtp.sendgrid.net/" "$BACKEND_DIR/.env"
        sed -i "s/EMAIL_USER=.*/EMAIL_USER=apikey/" "$BACKEND_DIR/.env"
        sed -i "s/EMAIL_PASSWORD=.*/EMAIL_PASSWORD=$sendgrid_key/" "$BACKEND_DIR/.env"
        
        log_success "Configuration SendGrid mise à jour"
    fi
}

# Configuration email personnalisée
configure_custom_email() {
    log_info "Configuration email personnalisée..."
    
    read -p "Serveur SMTP : " smtp_server
    read -p "Port SMTP [587]: " smtp_port
    smtp_port=${smtp_port:-587}
    read -p "Utiliser TLS ? [y/N]: " use_tls
    read -p "Nom d'utilisateur : " email_user
    
    if [ -n "$smtp_server" ] && [ -n "$email_user" ]; then
        sed -i "s/SMTP_SERVER=.*/SMTP_SERVER=$smtp_server/" "$BACKEND_DIR/.env"
        sed -i "s/SMTP_PORT=.*/SMTP_PORT=$smtp_port/" "$BACKEND_DIR/.env"
        sed -i "s/EMAIL_USER=.*/EMAIL_USER=$email_user/" "$BACKEND_DIR/.env"
        
        if [[ $use_tls =~ ^[Yy]$ ]]; then
            sed -i "s/EMAIL_USE_TLS=.*/EMAIL_USE_TLS=true/" "$BACKEND_DIR/.env"
        else
            sed -i "s/EMAIL_USE_TLS=.*/EMAIL_USE_TLS=false/" "$BACKEND_DIR/.env"
        fi
        
        log_success "Configuration email personnalisée mise à jour"
        log_warning "N'oubliez pas de mettre à jour EMAIL_PASSWORD"
    fi
}

# Rendre les scripts exécutables
setup_scripts() {
    log_info "Configuration des scripts..."
    
    # Scripts de test
    if [ -f "$PROJECT_ROOT/scripts/test-notifications.sh" ]; then
        chmod +x "$PROJECT_ROOT/scripts/test-notifications.sh"
        log_success "Script test-notifications.sh rendu exécutable"
    fi
    
    if [ -f "$PROJECT_ROOT/scripts/test-eir-notifications.sh" ]; then
        chmod +x "$PROJECT_ROOT/scripts/test-eir-notifications.sh"
        log_success "Script test-eir-notifications.sh rendu exécutable"
    fi
    
    # Ce script lui-même
    chmod +x "$0"
    
    echo ""
}

# Test de configuration
test_configuration() {
    log_info "Test de la configuration..."
    
    read -p "Voulez-vous tester la configuration maintenant ? [y/N] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Démarrage du backend pour les tests..."
        
        # Démarrer temporairement le backend en arrière-plan
        cd "$BACKEND_DIR"
        python3 -c "
import sys
sys.path.append('.')
try:
    from app.main import app
    print('✅ Import de l\'application réussi')
except Exception as e:
    print(f'❌ Erreur d\'import: {e}')
    sys.exit(1)
" || {
            log_error "Impossible de démarrer l'application - vérifiez la configuration"
            return 1
        }
        
        log_success "Configuration semble correcte"
        
        # Si curl est disponible et le backend peut démarrer
        if command -v curl &> /dev/null; then
            log_info "Pour tester complètement, démarrez le backend avec :"
            echo "  cd $BACKEND_DIR && uvicorn app.main:app --reload"
            log_info "Puis exécutez :"
            echo "  $PROJECT_ROOT/scripts/test-eir-notifications.sh --basic"
        fi
        
        cd "$PROJECT_ROOT"
    fi
    
    echo ""
}

# Affichage du résumé final
show_summary() {
    log_success "Configuration terminée !"
    echo ""
    echo "📋 Résumé de la configuration :"
    echo "  ✅ Environnement configuré"
    echo "  ✅ Dépendances installées"
    echo "  ✅ Scripts configurés"
    echo ""
    echo "🚀 Étapes suivantes :"
    echo ""
    echo "1. Personnalisez votre configuration :"
    echo "   nano $BACKEND_DIR/.env"
    echo ""
    echo "2. Appliquez le schéma de base de données si ce n'est pas fait :"
    echo "   psql -d eir_project -f $BACKEND_DIR/schema_postgres.sql"
    echo ""
    echo "3. Démarrez le backend :"
    echo "   cd $BACKEND_DIR && uvicorn app.main:app --reload"
    echo ""
    echo "4. Testez les notifications :"
    echo "   $PROJECT_ROOT/scripts/test-eir-notifications.sh"
    echo ""
    echo "📚 Documentation :"
    echo "   - Guide rapide : $PROJECT_ROOT/NOTIFICATIONS_QUICK_START.md"
    echo "   - Documentation complète : $PROJECT_ROOT/NOTIFICATIONS_SYSTEM.md"
    echo "   - API : http://localhost:8000/docs (une fois le backend démarré)"
    echo ""
    log_success "Système de notifications EIR prêt ! 🔔"
}

# Fonction principale
main() {
    echo "Ce script va configurer automatiquement le système de notifications EIR."
    echo ""
    
    read -p "Continuer ? [Y/n] " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "Configuration annulée"
        exit 0
    fi
    
    check_prerequisites
    setup_environment
    install_dependencies
    setup_database
    configure_email
    setup_scripts
    test_configuration
    show_summary
}

# Gestion des arguments
case "$1" in
    --help|-h)
        echo "Configuration automatique du système de notifications EIR"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options :"
        echo "  --help, -h     Afficher cette aide"
        echo "  --env-only     Configurer uniquement l'environnement"
        echo "  --deps-only    Installer uniquement les dépendances"
        echo "  --db-only      Configurer uniquement la base de données"
        echo ""
        exit 0
        ;;
    --env-only)
        setup_environment
        ;;
    --deps-only)
        check_prerequisites
        install_dependencies
        ;;
    --db-only)
        setup_database
        ;;
    *)
        main
        ;;
esac
