# 🚀 API EIR Tests v2.0 - Configuration Centralisée

## 🎯 Nouveautés Version 2.0

### ✨ **Configuration Centralisée**
- 📋 **42 endpoints** définis dans `api_endpoints_config.py`
- 🎯 **6 groupes de test** prédéfinis (smoke, core, full, etc.)
- 🏷️ **Tags et priorités** pour organiser les tests
- 📊 **Métadonnées complètes** pour chaque endpoint

### 🛠️ **Nouveaux Scripts**

#### 1. **`api_endpoints_config.py`** - Configuration Centrale
```python
# Configuration complète de tous les endpoints
ENDPOINTS = {
    "system": {...},
    "auth": {...},
    "devices": {...},
    # ... 12 catégories au total
}
```

#### 2. **`test_api_v2.py`** - Testeur Avancé
```bash
# Tests par groupe
python3 test_api_v2.py --group smoke    # Tests critiques
python3 test_api_v2.py --group core     # Tests essentiels  
python3 test_api_v2.py --group all      # Tous les endpoints

# Tests par tag
python3 test_api_v2.py --tag Admin      # Endpoints admin
python3 test_api_v2.py --tag Public     # Endpoints publics

# Informations
python3 test_api_v2.py --list-groups    # Lister les groupes
python3 test_api_v2.py --list-endpoints # Lister tous les endpoints
```

#### 3. **`quick_api_test_v2.sh`** - Test Rapide v2
```bash
./quick_api_test_v2.sh [URL]  # Tests smoke en ~5 secondes
```

#### 4. **`run_api_tests_v2.sh`** - Tests Complets v2
```bash
./run_api_tests_v2.sh [URL] [GROUPE]

# Exemples
./run_api_tests_v2.sh                           # Tests core
./run_api_tests_v2.sh http://localhost:8000 all # Tous les tests
./run_api_tests_v2.sh https://api.prod.com smoke # Tests smoke en prod
```

## 📊 Groupes de Test Disponibles

| Groupe | Endpoints | Description |
|--------|-----------|-------------|
| 🚀 **smoke** | 4 | Tests critiques ultra-rapides |
| 🎯 **core** | 9 | Tests essentiels pour validation |
| 🔐 **authenticated** | 34 | Tous les endpoints nécessitant auth |
| 🌐 **public** | 8 | Tous les endpoints publics |
| 👑 **admin** | 7 | Endpoints administratifs |
| 🌍 **all** | 42 | Tous les endpoints disponibles |

## 🏷️ Tags et Priorités

### **Tags par Fonctionnalité:**
- `Système` - Endpoints de base (health, welcome)
- `Authentification` - Login, logout, profil
- `IMEI` - Recherche et validation IMEI
- `Appareils` - Gestion des dispositifs
- `Admin` - Opérations administratives
- `Public` - Endpoints sans authentification

### **Priorités de Test:**
- 🔴 **High** - Endpoints critiques (8 endpoints)
- 🟡 **Medium** - Endpoints importants (25 endpoints)
- 🟢 **Low** - Endpoints secondaires (9 endpoints)

## 🎮 Utilisation via Menu

Le menu interactif inclut maintenant les tests v2 :

```bash
./menu_tests.sh

# Nouvelles options v2.0
12. Test Rapide v2 (smoke)     - Endpoints critiques
13. Tests Core v2 (core)       - Endpoints essentiels  
14. Tests Complets v2 (all)    - Configuration centralisée
```

## 📋 Avantages de la v2.0

### ✅ **Configuration Unifiée**
- ✨ **Une seule source de vérité** pour tous les endpoints
- 🔄 **Évite la duplication** entre scripts
- 📝 **Documentation automatique** des endpoints
- 🛠️ **Maintenance simplifiée**

### ✅ **Tests Plus Intelligents**
- 🎯 **Tests ciblés** par groupe ou tag
- 📊 **Métriques détaillées** (temps, priorités)
- 🔍 **Validation automatique** des champs attendus
- 📈 **Rapports enrichis** avec métadonnées

### ✅ **Flexibilité**
- 🌐 **Support multi-environnement** (dev, staging, prod)
- 🏷️ **Tests personnalisés** par tag
- ⚙️ **Configuration modulaire** par catégorie
- 📊 **Analyse granulaire** des résultats

## 🔧 Configuration des Endpoints

Chaque endpoint est défini avec :

```python
"endpoint_name": {
    "path": "/api/endpoint",
    "method": "GET|POST|PUT|DELETE",
    "summary": "Description courte",
    "tags": ["Catégorie1", "Catégorie2"],
    "auth_required": True|False,
    "test_priority": "high|medium|low",
    "expected_fields": ["champ1", "champ2"],
    "test_data": {...},  # Données pour POST/PUT
    "path_params": {...} # Paramètres d'URL
}
```

## 📊 Exemple de Rapport v2

```json
{
  "summary": {
    "total_tests": 42,
    "passed": 38,
    "failed": 2,
    "warnings": 2,
    "test_group": "all",
    "duration": 15.3
  },
  "results": [
    {
      "name": "Bienvenue API",
      "category": "system", 
      "tags": ["Système"],
      "status": "PASS",
      "response_time": 0.045,
      ...
    }
  ]
}
```

## 🚀 Migration v1 → v2

### **Scripts Existants (v1)**
- ✅ Conservés et fonctionnels
- 📝 `test_api_endpoints.py` (v1)
- 🚀 `quick_api_test.sh` (v1)
- 🔧 `run_api_tests.sh` (v1)

### **Nouveaux Scripts (v2)**
- 🆕 `api_endpoints_config.py` - Configuration centrale
- 🆕 `test_api_v2.py` - Testeur avancé
- 🆕 `quick_api_test_v2.sh` - Test rapide v2
- 🆕 `run_api_tests_v2.sh` - Tests complets v2

### **Recommandations**
- 🎯 **Utilisez v2** pour nouveaux tests
- 📊 **v2 offre plus de fonctionnalités**
- 🔄 **v1 reste disponible** pour compatibilité

## 💡 Cas d'Usage Typiques

### **Développement**
```bash
# Tests rapides pendant le développement
./quick_api_test_v2.sh

# Tests core après changements
python3 test_api_v2.py --group core
```

### **CI/CD**
```bash
# Tests smoke en pré-production
python3 test_api_v2.py --group smoke

# Tests complets avant release
python3 test_api_v2.py --group all
```

### **Production**
```bash
# Monitoring endpoints publics
python3 test_api_v2.py --tag Public

# Validation admin après maintenance
python3 test_api_v2.py --tag Admin
```

## 📞 Support et Debug

### **Problèmes Courants**
```bash
# Module manquant
pip3 install requests

# Permissions
chmod +x *.sh

# API non accessible
docker-compose ps
sudo docker logs eir_web
```

### **Debug Avancé**
```bash
# Tests détaillés avec verbose
python3 test_api_v2.py --group core --verbose

# Test d'un endpoint spécifique
python3 test_api_v2.py --tag IMEI

# Analyse de rapport
python3 analyze_test_results.py api_test_report_v2_*.json
```

---

🎉 **La version 2.0 offre une approche moderne et structurée pour tester l'API EIR avec une configuration centralisée et des fonctionnalités avancées !**
