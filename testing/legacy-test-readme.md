# 🧪 Suite de Tests API EIR Project

Ce répertoire contient une suite complète d'outils de test pour l'API EIR Project, permettant de valider tous les endpoints, vérifier la conformité et automatiser les tests de régression.

## 📁 Structure des Fichiers

```
test/
├── api_endpoints.json          # Configuration complète des endpoints
├── test_api_comprehensive.py   # Script de test principal
├── validate_endpoints.py       # Validateur de conformité des endpoints
├── README.md                   # Ce fichier
└── quick_api_test.sh           # Script de test rapide (racine du projet)
```

## 🚀 Démarrage Rapide

### Test Rapide
```bash
# Depuis la racine du projet
./quick_api_test.sh -q
```

### Test Complet
```bash
./quick_api_test.sh -f -a
```

### Test d'un Groupe Spécifique
```bash
./quick_api_test.sh auth
./quick_api_test.sh devices -a
```

## 📋 Configuration des Endpoints

Le fichier `api_endpoints.json` contient la configuration complète de tous les endpoints de l'API :

### Structure de Configuration

```json
{
  "endpoints": {
    "category": {
      "endpoint_name": {
        "method": "GET|POST|PUT|DELETE",
        "path": "/api/path/{param}",
        "description": "Description de l'endpoint",
        "test_data": {
          "key": "value"
        },
        "expected_fields": ["field1", "field2"],
        "content_type": "application/json",
        "path_params": {
          "param": "test_value"
        }
      }
    }
  },
  "test_groups": {
    "group_name": [
      "category.endpoint_name"
    ]
  }
}
```

### Catégories d'Endpoints

1. **auth** - Authentification et autorisation
2. **users** - Gestion des utilisateurs
3. **devices** - Gestion des appareils et IMEI
4. **notifications** - Système de notifications
5. **access** - Gestion des accès et permissions
6. **admin** - Fonctions administratives
7. **import** - Import/export de données
8. **protocols** - Protocoles de vérification
9. **debug** - Outils de débogage

## 🔧 Outils de Test

### 1. Script de Test Complet (`test_api_comprehensive.py`)

Script Python avancé pour tester tous les endpoints avec rapports détaillés.

#### Utilisation
```bash
python3 test/test_api_comprehensive.py [OPTIONS]
```

#### Options
- `--base-url URL` : URL de base de l'API (défaut: http://localhost:8000)
- `--group GROUP` : Tester un groupe spécifique
- `--list-groups` : Lister les groupes disponibles
- `--auth` : Activer l'authentification admin
- `--config FILE` : Fichier de configuration

#### Exemples
```bash
# Test complet
python3 test/test_api_comprehensive.py --auth

# Test d'un groupe spécifique
python3 test/test_api_comprehensive.py --group auth

# Test sur serveur distant
python3 test/test_api_comprehensive.py --base-url https://api.example.com --auth

# Lister les groupes disponibles
python3 test/test_api_comprehensive.py --list-groups
```

#### Fonctionnalités
- ✅ Authentification automatique
- ✅ Tests par groupe ou complets
- ✅ Mesure des temps de réponse
- ✅ Validation des champs attendus
- ✅ Rapports détaillés avec statistiques
- ✅ Gestion des erreurs et retry

### 2. Script de Test Rapide (`quick_api_test.sh`)

Script Bash pour des tests rapides et validation de base.

#### Utilisation
```bash
./quick_api_test.sh [OPTIONS] [GROUP]
```

#### Options
- `-h, --help` : Afficher l'aide
- `-u, --url URL` : URL de base de l'API
- `-a, --auth` : Activer l'authentification admin
- `-l, --list` : Lister les groupes disponibles
- `-q, --quick` : Test rapide (endpoints de base)
- `-f, --full` : Test complet
- `-v, --verbose` : Mode verbeux
- `--no-setup` : Ne pas configurer l'environnement Python

#### Exemples
```bash
# Test rapide
./quick_api_test.sh -q

# Test complet avec auth
./quick_api_test.sh -f -a

# Test d'un groupe spécifique
./quick_api_test.sh devices -a

# Test sur serveur distant
./quick_api_test.sh -u https://api.example.com -f
```

### 3. Validateur d'Endpoints (`validate_endpoints.py`)

Outil pour vérifier la conformité entre la configuration et l'implémentation réelle.

#### Utilisation
```bash
python3 test/validate_endpoints.py [OPTIONS]
```

#### Options
- `--suggest` : Générer des suggestions pour les endpoints manquants
- `--config FILE` : Fichier de configuration
- `--app-dir DIR` : Répertoire de l'application

