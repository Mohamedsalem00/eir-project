# 📧 Guide d'utilisation - Endpoints Administratifs de Notifications

## 🎯 Nouveaux endpoints créés

Vous disposez maintenant de **3 nouveaux endpoints** spécialement conçus pour les administrateurs :

### 1. 📋 Lister les utilisateurs
```http
GET /notifications/admin/liste-utilisateurs
```

**Paramètres de requête :**
- `actifs_seulement`: bool (défaut: true) - Filtrer les utilisateurs actifs uniquement
- `avec_email`: bool (défaut: true) - Filtrer les utilisateurs ayant un email
- `recherche`: string (optionnel) - Rechercher par nom ou email
- `limite`: int (défaut: 50, max: 100) - Nombre max de résultats

**Exemple de réponse :**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "nom": "Mohamed Salem",
    "email": "mohamed@eir-project.com",
    "type_utilisateur": "utilisateur_authentifie",
    "niveau_acces": "standard",
    "organisation": "EIR Corp",
    "est_actif": true,
    "date_creation": "2025-08-10T10:30:00"
  }
]
```

### 2. 📧 Envoyer une notification à un utilisateur
```http
POST /notifications/admin/envoyer-a-utilisateur
```

**Corps de la requête :**
```json
{
  "utilisateur_id": "550e8400-e29b-41d4-a716-446655440000",
  "type": "email",
  "destinataire": "mohamed@example.com",
  "sujet": "🔔 Notification importante",
  "contenu": "Votre compte a été mis à jour avec succès.",
  "envoyer_immediatement": true,
  "priorite": "haute"
}
```

**Notes importantes :**
- Si `destinataire` n'est pas spécifié, l'email de l'utilisateur sera utilisé
- Le `sujet` est obligatoire pour les emails
- `priorite` peut être : "normale", "haute", "urgente"
- Le contenu sera automatiquement enrichi avec des informations administratives

### 3. 📢 Envoyer des notifications en lot
```http
POST /notifications/admin/envoyer-lot-utilisateurs
```

**Corps de la requête :**
```json
{
  "utilisateurs_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002"
  ],
  "type": "email",
  "sujet": "📢 Maintenance programmée",
  "contenu": "Le système sera en maintenance demain de 2h à 4h du matin.",
  "priorite": "normale",
  "filtre_utilisateurs_actifs": true
}
```

**Réponse détaillée :**
```json
{
  "total_utilisateurs": 3,
  "envoyes_succes": 2,
  "envoyes_echec": 1,
  "utilisateurs_introuvables": [],
  "utilisateurs_inactifs": ["550e8400-e29b-41d4-a716-446655440002"],
  "details_envois": [
    {
      "utilisateur_id": "550e8400-e29b-41d4-a716-446655440000",
      "nom": "Mohamed Salem",
      "email": "mohamed@example.com",
      "statut": "succès",
      "notification_id": "notif-123"
    }
  ],
  "duree_traitement_secondes": 2.45
}
```

## 🔐 Authentification requise

Tous ces endpoints nécessitent un **niveau d'accès administrateur**. Utilisez votre token JWT admin :

```bash
curl -X GET "http://localhost:8000/notifications/admin/liste-utilisateurs" \
  -H "Authorization: Bearer VOTRE_TOKEN_ADMIN" \
  -H "Content-Type: application/json"
```

## 🚀 Exemples d'utilisation pratiques

### Cas 1: Notification de maintenance
```bash
# 1. Lister tous les utilisateurs actifs
curl -X GET "http://localhost:8000/notifications/admin/liste-utilisateurs?actifs_seulement=true&limite=100" \
  -H "Authorization: Bearer TOKEN_ADMIN"

# 2. Envoyer à tous en lot
curl -X POST "http://localhost:8000/notifications/admin/envoyer-lot-utilisateurs" \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "utilisateurs_ids": ["id1", "id2", "id3"],
    "type": "email",
    "sujet": "🔧 Maintenance programmée",
    "contenu": "Le système EIR sera indisponible demain de 2h à 4h.",
    "priorite": "haute"
  }'
```

### Cas 2: Alerte sécurité urgente
```bash
curl -X POST "http://localhost:8000/notifications/admin/envoyer-a-utilisateur" \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "utilisateur_id": "user-123",
    "type": "email",
    "sujet": "🚨 ALERTE SÉCURITÉ",
    "contenu": "Activité suspecte détectée sur votre compte. Changez votre mot de passe immédiatement.",
    "priorite": "urgente",
    "envoyer_immediatement": true
  }'
```

### Cas 3: Communication générale
```bash
# Rechercher des utilisateurs spécifiques
curl -X GET "http://localhost:8000/notifications/admin/liste-utilisateurs?recherche=mohamed&limite=10" \
  -H "Authorization: Bearer TOKEN_ADMIN"

# Envoyer à un utilisateur spécifique
curl -X POST "http://localhost:8000/notifications/admin/envoyer-a-utilisateur" \
  -H "Authorization: Bearer TOKEN_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{
    "utilisateur_id": "user-mohamed",
    "type": "email",
    "sujet": "🎉 Félicitations",
    "contenu": "Votre compte a été activé avec succès!",
    "priorite": "normale"
  }'
```

## ✨ Fonctionnalités avancées

### Enrichissement automatique du contenu
Pour les emails, le contenu est automatiquement enrichi avec :
- Un en-tête indiquant qu'il s'agit d'une notification administrative
- La date et heure d'envoi
- Le niveau de priorité
- Les informations du destinataire
- Un pied de page avec contact admin

### Gestion des erreurs
- Utilisateurs introuvables sont listés séparément
- Utilisateurs inactifs sont filtrés si demandé
- Détails complets des envois (succès/échec) avec raisons
- Temps de traitement pour les envois en lot

### Logs et traçabilité
Toutes les actions administratives sont loggées avec :
- L'ID de l'admin qui envoie
- Les destinataires
- Le type et priorité
- Les résultats d'envoi

## 🔧 Intégration avec l'interface admin

Ces endpoints peuvent être facilement intégrés dans une interface d'administration :

1. **Page de gestion des utilisateurs** : Utiliser `/admin/liste-utilisateurs`
2. **Bouton "Envoyer notification"** : Utiliser `/admin/envoyer-a-utilisateur`
3. **Communication de masse** : Utiliser `/admin/envoyer-lot-utilisateurs`

## 📊 Monitoring et statistiques

Utilisez les endpoints existants pour monitorer :
- `/admin/notifications/statistiques-dispatcher` - Stats générales
- `/notifications/statistiques/globales` - Stats personnelles de l'admin

---

**🎯 Les endpoints sont maintenant prêts et fonctionnels !**

Pour tester, utilisez le script `test_admin_notifications.py` fourni ou intégrez directement dans votre interface d'administration.
