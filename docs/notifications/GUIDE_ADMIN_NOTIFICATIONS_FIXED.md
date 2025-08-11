# Guide d'utilisation des notifications administrateur - EIR Project

## 🎯 Fonctionnalités corrigées

Le système de notifications administrateur a été corrigé pour **envoyer réellement les emails** et pas seulement créer des enregistrements en base de données.

### ✅ Corrections apportées

1. **Envoi effectif des emails** : Les endpoints admin envoient maintenant vraiment les emails via le service SMTP
2. **Gestion des erreurs** : Traitement approprié des échecs d'envoi avec stockage des erreurs
3. **Support SMS** : Support pour l'envoi de SMS en plus des emails
4. **Validation renforcée** : Validation des destinataires et types de notifications
5. **Endpoints de test** : Nouveaux endpoints pour tester la configuration

## 📡 Endpoints disponibles

### 1. Envoyer une notification à un utilisateur spécifique

```bash
POST /api/notifications/admin/envoyer-a-utilisateur
```

**Body (JSON):**
```json
{
  "utilisateur_id": "uuid-de-l-utilisateur",
  "type": "email",
  "destinataire": "optional@email.com",  // Optionnel, utilise l'email de l'utilisateur par défaut
  "sujet": "Sujet de votre email",
  "contenu": "Contenu détaillé du message...",
  "priorite": "normale"
}
```

**Réponse de succès:**
```json
{
  "success": true,
  "message": "Notification administrative envoyée avec succès",
  "notification_id": "uuid-notification"
}
```

### 2. Envoyer des notifications en lot

```bash
POST /api/notifications/admin/envoyer-lot-utilisateurs
```

**Body (JSON):**
```json
{
  "utilisateurs_ids": ["uuid1", "uuid2", "uuid3"],
  "type": "email",
  "sujet": "Message important",
  "contenu": "Contenu du message pour tous...",
  "priorite": "haute",
  "filtre_utilisateurs_actifs": true
}
```

**Réponse:**
```json
{
  "total_utilisateurs": 3,
  "envoyes_succes": 2,
  "envoyes_echec": 1,
  "utilisateurs_introuvables": [],
  "utilisateurs_inactifs": [],
  "details_envois": [
    {
      "utilisateur_id": "uuid1",
      "nom": "Jean Dupont",
      "destinataire": "jean@example.com",
      "statut": "succès",
      "notification_id": "uuid-notif"
    }
  ],
  "duree_traitement_secondes": 2.5
}
```

### 3. Lister les utilisateurs disponibles

```bash
GET /api/notifications/admin/liste-utilisateurs?actifs_seulement=true&avec_email=true&limite=50
```

### 4. Tester la configuration email

```bash
POST /api/notifications/admin/test-email?email_test=test@example.com
```

### 5. Tester la configuration SMS

```bash
POST /api/notifications/admin/test-sms?numero_test=+33123456789
```

## 🔧 Configuration requise

### 1. Variables d'environnement (.env)

```bash
# Configuration Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_USER=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe-app

# Configuration SMS (optionnel)
SMS_PROVIDER=console  # ou twilio, aws_sns
TWILIO_ACCOUNT_SID=votre-sid
TWILIO_AUTH_TOKEN=votre-token
TWILIO_PHONE_NUMBER=+33123456789

# Configuration générale
NOTIFICATIONS_ENABLED=true
EMAIL_TEST_MODE=false  # false pour envoyer vraiment
DEBUG_MODE=true
```

### 2. Authentification administrateur

Les endpoints admin nécessitent une authentification avec des privilèges administrateur.

**Header requis:**
```
Authorization: Bearer YOUR_ADMIN_JWT_TOKEN
```

## 🧪 Tests et validation

### 1. Script de test automatisé

```bash
python test_admin_email_notifications.py
```

### 2. Test manuel avec curl

```bash
# Test d'envoi d'email admin
curl -X POST "http://localhost:8000/api/notifications/admin/test-email?email_test=test@example.com" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"

# Test d'envoi de notification
curl -X POST "http://localhost:8000/api/notifications/admin/envoyer-a-utilisateur" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "utilisateur_id": "uuid-utilisateur",
    "type": "email",
    "sujet": "Test admin",
    "contenu": "Message de test"
  }'
```

## 🚨 Gestion des erreurs

Le système gère maintenant correctement les erreurs:

1. **Envoi échoué** : La notification est créée avec le statut 'échoué' et l'erreur est stockée
2. **Utilisateur introuvable** : Erreur HTTP 404 avec message explicite
3. **Validation échouée** : Erreur HTTP 422 avec détails de validation
4. **Problème de configuration** : Erreur HTTP 500 avec logs détaillés

## 📊 Monitoring et logs

### Vérification des logs

```bash
# Logs des notifications
tail -f backend/logs/notifications.log

# Logs généraux de l'application
tail -f backend/logs/app.log
```

### Statistiques en base de données

```sql
-- Vérifier les notifications récentes
SELECT * FROM notifications 
WHERE date_creation > NOW() - INTERVAL '1 hour'
ORDER BY date_creation DESC;

-- Statistiques par statut
SELECT statut, COUNT(*) 
FROM notifications 
GROUP BY statut;
```

## 📝 Exemples d'utilisation pratiques

### 1. Notification de maintenance

```json
{
  "utilisateurs_ids": ["all-admin-users"],
  "type": "email",
  "sujet": "Maintenance programmée - EIR Project",
  "contenu": "Une maintenance est programmée le 15/08/2025 de 2h à 4h. Le système sera temporairement indisponible.",
  "priorite": "haute"
}
```

### 2. Alerte de sécurité

```json
{
  "utilisateur_id": "uuid-user",
  "type": "email",
  "sujet": "🚨 Alerte de sécurité - Connexion suspecte",
  "contenu": "Une connexion suspecte a été détectée sur votre compte. Si ce n'est pas vous, veuillez changer votre mot de passe immédiatement."
}
```

### 3. Rapport mensuel

```json
{
  "utilisateurs_ids": ["active-users"],
  "type": "email",
  "sujet": "📊 Votre rapport mensuel EIR Project",
  "contenu": "Retrouvez votre rapport d'activité du mois dernier en pièce jointe."
}
```

## 🔄 Intégration avec les templates

Le système est compatible avec les templates JSON existants dans `backend/app/templates/`. Vous pouvez:

1. Utiliser les templates prédéfinis
2. Créer de nouveaux templates personnalisés
3. Utiliser les variables dynamiques dans les contenus

## 🎯 Bonnes pratiques

1. **Testez toujours** avec l'endpoint de test avant l'envoi en masse
2. **Vérifiez les logs** après chaque envoi important
3. **Utilisez la pagination** pour les envois en lot important (> 100 utilisateurs)
4. **Personnalisez les contenus** selon le contexte de votre organisation
5. **Surveillez les taux d'échec** et ajustez la configuration si nécessaire

---

**Note**: Ce système remplace les anciennes implémentations qui ne faisaient que créer des enregistrements en base sans envoyer réellement les emails.
