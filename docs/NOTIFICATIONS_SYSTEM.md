# Système de Notifications EIR Project

## Vue d'ensemble

Le système de notifications EIR Project est un système complet de gestion des notifications par email et SMS intégré à l'API FastAPI. Il supporte l'envoi asynchrone, les retry automatiques, la planification, et la gestion des erreurs.

## Architecture

### Composants principaux

1. **Services d'envoi** (`backend/app/services/`)
   - `email_service.py` - Service d'envoi d'emails (SMTP/Gmail)
   - `sms_service.py` - Service d'envoi de SMS (Console/Twilio/AWS SNS)

2. **Dispatcher** (`backend/app/tasks/`)
   - `notification_dispatcher.py` - Traitement automatique des notifications
   - `notification_scheduler.py` - Planificateur APScheduler

3. **API Routes** (`backend/app/routes/`)
   - `notifications.py` - Endpoints FastAPI pour la gestion des notifications

4. **Modèles et Schémas**
   - `models/notification.py` - Modèle SQLAlchemy
   - `schemas/notifications.py` - Schémas Pydantic

5. **Configuration**
   - `config/notifications.yml` - Configuration centralisée
   - `.env.notifications.example` - Variables d'environnement

## Configuration

### Fichier de configuration principal

Le fichier `config/notifications.yml` contient toute la configuration :

```yaml
notifications:
  enabled: true
  
  email:
    enabled: true
    provider: "smtp"  # ou "gmail"
    retry:
      max_attempts: 3
      retry_delay_seconds: 300
  
  sms:
    enabled: false  # Mode développement
    provider: "console"  # ou "twilio", "aws_sns"
  
  scheduler:
    enabled: true
    check_interval_seconds: 60
    batch_size: 50
```

### Variables d'environnement

Créez un fichier `.env` avec vos paramètres :

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app
SMTP_FROM_EMAIL=noreply@eir-project.com

# SMS Configuration (optionnel)
SMS_PROVIDER=console
TWILIO_ACCOUNT_SID=votre-account-sid
TWILIO_AUTH_TOKEN=votre-auth-token
```

### Configuration Gmail

1. Activez l'authentification à 2 facteurs
2. Générez un mot de passe d'application :
   - Google Account → Sécurité → Authentification en 2 étapes
   - Mots de passe des applications → Créer
3. Utilisez ce mot de passe dans `SMTP_PASSWORD`

## Utilisation

### 1. Créer une notification

```python
# Via l'API
POST /notifications/
{
    "type": "email",
    "destinataire": "user@example.com",
    "sujet": "Votre IMEI a été vérifié",
    "contenu": "Votre IMEI 123456789012345 a été vérifié avec succès.",
    "envoyer_immediatement": false
}
```

### 2. Envoyer immédiatement

```python
# Bypass de la queue pour envoi urgent
POST /notifications/envoyer-immediatement
{
    "type": "sms",
    "destinataire": "+33123456789",
    "contenu": "Alerte sécurité: Activité suspecte détectée"
}
```

### 3. Traitement automatique

Le système traite automatiquement les notifications en attente :
- Vérification toutes les 60 secondes (configurable)
- Retry automatique en cas d'échec
- Respect des limites de débit
- Heures de fonctionnement configurables

### 4. Administration

```python
# Déclencher le traitement manuellement
POST /admin/notifications/scheduler/trigger/process_notifications

# Voir les statistiques
GET /admin/notifications/statistiques-dispatcher

