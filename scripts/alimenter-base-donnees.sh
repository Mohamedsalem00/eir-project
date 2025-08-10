#!/bin/bash
# scripts/alimenter-base-donnees.sh
# Script pour alimenter la base de données EIR avec des données personnalisées

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

echo "🗃️ Script d'Alimentation de la Base de Données EIR"
echo "================================================="

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    log_error "Docker n'est pas en cours d'exécution. Veuillez démarrer Docker."
    exit 1
fi

# Check if containers are running
if ! docker compose ps | grep -q "Up"; then
    log_warning "Les conteneurs ne sont pas démarrés. Démarrage..."
    docker compose up -d
    sleep 10
fi

log_info "Vérification de l'état des conteneurs..."
docker compose ps

# Function to load test data
load_test_data() {
    log_info "Chargement des données de test..."
    
    # Copy test data file to container
    docker compose cp backend/test_data.sql db:/tmp/test_data.sql
    
    # Execute the SQL file
    docker compose exec db psql -U postgres -d eir_project -f /tmp/test_data.sql
    
    log_success "Données de test chargées avec succès"
}

# Function to load custom CSV data
load_csv_data() {
    local csv_file="$1"
    
    if [[ ! -f "$csv_file" ]]; then
        log_error "Fichier CSV non trouvé: $csv_file"
        return 1
    fi
    
    log_info "Chargement du fichier CSV: $csv_file"
    
    # Copy CSV to container
    docker compose cp "$csv_file" web:/tmp/data.csv
    
    # Use Python script to import CSV
    docker compose exec web python -c "
import pandas as pd
import uuid
import psycopg2
from sqlalchemy import create_engine

# Read CSV
df = pd.read_csv('/tmp/data.csv')

# Connect to database
engine = create_engine('postgresql://postgres:postgres@db:5432/eir_project')

# Process each row
for index, row in df.iterrows():
    try:
        # Create device
        device_id = str(uuid.uuid4())
        
        # Insert device
        device_query = '''
        INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
        VALUES (%s, %s, %s, %s, NULL)
        '''
        
        # Insert IMEI
        imei_id = str(uuid.uuid4())
        imei_query = '''
        INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
        VALUES (%s, %s, 1, 'active', %s)
        '''
        
        with engine.connect() as conn:
            conn.execute(device_query, (device_id, row['marque'], row['modele'], row.get('emmc', ''), ))
            conn.execute(imei_query, (imei_id, row['imei'], device_id))
            conn.commit()
            
        print(f'✅ Imported: {row[\"imei\"]} - {row[\"marque\"]} {row[\"modele\"]}')
    except Exception as e:
        print(f'❌ Error importing {row[\"imei\"]}: {e}')
"
    
    log_success "Fichier CSV traité"
}

# Function to create sample CSV template
create_csv_template() {
    local template_file="data/sample_devices.csv"
    
    # Create data directory if it doesn't exist
    mkdir -p data
    
    cat > "$template_file" << 'EOF'
imei,marque,modele,emmc
123456789012345,Samsung,Galaxy S23,256GB
987654321098765,Apple,iPhone 14,128GB
456789012345678,Huawei,P50 Pro,512GB
789012345678901,Xiaomi,Mi 12,256GB
345678901234567,OnePlus,10 Pro,128GB
EOF

    log_success "Modèle CSV créé: $template_file"
    log_info "Vous pouvez modifier ce fichier avec vos données et utiliser: $0 --csv $template_file"
}

