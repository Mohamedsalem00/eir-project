# 📚 Documentation du Projet EIR - Organisation

## 🗂️ Structure de Documentation Organisée

Cette documentation a été réorganisée pour une meilleure maintenance et navigation. Voici comment naviguer dans la documentation du projet.

## 📁 Structure des Dossiers

### `/documentation/` - Documentation Principale
```
documentation/
├── README.md                     # Ce fichier - Index de navigation
├── user-guides/                  # Guides utilisateur
│   ├── installation.md           # Guide d'installation
│   ├── quick-start.md            # Démarrage rapide
│   ├── user-interface.md         # Utilisation de l'interface
│   └── troubleshooting.md        # Résolution de problèmes
├── technical/                    # Documentation technique
│   ├── architecture.md           # Architecture du système
│   ├── database-schema.md        # Schéma de base de données
│   ├── security.md              # Sécurité et authentification
│   ├── notifications.md         # Système de notifications
│   └── translations.md          # Système de traduction
├── deployment/                   # Guides de déploiement
│   ├── docker.md               # Déploiement Docker
│   ├── cloud-platforms.md      # Plateformes cloud
│   ├── production.md           # Configuration production
│   └── monitoring.md           # Monitoring et maintenance
└── api/                         # Documentation API
    ├── endpoints.md             # Liste des endpoints
    ├── authentication.md       # Authentification API
    ├── examples.md             # Exemples d'utilisation
    └── webhooks.md             # Configuration webhooks
```

### `/testing/` - Tests et Validation
```
testing/
├── README.md                    # Guide de testing
├── unit/                       # Tests unitaires
│   ├── test_api.py             # Tests API
│   ├── test_models.py          # Tests modèles
│   └── test_auth.py            # Tests authentification
├── integration/                # Tests d'intégration
│   ├── test_full_workflow.py   # Tests workflow complet
│   ├── test_notifications.py   # Tests notifications
│   └── test_database.py        # Tests base de données
└── api/                        # Tests API spécialisés
    ├── test_endpoints.py       # Tests endpoints
    ├── test_performance.py     # Tests performance
    └── api_test_config.json    # Configuration tests API
```

## 📖 Guides Principaux

### 🚀 Pour Commencer
1. **[Installation](user-guides/installation.md)** - Installation et configuration initiale
2. **[Démarrage Rapide](user-guides/quick-start.md)** - Premiers pas avec le système
3. **[Interface Utilisateur](user-guides/user-interface.md)** - Utilisation de l'interface web

### 🔧 Documentation Technique
1. **[Architecture](technical/architecture.md)** - Vue d'ensemble du système
2. **[Base de Données](technical/database-schema.md)** - Schéma et modèles de données
3. **[Sécurité](technical/security.md)** - Authentification et permissions
4. **[API](api/endpoints.md)** - Documentation complète de l'API

### 🚀 Déploiement
1. **[Docker](deployment/docker.md)** - Conteneurisation et orchestration
2. **[Production](deployment/production.md)** - Configuration pour la production
3. **[Cloud](deployment/cloud-platforms.md)** - Déploiement sur différentes plateformes

## 🧪 Tests et Validation

### Types de Tests Disponibles
- **Tests Unitaires** : Validation des composants individuels
- **Tests d'Intégration** : Validation des workflows complets
- **Tests API** : Validation des endpoints et réponses
- **Tests de Performance** : Validation des performances sous charge

### Exécution des Tests
```bash
# Tests unitaires
python -m pytest testing/unit/

# Tests d'intégration  
python -m pytest testing/integration/

# Tests API complets
python -m pytest testing/api/

# Tous les tests
python -m pytest testing/
```

## 📝 Contribution à la Documentation

### Ajout de Nouvelle Documentation
1. Identifiez la catégorie appropriée (`user-guides`, `technical`, `deployment`, `api`)
2. Créez le fichier dans le bon dossier
3. Mettez à jour ce README.md avec le lien
4. Suivez le format Markdown standard

### Standards de Documentation
- **Français** comme langue principale
- **Markdown** pour le formatage
- **Exemples pratiques** dans chaque guide
- **Captures d'écran** quand approprié
- **Liens croisés** entre les documents

## 🔄 Migration des Fichiers Existants

Les fichiers suivants ont été déplacés/organisés :

### Fichiers Principaux (Racine)
- `README.md` - Documentation principale du projet
- `DEPLOYMENT_GUIDE.md` → `documentation/deployment/`
- `NOTIFICATIONS_QUICK_START.md` → `documentation/technical/notifications.md`
- `TRANSLATION_SYSTEM_SUMMARY.md` → `documentation/technical/translations.md`

### Fichiers Techniques
- `docs/` → `documentation/technical/` (contenu réorganisé)
- Tests éparpillés → `testing/` (organisés par type)

### Fichiers de Configuration
- `config/` - Conservé à la racine (requis par l'application)
- `scripts/` - Conservé à la racine (scripts d'administration)

## 🚫 Fichiers Ignorés par Git

Le `.gitignore` a été mis à jour pour exclure :
- Fichiers temporaires de test
- Logs de développement
- Fichiers de configuration locaux
- Sauvegardes automatiques
- Données sensibles

## 🔗 Liens Utiles

- **[GitHub Repository](https://github.com/Mohamedsalem00/eir-project)**
- **[API Documentation](http://localhost:8000/docs)** (mode développement)
- **[Frontend Interface](http://localhost:3000)** (mode développement)

## 📞 Support

Pour toute question sur la documentation :
1. Consultez d'abord les guides appropriés
2. Vérifiez les [FAQ](user-guides/troubleshooting.md)
3. Créez une issue GitHub si nécessaire

---

*Documentation mise à jour le : 12 août 2025*
