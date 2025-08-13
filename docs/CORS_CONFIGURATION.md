# Configuration CORS pour EIR Project

## Vue d'ensemble

La configuration CORS (Cross-Origin Resource Sharing) a été modifiée pour être plus flexible et configurable via des variables d'environnement. Cela permet de modifier facilement les URLs autorisées sans toucher au code.

## Variables d'environnement

### `CORS_ALLOWED_ORIGINS`
Liste des URLs autorisées pour les requêtes CORS, séparées par des virgules.

**Format :** `url1,url2,url3` (sans espaces)

**Exemple :**
```bash
CORS_ALLOWED_ORIGINS=https://eir-project.vercel.app,http://localhost:3000,https://mon-domaine.com
```

### `CORS_ALLOWED_METHODS`
Méthodes HTTP autorisées pour les requêtes CORS.

**Défaut :** `GET,POST,PUT,DELETE,OPTIONS`

### `CORS_ALLOWED_HEADERS`
En-têtes autorisés pour les requêtes CORS.

**Défaut :** `Authorization,Content-Type,Accept,Accept-Language,X-Requested-With,Access-Control-Allow-Origin`

## Configuration pour différents environnements

### Développement local
```bash
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000
```

### Production avec Vercel
```bash
CORS_ALLOWED_ORIGINS=https://eir-project.vercel.app,https://eir-project-git-main-mohamedsalem00s-projects.vercel.app
```

### Environnement de test
```bash
CORS_ALLOWED_ORIGINS=https://staging.eir-project.com,http://localhost:3000
```

## Instructions de configuration

1. **Modifier le fichier `.env`** dans le dossier `backend/`
2. **Ajouter ou modifier** la variable `CORS_ALLOWED_ORIGINS`
3. **Redémarrer le serveur backend** pour que les changements prennent effet
4. **Tester** les requêtes depuis votre frontend

## Exemples pratiques

### Ajouter un nouveau domaine
Si vous déployez sur un nouveau domaine `https://mon-nouveau-site.com` :

```bash
CORS_ALLOWED_ORIGINS=https://eir-project.vercel.app,https://mon-nouveau-site.com,http://localhost:3000
```

### Configuration pour plusieurs environnements
```bash
# Production + Staging + Développement
CORS_ALLOWED_ORIGINS=https://eir-project.vercel.app,https://staging-eir.vercel.app,http://localhost:3000,http://localhost:3001
```

## Sécurité

⚠️ **Important :** 
- Ne jamais utiliser `*` en production
- Limiter aux domaines strictement nécessaires
- Toujours utiliser HTTPS en production
- Vérifier régulièrement les domaines configurés

## Résolution des problèmes

### Erreur CORS lors des requêtes
1. Vérifiez que votre URL frontend est dans `CORS_ALLOWED_ORIGINS`
2. Assurez-vous d'utiliser le bon protocole (http/https)
3. Redémarrez le serveur backend après modification
4. Vérifiez les logs du navigateur pour plus de détails

### Test de la configuration
```bash
# Tester depuis le navigateur ou curl
curl -H "Origin: https://eir-project.vercel.app" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     http://localhost:8000/
```

## Migration depuis l'ancienne configuration

L'ancienne configuration codée en dur :
```python
allow_origins=[
    "https://eir-project.vercel.app",
    "http://localhost:3000",
    # ...
]
```

Nouvelle configuration basée sur les variables d'environnement :
```python
allow_origins=get_cors_origins()
```

Avantages :
- ✅ Configuration flexible sans modification du code
- ✅ Différents paramètres par environnement  
- ✅ Ajout/suppression facile de domaines
- ✅ Meilleure sécurité en production