# Function to load TAC database from CSV
load_tac_database() {
    local tac_csv_file="$1"
    
    if [[ ! -f "$tac_csv_file" ]]; then
        log_error "Fichier TAC CSV non trouvé: $tac_csv_file"
        return 1
    fi
    
    log_info "Chargement de la base de données TAC depuis: $tac_csv_file"
    
    # Copy TAC CSV to container
    docker compose cp "$tac_csv_file" web:/tmp/tac_data.csv
    
    # Use Python script to import TAC data
    docker compose exec web python -c "
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import uuid
from datetime import datetime

# Read CSV
df = pd.read_csv('/tmp/tac_data.csv')

# Connect to database
engine = create_engine('postgresql://postgres:postgres@db:5432/eir_project')

# Process each row
imported_count = 0
error_count = 0

for index, row in df.iterrows():
    try:
        # Prepare TAC data
        tac_query = '''
        INSERT INTO tac_database (tac, marque, modele, annee_sortie, type_appareil, statut)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (tac) DO UPDATE SET
            marque = EXCLUDED.marque,
            modele = EXCLUDED.modele,
            annee_sortie = EXCLUDED.annee_sortie,
            type_appareil = EXCLUDED.type_appareil,
            statut = EXCLUDED.statut,
            date_modification = CURRENT_TIMESTAMP
        '''
        
        with engine.connect() as conn:
            conn.execute(tac_query, (
                str(row['tac']).zfill(8),  # Ensure 8 digits
                row['marque'],
                row['modele'],
                row.get('annee_sortie', None),
                row.get('type_appareil', 'smartphone'),
                row.get('statut', 'valide')
            ))
            conn.commit()
            
        imported_count += 1
        if imported_count % 100 == 0:
            print(f'📊 Importé {imported_count} enregistrements TAC...')
            
    except Exception as e:
        error_count += 1
        print(f'❌ Erreur importation TAC {row[\"tac\"]}: {e}')

print(f'✅ Import TAC terminé: {imported_count} succès, {error_count} erreurs')
"
    
    log_success "Base de données TAC mise à jour"
}

# Function to create TAC CSV template
create_tac_csv_template() {
    local template_file="data/sample_tac_database.csv"
    
    # Create data directory if it doesn't exist
    mkdir -p data
    
    cat > "$template_file" << 'EOF'
tac,marque,modele,annee_sortie,type_appareil,statut
35326005,Samsung,Galaxy S23,2023,smartphone,valide
35692005,Apple,iPhone 14,2022,smartphone,valide
86234567,Huawei,P50 Pro,2021,smartphone,valide
35847200,Xiaomi,Mi 12,2022,smartphone,valide
35404806,OnePlus,10 Pro,2022,smartphone,valide
35404807,OnePlus,Nord 2,2021,smartphone,valide
99000000,TestDevice,Test Model,2020,test_device,test
EOF

    log_success "Modèle CSV TAC créé: $template_file"
    log_info "Format requis: tac,marque,modele,annee_sortie,type_appareil,statut"
    log_info "Utilisez: $0 --tac-csv $template_file"
}

