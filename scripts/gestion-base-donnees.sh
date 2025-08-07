#!/bin/bash

# Script de gestion de la base de données EIR
# Permet d'explorer, manipuler et administrer la base PostgreSQL

echo "🗄️  Gestionnaire de Base de Données EIR"
echo "========================================"

# Couleurs pour l'interface
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration de la base de données Docker
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="imei_db"
DB_USER="postgres"
DB_PASSWORD="postgres"

# Fonction pour exécuter une requête SQL via Docker
execute_sql() {
    local query="$1"
    local show_headers="${2:-true}"
    
    if [ "$show_headers" = "true" ]; then
        docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c "$query"
    else
        docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -t -c "$query"
    fi
}

# Fonction pour vérifier la connexion Docker
check_connection() {
    echo -n "🔌 Vérification du conteneur PostgreSQL... "
    if docker compose ps db | grep -q "running"; then
        if execute_sql "SELECT 1;" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ CONNECTÉ${NC}"
            return 0
        else
            echo -e "${RED}❌ ERREUR SQL${NC}"
            echo "Le conteneur est en marche mais la base n'est pas accessible"
            return 1
        fi
    else
        echo -e "${RED}❌ CONTENEUR ARRÊTÉ${NC}"
        echo "Démarrez les conteneurs avec: docker compose up -d"
        return 1
    fi
}

# Fonction pour afficher toutes les tables
show_all_tables() {
    echo -e "\n${CYAN}📋 Tables disponibles dans la base EIR:${NC}"
    echo "======================================"
    
    execute_sql "
    SELECT 
        schemaname as \"Schéma\",
        tablename as \"Nom de la Table\",
        tableowner as \"Propriétaire\"
    FROM pg_tables 
    WHERE schemaname = 'public' 
    ORDER BY tablename;"
}

# Fonction pour compter les enregistrements de chaque table
show_table_counts() {
    echo -e "\n${CYAN}📊 Nombre d'enregistrements par table:${NC}"
    echo "====================================="
    
    tables=($(execute_sql "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;" false | tr -d ' '))
    
    for table in "${tables[@]}"; do
        if [ ! -z "$table" ]; then
            count=$(execute_sql "SELECT COUNT(*) FROM $table;" false | tr -d ' ')
            printf "%-20s: %s enregistrements\n" "$table" "$count"
        fi
    done
}

# Fonction pour afficher la structure d'une table
show_table_structure() {
    echo -e "\n${YELLOW}📝 Entrez le nom de la table à analyser:${NC}"
    read -p "Table: " table_name
    
    if [ -z "$table_name" ]; then
        echo -e "${RED}❌ Nom de table requis${NC}"
        return
    fi
    
    echo -e "\n${CYAN}🏗️  Structure de la table '$table_name':${NC}"
    echo "=================================="
    
    execute_sql "
    SELECT 
        column_name as \"Colonne\",
        data_type as \"Type\",
        is_nullable as \"NULL?\",
        column_default as \"Défaut\"
    FROM information_schema.columns 
    WHERE table_name = '$table_name' 
    AND table_schema = 'public'
    ORDER BY ordinal_position;"
}

# Fonction pour afficher le contenu d'une table
show_table_data() {
    echo -e "\n${YELLOW}📝 Entrez le nom de la table à consulter:${NC}"
    read -p "Table: " table_name
    
    if [ -z "$table_name" ]; then
        echo -e "${RED}❌ Nom de table requis${NC}"
        return
    fi
    
    echo -e "\n${YELLOW}📝 Nombre de lignes à afficher (défaut: 10):${NC}"
    read -p "Limite: " limit
    limit=${limit:-10}
    
    echo -e "\n${CYAN}📄 Contenu de la table '$table_name' (limite: $limit):${NC}"
    echo "================================================"
    
    execute_sql "SELECT * FROM $table_name LIMIT $limit;"
}

