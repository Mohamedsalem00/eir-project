#!/bin/bash

# 🚀 Script de Configuration Automatique des Tests API EIR
# Ce script configure automatiquement l'environnement de test

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Configuration Automatique des Tests API EIR${NC}"
echo "=============================================="

# Fonction pour afficher les étapes
print_step() {
    echo -e "\n${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification du répertoire courant
print_step "Vérification du répertoire de travail"
if [[ ! -f "test_api_endpoints.py" ]]; then
    echo -e "${RED}Erreur: Ce script doit être exécuté depuis le dossier test/${NC}"
    echo "Utilisation: cd /home/mohamed/Documents/projects/eir-project/test && ./setup_tests.sh"
    exit 1
fi
print_success "Répertoire correct"

# Vérification de Python
print_step "Vérification de Python"
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 n'est pas installé"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
print_success "Python disponible: $PYTHON_VERSION"

# Vérification des dépendances Python
print_step "Vérification des dépendances Python"
REQUIRED_PACKAGES=("requests" "datetime" "json" "urllib.parse")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    print_warning "Packages Python manquants: ${MISSING_PACKAGES[*]}"
    print_step "Installation des packages manquants"
    
    # Essayer d'installer requests (le seul qui peut ne pas être présent)
    if [[ " ${MISSING_PACKAGES[*]} " =~ " requests " ]]; then
        echo "Installation de requests..."
        if pip3 install requests; then
            print_success "Package requests installé"
        else
            print_error "Impossible d'installer requests. Installez-le manuellement: pip3 install requests"
        fi
    fi
else
    print_success "Toutes les dépendances Python sont disponibles"
fi

# Vérification de Docker
print_step "Vérification de Docker"
if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose n'est pas installé"
    exit 1
fi
print_success "Docker et Docker Compose disponibles"

# Vérification du projet EIR
print_step "Vérification du projet EIR"
cd ..
if [[ ! -f "docker-compose.yml" ]]; then
    print_error "Fichier docker-compose.yml introuvable"
    exit 1
fi
print_success "Projet EIR détecté"

# Vérification du statut des conteneurs
print_step "Vérification du statut des conteneurs"
CONTAINER_STATUS=$(sudo docker-compose ps --format "table {{.Name}}\t{{.State}}" 2>/dev/null || echo "")

if [[ -z "$CONTAINER_STATUS" ]]; then
    print_warning "Aucun conteneur en cours d'exécution"
    echo "Souhaitez-vous démarrer les conteneurs ? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_step "Démarrage des conteneurs"
        sudo docker-compose up -d
        sleep 10
        print_success "Conteneurs démarrés"
    else
        print_warning "Les tests nécessitent que les conteneurs soient en cours d'exécution"
    fi
else
    echo "$CONTAINER_STATUS"
    print_success "Conteneurs détectés"
fi

# Test de connectivité API
print_step "Test de connectivité API"
cd test
API_URL="http://localhost:8000"

# Attendre que l'API soit prête
echo "Attente de l'API..."
for i in {1..30}; do
    if curl -s "$API_URL/" > /dev/null 2>&1; then
        print_success "API accessible sur $API_URL"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Impossible de se connecter à l'API après 30 tentatives"
        echo "Vérifiez que les conteneurs fonctionnent avec: sudo docker-compose ps"
        exit 1
    fi
    sleep 2
done

# Configuration des permissions d'exécution
print_step "Configuration des permissions d'exécution"
SCRIPTS=("run_api_tests.sh" "quick_api_test.sh" "test_dashboard.sh" "setup_tests.sh")

for script in "${SCRIPTS[@]}"; do
    if [[ -f "$script" ]]; then
        chmod +x "$script"
        print_success "Permissions configurées pour $script"
    fi
done

# Test rapide de l'API
print_step "Test rapide de l'API"
echo "Exécution d'un test de base..."

if python3 -c "
import requests
import sys
try:
    response = requests.get('$API_URL/', timeout=10)
    if response.status_code == 200:
        print('✅ API répond correctement')
        sys.exit(0)
    else:
        print(f'⚠️  API répond avec le code: {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'❌ Erreur de connexion: {e}')
    sys.exit(1)
"; then
    print_success "Test de base réussi"
else
    print_warning "Test de base échoué - l'API peut avoir des problèmes"
fi

# Création du répertoire de rapports
print_step "Configuration du répertoire de rapports"
REPORTS_DIR="reports"
if [[ ! -d "$REPORTS_DIR" ]]; then
    mkdir -p "$REPORTS_DIR"
    print_success "Répertoire de rapports créé: $REPORTS_DIR"
else
    print_success "Répertoire de rapports existant: $REPORTS_DIR"
fi

# Résumé final
echo -e "\n${GREEN}🎉 Configuration terminée avec succès !${NC}"
echo "=============================================="
echo -e "${BLUE}Commandes disponibles:${NC}"
echo "  ./quick_api_test.sh        - Test rapide"
echo "  ./run_api_tests.sh         - Tests complets"
echo "  ./test_dashboard.sh        - Tableau de bord interactif"
echo "  ./analyze_test_results.py  - Analyser les résultats"
echo ""
echo -e "${BLUE}Pour commencer:${NC}"
echo "  ./test_dashboard.sh"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  cat README_TESTS.md"
echo ""
echo -e "${GREEN}✨ Environnement de test prêt !${NC}"