# Function to load TAC database from Osmocom format
load_osmocom_tac_database() {
    local tac_csv_file="$1"
    
    if [[ ! -f "$tac_csv_file" ]]; then
        log_error "Fichier TAC CSV non trouvé: $tac_csv_file"
        return 1
    fi
    
    log_info "Chargement de la base de données TAC Osmocom depuis: $tac_csv_file"
    
    # Copy TAC CSV to container
    docker compose cp "$tac_csv_file" web:/tmp/osmocom_tac_data.csv
    
    # Use a more efficient approach for large files
    log_info "Import des données TAC via PostgreSQL (traitement par chunks)..."
    
    docker compose exec -T web bash -c '
        # First, clean the CSV file to handle carriage returns and malformed data
        echo "Nettoyage du fichier CSV..."
        
        # Convert Windows line endings to Unix and clean up the CSV
        sed "s/\r//g" /tmp/osmocom_tac_data.csv > /tmp/osmocom_clean.csv
        
        # Skip the first two lines (copyright notice and header) and process the data
        tail -n +3 /tmp/osmocom_clean.csv > /tmp/osmocom_data_only.csv
        
        # Create a temporary SQL script for the import
        cat > /tmp/import_tac.sql << "EOSQL"
-- Import TAC data from cleaned CSV file
CREATE TEMP TABLE temp_csv_data (
    tac_raw TEXT,
    name1 TEXT,
    name2 TEXT,
    contributor TEXT,
    comment TEXT,
    gsmarena1 TEXT,
    gsmarena2 TEXT,
    aka TEXT
);

-- Copy CSV data into temp table with proper error handling
\\copy temp_csv_data FROM '"'"'/tmp/osmocom_data_only.csv'"'"' WITH (FORMAT CSV, DELIMITER '"'"','"'"', QUOTE '"'"'"'"'"'"'"', ESCAPE '"'"'"'"'"'"'"', NULL '"'"''"'"', HEADER false);

-- Clean and process data before inserting
INSERT INTO tac_database (tac, marque, modele, type_appareil, statut)
SELECT DISTINCT
    LPAD(REGEXP_REPLACE(TRIM(tac_raw), '"'"'^0+'"'"', '"'"''"'"'), 8, '"'"'0'"'"') as tac,
    COALESCE(
        CASE 
            WHEN TRIM(name1) = '"'"''"'"' OR TRIM(name1) IS NULL THEN '"'"'Unknown'"'"'
            ELSE TRIM(name1)
        END, 
        '"'"'Unknown'"'"'
    ) as marque,
    COALESCE(
        CASE 
            WHEN TRIM(name2) = '"'"''"'"' OR TRIM(name2) IS NULL THEN 
                CASE 
                    WHEN TRIM(aka) != '"'"''"'"' AND TRIM(aka) IS NOT NULL THEN TRIM(aka)
                    ELSE '"'"'Unknown Model'"'"'
                END
            ELSE TRIM(name2)
        END,
        '"'"'Unknown Model'"'"'
    ) as modele,
    '"'"'smartphone'"'"' as type_appareil,
    '"'"'valide'"'"' as statut
FROM temp_csv_data
WHERE 
    tac_raw IS NOT NULL 
    AND LENGTH(TRIM(tac_raw)) >= 6
    AND LENGTH(TRIM(tac_raw)) <= 10
    AND TRIM(tac_raw) ~ '"'"'^\\s*[0-9]+\\s*$'"'"'
    AND TRIM(tac_raw) NOT ILIKE '"'"'%tac%'"'"'
    AND TRIM(tac_raw) NOT ILIKE '"'"'%name%'"'"'
ON CONFLICT (tac) DO UPDATE SET
    marque = EXCLUDED.marque,
    modele = EXCLUDED.modele,
    type_appareil = EXCLUDED.type_appareil,
    statut = EXCLUDED.statut,
    date_modification = CURRENT_TIMESTAMP;

-- Show import results
SELECT 
    '"'"'Import completed'"'"' as status,
    COUNT(*) as total_imported
FROM tac_database 
WHERE date_modification >= CURRENT_TIMESTAMP - INTERVAL '"'"'5 minutes'"'"';

-- Log the successful import
INSERT INTO tac_sync_log (source_name, source_url, sync_type, format_type, status, records_imported, sync_date)
SELECT 
    '"'"'osmocom_local_csv'"'"',
    '"'"'local_file'"'"',
    '"'"'manual'"'"',
    '"'"'csv'"'"',
    '"'"'success'"'"',
    COUNT(*),
    CURRENT_TIMESTAMP
FROM tac_database 
WHERE date_modification >= CURRENT_TIMESTAMP - INTERVAL '"'"'5 minutes'"'"';

DROP TABLE temp_csv_data;
EOSQL

        # Execute the SQL script
        PGPASSWORD=postgres psql -h db -U postgres -d eir_project -f /tmp/import_tac.sql
        
        # Clean up temporary files
        rm -f /tmp/import_tac.sql /tmp/osmocom_clean.csv /tmp/osmocom_data_only.csv
    '
    
    if [ $? -eq 0 ]; then
        log_success "Base de données TAC Osmocom mise à jour"
        
        # Show import statistics
        log_info "Affichage des statistiques d'import..."
        docker compose exec -T db psql -U postgres -d eir_project -c "
            SELECT 
                'Statistiques TAC' as info,
                COUNT(*) as total_entries,
                COUNT(DISTINCT marque) as brands,
                COUNT(*) FILTER (WHERE statut = 'valide') as valid_entries,
                MAX(date_modification) as last_update
            FROM tac_database;
            
            SELECT 'Top 10 marques:' as title;
            SELECT marque, COUNT(*) as models 
            FROM tac_database 
            GROUP BY marque 
            ORDER BY COUNT(*) DESC 
            LIMIT 10;
            
            SELECT 'Exemples TAC importés:' as title;
            SELECT tac, marque, modele 
            FROM tac_database 
            ORDER BY date_modification DESC 
            LIMIT 5;
        "
    else
        log_error "Échec de l'import TAC Osmocom"
        return 1
    fi
}

