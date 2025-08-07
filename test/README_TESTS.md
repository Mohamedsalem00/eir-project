# Scripts de Test API EIR 🧪

Ce dossier contient une suite complète de scripts pour tester tous les endpoints de l'API EIR francisée.

## 📋 Scripts Disponibles

### 1. **Test Rapide** - `quick_api_test.sh`
```bash
./quick_api_test.sh
```
- ✅ Test rapide des endpoints critiques
- ⚡ Exécution en ~5 secondes
- 🎯 Parfait pour vérification de base

### 2. **Tests Complets** - `run_api_tests.sh`
```bash
./run_api_tests.sh [URL_API]
```
- 🔬 Test de tous les endpoints disponibles
- 📊 Rapport détaillé avec métriques
- 💾 Sauvegarde en JSON pour analyse
- ⏱️ Durée: ~1 minute

### 3. **Analyseur de Résultats** - `analyze_test_results.py`
```bash
python3 analyze_test_results.py [fichier_rapport.json]
```
- 📈 Analyse des performances
- 🔍 Détection d'erreurs
- 💡 Recommandations d'amélioration
- 📊 Statistiques de couverture

### 4. **Tableau de Bord** - `test_dashboard.sh`
```bash
./test_dashboard.sh
```
- 🎯 Interface interactive
- 📊 Statut en temps réel de l'API
- 🛠️ Actions rapides (test, redémarrage, logs)
- 📄 Historique des tests

### 5. **Tests Détaillés** - `test_api_endpoints.py`
```bash
python3 test_api_endpoints.py [URL_API]
```
- 🐍 Script Python complet
- 🔐 Tests d'authentification
- 📱 Validation des endpoints IMEI
- 👥 Tests des permissions utilisateur

## 🚀 Démarrage Rapide

1. **Vérifier que l'API fonctionne :**
   ```bash
   cd /home/mohamed/Documents/projects/eir-project
   sudo docker-compose ps
   ```

2. **Lancer le tableau de bord :**
   ```bash
   cd test
   ./test_dashboard.sh
   ```

3. **Ou exécuter directement tous les tests :**
   ```bash
   ./run_api_tests.sh
   ```

## 📊 Types de Tests

### 🔧 **Endpoints Système**
- `/` - Page d'accueil
- `/verification-etat` - Santé de l'API
- `/languages` - Langues supportées

### 📱 **Endpoints IMEI**
- `/imei/{imei}` - Recherche IMEI
- `/imei/{imei}/historique` - Historique des recherches

### 🔐 **Endpoints Authentification**
- `/authentification/connexion` - Connexion utilisateur
- `/authentification/inscription` - Inscription utilisateur
- `/authentification/deconnexion` - Déconnexion

### 👤 **Endpoints Utilisateurs**
- `/mes-permissions` - Permissions de l'utilisateur actuel
- `/utilisateurs/{id}` - Détails utilisateur
- `/admin/utilisateurs` - Liste tous les utilisateurs (admin)

### 📱 **Endpoints Appareils**
- `/appareils` - Liste/création d'appareils
- `/cartes-sim` - Gestion des cartes SIM

### 📊 **Endpoints Analyses**
- `/public/statistiques` - Statistiques publiques
- `/analyses/appareils` - Analyses des appareils
- `/analyses/recherches` - Analyses des recherches

## 🎯 Interprétation des Résultats

### ✅ **PASS** - Test réussi
- Endpoint accessible
- Réponse conforme aux attentes
- Performance acceptable

### ❌ **FAIL** - Test échoué
- Erreur serveur (500)
- Endpoint non trouvé (404)
- Problème de logique métier

### ⚠️ **WARN** - Avertissement
- Authentification requise (401) - Normal pour certains endpoints
- Autorisation refusée (403) - Normal selon les permissions
- Données partielles

## 📈 Métriques Analysées

### ⚡ **Performance**
- Temps de réponse par endpoint
- Endpoints les plus lents/rapides
- Temps moyen global

### 🔍 **Couverture**
- Endpoints testés par catégorie
- Méthodes HTTP couvertes
- Codes de réponse analysés

### 🛠️ **Qualité**
- Taux de réussite global
- Erreurs par type
- Recommandations d'amélioration

## 🔧 Dépannage

### 🚫 **API non accessible**
```bash
cd /home/mohamed/Documents/projects/eir-project
sudo docker-compose up -d
```

### 📝 **Voir les logs d'erreur**
```bash
sudo docker logs eir_web --tail 50
```

### 🔄 **Redémarrer l'API**
```bash
sudo docker-compose restart web
```

### 🗄️ **Problème de base de données**
```bash
sudo docker-compose restart db
# Ou reconstruction complète :
sudo docker-compose down
sudo docker volume rm eir-project_postgres_data
sudo docker-compose up -d
```

## 📁 Fichiers Générés

- `api_test_report_YYYYMMDD_HHMMSS.json` - Rapport détaillé des tests
- `/tmp/response.json` - Dernière réponse API (temporaire)

## 🎯 Exemples d'Utilisation

### Test d'une API distante :
```bash
./run_api_tests.sh https://api.example.com
```

### Analyse d'un rapport spécifique :
```bash
python3 analyze_test_results.py api_test_report_20250803_010544.json
```

### Intégration en CI/CD :
```bash
# Le script retourne un code d'erreur si des tests échouent
./run_api_tests.sh
if [ $? -eq 0 ]; then
    echo "Tous les tests passent ✅"
else
    echo "Des tests ont échoué ❌"
    exit 1
fi
```

## 🎨 Personnalisation

Les scripts peuvent être modifiés pour :
- Ajouter de nouveaux endpoints à tester
- Modifier les critères de performance
- Personnaliser les données de test
- Changer les formats de rapport

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez que Docker est en cours d'exécution
2. Assurez-vous que les ports 8000 et 5432 sont libres
3. Consultez les logs avec `sudo docker logs eir_web`
4. Redémarrez complètement avec `sudo docker-compose restart`
