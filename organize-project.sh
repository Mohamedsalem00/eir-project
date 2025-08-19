#!/bin/bash

# 🗂️ Script d'Organisation du Projet EIR
# Organise la documentation et les fichiers de test pour une meilleure structure

set -e

echo "🗂️ Organisation du Projet EIR - Début"
echo "======================================="

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction d'affichage coloré
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification que nous sommes dans la racine du projet
if [[ ! -f "README.md" ]] || [[ ! -d "backend" ]]; then
    print_error "Ce script doit être exécuté depuis la racine du projet EIR"
    exit 1
fi

echo "📁 Création de la structure de dossiers..."

# Création des dossiers s'ils n'existent pas déjà
mkdir -p documentation/{user-guides,technical,deployment,api}
mkdir -p testing/{unit,integration,api,performance}

print_status "Structure de dossiers créée"

echo "📄 Déplacement et organisation des fichiers de documentation..."

# Déplacement des fichiers de documentation
if [[ -f "DEPLOYMENT_GUIDE.md" ]]; then
    mv "DEPLOYMENT_GUIDE.md" "documentation/deployment/"
    print_status "DEPLOYMENT_GUIDE.md → documentation/deployment/"
fi

if [[ -f "NOTIFICATIONS_QUICK_START.md" ]]; then
    mv "NOTIFICATIONS_QUICK_START.md" "documentation/technical/notifications.md"
    print_status "NOTIFICATIONS_QUICK_START.md → documentation/technical/notifications.md"
fi

if [[ -f "TRANSLATION_SYSTEM_SUMMARY.md" ]]; then
    mv "TRANSLATION_SYSTEM_SUMMARY.md" "documentation/technical/translations.md"
    print_status "TRANSLATION_SYSTEM_SUMMARY.md → documentation/technical/translations.md"
fi

if [[ -f "MULTI_PROTOCOL_README.md" ]]; then
    mv "MULTI_PROTOCOL_README.md" "documentation/technical/multi-protocol.md"
    print_status "MULTI_PROTOCOL_README.md → documentation/technical/multi-protocol.md"
fi

if [[ -f "POSTGRES_SETUP.md" ]]; then
    mv "POSTGRES_SETUP.md" "documentation/technical/database-setup.md"
    print_status "POSTGRES_SETUP.md → documentation/technical/database-setup.md"
fi

echo "🧪 Organisation des fichiers de test..."

# Déplacement des fichiers de test vers la nouvelle structure
for test_file in test_*.py; do
    if [[ -f "$test_file" ]]; then
        # Analyse du type de test basé sur le nom
        if [[ "$test_file" == *"admin"* ]] || [[ "$test_file" == *"email"* ]] || [[ "$test_file" == *"notification"* ]]; then
            mv "$test_file" "testing/integration/"
            print_status "$test_file → testing/integration/"
        elif [[ "$test_file" == *"api"* ]] || [[ "$test_file" == *"endpoint"* ]]; then
            mv "$test_file" "testing/api/"
            print_status "$test_file → testing/api/"
        else
            mv "$test_file" "testing/unit/"
            print_status "$test_file → testing/unit/"
        fi
    fi
done

# Déplacement du dossier test/ existant s'il existe
if [[ -d "test" ]]; then
    echo "📦 Fusion du dossier test/ existant..."
    
    # Déplacement des fichiers de configuration API
    if [[ -f "test/api_endpoints_config_v2.py" ]]; then
        mv "test/api_endpoints_config_v2.py" "testing/api/"
        print_status "api_endpoints_config_v2.py → testing/api/"
    fi
    
    # Déplacement d'autres fichiers de test
    find test/ -name "*.py" -type f | while read file; do
        filename=$(basename "$file")
        if [[ "$filename" == *"api"* ]]; then
            mv "$file" "testing/api/"
            print_status "$filename → testing/api/"
        elif [[ "$filename" == *"integration"* ]] || [[ "$filename" == *"complete"* ]]; then
            mv "$file" "testing/integration/"
            print_status "$filename → testing/integration/"
        else
            mv "$file" "testing/unit/"
            print_status "$filename → testing/unit/"
        fi
    done
    
    # Déplacement des fichiers de configuration
    find test/ -name "*.json" -type f | while read file; do
        mv "$file" "testing/api/"
        print_status "$(basename "$file") → testing/api/"
    done
    
    # Suppression du dossier test/ vide
    if [[ -z "$(ls -A test/)" ]]; then
        rmdir test/
        print_status "Dossier test/ vide supprimé"
    else
        print_warning "Dossier test/ non vide, vérification manuelle requise"
    fi
fi

echo "🧹 Nettoyage des fichiers temporaires..."

# Suppression des fichiers temporaires identifiés
temp_files=(
    "COMMIT_SUMMARY_OLD.md"
    "NOTIFICATION_SYSTEM_SUCCESS_REPORT.md"
    "PROJECT_CLEANUP_SUCCESS.md"
    "diagnostic_test.py"
    "test_example.py"
)

for file in "${temp_files[@]}"; do
    if [[ -f "$file" ]]; then
        rm "$file"
        print_status "Supprimé: $file"
    fi
done

echo "📝 Création des fichiers de configuration de test..."

# Création du fichier requirements-test.txt
cat > testing/requirements-test.txt << 'EOF'
# Dépendances pour les tests du projet EIR
pytest>=7.0.0
pytest-asyncio>=0.20.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-html>=3.1.0
pytest-xdist>=3.0.0
requests-mock>=1.9.0
factory-boy>=3.2.0
faker>=18.0.0
locust>=2.14.0
httpx>=0.24.0
EOF