# Function to sync from Osmocom CSV API
sync_osmocom_csv() {
    log_info "Synchronisation depuis l'API CSV Osmocom..."
    
    docker compose exec -T web bash -c '
        # Download CSV data with retry logic
        for i in {1..3}; do
            if curl -s --connect-timeout 10 --max-time 30 "https://tacdb.osmocom.org/export/tacdb.csv" > /tmp/osmocom_tac_api.csv; then
                if [ -s /tmp/osmocom_tac_api.csv ]; then
                    echo "✅ Téléchargement CSV réussi (tentative $i)"
                    break
                fi
            fi
            echo "⚠️ Tentative $i échouée, retry..."
            sleep 5
        done
        
        if [ ! -s /tmp/osmocom_tac_api.csv ]; then
            echo "❌ Échec du téléchargement CSV après 3 tentatives"
            exit 1
        fi
        
        # Clean and prepare the downloaded CSV
        sed "s/\r//g" /tmp/osmocom_tac_api.csv > /tmp/osmocom_api_clean.csv
        tail -n +3 /tmp/osmocom_api_clean.csv > /tmp/osmocom_api_data.csv
        
        # Use the same import logic as local file
        cat > /tmp/import_csv_api.sql << "EOSQL"
CREATE TEMP TABLE temp_csv_api_data (
    tac_raw TEXT,
    name1 TEXT,
    name2 TEXT,
    contributor TEXT,
    comment TEXT,
    gsmarena1 TEXT,
    gsmarena2 TEXT,
    aka TEXT
);

\\copy temp_csv_api_data FROM '"'"'/tmp/osmocom_api_data.csv'"'"' WITH (FORMAT CSV, DELIMITER '"'"','"'"', QUOTE '"'"'"'"'"'"'"', ESCAPE '"'"'"'"'"'"'"', NULL '"'"''"'"', HEADER false);

INSERT INTO tac_database (tac, marque, modele, type_appareil, statut)
SELECT DISTINCT
    LPAD(REGEXP_REPLACE(TRIM(tac_raw), '"'"'^0+'"'"', '"'"''"'"'), 8, '"'"'0'"'"') as tac,
    COALESCE(TRIM(name1), '"'"'Unknown'"'"') as marque,
    COALESCE(
        CASE 
            WHEN TRIM(name2) = '"'"''"'"' OR TRIM(name2) IS NULL THEN 
                CASE 
                    WHEN TRIM(aka) != '"'"''"'"' AND TRIM(aka) IS NOT NULL THEN TRIM(aka)
                    ELSE '"'"'Unknown Model'"'"'
                END
            ELSE TRIM(name2)
        END,
        '"'"'Unknown Model'"'"'
    ) as modele,
    '"'"'smartphone'"'"' as type_appareil,
    '"'"'valide'"'"' as statut
FROM temp_csv_api_data
WHERE 
    tac_raw IS NOT NULL 
    AND LENGTH(TRIM(tac_raw)) >= 6
    AND LENGTH(TRIM(tac_raw)) <= 10
    AND TRIM(tac_raw) ~ '"'"'^\\s*[0-9]+\\s*$'"'"'
    AND TRIM(tac_raw) NOT ILIKE '"'"'%tac%'"'"'
    AND TRIM(tac_raw) NOT ILIKE '"'"'%name%'"'"'
ON CONFLICT (tac) DO UPDATE SET
    marque = EXCLUDED.marque,
    modele = EXCLUDED.modele,
    type_appareil = EXCLUDED.type_appareil,
    statut = EXCLUDED.statut,
    date_modification = CURRENT_TIMESTAMP;

-- Log the sync
INSERT INTO tac_sync_log (source_name, source_url, sync_type, format_type, status, records_imported)
SELECT 
    '"'"'osmocom_csv_api'"'"',
    '"'"'https://tacdb.osmocom.org/export/tacdb.csv'"'"',
    '"'"'automatic'"'"',
    '"'"'csv'"'"',
    '"'"'success'"'"',
    COUNT(*)
FROM tac_database 
WHERE date_modification >= CURRENT_TIMESTAMP - INTERVAL '"'"'5 minutes'"'"';

SELECT '"'"'CSV API import completed'"'"' as status;
DROP TABLE temp_csv_api_data;
EOSQL
        
        PGPASSWORD=postgres psql -h db -U postgres -d eir_project -f /tmp/import_csv_api.sql
        
        # Clean up
        rm -f /tmp/osmocom_tac_api.csv /tmp/osmocom_api_clean.csv /tmp/osmocom_api_data.csv /tmp/import_csv_api.sql
    '
    
    if [ $? -eq 0 ]; then
        log_success "Synchronisation CSV Osmocom terminée"
    else
        log_error "Échec de la synchronisation CSV Osmocom"
        return 1
    fi
}

