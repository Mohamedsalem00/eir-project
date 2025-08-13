"# 🇫🇷 Projet EIR Francisé - Système de Gestion des IMEI

> **Version francisée complète** avec API entièrement traduite en français, système de permissi### 📧 Notifications et Audit
-### 📧 Notifications et Communicat### 🌍 Système et Validation
- `GET /verification-etat` - État de santé complet du système avec métriques
- `GET /languages` - Langues supportées avec détails culturels
- `GET /protocols/status` - Statut des protocoles d'intégration (SS7, Diameter)
- `GET /public/statistiques` - Statistiques publiques avec limitations
- `GET /debug-env` - Variables d'environnement (admin seulement)
- `POST /test-send-email` - Test envoi email complet
- `GET /test-email-config` - Test configuration email`GET /notifications` - Liste des notifications avec filtres avancés
- `GET /notifications/statistiques/globales` - Statistiques complètes des notifications
- `POST /admin/notifications/envoyer-a-utilisateur` - Envoi administrateur par email/utilisateur
- `POST /admin/notifications/envoyer-lot-utilisateurs` - Envoi en lot par IDs utilisateur
- `POST /admin/notifications/envoyer-lot-emails` - Envoi en lot par emails
- `GET /admin/notifications/liste-utilisateurs` - Liste utilisateurs pour notifications admin
- `POST /admin/notifications/test-email` - Test configuration email avec diagnostic
- `POST /admin/notifications/test-sms` - Test configuration SMS avec diagnostic

### 🔧 Gestion des Accès et Permissions
- `GET /admin/gestion-acces/niveaux-acces` - Niveaux d'accès disponibles avec descriptions
- `GET /admin/gestion-acces/utilisateurs` - Liste utilisateurs avec permissions détaillées
- `GET /admin/gestion-acces/utilisateurs/{id}/permissions` - Permissions granulaires utilisateur
- `PUT /admin/gestion-acces/utilisateurs/{id}/permissions` - Mise à jour permissions avec audit
- `POST /admin/gestion-acces/utilisateurs/{id}/regles-acces` - Ajouter règle d'accès
- `DELETE /admin/gestion-acces/utilisateurs/{id}/regles-acces/{index}` - Supprimer règle
- `GET /admin/gestion-acces/audit/changements-permissions` - Audit changements permissions
- `POST /admin/gestion-acces/mise-a-jour-lot-permissions` - Mise à jour permissions en lot
- `GET /admin/gestion-acces/modeles` - Modèles de permissions prédéfinis

