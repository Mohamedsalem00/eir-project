#!/bin/bash

# Script rapide pour les actions courantes sur la base EIR
# Version simplifiée du gestionnaire principal

echo "⚡ Actions Rapides Base EIR"
echo "=========================="

# Configuration base Docker
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="eir_project"
DB_USER="postgres"
DB_PASSWORD="postgres"

# Couleurs
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Fonction SQL via Docker
sql() {
    docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c "$1"
}

# Actions rapides
case "$1" in
    "tables"|"t")
        echo -e "${CYAN}📋 Tables de la base EIR:${NC}"
        sql "SELECT tablename as \"Tables\" FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"
        ;;
    
    "counts"|"c")
        echo -e "${CYAN}📊 Nombre d'enregistrements:${NC}"
        echo "Utilisateurs: $(docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM utilisateur;" | tr -d ' ')"
        echo "Appareils: $(docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM appareil;" | tr -d ' ')"
        echo "IMEIs: $(docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM imei;" | tr -d ' ')"
        echo "SIMs: $(docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM sim;" | tr -d ' ')"
        echo "Recherches: $(docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM recherche;" | tr -d ' ')"
        echo "Notifications: $(docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM notification;" | tr -d ' ')"
        echo "Tac Database: $(docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM tac_database;" | tr -d ' ')"
        echo "Password Reset: $(docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM password_reset;" | tr -d ' ')"
        
        ;;
    
    "users"|"u")
        echo -e "${CYAN}👥 Utilisateurs actifs:${NC}"
        sql "SELECT nom, email, type_utilisateur, niveau_acces FROM utilisateur WHERE est_actif = true ORDER BY nom LIMIT 10;"
        ;;
    
    "devices"|"d")
        echo -e "${CYAN}📱 Top appareils:${NC}"
        sql "SELECT marque, modele, COUNT(i.id) as nb_imeis FROM appareil a LEFT JOIN imei i ON a.id = i.appareil_id GROUP BY a.marque, a.modele ORDER BY nb_imeis DESC LIMIT 10;"
        ;;
    
    "imeis"|"i")
        echo -e "${CYAN}📱 IMEIs récents:${NC}"
        sql "SELECT i.numero_imei, i.statut, a.marque, a.modele FROM imei i LEFT JOIN appareil a ON i.appareil_id = a.id ORDER BY i.numero_imei DESC LIMIT 10;"
        ;;
    
    "search"|"s")
        if [ -z "$2" ]; then
            echo "Usage: ./actions-rapides.sh search <terme>"
            exit 1
        fi
        echo -e "${CYAN}🔍 Recherche IMEI: $2${NC}"
        sql "SELECT i.numero_imei, i.statut, a.marque, a.modele FROM imei i LEFT JOIN appareil a ON i.appareil_id = a.id WHERE i.numero_imei LIKE '%$2%';"
        ;;
    
    "stats"|"st")
        echo -e "${CYAN}📊 Statistiques rapides:${NC}"
        echo "==========================="
        echo "📊 Status IMEI:"
        sql "SELECT statut, COUNT(*) FROM imei GROUP BY statut;"
        echo ""
        echo "📱 Top marques:"
        sql "SELECT marque, COUNT(*) FROM appareil GROUP BY marque ORDER BY COUNT(*) DESC LIMIT 5;"
        ;;
    
    "backup"|"b")
        timestamp=$(date +"%Y%m%d_%H%M%S")
        backup_file="backups/quick_backup_$timestamp.sql"
        mkdir -p backups
        echo -e "${YELLOW}💾 Sauvegarde en cours via Docker...${NC}"
        docker compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" > "$backup_file"
        echo -e "${GREEN}✅ Sauvegarde: $backup_file${NC}"
        ;;
    
    "structure"|"str")
        if [ -z "$2" ]; then
            echo "Usage: ./actions-rapides.sh structure <table>"
            exit 1
        fi
        echo -e "${CYAN}🏗️  Structure de la table: $2${NC}"
        sql "SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '$2' AND table_schema = 'public' ORDER BY ordinal_position;"
        ;;
    
    "show")
        if [ -z "$2" ]; then
            echo "Usage: ./actions-rapides.sh show <table> [limite]"
            exit 1
        fi
        limit=${3:-5}
        echo -e "${CYAN}📄 Contenu de $2 (limit: $limit):${NC}"
        sql "SELECT * FROM $2 LIMIT $limit;"
        ;;
    
    "help"|"h"|"")
        echo "🚀 Actions rapides disponibles:"
        echo "==============================="
        echo "  tables, t        - Lister toutes les tables"
        echo "  counts, c        - Compter les enregistrements"
        echo "  users, u         - Voir les utilisateurs"
        echo "  devices, d       - Top appareils"
        echo "  imeis, i         - IMEIs récents"
        echo "  search, s <term> - Rechercher un IMEI"
        echo "  stats, st        - Statistiques rapides"
        echo "  backup, b        - Sauvegarde rapide"
        echo "  structure, str <table> - Structure d'une table"
        echo "  show <table> [n] - Afficher contenu (défaut: 5 lignes)"
        echo "  help, h          - Cette aide"
        echo ""
        echo "Exemples:"
        echo "  ./actions-rapides.sh tables"
        echo "  ./actions-rapides.sh search 352745"
        echo "  ./actions-rapides.sh show users 10"
        echo "  ./actions-rapides.sh structure devices"
        ;;
    
    *)
        echo "❌ Action inconnue: $1"
        echo "Tapez './actions-rapides.sh help' pour voir les options"
        exit 1
        ;;
esac