# Function to show TAC sync statistics
show_tac_sync_stats() {
    log_info "Statistiques de synchronisation TAC..."
    
    docker compose exec -T db psql -U postgres -d eir_project -c "
        SELECT obtenir_stats_sync_tac() as stats;
        
        SELECT 'Synchronisations récentes:' as title;
        SELECT * FROM vue_sync_tac_recent LIMIT 10;
    "
}

# Enhanced function to load TAC database with format detection
load_tac_database() {
    local tac_csv_file="$1"
    local format_type="${2:-auto}"
    
    if [[ ! -f "$tac_csv_file" ]]; then
        log_error "Fichier TAC CSV non trouvé: $tac_csv_file"
        return 1
    fi
    
    # Auto-detect format
    if [[ "$format_type" == "auto" ]]; then
        if head -5 "$tac_csv_file" | grep -q "Osmocom TAC\|tac,name,name,contributor"; then
            format_type="osmocom"
            log_info "Format Osmocom TAC détecté"
        else
            format_type="standard"
            log_info "Format standard TAC détecté"
        fi
    fi
    
    case "$format_type" in
        "osmocom")
            load_osmocom_tac_database "$tac_csv_file"
            ;;
        "standard")
            log_info "Chargement de la base de données TAC format standard depuis: $tac_csv_file"
            
            docker compose cp "$tac_csv_file" web:/tmp/tac_data.csv
            
            # Use direct PostgreSQL import for standard format
            docker compose exec -T web bash -c "
                CSV_CONTENT=\$(cat /tmp/tac_data.csv)
                
                PGPASSWORD=postgres psql -h db -U postgres -d eir_project -c \"
                    SELECT importer_tac_avec_mapping('\$CSV_CONTENT', 'standard');
                \"
            "
            ;;
        *)
            log_error "Format TAC non supporté: $format_type"
            return 1
            ;;
    esac
    
    log_success "Base de données TAC mise à jour"
}