### 📊 Administration et Audit
- `GET /admin/journaux-audit` - Consultation détaillée des journaux d'audit
- `GET /admin/notifications/scheduler/status` - Statut du planificateur avec tâches
- `POST /admin/notifications/scheduler/trigger/{job_id}` - Déclencher tâche manuelle
- `GET /admin/utilisateurs` - Gestion administrative des utilisateurs
- `POST /admin/utilisateurs/{user_id}/desactiver` - Désactiver utilisateur
- `POST /admin/utilisateurs/{user_id}/activer` - Réactiver utilisateur/notifications` - Liste des notifications avec filtres
- `GET /notifications/statistiques/globales` - Statistiques des notifications
- `POST /admin/notifications/envoyer-a-utilisateur` - Envoi administrateur par email
- `POST /admin/notifications/envoyer-lot-utilisateurs` - Envoi en lot par IDs
- `POST /admin/notifications/envoyer-lot-emails` - Envoi en lot par emails
- `GET /admin/liste-utilisateurs` - Liste pour notifications admin
- `POST /admin/test-email` - Test configuration email
- `POST /admin/test-sms` - Test configuration SMS
- `GET /admin/journaux-audit` - Consultation des journaux d'audit
- `GET /admin/notifications/scheduler/status` - Statut du planificateur
- `POST /admin/notifications/scheduler/trigger/{job_id}` - Déclencher tâche manuelle

### 🛡️ Gestion des Accès et Permissions
- `GET /admin/gestion-acces/niveaux-acces` - Niveaux d'accès disponibles
- `GET /admin/gestion-acces/utilisateurs` - Liste avec permissions
- `GET /admin/gestion-acces/utilisateurs/{id}/permissions` - Permissions détaillées
- `PUT /admin/gestion-acces/utilisateurs/{id}/permissions` - Mise à jour permissions
- `POST /admin/gestion-acces/utilisateurs/{id}/regles-acces` - Ajouter règle d'accès
- `DELETE /admin/gestion-acces/utilisateurs/{id}/regles-acces/{index}` - Supprimer règle
- `GET /admin/gestion-acces/audit/changements-permissions` - Audit permissions
- `POST /admin/gestion-acces/mise-a-jour-lot-permissions` - Mise à jour en lot
- `GET /admin/gestion-acces/modeles` - Modèles de permissions prédéfinisanulaires en français, et interface de gestion intuitive.

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/Mohamedsalem00/eir-project)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](https://eir-project.com/license)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-brightgreen.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)

## 🌟 Caractéristiques Principales

- ✅ **API 100% francisée** : Tous les endpoints, messages et erreurs en français
- ✅ **Système de permissions granulaires** avec valeurs françaises cohérentes en base de données
- ✅ **Support multilingue** : Français (par défaut), Anglais, Arabe avec traduction dynamique
- ✅ **Interface de gestion intuitive** avec scripts automatisés et menu interactif
- ✅ **Architecture Docker** pour un déploiement simplifié sur tous les environnements
- ✅ **Documentation interactive** Swagger entièrement francisée
- ✅ **Base de données PostgreSQL** universelle compatible avec tous les clouds
- ✅ **Système d'audit complet** pour traçabilité et conformité réglementaire
- ✅ **Validation IMEI avancée** avec base de données TAC intégrée et algorithme Luhn
- ✅ **Système de notifications** email/SMS automatisé avec planificateur
- ✅ **Gestion multi-protocoles** (REST, SS7, Diameter) pour intégration réseau
- ✅ **Import/Export en lot** avec mapping de colonnes flexible
- ✅ **Robustesse production** avec gestion d'erreurs gracieuse
- ✅ **Déploiement universel** compatible avec Render, Heroku, AWS, Google Cloud, Azure

## 🚀 Démarrage Ultra-Rapide

### Option 1 : Lancement Automatique (Recommandé)
```bash
# Clone du projet
git clone https://github.com/Mohamedsalem00/eir-project.git
cd eir-project

# Démarrage automatique
./quick-start.sh
```

### Option 2 : Script de Gestion Interactif
```bash
./scripts/manage-eir.sh
```

### Option 3 : Démarrage Manuel Docker
```bash
# Construction et démarrage
docker compose up --build -d

# Vérification du statut
docker compose ps
```

**🎉 L'application sera accessible sur :**
- **Interface API** : http://localhost:8000
- **Documentation** : http://localhost:8000/docs
- **Santé système** : http://localhost:8000/verification-etat
- **Interface de test** : http://localhost:8000

## 📋 Menu de Gestion Complet

Le script `manage-eir.sh` offre un menu interactif avec :

### 🔄 Gestion des Conteneurs
- **Reconstruction complète** : Build et déploiement depuis zéro
- **Redémarrage intelligent** : Redémarrage rapide avec conservation des données
- **Gestion par service** : Web ou base de données individuellement

### 🗄️ Gestion de la Base de Données
- **Reconstruction complète** : Nouveau schéma avec données de test
- **Réinitialisation rapide** : Conservation du schéma, nouvelles données
- **Sauvegarde/Restauration** : Protection et récupération des données

### 📊 Monitoring et Tests
- **Statut des services** : Vue d'ensemble de l'état du système
- **Tests API francisée** : Validation des endpoints français
- **Consultation des logs** : Debugging facilité

### 🛠️ Utilitaires
- **Nettoyage Docker** : Libération d'espace disque
- **Gestion des sauvegardes** : Archivage et restauration

## 🏗️ Architecture du Projet

```
eir-project/
├── 🚀 quick-start.sh           # Démarrage automatique
├── 🔧 scripts/                 # Suite complète de gestion
│   ├── manage-eir.sh           # Script principal interactif
│   ├── rebuild-containers.sh   # Reconstruction des conteneurs
│   ├── restart-containers.sh   # Redémarrage des services
│   ├── rebuild-database.sh     # Reconstruction de la DB
│   └── reset-database.sh       # Réinitialisation des données
├── 📦 backend/                 # API FastAPI francisée
│   ├── app/
│   │   ├── main.py            # Point d'entrée principal
│   │   ├── api/               # Endpoints API francisés
│   │   ├── models/            # Modèles SQLAlchemy
│   │   ├── schemas/           # Schémas Pydantic
│   │   ├── core/              # Configuration et authentification
│   │   ├── i18n/              # Système de traduction
│   │   └── services/          # Logique métier
│   ├── Dockerfile
│   └── requirements.txt
├── 🐳 docker compose.yml       # Configuration multi-services
├── 📚 docs/                    # Documentation technique
└── 📖 README.md               # Ce fichier
```

## 🌐 Endpoints API Francisés

### 🏠 Points d'Accès Principaux
- **Documentation interactive** : `http://localhost:8000/docs`
- **Santé du système** : `http://localhost:8000/verification-etat`
- **Langues supportées** : `http://localhost:8000/languages`
- **Page d'accueil** : `http://localhost:8000/`

