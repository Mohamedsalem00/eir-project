# 🌐 Frontend EIR - Interface Web Moderne

> **Interface utilisateur moderne** pour le système EIR avec support multilingue (fr/en/ar), rate limiting pour visiteurs, et interface d'administration complète.

[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.0+-38B2AC.svg)](https://tailwindcss.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

## 🎯 Vue d'Ensemble

Cette interface frontend moderne s'intègre parfaitement avec l'API EIR backend pour offrir :

- ✅ **Interface publique IMEI** avec rate limiting pour visiteurs et intégration API complète
- ✅ **Support multilingue** français/anglais/arabe avec détection automatique
- ✅ **Tableau de bord utilisateur** avec gestion d'appareils et notifications
- ✅ **Panel administrateur** complet avec toutes les fonctionnalités backend
- ✅ **Authentication JWT** sécurisée avec gestion de sessions
- ✅ **Design responsive** optimisé mobile/tablet/desktop
- ✅ **SEO optimisé** pour la recherche publique d'IMEI
- ✅ **Validation IMEI en temps réel** avec feedback visuel et gestion d'erreurs avancée
- ✅ **Rate limiting intelligent** avec compteurs et informations de retry
- ✅ **Interface de test API** pour développeurs et debugging

## 🔍 Fonctionnalités IMEI Intégrées

### **Recherche IMEI Principale (`/`)**
- **Validation en temps réel** : Format IMEI vérifié pendant la saisie
- **Nettoyage automatique** : Suppression des caractères non numériques
- **Rate limiting visuel** : Compteur de recherches avec limites affichées
- **Gestion d'erreurs avancée** : Messages détaillés selon le type d'erreur
- **Affichage contextualisé** : Informations adaptées au niveau d'accès utilisateur

### **Interface de Test API (`/test`)**
- **Test de connectivité** : Vérification de l'état du backend en temps réel
- **IMEI d'exemple** : Base de données d'IMEI valides/invalides pour test
- **Monitoring rate limiting** : Visualisation des compteurs et limites
- **Debug responses** : Affichage détaillé des réponses API

### **Intégration Backend Complète**
```typescript
// Service API centralisé
EIRApiService.searchIMEI(imei) → {
  success: boolean,
  data?: IMEIResponse,
  error?: string,
  rateLimitInfo?: RateLimitInfo
}

// Gestion intelligente des erreurs
- 429: Rate limit avec retry info
- 403: Accès refusé avec motif
- 404: IMEI non trouvé confirmé
- 422: Format invalide détecté
- 500: Erreur serveur gérée
```

## 🚀 Architecture Technique

### **Stack Technologique**
```
Frontend Stack:
├── ⚛️  Next.js 14 (App Router)     # Framework React full-stack
├── 🔷  TypeScript 5.0+             # Typage statique
├── 🎨  Tailwind CSS 3.0+           # Framework CSS utilitaire
├── 🔗  Axios                       # Client HTTP pour API
├── 📱  React Hook Form             # Gestion des formulaires
├── 🗃️  Zustand                     # State management léger
├── 🌍  next-intl                   # Internationalisation
└── 📦  Vercel                      # Déploiement (recommandé)
```

### **Structure du Projet**
```
frontend/
├── 📄 README.md                    # Ce fichier
├── ⚙️  next.config.js              # Configuration Next.js
├── 🎨 tailwind.config.js           # Configuration Tailwind
├── 📦 package.json                 # Dépendances npm
├── 🔧 .env.local                   # Variables d'environnement
├── 🛡️  middleware.ts               # Rate limiting & auth
├── 📱 app/                         # Routes Next.js 14 (App Router)
│   ├── [locale]/                  # Support multilingue
│   │   ├── page.tsx              # Page d'accueil publique IMEI
│   │   ├── about/                # Pages à propos
│   │   ├── stats/                # Statistiques publiques
│   │   └── layout.tsx            # Layout multilingue
│   ├── (auth)/                   # Routes protégées
│   │   ├── dashboard/            # Tableau de bord utilisateur
│   │   ├── devices/              # Gestion d'appareils
│   │   ├── notifications/        # Centre de notifications
│   │   ├── profile/              # Profil utilisateur
│   │   └── admin/                # Panel administrateur
│   │       ├── users/            # Gestion utilisateurs
│   │       ├── devices/          # Administration appareils
│   │       ├── tac/              # Gestion base TAC
│   │       ├── audit/            # Journaux d'audit
│   │       ├── notifications/    # Notifications admin
│   │       ├── access/           # Gestion des accès
│   │       └── import-export/    # Opérations en lot
│   ├── api/                      # API Routes Next.js
│   │   ├── auth/                 # Proxies d'authentification
│   │   └── rate-limit/           # Middleware rate limiting
│   └── globals.css               # Styles globaux
├── 🧩 components/                  # Composants réutilisables
│   ├── public/                   # Interface publique
│   │   ├── IMEISearchForm.tsx    # Formulaire recherche IMEI
│   │   ├── PublicStats.tsx       # Statistiques publiques
│   │   └── Header.tsx            # En-tête publique
│   ├── auth/                     # Composants d'authentification
│   │   ├── LoginForm.tsx         # Formulaire de connexion
│   │   ├── RegisterForm.tsx      # Formulaire d'inscription
│   │   └── ProtectedRoute.tsx    # Wrapper de protection
│   ├── admin/                    # Interface d'administration
│   │   ├── UserManagement.tsx    # Gestion des utilisateurs
│   │   ├── DeviceManagement.tsx  # Gestion des appareils
│   │   ├── TACManagement.tsx     # Gestion base TAC
│   │   ├── AuditLogs.tsx         # Journaux d'audit
│   │   ├── AccessControl.tsx     # Contrôle d'accès
│   │   └── BulkOperations.tsx    # Opérations en lot
│   ├── dashboard/                # Tableau de bord
│   │   ├── StatsCards.tsx        # Cartes de statistiques
│   │   ├── RecentActivity.tsx    # Activité récente
│   │   └── QuickActions.tsx      # Actions rapides
│   ├── shared/                   # Composants partagés
│   │   ├── Layout.tsx            # Layout principal
│   │   ├── Navigation.tsx        # Navigation
│   │   ├── Footer.tsx            # Pied de page
│   │   ├── LoadingSpinner.tsx    # Indicateur de chargement
│   │   ├── ErrorBoundary.tsx     # Gestion d'erreurs
│   │   ├── Modal.tsx             # Composant modal
│   │   ├── Table.tsx             # Tableau réutilisable
│   │   └── Form/                 # Éléments de formulaire
│   └── ui/                       # Composants UI de base
│       ├── Button.tsx            # Boutons
│       ├── Input.tsx             # Champs de saisie
│       ├── Select.tsx            # Listes déroulantes
│       └── Toast.tsx             # Notifications toast
├── 🔧 lib/                        # Utilitaires et configuration
│   ├── api.ts                    # Client API EIR
│   ├── auth.ts                   # Gestion authentification JWT
│   ├── utils.ts                  # Fonctions utilitaires
│   ├── constants.ts              # Constantes de l'application
│   └── validators.ts             # Schémas de validation
├── 🌍 messages/                   # Traductions i18n
│   ├── fr.json                   # Français (défaut)
│   ├── en.json                   # Anglais
│   └── ar.json                   # Arabe
├── 🎨 styles/                     # Styles personnalisés
│   └── globals.css               # Styles globaux
├── 📁 public/                     # Assets statiques
│   ├── images/                   # Images
│   ├── icons/                    # Icônes
│   └── favicon.ico               # Favicon
└── 🔧 hooks/                      # Hooks React personnalisés
    ├── useAuth.ts                # Hook d'authentification
    ├── useAPI.ts                 # Hook API générique
    ├── useTranslation.ts         # Hook de traduction
    └── useRateLimit.ts           # Hook rate limiting
```

## 🛠️ Installation et Configuration

### **Prérequis**
```bash
# Option 1: Développement local avec Node.js
node --version   # Node.js 18.0+
npm --version    # npm 8.0+

# Option 2: Développement avec Docker (recommandé)
docker --version          # Docker 20.0+
docker-compose --version  # Docker Compose 2.0+
```

### **🐳 Installation avec Docker (Recommandé)**
```bash
# 1. Cloner le projet (si pas déjà fait)
git clone <votre-repo>
cd eir-project

# 2. Lancer tout l'environnement (backend + frontend + database)
docker-compose up -d

# 3. Vérifier que tout fonctionne
docker-compose ps

# 4. Voir les logs en temps réel
docker-compose logs -f frontend
docker-compose logs -f web

# 5. Arrêter l'environnement
docker-compose down
```

**URLs de développement avec Docker:**
- 🌐 **Frontend:** http://localhost:3000
- 🔧 **Backend API:** http://localhost:8000
- 📊 **Docs API:** http://localhost:8000/docs
- 🗄️ **PostgreSQL:** localhost:5432

### **Installation Locale (Alternative)**
```bash
# 1. Aller dans le dossier frontend
cd frontend

# 2. Installer les dépendances
npm install

# 3. Configuration des variables d'environnement
cp .env.example .env.local

# 4. Démarrer le serveur de développement
npm run dev
```

### **Variables d'Environnement**
```bash
# .env.local
# Configuration API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1

# Configuration Application
NEXT_PUBLIC_APP_NAME=Projet EIR
NEXT_PUBLIC_APP_DESCRIPTION=Système de Gestion des IMEI
NEXT_PUBLIC_DEFAULT_LOCALE=fr
NEXT_PUBLIC_SUPPORTED_LOCALES=fr,en,ar

# Configuration Rate Limiting (visiteurs)
NEXT_PUBLIC_RATE_LIMIT_REQUESTS=10
NEXT_PUBLIC_RATE_LIMIT_WINDOW=900000

# Configuration JWT
JWT_SECRET=votre-secret-jwt-ultra-securise
NEXT_PUBLIC_JWT_EXPIRY=3600

# Configuration Développement
NODE_ENV=development
NEXT_PUBLIC_DEBUG=false

# Configuration Production (déploiement)
NEXT_PUBLIC_SITE_URL=https://votre-domaine.com
NEXT_PUBLIC_API_URL_PROD=https://api.votre-domaine.com
```

## 🎨 Interfaces Principales

### **1. Interface Publique IMEI**
```typescript
// app/[locale]/page.tsx - Page d'accueil publique
'use client'

export default function PublicIMEISearch() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      <Header />
      <main className="container mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            🔍 Vérification IMEI
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Système EIR - Vérifiez l'authenticité de votre appareil mobile
          </p>
        </div>
        
        <div className="max-w-2xl mx-auto">
          <IMEISearchForm />
          <PublicStats />
        </div>
      </main>
      <Footer />
    </div>
  )
}
```

### **2. Tableau de Bord Utilisateur**
```typescript
// app/(auth)/dashboard/page.tsx
export default function UserDashboard() {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Tableau de Bord
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard title="Mes Appareils" value="12" icon="📱" />
        <StatsCard title="Recherches" value="45" icon="🔍" />
        <StatsCard title="Notifications" value="3" icon="🔔" />
        <StatsCard title="Dernière Activité" value="2h" icon="⏰" />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <RecentActivity />
        <MyDevices />
      </div>
    </div>
  )
}
```

### **3. Panel Administrateur**
```typescript
// app/(auth)/admin/page.tsx
export default function AdminPanel() {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Administration EIR
        </h1>
        <QuickActions />
      </div>
      
      <Tabs>
        <Tab label="👥 Utilisateurs">
          <UserManagement />
        </Tab>
        <Tab label="📱 Appareils">
          <DeviceManagement />
        </Tab>
        <Tab label="🏗️ Base TAC">
          <TACManagement />
        </Tab>
        <Tab label="📊 Audit">
          <AuditLogs />
        </Tab>
        <Tab label="🔐 Accès">
          <AccessControl />
        </Tab>
        <Tab label="📦 Import/Export">
          <BulkOperations />
        </Tab>
        <Tab label="🔔 Notifications">
          <NotificationCenter />
        </Tab>
      </Tabs>
    </div>
  )
}
```

## 🔐 Authentification et Sécurité

### **Middleware de Rate Limiting**
```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const rateLimitMap = new Map()

export function middleware(request: NextRequest) {
  // Rate limiting pour visiteurs
  if (request.nextUrl.pathname.startsWith('/api/public')) {
    const ip = request.ip ?? '127.0.0.1'
    const now = Date.now()
    const windowMs = 15 * 60 * 1000 // 15 minutes
    const maxRequests = 10

    const requests = rateLimitMap.get(ip) || []
    const validRequests = requests.filter((time: number) => time > now - windowMs)

    if (validRequests.length >= maxRequests) {
      return new Response('Rate limit exceeded', { status: 429 })
    }

    validRequests.push(now)
    rateLimitMap.set(ip, validRequests)
  }

  // Protection des routes authentifiées
  if (request.nextUrl.pathname.startsWith('/dashboard') || 
      request.nextUrl.pathname.startsWith('/admin')) {
    const token = request.cookies.get('auth_token')
    
    if (!token) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/api/:path*', '/dashboard/:path*', '/admin/:path*']
}
```

### **Hook d'Authentification**
```typescript
// hooks/useAuth.ts
export const useAuth = () => {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  const login = async (email: string, password: string) => {
    const response = await api.post('/authentification/connexion', {
      email,
      mot_de_passe: password
    })
    
    const { access_token, user_info } = response.data
    localStorage.setItem('auth_token', access_token)
    setUser(user_info)
    
    return response.data
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setUser(null)
    router.push('/login')
  }

  return { user, isLoading, login, logout, isAuthenticated: !!user }
}
```

## 🌍 Support Multilingue

### **Configuration i18n**
```typescript
// next.config.js
const withNextIntl = require('next-intl/plugin')()

module.exports = withNextIntl({
  i18n: {
    locales: ['fr', 'en', 'ar'],
    defaultLocale: 'fr',
    localeDetection: true
  }
})
```

### **Messages de Traduction**
```json
// messages/fr.json
{
  "imei": {
    "search": "Rechercher un IMEI",
    "placeholder": "Entrez votre IMEI (15 chiffres)",
    "search_button": "🔍 Vérifier IMEI",
    "result_found": "✅ IMEI trouvé",
    "result_not_found": "❌ IMEI non trouvé",
    "rate_limit": "Limite de recherche atteinte. Réessayez plus tard."
  },
  "navigation": {
    "home": "Accueil",
    "dashboard": "Tableau de Bord",
    "devices": "Appareils",
    "admin": "Administration",
    "logout": "Déconnexion"
  }
}
```

## 📱 Composants Clés

### **Formulaire de Recherche IMEI**
```typescript
// components/public/IMEISearchForm.tsx
export default function IMEISearchForm() {
  const [imei, setImei] = useState('')
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const searchIMEI = async () => {
    setIsLoading(true)
    try {
      const response = await api.get(`/imei/${imei}`)
      setResult(response.data)
    } catch (error) {
      if (error.response?.status === 429) {
        toast.error('Limite de recherche atteinte')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
      <div className="flex gap-4">
        <input
          type="text"
          value={imei}
          onChange={(e) => setImei(e.target.value)}
          placeholder="Entrez votre IMEI (ex: 123456789012345)"
          className="flex-1 p-4 border-2 border-gray-300 rounded-lg text-lg"
          maxLength={15}
        />
        <button
          onClick={searchIMEI}
          disabled={isLoading || imei.length < 14}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 
                     text-white font-semibold py-4 px-8 rounded-lg"
        >
          {isLoading ? '🔄' : '🔍'} Vérifier
        </button>
      </div>
      
      {result && <IMEIResult result={result} />}
    </div>
  )
}
```

## 🚀 Démarrage du Développement

### **🐳 Avec Docker (Recommandé)**
```bash
# Démarrage complet de l'environnement
docker-compose up -d

# Voir les logs du frontend
docker-compose logs -f frontend

# Redémarrer uniquement le frontend
docker-compose restart frontend

# Reconstruire le frontend après changements de dépendances
docker-compose build frontend
docker-compose up -d frontend

# Arrêt de l'environnement
docker-compose down

# Arrêt avec suppression des volumes (attention: perte de données)
docker-compose down -v
```

### **Développement Local (Alternative)**
```bash
# Démarrage du serveur de développement
npm run dev

# Construction pour la production
npm run build

# Démarrage de la production
npm run start

# Linting et formatage
npm run lint
npm run type-check
```

### **🚀 Scripts Docker Utiles**
```bash
# Construire seulement l'image frontend
docker build -t eir-frontend ./frontend

# Démarrage en mode production
docker-compose -f docker-compose.prod.yml up -d

# Voir l'utilisation des ressources
docker stats

# Nettoyer les images non utilisées
docker system prune -f
```

### **Scripts Utilitaires**
```json
// package.json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "analyze": "ANALYZE=true next build"
  }
}
```

## 🎨 Design et UX

### **Thème et Couleurs**
```css
/* styles/globals.css */
:root {
  --primary: #2563eb;      /* Bleu EIR */
  --secondary: #64748b;    /* Gris ardoise */
  --success: #10b981;      /* Vert succès */
  --warning: #f59e0b;      /* Orange alerte */
  --error: #ef4444;        /* Rouge erreur */
  --background: #f8fafc;   /* Fond clair */
  --surface: #ffffff;      /* Surface blanche */
  --text: #1e293b;         /* Texte sombre */
}

.theme-dark {
  --background: #0f172a;
  --surface: #1e293b;
  --text: #f1f5f9;
}
```

### **Responsive Design**
```typescript
// Breakpoints Tailwind utilisés
const breakpoints = {
  sm: '640px',   // Mobile large
  md: '768px',   // Tablet
  lg: '1024px',  // Desktop
  xl: '1280px',  // Desktop large
  '2xl': '1536px' // Desktop très large
}
```

## 🔧 Configuration et Optimisation

### **Performance**
- ✅ **Code Splitting** automatique avec Next.js
- ✅ **Image Optimization** avec next/image
- ✅ **Static Generation** pour les pages publiques
- ✅ **API Routes** pour la logique backend
- ✅ **Caching** intelligent des requêtes API

### **SEO et Accessibilité**
- ✅ **Meta tags** dynamiques
- ✅ **Open Graph** pour partage social
- ✅ **Schema.org** pour données structurées
- ✅ **ARIA labels** pour accessibilité
- ✅ **Support RTL** pour l'arabe

## 📦 Déploiement

### **🐳 Production avec Docker**
```bash
# 1. Construction des images de production
docker-compose -f docker-compose.prod.yml build

# 2. Démarrage en production
docker-compose -f docker-compose.prod.yml up -d

# 3. Variables d'environnement de production
# Modifiez les variables dans docker-compose.prod.yml ou utilisez un fichier .env
export NEXT_PUBLIC_API_URL=https://api.votre-domaine.com
export NEXT_PUBLIC_SITE_URL=https://votre-domaine.com
export JWT_SECRET=votre-secret-jwt-ultra-securise-production
```

### **Vercel (Alternative)**
```bash
# Installation CLI Vercel
npm i -g vercel

# Déploiement
vercel

# Variables d'environnement
vercel env add NEXT_PUBLIC_API_URL
vercel env add JWT_SECRET
```

### **Docker Swarm / Kubernetes**
```yaml
# docker-stack.yml pour Docker Swarm
version: '3.8'
services:
  frontend:
    image: eir-frontend:latest
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://api.votre-domaine.com
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
```

### **Variables de Production**
```bash
# Configuration production obligatoire
NEXT_PUBLIC_API_URL=https://api.votre-domaine.com
NEXT_PUBLIC_SITE_URL=https://votre-domaine.com
NODE_ENV=production
JWT_SECRET=secret-ultra-securise-256-bits

# Configuration optionnelle
NEXT_PUBLIC_RATE_LIMIT_REQUESTS=50
NEXT_PUBLIC_RATE_LIMIT_WINDOW=900000
```

## 🤝 Intégration avec le Backend EIR

### **Client API**
```typescript
// lib/api.ts
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept-Language': 'fr'
  }
})

// Intercepteur pour JWT
api.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### **Endpoints Utilisés**
```typescript
// Correspondance avec l'API backend
export const endpoints = {
  // Public
  imei: (imei: string) => `/imei/${imei}`,
  stats: '/public/statistiques',
  health: '/verification-etat',
  
  // Auth
  login: '/authentification/connexion',
  register: '/authentification/inscription',
  profile: '/authentification/profile',
  
  // User
  devices: '/appareils',
  notifications: '/notifications',
  searches: '/recherches',
  
  // Admin
  users: '/admin/gestion-acces/utilisateurs',
  audit: '/admin/journaux-audit',
  tac: '/admin/tac/stats',
  bulkImport: '/admin/import-file'
}
```

## 📝 Documentation Complémentaire

- 📖 **[Guide d'Utilisation](./docs/USER_GUIDE.md)** - Guide utilisateur détaillé
- 🔧 **[Guide Développeur](./docs/DEVELOPER_GUIDE.md)** - Guide technique complet
- 🎨 **[Design System](./docs/DESIGN_SYSTEM.md)** - Système de design et composants
- 🌍 **[Guide i18n](./docs/I18N_GUIDE.md)** - Internationalisation et traductions
- 🚀 **[Guide Déploiement](./docs/DEPLOYMENT_GUIDE.md)** - Déploiement en production

---

🔗 **Liens Utiles**
- [Backend EIR](../README.md) - Documentation du backend
- [API Documentation](http://localhost:8000/docs) - Documentation interactive
- [Next.js Documentation](https://nextjs.org/docs) - Framework officiel
- [Tailwind CSS](https://tailwindcss.com/docs) - Documentation CSS

💬 **Support et Contact**
- 📧 Email: support@eir-project.com
- 💬 Issues: [GitHub Issues](https://github.com/Mohamedsalem00/eir-project/issues)
- 📖 Wiki: [Project Wiki](https://github.com/Mohamedsalem00/eir-project/wiki)