# Function to create TAC CSV template for Osmocom format
create_osmocom_tac_template() {
    local template_file="data/sample_osmocom_tac.csv"
    
    mkdir -p data
    
    cat > "$template_file" << 'EOF'
Osmocom TAC database under CC-BY-SA v3.0 (c) Harald Welte 2016
tac,name,name,contributor,comment,gsmarena,gsmarena,aka
35675904,Oppo,N1,Kévin Redon,,http://www.gsmarena.com/oppo_n1-5724.php,http://www.gsmarena.com/oppo-phones-82.php,
49013920,Nokia,1610,OsmoDevCon 2014,,,http://www.gsmarena.com/nokia-phones-1.php,"1610+,1611,1611+,NHE-5NX"
35250500,Nokia,6820,OsmoDevCon 2014,,http://www.gsmarena.com/nokia_6820-565.php,http://www.gsmarena.com/nokia-phones-1.php,"6820a,6820i,NHL-9,NHL-9 (DCT-4)"
EOF

    log_success "Modèle CSV TAC Osmocom créé: $template_file"
    log_info "Format: tac,name,name,contributor,comment,gsmarena,gsmarena,aka"
    log_info "Utilisez: $0 --osmocom-tac $template_file"
}

# Function to analyze TAC coverage
analyze_tac_coverage() {
    log_info "Analyse de la couverture de la base de données TAC..."
    
    docker compose exec db psql -U postgres -d eir_project -c "
    SELECT 'Statistiques TAC' as info;
    
    SELECT 
        'Total TAC enregistrés' as metric,
        COUNT(*) as valeur
    FROM tac_database
    UNION ALL
    SELECT 
        'Marques uniques' as metric,
        COUNT(DISTINCT marque) as valeur
    FROM tac_database
    UNION ALL
    SELECT 
        'TAC valides' as metric,
        COUNT(*) as valeur
    FROM tac_database WHERE statut = 'valide'
    UNION ALL
    SELECT 
        'TAC obsolètes' as metric,
        COUNT(*) as valeur
    FROM tac_database WHERE statut = 'obsolete';
    
    SELECT '--- Top 10 Marques ---' as info;
    SELECT * FROM vue_analyse_tac LIMIT 10;
    "
}

# Function to validate existing IMEIs against TAC database
validate_existing_imeis() {
    log_info "Validation des IMEIs existants avec la base TAC..."
    
    docker compose exec db psql -U postgres -d eir_project -c "
    WITH imei_validation AS (
        SELECT 
            i.numero_imei,
            a.marque as marque_actuelle,
            a.modele as modele_actuel,
            valider_imei_avec_tac(i.numero_imei) as validation_tac
        FROM imei i
        JOIN appareil a ON i.appareil_id = a.id
    )
    SELECT 
        numero_imei,
        marque_actuelle,
        validation_tac->>'marque' as marque_tac,
        modele_actuel,
        validation_tac->>'modele' as modele_tac,
        validation_tac->>'valide' as tac_valide,
        validation_tac->>'statut' as statut_tac
    FROM imei_validation
    WHERE validation_tac->>'marque' != 'Inconnue'
    ORDER BY numero_imei;
    "
}

# Function to use the sync-device API endpoint with TAC validation
sync_devices_via_api() {
    log_info "Synchronisation via l'API /sync-device avec validation TAC..."
    
    # Sample data for sync
    local sync_data='{
        "appareils": [
            {
                "imei": "353260051234567",
                "marque": "Samsung",
                "modele": "Galaxy A54",
                "statut": "actif",
                "emmc": "128GB",
                "metadata": {
                    "source_dms": "manual_import_with_tac",
                    "import_date": "'$(date -Iseconds)'",
                    "validate_tac": true
                }
            },
            {
                "imei": "356920051234567",
                "marque": "Apple",
                "modele": "iPhone 15",
                "statut": "actif",
                "emmc": "256GB",
                "metadata": {
                    "source_dms": "manual_import_with_tac",
                    "import_date": "'$(date -Iseconds)'",
                    "validate_tac": true
                }
            }
        ],
        "sync_mode": "upsert",
        "source_system": "Manual_Import_Script_TAC_Enabled"
    }'
    
    # Make API call
    response=$(curl -s -X POST "http://localhost:8000/sync-device" \
        -H "Content-Type: application/json" \
        -d "$sync_data")
    
    echo "$response" | jq .
    
    log_success "Synchronisation avec validation TAC terminée"
}

