#!/bin/bash

# Script pour analyser et organiser les scripts du dossier scripts/

echo "📁 ANALYSE DU DOSSIER SCRIPTS"
echo "============================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

cd /home/mohamed/Documents/projects/eir-project/scripts

echo "📊 Analyse des scripts dans scripts/ :"
echo ""

# Scripts à organiser par catégorie
declare -A SCRIPTS_CATEGORIES=(
    # Scripts de gestion Docker (à conserver - utiles)
    ["manage-eir.sh"]="docker-management"
    ["rebuild-containers.sh"]="docker-management" 
    ["restart-containers.sh"]="docker-management"
    
    # Scripts de gestion base de données (à conserver - essentiels)
    ["rebuild-database.sh"]="database-management"
    ["reset-database.sh"]="database-management"
    ["gestion-base-donnees.sh"]="database-management"
    ["alimenter-base-donnees.sh"]="database-management"
    
    # Scripts de configuration (à conserver - utiles)
    ["configurer-apis-externes.sh"]="configuration"
    ["setup-notifications.sh"]="configuration"
    
    # Scripts de test (à réorganiser vers testing/)
    ["test-complete-api.sh"]="testing-to-move"
    ["test-apis-externes.sh"]="testing-to-move"
    ["test-eir-notifications.sh"]="testing-to-move"
    ["test-notifications.sh"]="testing-to-move"
    ["test-system.sh"]="testing-to-move"
    ["test-updated-data.sh"]="testing-to-move"
    
    # Scripts divers (à évaluer)
    ["actions-rapides.sh"]="utilities"
    ["guide-apis-payantes.sh"]="documentation"
    ["integrate-notification-templates.sh"]="legacy"
    
    # Script récent (à conserver)
    ["cleanup-old-scripts.sh"]="utilities"
)

# Création des dossiers d'organisation
echo "1️⃣ Création de la structure d'organisation..."
mkdir -p ../testing/scripts/api
mkdir -p ../testing/scripts/system
mkdir -p ../testing/scripts/notifications
mkdir -p scripts-organized/docker
mkdir -p scripts-organized/database
mkdir -p scripts-organized/config
mkdir -p scripts-organized/utilities
mkdir -p scripts-organized/legacy
echo ""

# Analyse et organisation
echo "2️⃣ Analyse des scripts par catégorie :"
echo ""

# Scripts Docker Management
echo "🐳 Scripts de gestion Docker (à conserver) :"
for script in manage-eir.sh rebuild-containers.sh restart-containers.sh; do
    if [ -f "$script" ]; then
        echo "   ✅ $script - Script de gestion Docker utile"
    fi
done
echo ""

# Scripts Database Management  
echo "🗄️  Scripts de gestion base de données (à conserver) :"
for script in rebuild-database.sh reset-database.sh gestion-base-donnees.sh alimenter-base-donnees.sh; do
    if [ -f "$script" ]; then
        echo "   ✅ $script - Script de DB essentiel"
    fi
done
echo ""

# Scripts de test (à déplacer vers testing/)
echo "🧪 Scripts de test (à déplacer vers testing/) :"
declare -a TEST_SCRIPTS=(
    "test-complete-api.sh:api"
    "test-apis-externes.sh:api" 
    "test-eir-notifications.sh:notifications"
    "test-notifications.sh:notifications"
    "test-system.sh:system"
    "test-updated-data.sh:system"
)

for script_info in "${TEST_SCRIPTS[@]}"; do
    script_name="${script_info%:*}"
    category="${script_info#*:}"
    
    if [ -f "$script_name" ]; then
        echo "   📦 $script_name → testing/scripts/$category/"
        cp "$script_name" "../testing/scripts/$category/"
        print_status "Copié $script_name vers testing/scripts/$category/"
    fi
done
echo ""

# Scripts de configuration
echo "⚙️  Scripts de configuration (à conserver) :"
for script in configurer-apis-externes.sh setup-notifications.sh; do
    if [ -f "$script" ]; then
        echo "   ✅ $script - Script de configuration important"
    fi
done
echo ""

# Scripts legacy/obsolètes
echo "📚 Scripts à archiver ou supprimer :"
if [ -f "integrate-notification-templates.sh" ]; then
    echo "   📦 integrate-notification-templates.sh → Probablement obsolète (notification templates déjà intégrés)"
    cp "integrate-notification-templates.sh" "scripts-organized/legacy/"
fi

if [ -f "guide-apis-payantes.sh" ]; then
    echo "   📝 guide-apis-payantes.sh → À déplacer vers documentation/"
    cp "guide-apis-payantes.sh" "../documentation/user-guides/"