### 📱 Gestion des IMEI et Validation TAC
- `GET /imei/{imei}` - Recherche d'un IMEI spécifique avec contrôle d'accès granulaire
- `GET /imei/{imei}/validate` - Validation IMEI avec algorithme Luhn et base TAC
- `GET /imei/{imei}/details` - Détails complets d'un IMEI avec statut global
- `POST /verify_imei` - Vérification IMEI multi-protocoles (REST, SS7, Diameter)
- `POST /imei/recherche-avancee` - Recherche avec filtres et journalisation
- `POST /imei/enregistrer` - Enregistrement d'un nouvel appareil

### 🏗️ Gestion TAC (Type Allocation Code)
- `GET /tac/{tac}` - Recherche d'informations TAC dans la base
- `GET /admin/tac/stats` - Statistiques avancées de la base TAC avec répartitions
- `POST /admin/tac/sync` - Synchronisation avec sources externes Osmocom
- `POST /admin/tac/import` - Import TAC depuis fichier CSV/JSON avec mapping
- `GET /admin/tac/sync/logs` - Historique détaillé des synchronisations

### 👤 Gestion des Utilisateurs
- `POST /utilisateurs/creer` - Création d'utilisateur
- `GET /utilisateurs/profil` - Profil utilisateur connecté
- `PUT /utilisateurs/modifier` - Modification du profil
- `GET /mes-permissions` - Permissions et niveaux d'accès détaillés de l'utilisateur
- `GET /utilisateurs/{user_id}` - Consultation d'un utilisateur
- `GET /utilisateurs/{user_id}/recherches` - Historique des recherches utilisateur

### 📦 Gestion des Appareils
- `GET /appareils` - Liste des appareils avec contrôle d'accès granulaire et filtrage
- `POST /appareils` - Enregistrement d'un nouvel appareil avec audit
- `PUT /appareils/{device_id}/assigner` - Assignation d'appareil à un utilisateur
- `DELETE /admin/appareils/{device_id}` - Suppression d'appareil avec audit
- `POST /admin/import-lot-appareils` - Import en lot d'appareils avec validation
- `POST /admin/import-file` - Import depuis fichier CSV/JSON avec mapping colonnes
- `GET /admin/import-template` - Télécharger template d'import
- `POST /admin/preview-import` - Prévisualiser import avec recommandations
- `POST /appareils/{appareil_id}/imeis` - Ajouter IMEI à un appareil
- `PUT /imeis/{imei_id}/status` - Mettre à jour statut IMEI

### 🔐 Authentification et Sécurité
- `POST /authentification/inscription` - Inscription nouvel utilisateur avec notification bienvenue
- `POST /authentification/connexion` - Connexion avec JWT et audit
- `POST /authentification/deconnexion` - Déconnexion sécurisée
- `GET /authentification/profile` - Profil utilisateur détaillé avec statistiques
- `GET /authentification/profile/simple` - Profil utilisateur simple
- `POST /authentification/mot-de-passe-oublie` - Demande reset mot de passe
- `POST /authentification/verifier-code-reset` - Vérification code reset
- `POST /authentification/nouveau-mot-de-passe` - Changement mot de passe sécurisé