print_status "requirements-test.txt créé"

# Création du fichier conftest.py
cat > testing/conftest.py << 'EOF'
"""
Configuration globale pour les tests pytest du projet EIR
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import de l'application principale
try:
    from backend.app.main import app
except ImportError:
    app = None

@pytest.fixture(scope="session")
def event_loop():
    """Fixture pour l'event loop asyncio"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Client de test FastAPI synchrone"""
    if app is None:
        pytest.skip("Application backend non disponible")
    
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Client de test FastAPI asynchrone"""
    if app is None:
        pytest.skip("Application backend non disponible")
    
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client

@pytest.fixture
def auth_headers():
    """Headers d'authentification pour les tests"""
    return {
        "Authorization": "Bearer test-token-for-testing",
        "Content-Type": "application/json"
    }

@pytest.fixture
def test_user_data():
    """Données utilisateur de test"""
    return {
        "email": "test@example.com",
        "nom": "Test User",
        "mot_de_passe": "testpassword123"
    }

@pytest.fixture
def test_imei_data():
    """Données IMEI de test"""
    return {
        "valid_imei": "123456789012345",
        "invalid_imei": "invalid_imei",
        "test_tac": "12345678"
    }

# Configuration pytest
def pytest_configure(config):
    """Configuration globale pytest"""
    config.addinivalue_line(
        "markers", "slow: marque les tests lents"
    )
    config.addinivalue_line(
        "markers", "integration: marque les tests d'intégration"
    )
    config.addinivalue_line(
        "markers", "api: marque les tests API"
    )
EOF

print_status "conftest.py créé"

# Création d'un Makefile pour simplifier l'exécution des tests
cat > Makefile << 'EOF'
# Makefile pour le projet EIR
# Simplification des commandes de développement et test

.PHONY: help test test-unit test-integration test-api test-all coverage clean install-test

help:
	@echo "🚀 Commandes disponibles pour le projet EIR:"
	@echo "  make test          - Exécuter tous les tests"
	@echo "  make test-unit     - Tests unitaires seulement"
	@echo "  make test-integration - Tests d'intégration seulement"
	@echo "  make test-api      - Tests API seulement"
	@echo "  make coverage      - Tests avec rapport de couverture"
	@echo "  make install-test  - Installer les dépendances de test"
	@echo "  make clean         - Nettoyer les fichiers temporaires"

install-test:
	pip install -r testing/requirements-test.txt

test:
	python -m pytest testing/ -v

test-unit:
	python -m pytest testing/unit/ -v

test-integration:
	python -m pytest testing/integration/ -v

test-api:
	python -m pytest testing/api/ -v

coverage:
	python -m pytest testing/ --cov=backend/app --cov-report=html --cov-report=term-missing

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
EOF

print_status "Makefile créé"

echo "📋 Mise à jour du README principal..."

# Ajout d'une section sur la nouvelle organisation dans le README
if ! grep -q "## 📚 Documentation Organisée" README.md; then
    cat >> README.md << 'EOF'

## 📚 Documentation Organisée

La documentation du projet a été réorganisée pour une meilleure navigation :

- **[📁 Guide de Documentation](documentation/README.md)** - Index complet de la documentation
- **[🧪 Guide des Tests](testing/README.md)** - Tests et validation du système
- **[🔧 Scripts de Gestion](scripts/README.md)** - Scripts d'administration

### Structure Organisée
```
📁 documentation/          # Documentation technique et utilisateur
├── user-guides/          # Guides d'utilisation
├── technical/            # Documentation technique
├── deployment/           # Guides de déploiement
└── api/                  # Documentation API

📁 testing/               # Tests organisés par type
├── unit/                 # Tests unitaires
├── integration/          # Tests d'intégration
└── api/                  # Tests API spécialisés
```

EOF
    print_status "Section documentation ajoutée au README principal"
fi

echo "🔍 Vérification de l'état Git..."

# Affichage des fichiers qui seront commités
echo ""
echo "📋 Résumé des changements:"
echo "=========================="

# Nouveaux fichiers créés
echo "✅ Nouveaux fichiers créés:"
echo "  - documentation/README.md"
echo "  - testing/README.md"
echo "  - testing/conftest.py"
echo "  - testing/requirements-test.txt"
echo "  - Makefile"

# Fichiers déplacés
echo ""
echo "📁 Fichiers déplacés vers documentation/:"
ls -la documentation/*/ 2>/dev/null | grep -E '\.(md|txt)$' | wc -l | xargs echo "  -" 2>/dev/null || echo "  - Aucun fichier déplacé"

echo ""
echo "🧪 Fichiers déplacés vers testing/:"
find testing/ -name "*.py" -type f | wc -l | xargs echo "  - Scripts de test:" 2>/dev/null || echo "  - Aucun fichier de test"

echo ""
echo "🗑️ Fichiers temporaires supprimés:"
for file in "${temp_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "  - $file"
    fi
done

echo ""
echo "======================================="
print_status "Organisation terminée avec succès!"
echo ""
echo "📝 Prochaines étapes recommandées:"
echo "1. Vérifiez les changements: git status"
echo "2. Testez la nouvelle structure: make test"
echo "3. Mettez à jour les liens dans la documentation si nécessaire"
echo "4. Commitez les changements: git add . && git commit -m 'Réorganisation documentation et tests'"
echo ""
echo "💡 Utilisez 'make help' pour voir les nouvelles commandes disponibles"