# Fonction pour rechercher dans les données
search_data() {
    echo -e "\n${YELLOW}🔍 Recherche dans les données${NC}"
    echo "============================"
    
    echo "1️⃣  Recherche par IMEI"
    echo "2️⃣  Recherche par utilisateur"
    echo "3️⃣  Recherche par appareil"
    echo "4️⃣  Recherche personnalisée"
    
    read -p "Choix: " search_choice
    
    case $search_choice in
        1)
            echo -e "\n${YELLOW}📱 Entrez l'IMEI à rechercher:${NC}"
            read -p "IMEI: " imei
            if [ ! -z "$imei" ]; then
                echo -e "\n${CYAN}🔍 Résultats pour IMEI: $imei${NC}"
                execute_sql "
                SELECT 
                    i.imei,
                    i.status,
                    d.brand,
                    d.model,
                    i.created_at
                FROM imeis i
                LEFT JOIN devices d ON i.device_id = d.id
                WHERE i.imei LIKE '%$imei%';"
            fi
            ;;
        2)
            echo -e "\n${YELLOW}👤 Entrez le nom d'utilisateur:${NC}"
            read -p "Utilisateur: " username
            if [ ! -z "$username" ]; then
                echo -e "\n${CYAN}🔍 Résultats pour utilisateur: $username${NC}"
                execute_sql "
                SELECT 
                    u.username,
                    u.email,
                    u.role,
                    u.created_at,
                    u.is_active
                FROM users u
                WHERE u.username LIKE '%$username%' OR u.email LIKE '%$username%';"
            fi
            ;;
        3)
            echo -e "\n${YELLOW}📱 Entrez la marque ou modèle:${NC}"
            read -p "Appareil: " device
            if [ ! -z "$device" ]; then
                echo -e "\n${CYAN}🔍 Résultats pour appareil: $device${NC}"
                execute_sql "
                SELECT 
                    d.brand,
                    d.model,
                    d.tac,
                    COUNT(i.id) as nb_imeis
                FROM devices d
                LEFT JOIN imeis i ON d.id = i.device_id
                WHERE d.brand ILIKE '%$device%' OR d.model ILIKE '%$device%'
                GROUP BY d.id, d.brand, d.model, d.tac
                ORDER BY nb_imeis DESC;"
            fi
            ;;
        4)
            echo -e "\n${YELLOW}💻 Entrez votre requête SQL:${NC}"
            read -p "SQL: " custom_sql
            if [ ! -z "$custom_sql" ]; then
                echo -e "\n${CYAN}🔍 Résultats de la requête personnalisée:${NC}"
                execute_sql "$custom_sql"
            fi
            ;;
    esac
}

# Fonction pour afficher les statistiques
show_statistics() {
    echo -e "\n${CYAN}📊 Statistiques de la base EIR:${NC}"
    echo "==============================="
    
    echo -e "\n${WHITE}👥 Utilisateurs:${NC}"
    execute_sql "
    SELECT 
        role as \"Rôle\",
        COUNT(*) as \"Nombre\",
        COUNT(CASE WHEN is_active THEN 1 END) as \"Actifs\"
    FROM users 
    GROUP BY role 
    ORDER BY COUNT(*) DESC;"
    
    echo -e "\n${WHITE}📱 Appareils:${NC}"
    execute_sql "
    SELECT 
        brand as \"Marque\",
        COUNT(*) as \"Modèles\"
    FROM devices 
    GROUP BY brand 
    ORDER BY COUNT(*) DESC 
    LIMIT 10;"
    
    echo -e "\n${WHITE}📋 Status IMEI:${NC}"
    execute_sql "
    SELECT 
        status as \"Status\",
        COUNT(*) as \"Nombre\"
    FROM imeis 
    GROUP BY status 
    ORDER BY COUNT(*) DESC;"
    
    echo -e "\n${WHITE}🔍 Recherches récentes:${NC}"
    execute_sql "
    SELECT 
        DATE(created_at) as \"Date\",
        COUNT(*) as \"Recherches\"
    FROM search_history 
    WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    GROUP BY DATE(created_at) 
    ORDER BY DATE(created_at) DESC;"
}

# Fonction pour sauvegarder la base via Docker
backup_database() {
    echo -e "\n${YELLOW}💾 Sauvegarde de la base de données${NC}"
    echo "=================================="
    
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backups/backup_eir_$timestamp.sql"
    
    echo "Création de la sauvegarde via Docker..."
    mkdir -p backups
    
    docker compose exec -T db pg_dump -U "$DB_USER" -d "$DB_NAME" > "$backup_file"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Sauvegarde créée: $backup_file${NC}"
        echo "Taille: $(du -h "$backup_file" | cut -f1)"
    else
        echo -e "${RED}❌ Erreur lors de la sauvegarde${NC}"
    fi
}