### � Notifications et Audit
- `GET /notifications` - Liste des notifications
- `POST /admin/notifications/send` - Envoi de notifications administrateur
- `GET /admin/journaux-audit` - Consultation des journaux d'audit
- `GET /admin/notifications/scheduler/status` - Statut du planificateur
- `POST /admin/notifications/scheduler/trigger/{job_id}` - Déclencher une tâche

### �🔧 Système et Validation
- `GET /verification-etat` - État de santé du système
- `GET /imei/{imei}/validate` - Validation IMEI avec base TAC
- `GET /tac/{tac}` - Recherche d'informations TAC
- `GET /mes-permissions` - Permissions de l'utilisateur connecté
- `GET /protocols/status` - Statut des protocoles d'intégration
- `GET /languages` - Langues supportées par le système

## 🗃️ Base de Données

### Structure Principale
```mermaid
erDiagram
    Utilisateur ||--o{ Appareil : "possède"
    Utilisateur ||--o{ SIM : "possède"
    Utilisateur ||--o{ IMEI : "recherche"
    Appareil ||--o{ IMEI : "contient"
    Utilisateur ||--o{ Recherche : "effectue"
    Utilisateur ||--o{ Notification : "reçoit"
    Utilisateur ||--o{ JournalAudit : "génère"
    Utilisateur ||--o{ PasswordReset : "demande"
    IMEI }o--|| TAC_Database : "valide_avec"
    TAC_Database ||--o{ TAC_Sync_Log : "synchronise"
    
    Utilisateur {
        UUID id
        string nom
        string email
        string mot_de_passe
        string type_utilisateur
        string niveau_acces
        string portee_donnees
        string organisation
        jsonb marques_autorisees
        jsonb plages_imei_autorisees
        boolean est_actif
        timestamp date_creation
    }
    
    Appareil {
        UUID id
        string marque
        string modele
        string emmc
        UUID utilisateur_id
    }
    
    IMEI {
        UUID id
        string numero_imei
        integer numero_slot
        string statut
        UUID appareil_id
    }
    
    TAC_Database {
        string tac
        string marque
        string modele
        integer annee_sortie
        string type_appareil
        string statut
        string raison
        timestamp date_creation
        timestamp date_modification
    }
    
    TAC_Sync_Log {
        UUID id
        string source_name
        string source_url
        string sync_type
        string format_type
        string status
        integer records_imported
        integer records_updated
        integer records_errors
        timestamp sync_date
    }
    
    SIM {
        UUID id
        string iccid
        string operateur
        UUID utilisateur_id
    }
    
    Notification {
        UUID id
        string type
        string destinataire
        string sujet
        text contenu
        string source
        string statut
        integer tentative
        timestamp date_creation
        timestamp date_envoi
        UUID utilisateur_id
    }
    
    PasswordReset {
        UUID id
        UUID utilisateur_id
        string token
        string methode_verification
        string code_verification
        string email
        string telephone
        boolean utilise
        timestamp date_creation
        timestamp date_expiration
    }
    
    JournalAudit {
        UUID id
        text action
        timestamp date
        UUID utilisateur_id
    }
    
    ImportExport {
        UUID id
        string type_operation
        text fichier
        timestamp date
        UUID utilisateur_id
    }
```

### Fonctionnalités Avancées du Schéma PostgreSQL

#### 🔧 Fonctions de Validation IMEI
- **`valider_imei_avec_tac(VARCHAR)`** : Validation complète IMEI avec base TAC et algorithme Luhn
- **`valider_luhn(VARCHAR)`** : Validation algorithme Luhn pour vérification intégrité IMEI
- **`extraire_tac_depuis_imei(VARCHAR)`** : Extraction code TAC depuis numéro IMEI
- **`valider_lot_imeis_avec_tac(TEXT[])`** : Validation en lot jusqu'à 100 IMEIs simultanément

