# 📁 Scripts EIR - Structure Organisée

## 🎯 Scripts Principaux (à utiliser)

### 🐳 Gestion Docker
- `manage-eir.sh` - Script principal interactif de gestion
- `rebuild-containers.sh` - Reconstruction complète des conteneurs  
- `restart-containers.sh` - Redémarrage rapide des conteneurs

### 🗄️ Gestion Base de Données
- `rebuild-database.sh` - Reconstruction complète de la DB
- `reset-database.sh` - Réinitialisation rapide de la DB
- `gestion-base-donnees.sh` - Gestion interactive de la DB
- `alimenter-base-donnees.sh` - Alimentation de données

### ⚙️ Configuration
- `configurer-apis-externes.sh` - Configuration des APIs externes
- `setup-notifications.sh` - Configuration du système de notifications

### 🛠️ Utilitaires
- `actions-rapides.sh` - Actions de développement rapides
- `cleanup-old-scripts.sh` - Nettoyage des anciens scripts

## 📦 Scripts Déplacés

### → testing/scripts/
Tous les scripts de test ont été déplacés vers la structure de test organisée :
- `testing/scripts/api/` - Tests API
- `testing/scripts/notifications/` - Tests notifications  
- `testing/scripts/system/` - Tests système

### → documentation/
- `guide-apis-payantes.sh` → `documentation/user-guides/`

## 🎯 Utilisation Recommandée

### Via Makefile (Recommandé)
```bash
make start     # Équivalent à manage-eir.sh
make test      # Tests complets
make clean     # Nettoyage
```

### Scripts Directs
```bash
# Gestion Docker
./scripts/manage-eir.sh
./scripts/rebuild-containers.sh

# Base de données
./scripts/rebuild-database.sh
./scripts/reset-database.sh

# Configuration
./scripts/configurer-apis-externes.sh
./scripts/setup-notifications.sh
```

---
*Documentation mise à jour le 12 août 2025*
