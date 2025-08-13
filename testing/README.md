# 🧪 Tests du Projet EIR

## 📋 Vue d'Ensemble

Ce dossier contient tous les tests pour le projet EIR, organisés par type et fonctionnalité. Les tests garantissent la qualité, la fiabilité et la performance du système.

## 📁 Structure des Tests

```
testing/
├── README.md                    # Ce fichier - Guide des tests
├── conftest.py                  # Configuration pytest globale
├── requirements-test.txt        # Dépendances pour les tests
├── unit/                       # Tests unitaires
│   ├── __init__.py
│   ├── test_api.py             # Tests API backend
│   ├── test_models.py          # Tests modèles de données
│   ├── test_auth.py            # Tests authentification
│   ├── test_imei_validation.py # Tests validation IMEI
│   └── test_notifications.py   # Tests système notifications
├── integration/                # Tests d'intégration
│   ├── __init__.py
│   ├── test_full_workflow.py   # Tests workflow complet
│   ├── test_database.py        # Tests intégration DB
│   ├── test_email_system.py    # Tests système email
│   └── test_api_integration.py # Tests intégration API
└── api/                        # Tests API spécialisés
    ├── __init__.py
    ├── test_endpoints.py       # Tests tous endpoints
    ├── test_performance.py     # Tests performance
    ├── test_security.py        # Tests sécurité
    ├── api_test_config.json    # Configuration tests API
    └── test_data.json          # Données de test
```

## 🚀 Exécution des Tests

### Prérequis
```bash
# Installation des dépendances de test
pip install -r testing/requirements-test.txt

# Ou avec l'environnement principal
pip install pytest pytest-asyncio pytest-cov requests-mock
```

### Tests Unitaires
```bash
# Tous les tests unitaires
python -m pytest testing/unit/ -v

# Test spécifique
python -m pytest testing/unit/test_api.py -v

# Tests avec couverture
python -m pytest testing/unit/ --cov=backend/app --cov-report=html
```

### Tests d'Intégration
```bash
# Tous les tests d'intégration
python -m pytest testing/integration/ -v

# Tests avec base de données de test
python -m pytest testing/integration/test_database.py -v
```

### Tests API
```bash
# Tests API complets
python -m pytest testing/api/ -v

# Tests de performance
python -m pytest testing/api/test_performance.py -v

# Tests de sécurité
python -m pytest testing/api/test_security.py -v
```

### Tous les Tests
```bash
# Exécution complète avec rapport
python -m pytest testing/ -v --cov=backend/app --cov-report=html --cov-report=term

# Tests en parallèle (plus rapide)
python -m pytest testing/ -n auto
```

## 🔧 Configuration des Tests

### Variables d'Environnement de Test
```bash
# .env.test
TEST_DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_eir
TEST_SECRET_KEY=test-secret-key-for-testing-only
TEST_EMAIL_BACKEND=console
TEST_DEBUG=true
```

### Configuration pytest
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    # Headers avec token de test
    return {"Authorization": "Bearer test-token"}
```

## 📊 Types de Tests

### 1. Tests Unitaires (`unit/`)
- **Validation des fonctions individuelles**
- **Modèles de données**
- **Logique métier**
- **Validation IMEI**
- **Authentification**

### 2. Tests d'Intégration (`integration/`)
- **Workflow complets utilisateur**
- **Intégration base de données**
- **Système de notifications**
- **Intégration services externes**

### 3. Tests API (`api/`)
- **Tous les endpoints**
- **Codes de statut HTTP**
- **Format des réponses**
- **Sécurité et authentification**
- **Performance sous charge**

## 🎯 Exemples de Tests

### Test Unitaire - Validation IMEI
```python
# testing/unit/test_imei_validation.py
def test_validate_imei_valid():
    """Test validation IMEI valide"""
    result = validate_imei("123456789012345")
    assert result.is_valid == True
    assert result.tac == "12345678"