# Fonction pour restaurer la base via Docker
restore_database() {
    echo -e "\n${YELLOW}📥 Restauration de la base de données${NC}"
    echo "===================================="
    
    echo "Fichiers de sauvegarde disponibles:"
    ls -la backups/*.sql 2>/dev/null || echo "Aucune sauvegarde trouvée"
    
    echo -e "\n${YELLOW}📝 Entrez le nom du fichier de sauvegarde:${NC}"
    read -p "Fichier: " backup_file
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}❌ Fichier non trouvé${NC}"
        return
    fi
    
    echo -e "${RED}⚠️  ATTENTION: Cette opération va remplacer toutes les données!${NC}"
    read -p "Confirmez-vous? (oui/non): " confirm
    
    if [ "$confirm" = "oui" ]; then
        echo "Restauration en cours via Docker..."
        docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" < "$backup_file"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Restauration terminée${NC}"
        else
            echo -e "${RED}❌ Erreur lors de la restauration${NC}"
        fi
    else
        echo "Restauration annulée"
    fi
}

# Fonction pour nettoyer les données
cleanup_data() {
    echo -e "\n${YELLOW}🧹 Nettoyage des données${NC}"
    echo "========================"
    
    echo "1️⃣  Supprimer les recherches anciennes (>30 jours)"
    echo "2️⃣  Supprimer les sessions expirées"
    echo "3️⃣  Nettoyer les logs anciens"
    echo "4️⃣  Optimiser la base (VACUUM)"
    
    read -p "Choix: " cleanup_choice
    
    case $cleanup_choice in
        1)
            echo "Suppression des recherches anciennes..."
            result=$(execute_sql "DELETE FROM search_history WHERE created_at < CURRENT_DATE - INTERVAL '30 days';" false)
            echo -e "${GREEN}✅ Recherches anciennes supprimées${NC}"
            ;;
        2)
            echo "Suppression des sessions expirées..."
            result=$(execute_sql "DELETE FROM user_sessions WHERE expires_at < NOW();" false)
            echo -e "${GREEN}✅ Sessions expirées supprimées${NC}"
            ;;
        3)
            echo "Nettoyage des logs anciens..."
            result=$(execute_sql "DELETE FROM audit_logs WHERE created_at < CURRENT_DATE - INTERVAL '90 days';" false)
            echo -e "${GREEN}✅ Logs anciens supprimés${NC}"
            ;;
        4)
            echo "Optimisation de la base..."
            execute_sql "VACUUM ANALYZE;"
            echo -e "${GREEN}✅ Base optimisée${NC}"
            ;;
    esac
}

# Menu principal
show_menu() {
    echo -e "\n${WHITE}📋 MENU PRINCIPAL${NC}"
    echo "================="
    echo "1️⃣   Afficher toutes les tables"
    echo "2️⃣   Compter les enregistrements"
    echo "3️⃣   Structure d'une table"
    echo "4️⃣   Contenu d'une table"
    echo "5️⃣   Rechercher dans les données"
    echo "6️⃣   Statistiques générales"
    echo "7️⃣   Sauvegarder la base"
    echo "8️⃣   Restaurer la base"
    echo "9️⃣   Nettoyer les données"
    echo "0️⃣   Quitter"
    echo ""
}

# Boucle principale
main() {
    # Vérification de la connexion
    if ! check_connection; then
        exit 1
    fi
    
    while true; do
        show_menu
        read -p "Votre choix: " choice
        
        case $choice in
            1) show_all_tables ;;
            2) show_table_counts ;;
            3) show_table_structure ;;
            4) show_table_data ;;
            5) search_data ;;
            6) show_statistics ;;
            7) backup_database ;;
            8) restore_database ;;
            9) cleanup_data ;;
            0) 
                echo -e "\n${GREEN}👋 Au revoir!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Choix invalide${NC}"
                ;;
        esac
        
        echo -e "\n${YELLOW}Appuyez sur Entrée pour continuer...${NC}"
        read
    done
}

# Démarrage du script
main