#### 📊 Fonctions de Synchronisation TAC
- **`sync_osmocom_csv()`** : Synchronisation automatique depuis API CSV Osmocom
- **`sync_osmocom_json()`** : Synchronisation depuis API JSON Osmocom
- **`importer_tac_avec_mapping(TEXT, VARCHAR)`** : Import flexible avec mapping de colonnes
- **`importer_tac_depuis_json(JSONB, VARCHAR)`** : Import depuis données JSON structurées

#### 📈 Fonctions de Statistiques et Monitoring
- **`obtenir_stats_tac_temps_reel()`** : Statistiques TAC en temps réel avec répartitions
- **`obtenir_stats_sync_tac()`** : Métriques de synchronisation des 30 derniers jours
- **`nettoyer_logs_sync_tac(INTEGER)`** : Nettoyage automatique logs anciens

#### 🎯 Vues Optimisées
- **`vue_analyse_tac`** : Analyse de couverture TAC par marques et années
- **`vue_sync_tac_recent`** : Monitoring synchronisations récentes avec statuts
- **`vue_monitoring_sync_tac`** : Surveillance avancée avec niveaux d'urgence

### Données de Test Intégrées
- **Utilisateurs administrateurs** avec permissions complètes (`eirrproject@gmail.com`)
- **Utilisateurs standards** avec accès personnel (`sidis9828@gmail.com`)
- **Utilisateurs opérateurs** avec accès organisationnel (Orange: `devvmrr@gmail.com`, Inwi: `inwi@eir.ma`)
- **Appareils d'exemple** avec IMEIs valides et multiples slots (Samsung, Apple, Huawei, OnePlus)
- **Base de données TAC** avec codes de validation (Samsung: 35326005, Apple: 35692005, etc.)
- **Cartes SIM de test** de différents opérateurs (Orange, Inwi)
- **Notifications système** prêtes à l'envoi avec contenu français
- **Historique d'audit** complet pour démonstration
- **Données de synchronisation TAC** pour tests d'intégration avec logs détaillés
- **Tokens de reset** pour tests de sécurité avec méthodes email/SMS
- **Journaux d'import/export** pour tests en lot avec mapping de colonnes
- **Fonctions PostgreSQL avancées** : validation IMEI avec algorithme Luhn, synchronisation TAC automatisée
- **Vues et statistiques** : monitoring des synchronisations, analyses TAC temps réel, nettoyage automatique des logs

### Comptes de Test Disponibles
```bash
# Administrateur système
Email: eirrproject@gmail.com
Mot de passe: admin123
Permissions: Accès complet (niveau: admin, portée: tout)

# Utilisateur standard
Email: sidis9828@gmail.com  
Mot de passe: admin123
Permissions: Accès personnel (niveau: standard, portée: personnel)

# Opérateur Orange
Email: devvmrr@gmail.com
Mot de passe: admin123
Permissions: Accès organisationnel Orange (niveau: standard, portée: organisation)

# Opérateur Inwi
Email: inwi@eir.ma
Mot de passe: admin123
Permissions: Accès organisationnel Inwi (niveau: standard, portée: organisation)
```

## 🔧 Configuration Avancée

