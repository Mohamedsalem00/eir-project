#!/bin/bash

# 🎯 Menu Principal des Outils de Test API EIR
# Interface unique pour accéder à tous les outils de test

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
API_URL="http://localhost:8000"

show_header() {
    clear
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║              🧪 OUTILS DE TEST API EIR 🧪               ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}🌐 API URL: ${YELLOW}$API_URL${NC}"
    echo -e "${CYAN}📅 $(date)${NC}"
    echo ""
}

show_menu() {
    echo -e "${GREEN}📋 OUTILS DISPONIBLES:${NC}"
    echo ""
    echo -e "${YELLOW}🚀 TESTS RAPIDES:${NC}"
    echo "  1️⃣  Test Rapide (5s)           - Vérification de base"
    echo "  2️⃣  Tests Complets (1min)      - Tous les endpoints"
    echo "  3️⃣  Tableau de Bord            - Interface interactive"
    echo ""
    echo -e "${YELLOW}🆕 TESTS V2.0 - CENTRALISÉS:${NC}"
    echo "  1️⃣2️⃣ Test Rapide v2 (smoke)     - Endpoints critiques"
    echo "  1️⃣3️⃣ Tests Core v2 (core)       - Endpoints essentiels"
    echo "  1️⃣4️⃣ Tests Complets v2 (all)    - Configuration centralisée"
    echo ""
    echo -e "${YELLOW}🔧 CONFIGURATION:${NC}"
    echo "  4️⃣  Configuration Automatique  - Setup complet"
    echo "  5️⃣  Vérifier l'État API       - Status de l'API"
    echo "  6️⃣  Redémarrer API             - Redémarrage conteneurs"
    echo ""
    echo -e "${YELLOW}📊 ANALYSE & MONITORING:${NC}"
    echo "  7️⃣  Analyser Résultats         - Analyse des rapports"
    echo "  8️⃣  Monitoring Continu         - Surveillance temps réel"
    echo "  9️⃣  Voir les Logs              - Logs de l'API"
    echo ""
    echo -e "${YELLOW}📚 AIDE:${NC}"
    echo "  🔟 Documentation               - Guide complet"
    echo "  1️⃣1️⃣ Liste des Fichiers        - Tous les scripts"
    echo ""
    echo -e "${RED}0️⃣  Quitter${NC}"
    echo ""
}

check_api_status() {
    echo -e "${CYAN}🔍 Vérification de l'état de l'API...${NC}"
    
    if curl -s "$API_URL/" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API accessible${NC}"
        return 0
    else
        echo -e "${RED}❌ API non accessible${NC}"
        return 1
    fi
}

run_option() {
    case $1 in
        1)
            echo -e "${BLUE}🚀 Exécution du test rapide...${NC}"
            ./quick_api_test.sh
            ;;
        2)
            echo -e "${BLUE}🔬 Exécution des tests complets...${NC}"
            ./run_api_tests.sh
            ;;
        3)
            echo -e "${BLUE}📊 Ouverture du tableau de bord...${NC}"
            ./test_dashboard.sh
            ;;
        12)
            echo -e "${BLUE}🚀 Test Rapide v2 (smoke)...${NC}"
            ./quick_api_test_v2.sh
            ;;
        13)
            echo -e "${BLUE}🎯 Tests Core v2 (essentiels)...${NC}"
            ./run_api_tests_v2.sh http://localhost:8000 core
            ;;
        14)
            echo -e "${BLUE}🌍 Tests Complets v2 (tous endpoints)...${NC}"
            ./run_api_tests_v2.sh http://localhost:8000 all
            ;;
        4)
            echo -e "${BLUE}⚙️  Configuration automatique...${NC}"
            ./setup_tests.sh
            ;;
        5)
            check_api_status
            echo ""
            echo "Appuyez sur Entrée pour continuer..."
            read
            ;;
        6)
            echo -e "${BLUE}🔄 Redémarrage de l'API...${NC}"
            cd ..
            sudo docker-compose restart
            echo -e "${GREEN}✅ API redémarrée${NC}"
            cd test
            echo ""
            echo "Appuyez sur Entrée pour continuer..."
            read
            ;;
        7)
            echo -e "${BLUE}📈 Analyse des résultats...${NC}"
            echo "Fichiers de rapport disponibles:"
            ls -la api_test_report_*.json 2>/dev/null || echo "Aucun rapport trouvé"
            echo ""
            echo "Entrez le nom du fichier à analyser (ou Entrée pour le plus récent):"
            read filename
            if [[ -z "$filename" ]]; then
                filename=$(ls -t api_test_report_*.json 2>/dev/null | head -1)
            fi
            if [[ -n "$filename" && -f "$filename" ]]; then
                python3 analyze_test_results.py "$filename"
            else
                echo -e "${RED}❌ Fichier non trouvé${NC}"
            fi
            echo ""
            echo "Appuyez sur Entrée pour continuer..."
            read
            ;;
        8)
            echo -e "${BLUE}📊 Démarrage du monitoring continu...${NC}"
            echo "Appuyez sur Ctrl+C pour arrêter"
            sleep 2
            ./monitor_api.sh
            ;;
        9)
            echo -e "${BLUE}📋 Affichage des logs...${NC}"
            cd ..
            echo "Logs de l'API (dernières 50 lignes):"
            sudo docker logs eir_web --tail 50
            echo ""
            echo "Logs de la base de données (dernières 20 lignes):"
            sudo docker logs eir_db --tail 20
            cd test
            echo ""
            echo "Appuyez sur Entrée pour continuer..."
            read
            ;;
        10)
            echo -e "${BLUE}📚 Affichage de la documentation...${NC}"
            if [[ -f "README_TESTS.md" ]]; then
                less README_TESTS.md
            else
                echo -e "${RED}❌ Documentation non trouvée${NC}"
            fi
            ;;
        11)
            echo -e "${BLUE}📁 Liste des fichiers de test:${NC}"
            echo ""
            echo -e "${GREEN}Scripts principaux:${NC}"
            ls -la *.sh 2>/dev/null || echo "Aucun script .sh trouvé"
            echo ""
            echo -e "${GREEN}Scripts Python:${NC}"
            ls -la *.py 2>/dev/null || echo "Aucun script .py trouvé"
            echo ""
            echo -e "${GREEN}Rapports générés:${NC}"
            ls -la api_test_report_*.json 2>/dev/null || echo "Aucun rapport trouvé"
            echo ""
            echo -e "${GREEN}Fichiers de log:${NC}"
            ls -la *.log 2>/dev/null || echo "Aucun log trouvé"
            echo ""
            echo "Appuyez sur Entrée pour continuer..."
            read
            ;;
        0)
            echo -e "${GREEN}👋 Au revoir !${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Option invalide${NC}"
            sleep 1
            ;;
    esac
}

# Vérification du répertoire
if [[ ! -f "test_api_endpoints.py" ]]; then
    echo -e "${RED}❌ Erreur: Ce script doit être exécuté depuis le dossier test/${NC}"
    echo "Utilisation: cd /home/mohamed/Documents/projects/eir-project/test && ./menu_tests.sh"
    exit 1
fi

# Boucle principale
while true; do
    show_header
    show_menu
    
    echo -ne "${CYAN}Choisissez une option: ${NC}"
    read choice
    
    echo ""
    run_option "$choice"
    echo ""
done
