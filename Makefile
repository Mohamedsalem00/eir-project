# Makefile pour le projet EIR
# Simplification des commandes de développement et test

.PHONY: help test test-unit test-integration test-api test-all coverage clean install-test

help:
	@echo "🚀 Commandes disponibles pour le projet EIR:"
	@echo ""
	@echo "🧪 Tests :"
	@echo "  make test                  - Exécuter tous les tests"
	@echo "  make test-unit             - Tests unitaires seulement"
	@echo "  make test-integration      - Tests d'intégration seulement"
	@echo "  make test-api              - Tests API seulement"
	@echo "  make test-api-scripts      - Tests API via scripts"
	@echo "  make test-notifications-scripts - Tests notifications via scripts"
	@echo "  make test-system-scripts   - Tests système via scripts"
	@echo "  make coverage              - Tests avec rapport de couverture"
	@echo ""
	@echo "🐳 Docker :"
	@echo "  make docker-start          - Démarrer l'environnement"
	@echo "  make docker-stop           - Arrêter l'environnement"  
	@echo "  make docker-restart        - Redémarrer l'environnement"
	@echo "  make docker-rebuild        - Reconstruction complète"
	@echo ""
	@echo "🗄️  Base de Données :"
	@echo "  make db-rebuild            - Reconstruction complète DB"
	@echo "  make db-reset              - Reset rapide DB"
	@echo "  make db-manage             - Gestion interactive DB"
	@echo ""
	@echo "🛠️  Utilitaires :"
	@echo "  make install-test          - Installer dépendances de test"
	@echo "  make clean                 - Nettoyer fichiers temporaires"
	@echo "  make scripts-help          - Voir tous les scripts disponibles"

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
	rm -f *.sh.backup *.sh.tmp
	@echo "🧹 Nettoyage terminé"

# === SCRIPTS ET UTILITAIRES ===
scripts-help:
	@echo "📜 Scripts disponibles :"
	@echo ""
	@echo "🐳 Gestion Docker :"
	@echo "  ./scripts/manage-eir.sh           - Menu interactif principal"
	@echo "  ./scripts/rebuild-containers.sh   - Reconstruction complète"
	@echo "  ./scripts/restart-containers.sh   - Redémarrage rapide"
	@echo ""
	@echo "🗄️  Base de Données :"
	@echo "  ./scripts/rebuild-database.sh     - Reconstruction complète DB"
	@echo "  ./scripts/reset-database.sh       - Reset rapide DB"
	@echo "  ./scripts/gestion-base-donnees.sh - Gestion interactive DB"
	@echo ""
	@echo "⚙️  Configuration :"
	@echo "  ./scripts/configurer-apis-externes.sh - Config APIs externes"
	@echo "  ./scripts/setup-notifications.sh      - Config notifications"
	@echo ""
	@echo "🧪 Tests (via make test recommandé) :"
	@echo "  ./testing/scripts/api/             - Tests API"
	@echo "  ./testing/scripts/notifications/   - Tests notifications"
	@echo "  ./testing/scripts/system/          - Tests système"

# Commandes Docker simplifiées
docker-start:
	@echo "🚀 Démarrage de l'environnement Docker..."
	@./scripts/manage-eir.sh start || ./eir-docker.sh start

docker-stop:
	@echo "🛑 Arrêt de l'environnement Docker..."
	@./scripts/manage-eir.sh stop || ./eir-docker.sh stop

docker-restart:
	@echo "🔄 Redémarrage de l'environnement Docker..."
	@./scripts/restart-containers.sh

docker-rebuild:
	@echo "🔧 Reconstruction complète des conteneurs..."
	@./scripts/rebuild-containers.sh

# Commandes base de données simplifiées  
db-rebuild:
	@echo "🗄️  Reconstruction de la base de données..."
	@./scripts/rebuild-database.sh

db-reset:
	@echo "🔄 Reset de la base de données..."
	@./scripts/reset-database.sh

db-manage:
	@echo "⚙️  Gestion interactive de la base de données..."
	@./scripts/gestion-base-donnees.sh

# Tests spécialisés
test-api-scripts:
	@echo "🔗 Lancement des tests API via scripts..."
	@./testing/scripts/api/test-complete-api.sh
	@./testing/scripts/api/test-apis-externes.sh

test-notifications-scripts:
	@echo "📬 Lancement des tests notifications via scripts..."
	@./testing/scripts/notifications/test-eir-notifications.sh
	@./testing/scripts/notifications/test-notifications.sh

test-system-scripts:
	@echo "🖥️  Lancement des tests système via scripts..."
	@./testing/scripts/system/test-system.sh
	@./testing/scripts/system/test-updated-data.sh

# Commande pour nettoyer les anciens scripts (déjà exécuté)
cleanup-old-scripts:
	@echo "ℹ️  Nettoyage des scripts obsolètes déjà effectué"
	@echo "📊 Voir documentation/technical/SCRIPTS_CLEANUP_REPORT.md pour le rapport"
