# 🔔 Guide de Démarrage Rapide - Système de Notifications EIR

## 🚀 Démarrage en 5 minutes

### 1. Configuration de base

```bash
# Copiez le fichier de configuration
cp backend/.env.example backend/.env

# Éditez les variables d'environnement
nano backend/.env
```

**Configuration minimale pour commencer :**
```env
# Gmail (le plus simple pour commencer)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_USER=votre-email@gmail.com
EMAIL_PASSWORD=votre-mot-de-passe-app

# Mode développement
EMAIL_TEST_MODE=true
SMS_TEST_MODE=true
NOTIFICATIONS_MODE=development
```

### 2. Installation des dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 3. Mise à jour de la base de données

```bash
# Appliquez le nouveau schéma
psql -d eir_project -f schema_postgres.sql

# Ou avec Docker
docker exec -i eir-postgres psql -U postgres -d eir_project < backend/schema_postgres.sql
```

### 4. Démarrage du backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 5. Test rapide

```bash
# Testez immédiatement
./scripts/test-eir-notifications.sh --basic
```

## 📧 Configuration Email

### Gmail (Recommandé pour débuter)

1. **Activez l'authentification à 2 facteurs** sur votre compte Gmail
2. **Générez un mot de passe d'application :**
   - Allez sur https://myaccount.google.com/security
   - "Mots de passe des applications"
   - Sélectionnez "Autre" et nommez-le "EIR Project"
   - Utilisez le mot de passe généré dans `EMAIL_PASSWORD`

3. **Configuration dans .env :**
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_USER=votre-email@gmail.com
EMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx  # Mot de passe d'application
```

### Autres providers

<details>
<summary>Outlook/Hotmail</summary>

```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_USER=votre-email@outlook.com
EMAIL_PASSWORD=votre-mot-de-passe
```
</details>

<details>
<summary>SendGrid (Production)</summary>

```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
EMAIL_USE_TLS=true
EMAIL_USER=apikey
EMAIL_PASSWORD=votre-api-key-sendgrid
```
</details>

## 📱 Configuration SMS

### Mode Console (Par défaut)
```env
SMS_PROVIDER=console
SMS_TEST_MODE=true
```
Les SMS s'affichent dans la console/logs.

### Twilio (Production)
```env
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_PHONE_NUMBER=+33123456789
```

### AWS SNS (Production)
```env
SMS_PROVIDER=aws_sns
AWS_ACCESS_KEY_ID=votre-access-key
AWS_SECRET_ACCESS_KEY=votre-secret-key
AWS_REGION=eu-west-1
```

## 🔧 Utilisation dans le code

### Envoi simple

```python
from app.tasks.notification_dispatcher import send_notification_now

# Email simple
result = await send_notification_now(
    user_id="user123",
    notification_type="email",
    destinataire="user@example.com",
    sujet="Test notification",
    contenu="Ceci est un test"
)
```

### Notifications EIR prêtes à l'emploi

```python
from app.services.eir_notifications import EIRNotificationService

# Notifier une vérification IMEI
await EIRNotificationService.notifier_verification_imei(
    user_id="user123",
    imei="123456789012345",
    resultat="valide",
    details={
        "marque": "Samsung",
        "modele": "Galaxy S21",
        "tac": "35123456",
        "luhn_valide": True
    }
)

# Notifier un IMEI bloqué
await EIRNotificationService.notifier_imei_bloque(
    user_id="user123",
    imei="987654321098765",
    raison="Appareil volé déclaré"
)

# Notifier un nouvel appareil
await EIRNotificationService.notifier_nouvel_appareil(
    user_id="user123",
    appareil_details={
        "marque": "Apple",
        "modele": "iPhone 14 Pro",
        "emmc": "A2894",
        "imeis": ["123456789012345", "123456789012346"]
    }
)
```

### Intégration dans les routes FastAPI

```python
from app.services.eir_notifications import EIRNotificationService

@router.post("/imei/{imei}/verifier")
async def verifier_imei(
    imei: str,
    current_user: Utilisateur = Depends(get_current_user)
):
    # ... logique de vérification ...
    
    # Notifier automatiquement le résultat
    await EIRNotificationService.notifier_verification_imei(
        user_id=str(current_user.id),
        imei=imei,
        resultat=resultat,
        details=details
    )
    
    return resultat
