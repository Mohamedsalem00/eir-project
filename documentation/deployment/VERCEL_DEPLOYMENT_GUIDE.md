# 🚀 Guide de Déploiement Vercel

## Pré-requis
- Repository GitHub avec le projet EIR
- Backend déjà déployé sur https://eir-project.onrender.com
- Compte Vercel (gratuit)

## Étapes de Déploiement

### 1. Préparation du Code
```bash
cd frontend/
./deploy-vercel.sh
```

### 2. Configuration Vercel

#### A. Création du Projet
1. Allez sur [vercel.com](https://vercel.com)
2. Connectez votre compte GitHub
3. Cliquez sur **"New Project"**
4. Sélectionnez votre repository **"eir-project"**

#### B. Configuration du Projet
- **Project Name**: `eir-project-frontend`
- **Framework Preset**: `Next.js` (détection automatique)
- **Root Directory**: `frontend` ⚠️ **IMPORTANT**
- **Build Command**: `npm run build` (par défaut, ne pas changer)
- **Output Directory**: `.next` (par défaut, ne pas changer)
- **Install Command**: `npm install` (par défaut, ou `npm ci` pour plus de vitesse)
- **Node.js Version**: `18.x` (recommandé)

#### C. Variables d'Environnement
Ajoutez ces variables dans la section "Environment Variables" :

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://eir-project.onrender.com
NEXT_PUBLIC_API_VERSION=v1

# App Configuration
NEXT_PUBLIC_APP_NAME=Projet EIR
NEXT_PUBLIC_APP_DESCRIPTION=Système de Gestion des IMEI
NEXT_PUBLIC_DEFAULT_LOCALE=fr
NEXT_PUBLIC_SUPPORTED_LOCALES=fr,en,ar

# Rate Limiting
NEXT_PUBLIC_RATE_LIMIT_DISPLAY=true
NEXT_PUBLIC_VISITOR_SEARCH_LIMIT=10
NEXT_PUBLIC_AUTHENTICATED_SEARCH_LIMIT=100
NEXT_PUBLIC_RATE_LIMIT_REQUESTS=10
NEXT_PUBLIC_RATE_LIMIT_WINDOW=900000

# JWT
JWT_SECRET=votre-secret-jwt-production-super-securise
NEXT_PUBLIC_JWT_EXPIRY=3600

# Environment
NODE_ENV=production
NEXT_PUBLIC_DEBUG=false
```

### 3. Déploiement
1. Cliquez sur **"Deploy"**
2. Attendez la fin du build (2-5 minutes)
3. Votre app sera disponible sur `https://votre-projet.vercel.app`

### 4. Configuration Post-Déploiement

#### A. Domaine Personnalisé (Optionnel)
1. Dans le dashboard Vercel → Settings → Domains
2. Ajoutez votre domaine personnalisé

#### B. CORS Backend
Assurez-vous que votre backend Render accepte les requêtes de votre domaine Vercel :

```python
# Dans votre backend FastAPI
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://votre-projet.vercel.app",
    "https://votre-domaine-personnalise.com"
]
```

### 5. Variables d'Environnement Critiques

| Variable | Valeur Production | Description |
|----------|------------------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://eir-project.onrender.com` | URL backend Render |
| `NODE_ENV` | `production` | Mode production |
| `NEXT_PUBLIC_DEBUG` | `false` | Désactiver debug |
| `JWT_SECRET` | `[secret-securise]` | Secret JWT production |

### 6. Test Post-Déploiement

1. **Connectivité API** : Vérifiez que l'indicateur de connexion est vert
2. **Recherche IMEI** : Testez une recherche
3. **Recherche TAC** : Testez une recherche TAC
4. **Statistiques** : Vérifiez le chargement des stats
5. **Multilingue** : Testez le changement de langue

### 7. Redéploiement Automatique

Vercel redéploie automatiquement à chaque push sur la branche `main`. Pour forcer un redéploiement :
1. Dashboard Vercel → Deployments
2. Cliquez sur les "..." → "Redeploy"

### 8. Monitoring

- **Logs** : Dashboard Vercel → Functions → View Function Logs
- **Analytics** : Dashboard Vercel → Analytics
- **Performance** : Dashboard Vercel → Speed Insights

## Résolution de Problèmes

### ⚠️ Prévention des Conflits de Configuration

**Avant le déploiement, vérifiez qu'il n'y a pas de fichiers conflictuels :**

```bash
# Dans le dossier frontend/
# Supprimez ces fichiers s'ils existent (ancienne convention)
rm -f now.json
rm -rf .now/
rm -f .nowignore

# Vérifiez qu'il n'y a qu'un seul fichier de config
ls -la vercel.json   # ✅ Doit exister
ls -la now.json      # ❌ Ne doit PAS exister
```

**Variables d'environnement - Utilisez UNIQUEMENT le préfixe `VERCEL_` si nécessaire :**
- ✅ `VERCEL_URL` (automatique)
- ❌ `NOW_URL` (obsolète)

### Erreur : "Module not found"
```bash
# Vérifiez package.json dans frontend/
npm install
npm run build
```

### Erreur : "API Connection Failed"
- Vérifiez `NEXT_PUBLIC_API_URL`
- Testez l'URL backend : `curl https://eir-project.onrender.com/verification-etat`

### Erreur : "Build failed"
- Vérifiez les erreurs TypeScript
- Lancez `npm run build` localement

### Erreur : "Environment variables not found"
- Re-vérifiez toutes les variables d'environnement
- Redéployez après modification

## Commandes Utiles

```bash
# Test local production
npm run build && npm start

# Déploiement via CLI Vercel (optionnel)
npm i -g vercel
vercel --prod

# Logs en temps réel
vercel logs
```

---

🎯 **URL de votre application** : Sera fournie après le déploiement  
🔗 **Backend API** : https://eir-project.onrender.com  
📧 **Support** : Documentation Vercel officielle
