# 📊 Guide d'Alimentation de la Base de Données EIR

Ce document explique comment alimenter la base de données de votre projet EIR avec différentes méthodes.

## 🎯 Vue d'ensemble

Votre projet EIR dispose de **4 méthodes principales** pour alimenter la base de données :

1. **📋 Données de test automatiques** (développement)
2. **📁 Import via fichiers CSV** (production)
3. **🔄 Synchronisation via API** (intégration systèmes externes)
4. **💾 Import manuel via SQL** (avancé)

---

## 🚀 Méthode 1 : Données de Test (Recommandée pour développement)

### Utilisation rapide :
```bash
cd /home/mohamed/Documents/projects/eir-project
./scripts/alimenter-base-donnees.sh --test-data
```

### Contenu des données de test :
- ✅ **5 utilisateurs** avec différents niveaux d'accès :
  - `eirrproject@gmail.com` (Administrateur)
  - `user@example.com` (Utilisateur standard)
  - `insurance@company.com` (Compagnie d'assurance)
  - `police@cybercrime.gov` (Forces de l'ordre)
  - `manufacturer@techcorp.com` (Fabricant)

- ✅ **3 appareils** avec IMEIs :
  - Samsung Galaxy S21 (`352745080123456`)
  - Apple iPhone 13 (`354123456789012`)
  - TechCorp TC-Pro-2024 (`352745080987654`)

- ✅ **1 carte SIM** et historique de recherches

### Mot de passe pour tous les utilisateurs de test :
```
admin123
```

---

## 📁 Méthode 2 : Import CSV (Recommandée pour production)

### Étape 1 : Créer un modèle CSV
```bash
./scripts/alimenter-base-donnees.sh --template
```

Cela crée le fichier `data/sample_devices.csv` :
```csv
imei,marque,modele,emmc
123456789012345,Samsung,Galaxy S23,256GB
987654321098765,Apple,iPhone 14,128GB
456789012345678,Huawei,P50 Pro,512GB
```

### Étape 2 : Modifier le fichier avec vos données
Éditez `data/sample_devices.csv` ou créez votre propre fichier CSV avec le même format.

### Étape 3 : Importer le fichier
```bash
./scripts/alimenter-base-donnees.sh --csv data/sample_devices.csv
```

### Format CSV requis :
- **imei** : Numéro IMEI (15 chiffres)
- **marque** : Marque de l'appareil
- **modele** : Modèle de l'appareil  
- **emmc** : Capacité de stockage (optionnel)

---

## 🔄 Méthode 3 : Synchronisation via API (Intégration systèmes)

### Utilisation de l'endpoint `/sync-device` :

```bash
curl -X POST "http://localhost:8000/sync-device" \
  -H "Content-Type: application/json" \
  -d '{
    "appareils": [
      {
        "imei": "123456789012345",
        "marque": "Samsung",
        "modele": "Galaxy S24",
        "statut": "actif",
        "emmc": "256GB",
        "metadata": {
          "source_dms": "system_external",
          "batch_id": "BATCH_001"
        }
      }
    ],
    "sync_mode": "upsert",
    "source_system": "External_DMS"
  }'
```

### Modes de synchronisation :
- **`upsert`** : Créer ou mettre à jour (défaut)
- **`insert_only`** : Créer uniquement (ignorer si existe)
- **`update_only`** : Mettre à jour uniquement (ignorer si n'existe pas)

### Test rapide :
```bash
./scripts/alimenter-base-donnees.sh --sync-api
```

---

## 💾 Méthode 4 : Import SQL Manuel (Avancé)

### Import direct via PostgreSQL :
```bash
# Copier votre fichier SQL dans le conteneur
docker compose cp mon_fichier.sql db:/tmp/mon_fichier.sql

# Exécuter le script
docker compose exec db psql -U postgres -d eir_project -f /tmp/mon_fichier.sql
```

### Format SQL recommandé :
```sql
-- Insérer un utilisateur
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur)
VALUES (gen_random_uuid(), 'Nom Utilisateur', 'email@example.com', 'mot_de_passe_hashé', 'utilisateur_authentifie');

-- Insérer un appareil
INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
VALUES (gen_random_uuid(), 'Samsung', 'Galaxy S25', '512GB', NULL);

-- Insérer un IMEI
INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
VALUES (gen_random_uuid(), '123456789012345', 1, 'active', 'appareil_id_ici');
```

---

## 🛠️ Script d'Administration Complet

### Utilisation interactive :
```bash
./scripts/alimenter-base-donnees.sh
```

### Options disponibles :
- **Option 1** : Charger données de test
- **Option 2** : Créer modèle CSV
- **Option 3** : Importer depuis CSV
- **Option 4** : Synchroniser via API
- **Option 5** : Afficher statistiques
- **Option 6** : Créer sauvegarde
- **Option 7** : Quitter

### Utilisation en ligne de commande :
```bash
# Afficher les statistiques
./scripts/alimenter-base-donnees.sh --stats

# Créer une sauvegarde
./scripts/alimenter-base-donnees.sh --backup

# Afficher l'aide
./scripts/alimenter-base-donnees.sh --help
```

---

## 📊 Vérification et Monitoring

### 1. Vérifier l'état de l'API :
```bash
curl http://localhost:8000/health
```

### 2. Tester une recherche IMEI :
```bash
curl "http://localhost:8000/imei/352745080123456"
```

### 3. Afficher les statistiques de la base :
```bash
./scripts/alimenter-base-donnees.sh --stats
```

### 4. Vérifier les protocoles multi-protocoles :
```bash
curl http://localhost:8000/protocols/status
```

---

## 🔧 Résolution de Problèmes

### Conteneurs non démarrés :
```bash
docker compose up -d
```

### Base de données corrompue :
```bash
./scripts/rebuild-database.sh
```

### Réinitialisation complète :
```bash
./scripts/reset-database.sh
```

### Logs en cas d'erreur :
```bash
# Logs de l'API
docker logs eir_web -f

# Logs de la base de données
docker logs eir_db -f
```

---

## 🎯 Recommandations par Environnement

### **Développement** :
- Utilisez `--test-data` pour des données cohérentes
- Utilisez `--stats` pour monitoring
- Créez des sauvegardes avant tests : `--backup`

### **Test/Staging** :
- Utilisez l'import CSV pour des données réalistes
- Testez les API de synchronisation
- Vérifiez les performances avec `curl http://localhost:8000/health`

### **Production** :
- Utilisez UNIQUEMENT l'API `/sync-device` pour l'intégration
- Planifiez des sauvegardes régulières : `--backup`
- Surveillez les logs et statistiques

---

## 📞 Support et Documentation

- **Documentation API** : http://localhost:8000/docs
- **Health Check** : http://localhost:8000/health
- **Statut Protocoles** : http://localhost:8000/protocols/status
- **Documentation technique** : `/docs/architecture_multi_protocoles_concis.tex`

---

*Ce guide couvre toutes les méthodes d'alimentation de votre base de données EIR. Choisissez la méthode qui correspond le mieux à votre cas d'usage.*