### Variables d'Environnement
```bash
# Base de données PostgreSQL
POSTGRES_DB=eir_project
POSTGRES_USER=postgres
POSTGRES_PASSWORD=motdepasse_securise
DATABASE_URL=postgresql://postgres:motdepasse_securise@localhost:5432/eir_project

# API et sécurité JWT
API_SECRET_KEY=cle_secrete_jwt_super_longue_et_securisee
API_ALGORITHM=HS256
API_ACCESS_TOKEN_EXPIRE_MINUTES=30
BCRYPT_ROUNDS=12

# Support multilingue
DEFAULT_LANGUAGE=fr
SUPPORTED_LANGUAGES=fr,en,ar
TIMEZONE=UTC

# Notifications Email (Gmail/Outlook/SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_app_gmail
SMTP_FROM_EMAIL=noreply@eir-project.com
SMTP_FROM_NAME=EIR Project
SMTP_USE_TLS=true

# Notifications SMS (Twilio/Africa's Talking)
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=votre_account_sid
TWILIO_AUTH_TOKEN=votre_auth_token  
TWILIO_PHONE_NUMBER=+1234567890

# Intégration TAC et validation IMEI
TAC_SYNC_ENABLED=true
TAC_SOURCE_URL=https://raw.githubusercontent.com/musalbas/mcc-mnc-table/master/imei_tac.csv
TAC_AUTO_SYNC_INTERVAL=24  # heures
TAC_CACHE_TTL=3600  # secondes
IMEI_VALIDATION_STRICT=true
LUHN_ALGORITHM_ENABLED=true

# Intégration multi-protocoles
ENABLE_SS7_PROTOCOL=false
ENABLE_DIAMETER_PROTOCOL=false
SS7_GATEWAY_URL=http://ss7-gateway:8080
DIAMETER_GATEWAY_URL=http://diameter-gateway:8080

# Déploiement Cloud (Render/Heroku/AWS/GCP/Azure)
PORT=8000
HOST=0.0.0.0
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]
RENDER_EXTERNAL_URL=https://your-app.onrender.com
HEROKU_APP_NAME=your-heroku-app

# Monitoring et logging
LOG_LEVEL=INFO
LOG_FORMAT=json
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
ENABLE_METRICS=true
METRICS_PORT=9090

# Cache et performance
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=300
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Personnalisation des Scripts
Tous les scripts peuvent être personnalisés via des options :

```bash
# Reconstruction avec données personnalisées
./scripts/rebuild-database.sh --custom-data

# Redémarrage en mode verbose
./scripts/restart-containers.sh --verbose

# Sauvegarde avec compression
./scripts/manage-eir.sh  # Option 10 dans le menu
```

## 🐛 Dépannage Rapide

### Problèmes Courants

#### 🚫 Docker non démarré
```bash
sudo systemctl start docker
# Ou démarrer Docker Desktop
```

#### 🔒 Ports occupés
```bash
sudo netstat -tulpn | grep :8000
sudo kill -9 <PID_DU_PROCESSUS>
```

#### 💾 Base de données corrompue
```bash
./scripts/rebuild-database.sh
```

#### 🔄 Conteneurs qui ne répondent pas
```bash
./scripts/rebuild-containers.sh
```

#### 🚫 Erreur 500 sur /appareils endpoint
```bash
# Vérifier les permissions et valeurs françaises
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/mes-permissions

# Tester l'endpoint avec utilisateur admin
curl -H "Authorization: Bearer ADMIN_TOKEN" \
     http://localhost:8000/appareils

# Reconstruire si nécessaire
./scripts/rebuild-database.sh
```

#### 📧 Notifications non envoyées
```bash
# Vérifier la configuration email
curl http://localhost:8000/test-email-config

# Tester l'envoi d'email admin
curl -X POST "http://localhost:8000/admin/test-email?email_test=test@example.com" \
     -H "Authorization: Bearer ADMIN_TOKEN"

# Voir les logs du planificateur
curl http://localhost:8000/admin/notifications/scheduler/status \
     -H "Authorization: Bearer ADMIN_TOKEN"

# Vérifier les statistiques des notifications
curl http://localhost:8000/notifications/statistiques/globales \
     -H "Authorization: Bearer YOUR_TOKEN"
```

#### ⚠️ Problèmes de permissions
```bash
# Vérifier les niveaux d'accès disponibles
curl http://localhost:8000/admin/gestion-acces/niveaux-acces \
     -H "Authorization: Bearer ADMIN_TOKEN"

# Lister les utilisateurs avec permissions
curl http://localhost:8000/admin/gestion-acces/utilisateurs \
     -H "Authorization: Bearer ADMIN_TOKEN"

# Audit des changements de permissions
curl http://localhost:8000/admin/gestion-acces/audit/changements-permissions \
     -H "Authorization: Bearer ADMIN_TOKEN"
```

#### 🔍 Problèmes de validation IMEI/TAC
```bash
# Tester la validation IMEI
curl http://localhost:8000/imei/353260051234567/validate

# Vérifier les statistiques TAC
curl http://localhost:8000/admin/tac/stats \
     -H "Authorization: Bearer ADMIN_TOKEN"

# Synchroniser la base TAC
curl -X POST http://localhost:8000/admin/tac/sync \
     -H "Authorization: Bearer ADMIN_TOKEN"
