#!/bin/bash
# quick-start.sh - Démarrage rapide du projet EIR avec gestion automatique des permissions Docker

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# Navigate to project directory
cd "$(dirname "$0")"

# Source Docker utilities
source scripts/docker-utils.sh

echo -e "${CYAN}${BOLD}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                   🚀 DÉMARRAGE RAPIDE EIR 🚀               ║"
echo "║           Projet francisé - Prêt en quelques clics        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}📋 Étapes de démarrage :${NC}"
echo "1. Vérification de Docker et des permissions..."
echo "2. Construction et démarrage des conteneurs..."
echo "3. Initialisation de la base de données..."
echo "4. Test de l'API francisée..."
echo ""

read -p "🚀 Démarrer le projet EIR ? (O/n) : " confirm

if [[ "$confirm" =~ ^[Nn]$ ]]; then
    echo "Démarrage annulé."
    exit 0
fi

echo ""
echo -e "${BOLD}🔄 Démarrage en cours...${NC}"

# Setup Docker commands with appropriate permissions
echo "🔍 Vérification des permissions Docker..."
setup_docker_commands

echo ""
echo "📦 Construction et démarrage des conteneurs..."
if run_docker_compose up -d --build; then
    echo -e "${GREEN}✅ Conteneurs démarrés avec succès${NC}"
else
    echo -e "${RED}❌ Erreur lors du démarrage des conteneurs${NC}"
    exit 1
fi

echo ""
echo "⏳ Attente du démarrage des services (30 secondes)..."
sleep 30

echo ""
echo "🧪 Test de l'API..."
if curl -s -f http://localhost:8000/verification-etat > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API accessible et opérationnelle${NC}"
else
    echo -e "${YELLOW}⚠️  API en cours de démarrage, cela peut prendre quelques minutes${NC}"
fi

echo ""
echo -e "${GREEN}✅ Démarrage terminé !${NC}"
echo ""
echo "📍 Accès à l'application :"
echo "  🌐 Documentation API : http://localhost:8000/docs"
echo "  🔍 Vérification santé : http://localhost:8000/verification-etat"
echo "  🏠 Page d'accueil : http://localhost:8000/"
echo ""
echo "💡 Utilisez './scripts/manage-eir.sh' pour la gestion complète"
echo ""

if [[ "$USE_SUDO" == "true" ]]; then
    echo -e "${YELLOW}💡 Info : Les commandes Docker utilisent sudo sur ce système${NC}"
    echo "   Pour éviter cela à l'avenir, ajoutez votre utilisateur au groupe docker :"
    echo "   sudo usermod -aG docker \$USER"
    echo "   Puis redémarrez votre session."
fi