#### Exemples
```bash
# Validation basique
python3 test/validate_endpoints.py

# Avec suggestions
python3 test/validate_endpoints.py --suggest

# Configuration personnalisée
python3 test/validate_endpoints.py --config custom.json --app-dir ../backend/app
```

#### Fonctionnalités
- 🔍 Analyse du code source FastAPI
- 📊 Comparaison avec la configuration
- ⚠️ Détection des endpoints manquants
- 💡 Génération automatique de configurations
- 📈 Statistiques de couverture

## 📊 Groupes de Test

### Groupes Disponibles

1. **basic** - Tests de base
   - health check
   - info système
   - documentation

2. **auth** - Authentification
   - login/logout
   - gestion des tokens
   - reset password

3. **devices** - Gestion des appareils
   - CRUD appareils
   - validation IMEI
   - recherche

4. **notifications** - Notifications
   - envoi de notifications
   - gestion des templates
   - configuration

5. **admin** - Administration
   - gestion des utilisateurs
   - logs d'audit
   - configuration système

6. **import** - Import/Export
   - import CSV/JSON
   - export de données
   - validation des fichiers

### Exécution par Groupe

```bash
# Test des authentifications
./quick_api_test.sh auth

# Test des appareils avec auth admin
./quick_api_test.sh devices -a

# Test des notifications
./quick_api_test.sh notifications -a
```

## 🔧 Configuration de l'Environnement

### Prérequis
- Python 3.8+
- Bibliothèque `requests`
- API EIR Project en cours d'exécution

### Installation des Dépendances
```bash
pip install requests
# ou dans l'environnement virtuel
source backend/venv/bin/activate
pip install requests
```

### Variables d'Environnement

Créez un fichier `.env` pour la configuration :

```bash
# URL de l'API
API_BASE_URL=http://localhost:8000

# Authentification admin
ADMIN_USERNAME=admin@eir.com
ADMIN_PASSWORD=admin123

# Configuration de test
TEST_TIMEOUT=30
TEST_RETRIES=3
```

## 📈 Rapports de Test

### Format de Rapport

Les rapports incluent :
- 📊 Statistiques globales
- ✅ Tests réussis
- ❌ Tests échoués avec détails
- ⏱️ Temps de réponse moyens
- 🐌 Endpoints lents (>1s)

### Exemple de Sortie

```
================================================================================
📋 RAPPORT DE TEST DÉTAILLÉ
================================================================================
📊 Résumé Global:
   • Total des tests: 45
   • Succès: 42
   • Échecs: 3
   • Taux de réussite: 93.3%

❌ Tests échoués (3):
   • devices.bulk_import: HTTP 422 - Validation error
   • notifications.send_bulk: HTTP 403 - Insufficient permissions
   • admin.delete_user: HTTP 404 - User not found

⏱️  Temps de réponse moyen: 156.7ms

🐌 Endpoints lents (>1s):
   • import.process_large_file: 2340ms
   • devices.validate_batch: 1450ms
```

## 🚨 Débogage

### Problèmes Courants

1. **API non accessible**
   ```bash
   # Vérifier que l'API est démarrée
   curl http://localhost:8000/health
   
   # Ou utiliser le test rapide
   ./quick_api_test.sh -q
   ```

2. **Échec d'authentification**
   ```bash
   # Vérifier les credentials admin
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin@eir.com","password":"admin123"}'
   ```

3. **Dépendances manquantes**
   ```bash
   # Installer les dépendances
   pip install -r backend/requirements.txt
   ```

### Logs Détaillés

Pour des logs détaillés :
```bash
# Mode verbeux
./quick_api_test.sh -v -f

# Ou directement avec Python
python3 test/test_api_comprehensive.py --auth --base-url http://localhost:8000
```

## 🔄 Intégration CI/CD

### GitHub Actions

Exemple de workflow :

```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup API
        run: docker-compose up -d
      - name: Run API Tests
        run: ./quick_api_test.sh -f -a
```

### Scripts de Validation

Pour les hooks pre-commit :
```bash
#!/bin/bash
echo "Validation des endpoints..."
python3 test/validate_endpoints.py
if [ $? -ne 0 ]; then
    echo "❌ Validation échouée"
    exit 1
fi
echo "✅ Validation réussie"
```

## 📚 Documentation API

Les tests génèrent automatiquement de la documentation basée sur :
- 📝 Endpoints disponibles
- 🔧 Paramètres requis
- 📊 Formats de réponse
- ⚡ Exemples d'utilisation

Pour générer la documentation :
```bash
python3 test/test_api_comprehensive.py --list-groups > API_ENDPOINTS.md
```

---

Pour plus d'informations, consultez la [documentation principale](../README.md) du projet EIR.
