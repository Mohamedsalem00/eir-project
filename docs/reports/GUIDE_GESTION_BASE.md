# 🗄️ Guide d'Utilisation - Scripts de Gestion Base EIR

**Date:** 5 Août 2025  
**Version:** Production Ready - Docker  
**Status:** ✅ OPÉRATIONNEL

## 📋 Scripts Disponibles

### 1️⃣ **Gestionnaire Complet** (Menu Interactif)
```bash
./scripts/gestion-base-donnees.sh
```
- ✅ Menu interactif en français
- ✅ Connexion via Docker
- ✅ 9 fonctions principales
- ✅ Sauvegardes et restaurations
- ✅ Interface colorée et intuitive

### 2️⃣ **Actions Rapides** (Ligne de Commande)
```bash
./scripts/actions-rapides.sh [commande]
```
- ✅ Commandes rapides sans menu
- ✅ Parfait pour automatisation
- ✅ Syntaxe simple et efficace

## 🚀 Actions Rapides - Commandes

### Exploration de Base
```bash
# Lister toutes les tables
./scripts/actions-rapides.sh tables
./scripts/actions-rapides.sh t

# Compter les enregistrements
./scripts/actions-rapides.sh counts
./scripts/actions-rapides.sh c
```

### Consultation des Données
```bash
# Voir les utilisateurs actifs
./scripts/actions-rapides.sh users
./scripts/actions-rapides.sh u

# Top appareils par nombre d'IMEIs
./scripts/actions-rapides.sh devices
./scripts/actions-rapides.sh d

# IMEIs récents
./scripts/actions-rapides.sh imeis
./scripts/actions-rapides.sh i
```

### Recherche et Analyse
```bash
# Rechercher un IMEI (partiel ou complet)
./scripts/actions-rapides.sh search 352745
./scripts/actions-rapides.sh s 354123

# Statistiques rapides
./scripts/actions-rapides.sh stats
./scripts/actions-rapides.sh st
```

### Structure et Contenu
```bash
# Structure d'une table
./scripts/actions-rapides.sh structure utilisateur
./scripts/actions-rapides.sh str appareil

# Afficher contenu (5 lignes par défaut)
./scripts/actions-rapides.sh show imei
./scripts/actions-rapides.sh show utilisateur 10
```

### Sauvegarde Rapide
```bash
# Sauvegarde automatique horodatée
./scripts/actions-rapides.sh backup
./scripts/actions-rapides.sh b
```

## 📊 Structure de Base Actuelle

### 📋 Tables Disponibles
- **utilisateur** (5 enregistrements)
- **appareil** (3 enregistrements)  
- **imei** (3 enregistrements)
- **sim** (1 enregistrement)
- **recherche** (5 enregistrements)
- **notification** (1 enregistrement)
- **journal_audit** 
- **importexport**

### 👥 Utilisateurs Types
- **admin@eir-project.com** - Administrateur
- **user@example.com** - Utilisateur standard
- **police@cybercrime.gov** - Forces de l'ordre
- **insurance@company.com** - Assurance
- **manufacturer@techcorp.com** - Fabricant

### 📱 Appareils Enregistrés
- **Samsung Galaxy S21** (IMEI: 352745080123456)
- **Apple iPhone 13** (IMEI: 354123456789012)
- **TechCorp TC-Pro-2024** (IMEI: 352745080987654)

## 🎯 Exemples d'Utilisation

### Recherche Rapide d'un IMEI
```bash
# Recherche partielle
./scripts/actions-rapides.sh search 352745
# Résultat: 2 IMEIs trouvés (Samsung + TechCorp)

# Recherche spécifique
./scripts/actions-rapides.sh search 354123456789012
# Résultat: Apple iPhone 13
```

### Analyse des Données
```bash
# Vue d'ensemble
./scripts/actions-rapides.sh counts

# Statistiques détaillées
./scripts/actions-rapides.sh stats

# Structure d'une table
./scripts/actions-rapides.sh structure imei
```

### Administration
```bash
# Sauvegarde rapide
./scripts/actions-rapides.sh backup
# Fichier: backups/quick_backup_20250805_HHMMSS.sql

# Consulter une table complètement
./scripts/actions-rapides.sh show utilisateur 100
```

## 🔧 Configuration Docker

### Connexion Automatique
- **Host:** Container `eir_db`
- **User:** `postgres`
- **Database:** `imei_db`
- **Port:** 5432 (exposé)

### Prérequis
- ✅ Docker et Docker Compose installés
- ✅ Conteneurs `eir_db` et `eir_web` en marche
- ✅ Scripts exécutables (`chmod +x`)

## 🛡️ Sécurité et Bonnes Pratiques

### Sauvegardes
```bash
# Sauvegarde quotidienne recommandée
./scripts/actions-rapides.sh backup

# Vérification de l'espace disque
du -h backups/

# Nettoyage des anciennes sauvegardes (>30 jours)
find backups/ -name "*.sql" -mtime +30 -delete
```

### Monitoring
```bash
# Vérification état conteneurs
docker compose ps

# Logs base de données
docker compose logs db

# État de la base
./scripts/actions-rapides.sh counts
```

## 🚨 Dépannage

### Problèmes Courants
```bash
# Conteneur arrêté
docker compose up -d

# Reconnexion base
docker compose restart db

# Problème de permissions
chmod +x scripts/*.sh
```

### Tests de Connectivité
```bash
# Test rapide
./scripts/actions-rapides.sh tables

# Test complet
./scripts/gestion-base-donnees.sh
# Choisir option 1 (Afficher toutes les tables)
```

---

## 📞 Support

**Scripts 100% opérationnels avec Docker**  
✅ Connexion automatique via conteneurs  
✅ Noms de tables français supportés  
✅ Interface bilingue (fr/en)  
✅ Sauvegarde et restauration intégrées
