# ✅ Checklist de Pré-Déploiement Vercel

## Avant de déployer sur Vercel

### 📋 Vérifications Obligatoires

- [ ] **Configuration Next.js**
  - [ ] `package.json` présent avec les scripts `build`, `start`, `dev`
  - [ ] Version Node.js compatible (16.x ou 18.x recommandé)
  - [ ] Pas d'erreurs TypeScript : `npm run type-check`
  - [ ] Build réussi : `npm run build`

- [ ] **Fichiers de Configuration**
  - [ ] `vercel.json` présent et valide
  - [ ] `.vercelignore` créé pour optimiser le déploiement
  - [ ] **PAS** de `now.json` (obsolète)
  - [ ] **PAS** de dossier `.now/` (obsolète)
  - [ ] **PAS** de `.nowignore` (obsolète)

- [ ] **Variables d'Environnement**
  - [ ] `NEXT_PUBLIC_API_URL` pointant vers Render
  - [ ] `NODE_ENV=production`
  - [ ] `NEXT_PUBLIC_DEBUG=false`
  - [ ] Pas de variables sensibles dans le code source

- [ ] **Sécurité**
  - [ ] Secrets JWT sécurisés
  - [ ] URLs API correctes (HTTPS)
  - [ ] CORS configuré sur le backend

### 🔧 Configuration Vercel

- [ ] **Paramètres Projet**
  - [ ] Root Directory : `frontend`
  - [ ] Framework : `Next.js`
  - [ ] Build Command : `npm run build` (par défaut)
  - [ ] Output Directory : `.next` (par défaut)
  - [ ] Install Command : `npm install` (par défaut)

- [ ] **Variables d'Environnement sur Vercel**
  ```
  NEXT_PUBLIC_API_URL=https://eir-project.onrender.com
  NEXT_PUBLIC_API_VERSION=v1
  NODE_ENV=production
  NEXT_PUBLIC_DEBUG=false
  JWT_SECRET=votre-secret-production-securise
  ```

### 🧪 Tests Pré-Déploiement

- [ ] **Build Local**
  ```bash
  cd frontend/
  npm install
  npm run build
  npm start  # Test de production locale
  ```

- [ ] **Tests Fonctionnels**
  - [ ] Page d'accueil se charge
  - [ ] Connexion API fonctionne
  - [ ] Recherche IMEI fonctionne
  - [ ] Changement de langue fonctionne
  - [ ] Responsive design OK

### 🚀 Déploiement

- [ ] **GitHub**
  - [ ] Code commité et pushé
  - [ ] Branche `main` à jour

- [ ] **Vercel**
  - [ ] Projet créé avec bonne configuration
  - [ ] Variables d'environnement ajoutées
  - [ ] Premier déploiement réussi
  - [ ] URL de production accessible

### ✅ Post-Déploiement

- [ ] **Tests Production**
  - [ ] Site accessible via URL Vercel
  - [ ] API backend connectée
  - [ ] Toutes les fonctionnalités testées
  - [ ] Performance acceptable

- [ ] **Monitoring**
  - [ ] Logs Vercel consultés
  - [ ] Erreurs éventuelles résolues
  - [ ] Analytics activées (optionnel)

### 🆘 En Cas de Problème

1. **Build Failed**
   - Vérifier `npm run build` en local
   - Consulter les logs Vercel
   - Vérifier les variables d'environnement

2. **API Connection Failed**
   - Vérifier `NEXT_PUBLIC_API_URL`
   - Tester l'API backend directement
   - Vérifier les CORS

3. **Environment Variables Missing**
   - Vérifier toutes les variables sur Vercel Dashboard
   - Redéployer après modification

---

🎯 **Utilisez ce checklist avant chaque déploiement pour éviter les erreurs courantes**
