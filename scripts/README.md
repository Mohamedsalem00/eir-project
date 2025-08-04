# 🛠️ Scripts de Gestion EIR

Ce dossier contient tous les scripts nécessaires pour gérer votre projet EIR francisé.

## 📁 Structure des Scripts

```
scripts/
├── manage-eir.sh           # 🎯 Script principal interactif
├── rebuild-containers.sh   # 🔄 Reconstruction complète des conteneurs
├── restart-containers.sh   # ⚡ Redémarrage rapide des conteneurs
├── rebuild-database.sh     # 🗄️  Reconstruction complète de la DB
├── reset-database.sh       # 🔄 Réinitialisation rapide de la DB
└── README.md              # 📖 Ce fichier
```

## 🚀 Démarrage Rapide

### Option 1 : Démarrage automatique
```bash
./quick-start.sh
```

### Option 2 : Script de gestion principal
```bash
./scripts/manage-eir.sh
```

## 📋 Scripts Disponibles

### 🎯 Script Principal (`manage-eir.sh`)
Script interactif avec menu complet pour toutes les opérations :
- ✅ Gestion des conteneurs (build, restart, logs)
- ✅ Gestion de la base de données (rebuild, reset, backup)
- ✅ Tests de l'API francisée
- ✅ Monitoring et statut des services
- ✅ Utilitaires de maintenance

```bash
./scripts/manage-eir.sh
```

### 🔄 Gestion des Conteneurs

#### Reconstruction Complète
```bash
./scripts/rebuild-containers.sh
```
- Arrête tous les conteneurs
- Supprime les conteneurs existants
- Reconstruit les images
- Redémarre avec la nouvelle configuration

#### Redémarrage Simple
```bash
./scripts/restart-containers.sh
```
- Redémarre tous les services
- Conserve les données existantes

#### Redémarrage d'un Service Spécifique
```bash
./scripts/restart-containers.sh --service web   # API seulement
./scripts/restart-containers.sh --service db    # Base de données seulement
```

### 🗄️ Gestion de la Base de Données

#### Reconstruction Complète
```bash
./scripts/rebuild-database.sh
```
- Sauvegarde automatique (optionnelle)
- Suppression et recréation de la base
- Réinitialisation du schéma
- Insertion des données de test

#### Réinitialisation Rapide
```bash
./scripts/reset-database.sh
```
- Supprime uniquement les données
- Conserve la structure
- Réinsère les données de test

## 🎨 Fonctionnalités des Scripts

### ✨ Interface Utilisateur
- 🌈 **Sortie colorée** pour une meilleure lisibilité
- 📊 **Barres de progression** pour les opérations longues
- ⚠️ **Messages d'erreur clairs** avec suggestions de résolution
- 🔍 **Logging détaillé** pour le debugging

### 🛡️ Sécurité et Fiabilité
- ✅ **Vérification des prérequis** (Docker, fichiers)
- 🔒 **Confirmations avant opérations destructives**
- 💾 **Sauvegardes automatiques** avant modifications
- 🚨 **Gestion d'erreurs robuste** avec rollback

### 🔧 Options Avancées
- 📝 **Mode verbeux** pour le debugging
- 🎯 **Actions ciblées** par service
- 📊 **Monitoring en temps réel**
- 🧹 **Nettoyage automatique** des ressources

## 📊 Monitoring et Tests

### Statut des Services
```bash
# Via le script principal
./scripts/manage-eir.sh
# Choisir option 6

# Ou directement avec Docker
docker compose ps
```

### Test de l'API Francisée
```bash
# Test automatique complet
curl http://localhost:8000/verification-etat

# Test manuel des endpoints
curl http://localhost:8000/langues
curl http://localhost:8000/docs
```

### Consultation des Logs
```bash
# Logs en temps réel
docker compose logs -f

# Logs d'un service spécifique
docker compose logs web
docker compose logs db
```

## 🐛 Dépannage

### Problèmes Courants

#### Docker n'est pas démarré
```bash
sudo systemctl start docker
# Ou sur macOS/Windows : démarrer Docker Desktop
```

#### Ports déjà utilisés
```bash
# Vérifier les ports occupés
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :5432

# Arrêter les services conflictuels
sudo kill -9 <PID>
```

#### Base de données corrompue
```bash
# Reconstruction complète
./scripts/rebuild-database.sh

# Ou suppression manuelle du volume
docker compose down
docker volume rm eir-project_postgres_data
```

#### Conteneurs qui ne démarrent pas
```bash
# Vérification des logs
docker compose logs

# Reconstruction forcée
./scripts/rebuild-containers.sh --force
```

## 🔧 Maintenance

### Nettoyage Régulier
```bash
# Via le script principal (option 9)
./scripts/manage-eir.sh

# Ou manuellement
docker system prune -f
docker volume prune -f
```

### Sauvegardes
```bash
# Sauvegarde automatique via le script principal (option 10)
./scripts/manage-eir.sh

# Sauvegarde manuelle
docker compose exec db pg_dump -U postgres imei_db > backup.sql
```

### Mises à Jour
```bash
# Mise à jour complète du projet
git pull
./scripts/rebuild-containers.sh
```

## 📞 Support

### Logs de Debug
```bash
# Logs détaillés de tous les services
docker compose logs --details

# Logs en mode verbose
docker compose up --verbose
```

### Vérification de la Configuration
```bash
# Validation du docker compose.yml
docker compose config

# Test de connectivité
docker compose exec web ping db
```

---

**💡 Astuce** : Utilisez toujours `./scripts/manage-eir.sh` pour une expérience interactive complète !

**🔗 Navigation** : [Documentation principale](../README.md) | [Guide d'accès granulaire](../docs/GRANULAR_ACCESS_GUIDE.md)