```

## 🛠️ API Endpoints

### Endpoints principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/notifications/send` | POST | Envoyer une notification |
| `/api/notifications/` | GET | Lister les notifications |
| `/api/notifications/stats` | GET | Statistiques |
| `/api/notifications/config` | GET/PUT | Configuration |
| `/api/notifications/process-pending` | POST | Traiter manuellement |
| `/api/notifications/test-email` | POST | Tester la connectivité email |
| `/api/notifications/test-sms` | POST | Tester la connectivité SMS |

### Exemple d'envoi via API

```bash
curl -X POST "http://localhost:8000/api/notifications/send" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user",
    "notification_type": "email",
    "destinataire": "test@example.com",
    "sujet": "Test EIR",
    "contenu": "Votre IMEI 123456789012345 est valide."
  }'
```

## 📊 Surveillance et Monitoring

### Logs
```bash
# Voir les logs en temps réel
tail -f backend/logs/notifications.log

# Filtrer les erreurs
grep "ERROR" backend/logs/notifications.log

# Statistiques des envois
grep "Notification sent" backend/logs/notifications.log | wc -l
```

### Statistiques via API
```bash
curl http://localhost:8000/api/notifications/stats
```

### Dashboard (en développement)
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

## 🧪 Tests

### Test complet
```bash
./scripts/test-eir-notifications.sh
```

### Tests spécifiques
```bash
# Endpoints de base uniquement
./scripts/test-eir-notifications.sh --basic

# Notifications réalistes EIR
./scripts/test-eir-notifications.sh --realistic

# Test de charge
./scripts/test-eir-notifications.sh --load

# Scénarios d'erreur
./scripts/test-eir-notifications.sh --errors
```

### Test manuel simple
```bash
# Test connectivité email
curl -X POST http://localhost:8000/api/notifications/test-email

# Test connectivité SMS
curl -X POST http://localhost:8000/api/notifications/test-sms

# Statistiques
curl http://localhost:8000/api/notifications/stats
```

## 🚀 Mise en production

### 1. Configuration production

```env
# .env pour production
NOTIFICATIONS_MODE=production
EMAIL_TEST_MODE=false
SMS_TEST_MODE=false
DEBUG_MODE=false
LOG_LEVEL=WARNING

# Utilisez des services externes
SMTP_SERVER=smtp.sendgrid.net
SMS_PROVIDER=twilio
```

### 2. Variables d'environnement Docker

```yaml
# docker-compose.prod.yml
environment:
  - SMTP_SERVER=smtp.sendgrid.net
  - EMAIL_USER=apikey
  - EMAIL_PASSWORD=${SENDGRID_API_KEY}
  - SMS_PROVIDER=twilio
  - TWILIO_ACCOUNT_SID=${TWILIO_SID}
  - TWILIO_AUTH_TOKEN=${TWILIO_TOKEN}
```

### 3. Monitoring production

- Activez les alertes sur les échecs d'envoi
- Surveillez les métriques de delivery
- Configurez la rotation des logs
- Mettez en place des alertes sur les quotas

## ❓ Résolution de problèmes

### Email ne fonctionne pas
```bash
# 1. Vérifiez la configuration
curl -X POST http://localhost:8000/api/notifications/test-email

# 2. Vérifiez les logs
grep "email" backend/logs/notifications.log

# 3. Problèmes Gmail courants :
# - Authentification 2FA activée ?
# - Mot de passe d'application généré ?
# - "Accès aux applications moins sécurisées" désactivé ?
```

### SMS ne fonctionne pas
```bash
# 1. Vérifiez la configuration
curl -X POST http://localhost:8000/api/notifications/test-sms

# 2. Mode console activé ?
grep "SMS_PROVIDER" backend/.env

# 3. Credentials Twilio corrects ?
```

### Notifications non traitées
```bash
# 1. Scheduler actif ?
curl http://localhost:8000/api/notifications/stats

# 2. Traitement manuel
curl -X POST http://localhost:8000/api/notifications/process-pending

# 3. Vérifiez les erreurs
grep "ERROR" backend/logs/notifications.log
```

## 📚 Ressources utiles

- **Documentation API :** http://localhost:8000/docs
- **Configuration complète :** `backend/.env.example`
- **Tests :** `scripts/test-eir-notifications.sh`
- **Logs :** `backend/logs/notifications.log`
- **Exemples d'usage :** `backend/app/services/eir_notifications.py`

## 🤝 Support

En cas de problème :

1. Vérifiez les logs : `tail -f backend/logs/notifications.log`
2. Testez la configuration : `./scripts/test-eir-notifications.sh --basic`
3. Consultez la documentation API : http://localhost:8000/docs
4. Vérifiez les variables d'environnement dans `.env`

---

*Système de notifications EIR - Prêt pour la production* 🚀