# Function to display current database statistics
show_database_stats() {
    log_info "Statistiques actuelles de la base de données..."
    
    docker compose exec db psql -U postgres -d eir_project -c "
    SELECT 
        'Statistiques EIR' as info,
        (SELECT COUNT(*) FROM utilisateur) as utilisateurs,
        (SELECT COUNT(*) FROM appareil) as appareils,
        (SELECT COUNT(*) FROM imei) as imeis,
        (SELECT COUNT(*) FROM sim) as cartes_sim,
        (SELECT COUNT(*) FROM recherche) as recherches,
        (SELECT COUNT(*) FROM tac_database) as tac_entries;
    "
}

# Main menu
show_menu() {
    echo ""
    echo "🔢 Options disponibles:"
    echo "  1) Charger les données de test (recommandé pour développement)"
    echo "  2) Créer un modèle CSV pour import personnalisé"
    echo "  3) Importer depuis un fichier CSV (avec validation TAC)"
    echo "  4) Synchroniser via l'API /sync-device (exemple avec TAC)"
    echo "  5) Afficher les statistiques de la base de données"
    echo "  6) Créer une sauvegarde de la base de données"
    echo "  7) Créer un modèle CSV pour base TAC standard"
    echo "  8) Importer une base de données TAC depuis CSV (auto-détection)"
    echo "  9) Créer un modèle CSV pour base TAC Osmocom"
    echo " 10) Importer une base TAC format Osmocom"
    echo " 11) Synchroniser depuis API JSON Osmocom"
    echo " 12) Synchroniser depuis API CSV Osmocom"
    echo " 13) Analyser la couverture TAC"
    echo " 14) Valider les IMEIs existants avec TAC"
    echo " 15) Afficher les stats de synchronisation TAC"
    echo " 16) Quitter"
    echo ""
}