fi
echo ""

# Scripts utilitaires
echo "🛠️  Scripts utilitaires (à conserver) :"
for script in actions-rapides.sh cleanup-old-scripts.sh; do
    if [ -f "$script" ]; then
        echo "   ✅ $script - Script utilitaire utile"
    fi
done
echo ""

# Mise à jour du README des scripts
echo "3️⃣ Mise à jour de la documentation..."
cat > README_ORGANIZED.md << 'EOF'
# 📁 Scripts EIR - Structure Organisée

## 🎯 Scripts Principaux (à utiliser)

### 🐳 Gestion Docker
- `manage-eir.sh` - Script principal interactif de gestion
- `rebuild-containers.sh` - Reconstruction complète des conteneurs  
- `restart-containers.sh` - Redémarrage rapide des conteneurs

### 🗄️ Gestion Base de Données
- `rebuild-database.sh` - Reconstruction complète de la DB
- `reset-database.sh` - Réinitialisation rapide de la DB
- `gestion-base-donnees.sh` - Gestion interactive de la DB
- `alimenter-base-donnees.sh` - Alimentation de données

### ⚙️ Configuration
- `configurer-apis-externes.sh` - Configuration des APIs externes
- `setup-notifications.sh` - Configuration du système de notifications

### 🛠️ Utilitaires
- `actions-rapides.sh` - Actions de développement rapides
- `cleanup-old-scripts.sh` - Nettoyage des anciens scripts

## 📦 Scripts Déplacés

### → testing/scripts/
Tous les scripts de test ont été déplacés vers la structure de test organisée :
- `testing/scripts/api/` - Tests API
- `testing/scripts/notifications/` - Tests notifications  
- `testing/scripts/system/` - Tests système

### → documentation/
- `guide-apis-payantes.sh` → `documentation/user-guides/`

## 🎯 Utilisation Recommandée

### Via Makefile (Recommandé)
```bash
make start     # Équivalent à manage-eir.sh
make test      # Tests complets
make clean     # Nettoyage
```

### Scripts Directs
```bash
# Gestion Docker
./scripts/manage-eir.sh
./scripts/rebuild-containers.sh

# Base de données
./scripts/rebuild-database.sh
./scripts/reset-database.sh

# Configuration
./scripts/configurer-apis-externes.sh
./scripts/setup-notifications.sh
```

---
*Documentation mise à jour le 12 août 2025*
EOF

print_status "Documentation mise à jour : README_ORGANIZED.md créé"
echo ""

# Résumé final
echo "📊 RÉSUMÉ DE L'ORGANISATION"
echo "=========================="
echo ""

DOCKER_SCRIPTS=$(ls -1 manage-eir.sh rebuild-containers.sh restart-containers.sh 2>/dev/null | wc -l)
DB_SCRIPTS=$(ls -1 rebuild-database.sh reset-database.sh gestion-base-donnees.sh alimenter-base-donnees.sh 2>/dev/null | wc -l)
CONFIG_SCRIPTS=$(ls -1 configurer-apis-externes.sh setup-notifications.sh 2>/dev/null | wc -l)
UTIL_SCRIPTS=$(ls -1 actions-rapides.sh cleanup-old-scripts.sh 2>/dev/null | wc -l)

echo "✅ Scripts conservés dans scripts/ :"
echo "   🐳 Gestion Docker : $DOCKER_SCRIPTS scripts"
echo "   🗄️  Base de données : $DB_SCRIPTS scripts"  
echo "   ⚙️  Configuration : $CONFIG_SCRIPTS scripts"
echo "   🛠️  Utilitaires : $UTIL_SCRIPTS scripts"
echo ""

TEST_MOVED=$(ls -1 ../testing/scripts/*/*.sh 2>/dev/null | wc -l)
echo "📦 Scripts déplacés :"
echo "   🧪 Tests → testing/scripts/ : $TEST_MOVED scripts"
echo "   📝 Guide → documentation/ : 1 script"
echo ""

TOTAL_SCRIPTS=$(ls -1 *.sh 2>/dev/null | wc -l)
echo "📈 Total scripts dans scripts/ : $TOTAL_SCRIPTS"
echo ""

print_status "Organisation des scripts terminée !"
echo ""
echo "🎯 Prochaines étapes :"
echo "   1. Vérifiez README_ORGANIZED.md pour la nouvelle structure"
echo "   2. Testez les scripts principaux : ./scripts/manage-eir.sh"
echo "   3. Utilisez 'make help' pour les commandes simplifiées"
echo ""
