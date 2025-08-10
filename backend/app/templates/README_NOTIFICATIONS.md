# 📧 Nouveau Système de Templates de Notifications

## 🎯 Vue d'ensemble

Le nouveau système de templates de notifications permet de **modifier facilement** le contenu des emails et SMS sans toucher au code Python. Tous les textes sont centralisés dans un fichier JSON facile à éditer.

## 📁 Structure des fichiers

```
backend/app/templates/
├── 📄 notifications_content.json    # ✏️ FICHIER À ÉDITER
├── 🔧 simple_notifications.py       # Gestionnaire automatique
└── 📚 README_NOTIFICATIONS.md       # Ce fichier

backend/app/services/
└── 🔄 eir_notifications.py          # Service intégré

backend/app/routes/
└── 🧪 notification_integration.py   # Routes de test
```

## ✏️ Comment modifier les notifications

### 1. Éditer le fichier JSON

```bash
nano backend/app/templates/notifications_content.json
```

### 2. Structure du fichier

```json
{
  "notifications": {
    "bienvenue": {
      "email": {
        "subject": "🎉 Bienvenue sur EIR Project !",
        "content": "Bonjour {nom_utilisateur},\n\n..."
      },
      "sms": {
        "content": "🎉 Bienvenue {nom_utilisateur}!"
      }
    }
  }
}
```

### 3. Variables disponibles

Les variables sont automatiquement remplacées :
- `{nom_utilisateur}` → Nom de l'utilisateur
- `{imei}` → Numéro IMEI
- `{marque}` → Marque de l'appareil
- `{modele}` → Modèle de l'appareil
- `{date_verification}` → Date de vérification
- `{raison}` → Raison en cas d'erreur

## 🔧 Intégration dans le code

### 1. Notification de bienvenue

```python
from app.services.eir_notifications import envoyer_notification_bienvenue

# Dans routes/auth.py après inscription
await envoyer_notification_bienvenue(str(new_user.id))
```

### 2. Vérification IMEI

```python
from app.services.eir_notifications import notifier_verification_imei

# Après vérification d'IMEI
await notifier_verification_imei(
    user_id=str(current_user.id),
    imei="353260051234567",
    statut="valide",  # "valide", "invalide", "blackliste"
    marque="Samsung",
    modele="Galaxy S23"
)
```

### 3. Reset password

```python
from app.services.eir_notifications import notifier_reset_password

# Pour reset de mot de passe
reset_link = f"https://eir-project.com/reset/{token}"
await notifier_reset_password(str(user.id), reset_link)
```

### 4. Alerte de sécurité

```python
from app.services.eir_notifications import notifier_alerte_securite

# Pour alerte de connexion suspecte
await notifier_alerte_securite(
    user_id=str(user.id),
    details_connexion={
        "date_connexion": "10/08/2025 à 14:30",
        "adresse_ip": "192.168.1.100",
        "localisation": "Casablanca, Maroc",
        "navigateur": "Chrome 115.0"
    }
)
```

## 🧪 Tests et vérification

### 1. Ajouter les routes de test dans main.py

```python
from app.routes.notification_integration import router as notification_integration_router

app.include_router(notification_integration_router)
```

### 2. Tester les templates

```bash
# Lister tous les templates
curl -X GET 'http://localhost:8000/notification-templates/templates-disponibles'

# Tester un template spécifique
curl -X GET 'http://localhost:8000/notification-templates/test-bienvenue'

# Voir les détails d'un template
curl -X GET 'http://localhost:8000/notification-templates/template/bienvenue?notification_type=email'
```

### 3. Script d'intégration

```bash
# Exécuter le script d'aide à l'intégration
./scripts/integrate-notification-templates.sh
```

## 📋 Templates disponibles

| Template | Email | SMS | Description |
|----------|-------|-----|-------------|
| `bienvenue` | ✅ | ✅ | Notification de bienvenue |
| `verification_imei_valide` | ✅ | ✅ | IMEI valide |
| `verification_imei_invalide` | ✅ | ✅ | IMEI invalide |
| `verification_imei_blackliste` | ✅ | ✅ | IMEI blacklisté |
| `reset_password` | ✅ | ❌ | Réinitialisation mot de passe |
| `alerte_securite` | ✅ | ✅ | Alerte de sécurité |

## 🔄 Migration depuis l'ancien système

### 1. Remplacer les anciens appels

**Avant :**
```python
# Ancien système
sujet = "Bienvenue"
contenu = f"Bonjour {user.nom}, bienvenue..."
await send_notification_now(user_id, "email", email, sujet, contenu)
```

**Après :**
```python
# Nouveau système
await envoyer_notification_bienvenue(str(user.id))
```

### 2. Avantages du nouveau système

- ✅ **Facilité** : Modification des textes sans redéploiement
- ✅ **Centralisation** : Tous les templates au même endroit
- ✅ **Cohérence** : Design uniforme des notifications
- ✅ **Variables** : Remplacement automatique des variables
- ✅ **Multilingue** : Support prêt pour plusieurs langues
- ✅ **Sécurité** : Validation automatique des templates

## 🛠️ Personnalisation avancée

### 1. Ajouter un nouveau template

```json
{
  "notifications": {
    "mon_nouveau_template": {
      "email": {
        "subject": "Mon sujet {variable}",
        "content": "Mon contenu avec {variable} et {autre_variable}"
      }
    }
  }
}
```

### 2. Utiliser le nouveau template

```python
from app.templates.simple_notifications import render_notification

result = render_notification(
    "mon_nouveau_template", 
    "email", 
    variable="valeur1",
    autre_variable="valeur2"
)
```

### 3. Variables globales

Modifiez la section `variables_globales` dans le JSON :

```json
{
  "variables_globales": {
    "company_name": "EIR Project",
    "support_email": "support@eir-project.com",
    "website_url": "https://eir-project.com"
  }
}
```

## 🔍 Débogage

### Vérifier les templates chargés

```python
from app.templates.simple_notifications import get_available_templates

templates = get_available_templates()
print(templates)
```

### Tester un rendu

```python
from app.templates.simple_notifications import render_notification

result = render_notification("bienvenue", "email", nom_utilisateur="Test")
print(result)
```

## 📞 Support

Si vous avez des questions ou des problèmes :

1. 📝 Vérifiez la syntaxe JSON dans `notifications_content.json`
2. 🧪 Utilisez les endpoints de test pour valider
3. 📋 Consultez les logs de l'application
4. 🔍 Vérifiez que toutes les variables requises sont fournies

---

**💡 Astuce :** Sauvegardez le fichier `notifications_content.json` avant de le modifier, au cas où vous auriez besoin de revenir en arrière.

**🚀 Prêt à utiliser !** Votre système de notifications est maintenant flexible et facile à maintenir.