def test_validate_imei_invalid():
    """Test validation IMEI invalide"""
    result = validate_imei("invalid")
    assert result.is_valid == False
    assert "format" in result.error.lower()
```

### Test API - Endpoint IMEI
```python
# testing/api/test_endpoints.py
def test_get_imei_found(client, auth_headers):
    """Test récupération IMEI existant"""
    response = client.get(
        "/imei/123456789012345",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "123456789012345" in response.json()["imei"]

def test_get_imei_not_found(client, auth_headers):
    """Test IMEI non trouvé"""
    response = client.get(
        "/imei/999999999999999",
        headers=auth_headers
    )
    assert response.status_code == 404
```

### Test d'Intégration - Workflow Complet
```python
# testing/integration/test_full_workflow.py
def test_complete_user_workflow(client):
    """Test workflow complet utilisateur"""
    # 1. Inscription
    register_response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert register_response.status_code == 201
    
    # 2. Connexion
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # 3. Recherche IMEI
    headers = {"Authorization": f"Bearer {token}"}
    imei_response = client.get("/imei/123456789012345", headers=headers)
    assert imei_response.status_code == 200
```

## 📈 Métriques et Rapports

### Couverture de Code
```bash
# Génération rapport de couverture
python -m pytest testing/ --cov=backend/app --cov-report=html

# Visualisation
open htmlcov/index.html
```

### Tests de Performance
```bash
# Tests de charge avec locust
pip install locust
locust -f testing/performance/locustfile.py --host=http://localhost:8000
```

### Rapport de Tests
```bash
# Rapport JUnit pour CI/CD
python -m pytest testing/ --junitxml=test-results.xml

# Rapport HTML détaillé
python -m pytest testing/ --html=report.html --self-contained-html
```

## 🔄 Intégration CI/CD

### GitHub Actions
```yaml
# .github/workflows/tests.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r testing/requirements-test.txt
    - name: Run tests
      run: python -m pytest testing/ --cov=backend/app
```

## 🛠️ Outils de Test

### Dépendances Principales
- **pytest** - Framework de test principal
- **pytest-asyncio** - Support tests asynchrones
- **pytest-cov** - Couverture de code
- **requests-mock** - Mock des requêtes HTTP
- **factory-boy** - Génération de données de test
- **faker** - Données factices réalistes

### Installation
```bash
pip install pytest pytest-asyncio pytest-cov requests-mock factory-boy faker
```

## 📝 Bonnes Pratiques

### Nommage
- **Fichiers** : `test_*.py` ou `*_test.py`
- **Fonctions** : `test_action_expected_result()`
- **Classes** : `TestFeatureName`

### Structure des Tests
```python
def test_feature_description():
    # Arrange (Préparation)
    setup_data()
    
    # Act (Action)
    result = function_to_test()
    
    # Assert (Vérification)
    assert result == expected_value
```

### Fixtures et Mocks
```python
@pytest.fixture
def sample_user():
    return User(email="test@example.com", name="Test User")

@pytest.mark.parametrize("imei,expected", [
    ("123456789012345", True),
    ("invalid", False),
])
def test_imei_validation(imei, expected):
    assert validate_imei(imei).is_valid == expected
```

## 🚨 Résolution de Problèmes

### Tests qui Échouent
1. **Vérifier les dépendances** : `pip install -r testing/requirements-test.txt`
2. **Base de données de test** : Vérifier la connexion DB de test
3. **Variables d'environnement** : Charger `.env.test`
4. **Logs détaillés** : `pytest -v -s`

### Tests Lents
1. **Parallélisation** : `pytest -n auto`
2. **Tests spécifiques** : `pytest testing/unit/test_specific.py`
3. **Profiling** : `pytest --profile`

## 📞 Support

Pour les questions sur les tests :
1. Consultez ce README
2. Vérifiez les exemples dans les fichiers de test
3. Créez une issue GitHub pour les bugs

---

*Documentation mise à jour le : 12 août 2025*
