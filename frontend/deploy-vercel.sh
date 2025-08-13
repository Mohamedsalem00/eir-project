#!/bin/bash

# Script de préparation pour le déploiement Vercel

echo "🚀 Préparation du déploiement Vercel..."
echo "======================================"

# Vérifier que nous sommes dans le bon dossier
if [ ! -f "package.json" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le dossier frontend/"
    exit 1
fi

# Vérifier et nettoyer les conflits de configuration
echo "🔍 Vérification des conflits de configuration..."

# Supprimer les anciens fichiers de configuration
if [ -f "now.json" ]; then
    echo "⚠️  Suppression de now.json (obsolète)"
    rm -f now.json
fi

if [ -d ".now" ]; then
    echo "⚠️  Suppression du dossier .now (obsolète)"
    rm -rf .now
fi

if [ -f ".nowignore" ]; then
    echo "⚠️  Suppression de .nowignore (obsolète)"
    rm -f .nowignore
fi

# Vérifier les fichiers de configuration requis
if [ ! -f "vercel.json" ]; then
    echo "❌ Erreur: vercel.json manquant"
    exit 1
else
    echo "✅ vercel.json présent"
fi

if [ ! -f ".vercelignore" ]; then
    echo "⚠️  .vercelignore manquant (recommandé)"
else
    echo "✅ .vercelignore présent"
fi

# Installer les dépendances
echo "📦 Installation des dépendances..."
npm install

# Vérifier la configuration
echo "🔍 Vérification de la configuration..."
if [ ! -f ".env.production" ]; then
    echo "⚠️  Attention: .env.production n'existe pas"
    echo "   Les variables d'environnement seront configurées sur Vercel"
fi

# Nettoyage avant build
echo "🧹 Nettoyage des fichiers temporaires..."
rm -rf .next
rm -rf node_modules/.cache

# Build de test
echo "🔨 Test de build..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build réussi !"
    echo ""
    echo "🎯 Prochaines étapes pour Vercel :"
    echo "================================="
    echo ""
    echo "1. Allez sur https://vercel.com"
    echo "2. Connectez votre compte GitHub"
    echo "3. Cliquez sur 'New Project'"
    echo "4. Sélectionnez votre repository 'eir-project'"
    echo "5. Dans 'Root Directory', sélectionnez 'frontend'"
    echo "6. Gardez 'Framework Preset' sur 'Next.js'"
    echo "7. NE MODIFIEZ PAS les commandes de build (par défaut)"
    echo "8. Dans 'Environment Variables', ajoutez :"
    echo "   NEXT_PUBLIC_API_URL=https://eir-project.onrender.com"
    echo "   JWT_SECRET=[votre-secret-securise]"
    echo "   NODE_ENV=production"
    echo "   NEXT_PUBLIC_DEBUG=false"
    echo "9. Cliquez 'Deploy'"
    echo ""
    echo "🔧 Variables d'environnement importantes :"
    echo "   NEXT_PUBLIC_API_URL=https://eir-project.onrender.com"
    echo "   NODE_ENV=production"
    echo "   NEXT_PUBLIC_DEBUG=false"
    echo ""
    echo "⚠️  ATTENTION :"
    echo "   - Ne pas utiliser 'builds' et 'functions' ensemble"
    echo "   - Pour Next.js, seuls 'maxDuration' et 'memory' sont supportés"
    echo "   - Les variables d'environnement sont définies sur Vercel, pas dans vercel.json"
else
    echo "❌ Erreur de build. Vérifiez les erreurs ci-dessus."
    exit 1
fi
