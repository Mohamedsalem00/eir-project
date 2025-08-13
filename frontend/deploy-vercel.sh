#!/bin/bash

# Script de préparation pour le déploiement Vercel

echo "🚀 Préparation du déploiement Vercel..."
echo "======================================"

# Vérifier que nous sommes dans le bon dossier
if [ ! -f "package.json" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le dossier frontend/"
    exit 1
fi

# Installer les dépendances
echo "📦 Installation des dépendances..."
npm install

# Vérifier la configuration
echo "🔍 Vérification de la configuration..."
if [ ! -f ".env.production" ]; then
    echo "⚠️  Attention: .env.production n'existe pas"
    echo "   Copiez .env.local vers .env.production et adaptez les URLs"
fi

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
    echo "7. Dans 'Environment Variables', ajoutez :"
    echo "   NEXT_PUBLIC_API_URL=https://eir-project.onrender.com"
    echo "   JWT_SECRET=[votre-secret-securise]"
    echo "8. Cliquez 'Deploy'"
    echo ""
    echo "🔧 Variables d'environnement importantes :"
    echo "   NEXT_PUBLIC_API_URL=https://eir-project.onrender.com"
    echo "   NEXT_PUBLIC_API_VERSION=v1"
    echo "   NODE_ENV=production"
    echo "   NEXT_PUBLIC_DEBUG=false"
else
    echo "❌ Erreur de build. Vérifiez les erreurs ci-dessus."
    exit 1
fi