# Tester les connexions
GET /admin/notifications/test-connexions
```

## API Endpoints

### Endpoints Utilisateur

- `POST /notifications/` - Créer une notification
- `GET /notifications/` - Lister ses notifications
- `GET /notifications/{id}` - Détails d'une notification
- `POST /notifications/envoyer-immediatement` - Envoi immédiat
- `GET /notifications/statistiques/globales` - Statistiques personnelles

### Endpoints Administrateur

- `POST /admin/notifications/traiter-en-attente` - Traiter les notifications
- `GET /admin/notifications/statistiques-dispatcher` - Stats du dispatcher
- `GET /admin/notifications/test-connexions` - Tester les services
- `GET /admin/notifications/configuration` - Configuration complète

### Endpoints Planificateur

- `GET /admin/notifications/scheduler/status` - Statut du planificateur
- `POST /admin/notifications/scheduler/trigger/{job_id}` - Déclencher une tâche

## Types de Notifications

### Email

```python
{
    "type": "email",
    "destinataire": "user@example.com",
    "sujet": "Sujet requis",
    "contenu": "Corps du message"
}
```

**Providers supportés :**
- `smtp` - SMTP générique
- `gmail` - Gmail avec mot de passe d'application

### SMS

```python
{
    "type": "sms",
    "destinataire": "+33123456789",
    "contenu": "Message SMS (max 1600 caractères)"
}
```

**Providers supportés :**
- `console` - Simulation pour développement
- `twilio` - Service Twilio SMS
- `aws_sns` - AWS Simple Notification Service

## Gestion des Erreurs

### Retry Automatique

- 3 tentatives maximum par défaut
- Délai croissant (backoff exponentiel)
- Sauvegarde des erreurs en base

### Rate Limiting

- Limites par utilisateur par heure/jour
- Limites globales par minute
- Configuration flexible

### Statuts des Notifications

- `en_attente` - En attente de traitement
- `envoyé` - Envoyé avec succès
- `échoué` - Échec définitif après retry

## Monitoring et Logs

### Logs

Les logs sont sauvegardés dans :
- `logs/notifications.log` - Log général
- `logs/email_notifications.log` - Logs email
- `logs/sms_notifications.log` - Logs SMS
- `logs/sms_simulation.log` - Simulation SMS

### Métriques

Le système fournit des métriques détaillées :
- Nombre total de notifications
- Taux de succès par type
- Statistiques du dispatcher
- Performance des services

## Déploiement

### Docker

Le système est compatible Docker. Ajoutez au `docker-compose.yml` :

```yaml
services:
  eir_backend:
    environment:
      - SMTP_HOST=${SMTP_HOST}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - SMS_PROVIDER=console
    volumes:
      - ./logs:/app/logs
```

### Variables d'environnement requises

```bash
# Obligatoires pour email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=votre-email@gmail.com
SMTP_PASSWORD=votre-mot-de-passe-app
SMTP_FROM_EMAIL=noreply@eir-project.com

# Optionnelles
NOTIFICATION_LOG_LEVEL=INFO
NOTIFICATION_SCHEDULER_INTERVAL=60
```

## Tests

### Script de test automatique

```bash
# Exécuter tous les tests
./scripts/test-notifications.sh

# Le script teste :
# - Santé de l'API
# - Connexions des services
# - Création de notifications
# - Envoi immédiat
# - Planificateur
# - Statistiques
```

### Tests manuels

1. **Test email SMTP :**
```bash
curl -X POST "http://localhost:8000/admin/notifications/test-connexions" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

2. **Créer une notification test :**
```bash
curl -X POST "http://localhost:8000/notifications/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "destinataire": "test@example.com",
    "sujet": "Test",
    "contenu": "Message de test"
  }'
```

3. **Déclencher le traitement :**
```bash
curl -X POST "http://localhost:8000/admin/notifications/scheduler/trigger/process_notifications" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Maintenance

### Nettoyage automatique

Le système nettoie automatiquement :
- Notifications envoyées après 30 jours
- Notifications échouées après 7 jours
- Exécution quotidienne à 2h00

### Configuration du nettoyage

```yaml
cleanup:
  enabled: true
  delete_sent_after_days: 30
  delete_failed_after_days: 7
  archive_before_delete: true
```

## Sécurité

### Authentification

- Endpoints protégés par JWT
- Permissions par niveau (utilisateur/admin)
- Isolation des données par utilisateur

### Validation

- Validation des emails et numéros de téléphone
- Sanitisation du contenu
- Limites de taille des messages

### Rate Limiting

- Protection contre l'abus
- Limites configurables
- Monitoring des quotas

## Troubleshooting

### Erreurs communes

1. **Authentification SMTP échouée**
   - Vérifiez le mot de passe d'application Gmail
   - Confirmez l'activation de l'auth 2FA

2. **Notifications non traitées**
   - Vérifiez que le planificateur fonctionne
   - Contrôlez les heures de fonctionnement

3. **Rate limiting dépassé**
   - Ajustez les limites dans la configuration
   - Vérifiez les quotas utilisateur

### Debug

```bash
# Voir les logs
tail -f logs/notifications.log

# Statut du planificateur
curl "http://localhost:8000/admin/notifications/scheduler/status"

# Statistiques détaillées
curl "http://localhost:8000/admin/notifications/statistiques-dispatcher"
```

## Intégration

### Dans votre code

```python
from app.tasks import send_notification_now

# Envoi immédiat
result = await send_notification_now(
    user_id="123",
    notification_type="email",
    destinataire="user@example.com",
    sujet="Bienvenue",
    contenu="Merci de votre inscription"
)
```

### Avec d'autres services

Le système s'intègre facilement avec :
- Systèmes d'authentification
- Webhooks externes
- APIs de validation IMEI
- Systèmes de monitoring

## Support

### Documentation

- API interactive : `/docs`
- Schémas OpenAPI : `/openapi.json`
- Cette documentation dans `docs/notifications/`

### Logs et monitoring

- Logs structurés en JSON
- Métriques temps réel
- Alertes configurables

Pour plus d'aide, consultez les logs ou contactez l'équipe de développement.