```

### Logs de Debug
```bash
# Via le menu principal
./scripts/manage-eir.sh  # Option 8

# Ou directement
docker compose logs -f
```

## 📊 Fonctionnalités Techniques

### 🛡️ Sécurité
- **Authentification JWT** avec expiration automatique et refresh tokens
- **Hashage bcrypt** des mots de passe avec salt rounds configurables
- **Permissions granulaires** par utilisateur avec portée de données française
- **Validation stricte** des données d'entrée avec Pydantic
- **Protection CORS** configurée pour domaines autorisés
- **Contrôle d'accès par marques** pour les parties concernées (opérateurs)
- **Gestion des plages IMEI** autorisées par organisation
- **Journalisation complète** des actions utilisateur pour audit
- **Reset mot de passe sécurisé** avec codes de vérification temporaires
- **Protection contre bruteforce** avec limitation de tentatives
- **Validation des tokens** avec blacklist pour déconnexions forcées

### 🌍 Internationalisation
- **Support multilingue** automatique
- **Détection de langue** via headers HTTP
- **Messages d'erreur traduits** dans toutes les langues
- **Format de dates localisé**

### 📈 Performance
- **Pool de connexions** à la base de données avec gestion automatique
- **Cache des traductions** en mémoire pour responses multilingues rapides
- **Validation asynchrone** des requêtes avec FastAPI
- **Compression gzip** automatique des réponses API
- **Indexation optimisée** des recherches IMEI avec GIN/BTREE
- **Gestion d'erreurs robuste** avec fallback gracieux et retry logic
- **Validation TAC intégrée** avec cache local et synchronisation automatique
- **Pagination intelligente** pour les listes d'appareils et notifications
- **Optimisation des requêtes** SQL avec jointures efficaces
- **Monitoring des performances** avec métriques Prometheus/Grafana
- **Rate limiting** configurable par endpoint et utilisateur

### 📝 Audit et Logging
- **Traçabilité complète** des actions utilisateur avec timestamps UTC
- **Logs structurés** en JSON pour parsing automatique
- **Rotation automatique** des fichiers de log avec archivage
- **Alertes temps réel** pour les erreurs critiques et tentatives d'intrusion
- **Synchronisation TAC** avec journalisation détaillée des sources
- **Notifications système** avec suivi des tentatives et statuts d'envoi
- **Historique des permissions** et changements d'accès granulaires
- **Audit des imports/exports** avec détails des mappings de colonnes
- **Suivi des connexions** avec géolocalisation IP et détection d'anomalies
- **Métriques de performance** avec dashboards temps réel
- **Archivage automatique** des logs avec compression et rétention configurable

## 🔗 Documentation Complémentaire

- **[📁 Scripts de Gestion](scripts/README.md)** - Guide détaillé des scripts d'automatisation
- **[🔐 Guide d'Accès Granulaire](docs/GRANULAR_ACCESS_GUIDE.md)** - Configuration des permissions françaises
- **[📋 Cahier des Charges](docs/cahier_de_charges_eir.tex)** - Spécifications techniques complètes
- **[🏗️ Diagrammes UML](docs/uml/)** - Architecture système et flux de données
- **[📧 Guide Notifications](NOTIFICATIONS_QUICK_START.md)** - Configuration email/SMS détaillée
- **[🔧 Guide Admin](GUIDE_ENDPOINTS_ADMIN_NOTIFICATIONS.md)** - Endpoints administrateur avancés
- **[🚀 Guide Déploiement](DEPLOYMENT_GUIDE.md)** - Déploiement production multi-cloud
- **[📊 Guide Import](docs/ENHANCED_IMPORT_API.md)** - Import de données en lot avec mapping
- **[🌐 API Multi-Protocoles](MULTI_PROTOCOL_README.md)** - Intégration SS7/Diameter
- **[🏥 Guide de Reprise](RESUME_ENDPOINTS_ADMIN_NOTIFICATIONS.md)** - Procédures de récupération
- **[📈 Monitoring](docs/MONITORING_GUIDE.md)** - Surveillance et métriques système

## 🆘 Support et Contribution

### 🐛 Signaler un Bug
1. **Consulter les logs** : `./scripts/manage-eir.sh` (option 8) ou `docker compose logs -f`
2. **Vérifier le statut** : `./scripts/manage-eir.sh` (option 6) ou `curl http://localhost:8000/verification-etat`
3. **Reproduire l'erreur** en mode verbose avec logs détaillés
4. **Créer une issue** GitHub avec logs, environnement et étapes de reproduction
5. **Tester les endpoints** de diagnostic disponibles