# Parse command line arguments
case "${1:-}" in
    --test-data)
        load_test_data
        show_database_stats
        ;;
    --csv)
        if [[ -n "${2:-}" ]]; then
            load_csv_data "$2"
            show_database_stats
        else
            log_error "Veuillez spécifier le fichier CSV: $0 --csv fichier.csv"
            exit 1
        fi
        ;;
    --template)
        create_csv_template
        ;;
    --tac-template)
        create_tac_csv_template
        ;;
    --osmocom-template)
        create_osmocom_tac_template
        ;;
    --tac-csv)
        if [[ -n "${2:-}" ]]; then
            format_type="${3:-auto}"
            load_tac_database "$2" "$format_type"
            analyze_tac_coverage
        else
            log_error "Veuillez spécifier le fichier TAC CSV: $0 --tac-csv fichier.csv [format]"
            exit 1
        fi
        ;;
    --osmocom-tac)
        if [[ -n "${2:-}" ]]; then
            load_osmocom_tac_database "$2"
            analyze_tac_coverage
        else
            log_error "Veuillez spécifier le fichier TAC Osmocom CSV: $0 --osmocom-tac fichier.csv"
            exit 1
        fi
        ;;
    --sync-osmocom-json)
        sync_osmocom_json
        show_tac_sync_stats
        ;;
    --sync-osmocom-csv)
        sync_osmocom_csv
        show_tac_sync_stats
        ;;
    --tac-sync-stats)
        show_tac_sync_stats
        ;;
    --sync-api)
        sync_devices_via_api
        show_database_stats
        ;;
    --stats)
        show_database_stats
        ;;
    --tac-analysis)
        analyze_tac_coverage
        ;;
    --validate-imeis)
        validate_existing_imeis
        ;;
    --backup)
        backup_database
        ;;
    --help)
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  --test-data       Charger les données de test"
        echo "  --csv FILE        Importer depuis un fichier CSV"
        echo "  --template        Créer un modèle CSV"
        echo "  --tac-template    Créer un modèle CSV TAC standard"
        echo "  --osmocom-template Créer un modèle CSV TAC Osmocom"
        echo "  --tac-csv FILE [FORMAT] Importer base TAC (auto|osmocom|standard)"
        echo "  --osmocom-tac FILE Importer base TAC format Osmocom"
        echo "  --sync-osmocom-json Synchroniser depuis API JSON Osmocom"
        echo "  --sync-osmocom-csv  Synchroniser depuis API CSV Osmocom"
        echo "  --sync-api        Synchroniser via l'API"
        echo "  --stats           Afficher les statistiques"
        echo "  --tac-analysis    Analyser la couverture TAC"
        echo "  --tac-sync-stats  Afficher les stats de sync TAC"
        echo "  --validate-imeis  Valider IMEIs existants avec TAC"
        echo "  --backup          Créer une sauvegarde"
        echo "  --help            Afficher cette aide"
        ;;
    *)
        # Interactive mode
        while true; do
            show_menu
            read -p "Choisissez une option (1-16): " choice
            
            case $choice in
                1)
                    load_test_data
                    show_database_stats
                    ;;
                2)
                    create_csv_template
                    ;;
                3)
                    read -p "Entrez le chemin du fichier CSV: " csv_file
                    load_csv_data "$csv_file"
                    show_database_stats
                    ;;
                4)
                    sync_devices_via_api
                    show_database_stats
                    ;;
                5)
                    show_database_stats
                    ;;
                6)
                    backup_database
                    ;;
                7)
                    create_tac_csv_template
                    ;;
                8)
                    read -p "Entrez le chemin du fichier TAC CSV: " tac_csv_file
                    load_tac_database "$tac_csv_file"
                    analyze_tac_coverage
                    ;;
                9)
                    create_osmocom_tac_template
                    ;;
                10)
                    read -p "Entrez le chemin du fichier TAC Osmocom CSV: " tac_csv_file
                    load_osmocom_tac_database "$tac_csv_file"
                    analyze_tac_coverage
                    ;;
                11)
                    sync_osmocom_json
                    show_tac_sync_stats
                    ;;
                12)
                    sync_osmocom_csv
                    show_tac_sync_stats
                    ;;
                13)
                    analyze_tac_coverage
                    ;;
                14)
                    validate_existing_imeis
                    ;;
                15)
                    show_tac_sync_stats
                    ;;
                16)
                    log_info "Au revoir!"
                    exit 0
                    ;;
                *)
                    log_warning "Option invalide. Veuillez choisir entre 1 et 16."
                    ;;
            esac
            
            echo ""
            read -p "Appuyez sur Entrée pour continuer..."
        done
        ;;
esac

log_success "Opération terminée"
                12)
                    sync_osmocom_csv
                    show_tac_sync_stats
                    ;;
                13)
                    analyze_tac_coverage
                    ;;
                14)
                    validate_existing_imeis
                    ;;
                15)
                    show_tac_sync_stats
                    ;;
                16)
                    log_info "Au revoir!"
                    exit 0
                    ;;
                *)
                    log_warning "Option invalide. Veuillez choisir entre 1 et 16."
                    ;;
            esac
            
            echo ""
            read -p "Appuyez sur Entrée pour continuer..."
        done
        ;;
esac

log_success "Opération terminée"