### 📞 Contact et Support
- **Issues GitHub** : [https://github.com/Mohamedsalem00/eir-project/issues](https://github.com/Mohamedsalem00/eir-project/issues)
- **Documentation** : Consultez les fichiers dans `/docs/` pour la documentation technique
- **Scripts** : Guide détaillé dans `/scripts/README.md` pour l'automatisation
- **Architecture** : Diagrammes UML dans `/docs/uml/` pour comprendre le système
- **API Interactive** : http://localhost:8000/docs pour tester les endpoints
- **Support Email** : contact@eir-project.com (pour les déploiements professionnels)

---

**🎯 Objectif** : Fournir un système EIR complet, francisé et prêt pour la production avec une interface de gestion intuitive, un système de permissions granulaires en français, et une robustesse éprouvée.

**✨ Innovation** : Premier système EIR entièrement francisé avec scripts de gestion automatisés, interface multilingue, validation TAC intégrée, système de notifications automatisé, et cohérence linguistique française complète.

**🔧 Dernières Améliorations (Août 2025)** :
- ✅ **Schéma PostgreSQL universel** : Compatible avec tous les clouds (Render, Heroku, AWS, GCP, Azure)
- ✅ **Fonctions PostgreSQL avancées** : 15+ fonctions pour validation IMEI, synchronisation TAC, statistiques temps réel
- ✅ **Base de données TAC intégrée** : Validation automatique avec algorithme Luhn et synchronisation Osmocom
- ✅ **Système de permissions français** : Cohérence linguistique complète avec valeurs françaises en base
- ✅ **Endpoints administratifs avancés** : Gestion granulaire permissions, notifications en lot, audit détaillé
- ✅ **System de reset mot de passe** : Sécurisé avec codes de vérification email/SMS et tokens temporaires
- ✅ **Notifications enrichies** : Templates français, planificateur automatisé, statistiques complètes
- ✅ **Import/Export robuste** : Mapping colonnes flexible, prévisualisation, recommandations automatiques
- ✅ **Monitoring avancé** : Vues PostgreSQL optimisées, métriques temps réel, alertes intégrées
- ✅ **Documentation complète** : 60+ endpoints documentés, guides techniques, exemples pratiques

**📊 Statistiques du Projet** :
- **Endpoints API** : 60+ endpoints francisés avec documentation Swagger complète
- **Modèles de données** : 12+ tables avec relations et contraintes optimisées PostgreSQL
- **Système de permissions** : 6 niveaux d'accès avec 5 portées de données en français
- **Support multilingue** : Français, Anglais, Arabe avec traduction dynamique temps réel
- **Tests intégrés** : Données de test complètes avec 4 comptes utilisateur et scénarios avancés
- **Scripts d'automatisation** : 15+ scripts pour gestion complète du système et déploiement
- **Documentation** : 12+ guides techniques et utilisateur en français avec exemples pratiques
- **Fonctions PostgreSQL** : 15+ fonctions avancées pour validation IMEI, synchronisation TAC, statistiques
- **Intégrations externes** : APIs Osmocom TAC, services email/SMS, protocoles SS7/Diameter
- **Système d'audit** : Journalisation complète avec 10+ types d'événements tracés

**🏆 Conformité et Standards** :
- **RGPD** : Gestion des données personnelles et audit trail complet
- **Sécurité** : Authentification JWT, hashage bcrypt, permissions granulaires
- **Internationali[ation** : Support I18N complet avec locale française par défaut
- **API REST** : Conformité OpenAPI 3.0 avec documentation interactive
- **Base de données** : PostgreSQL avec contraintes d'intégrité et indexation optimisée
- **Docker** : Containerisation complète pour déploiement multi-environnement
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

