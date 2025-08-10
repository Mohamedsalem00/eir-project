#!/bin/bash

echo "🧹 NETTOYAGE PROFESSIONNEL DU PROJET EIR"
echo "========================================"
echo ""

# 1. Supprimer les fichiers Python compilés
echo "1️⃣ Suppression des fichiers Python compilés..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "✅ Fichiers .pyc et dossiers __pycache__ supprimés"

# 2. Supprimer les fichiers de test temporaires
echo ""
echo "2️⃣ Suppression des fichiers de test temporaires..."
rm -f test_*.py test_*.sh 2>/dev/null || true
echo "✅ Fichiers de test temporaires supprimés"

# 3. Nettoyer les logs anciens (garder les plus récents)
echo ""
echo "3️⃣ Nettoyage des logs anciens..."
if [ -d "backend/logs" ]; then
    find backend/logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    echo "✅ Logs de plus de 7 jours supprimés"
else
    echo "ℹ️ Aucun dossier de logs trouvé"
fi

# 4. Nettoyer les fichiers de sauvegarde temporaires
echo ""
echo "4️⃣ Suppression des fichiers de sauvegarde temporaires..."
find . -name "*.bak" -delete 2>/dev/null || true
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*~" -delete 2>/dev/null || true
echo "✅ Fichiers de sauvegarde temporaires supprimés"

# 5. Organiser les fichiers de documentation
echo ""
echo "5️⃣ Organisation des fichiers de documentation..."
mkdir -p docs/reports 2>/dev/null || true
mv *_REPORT.md docs/reports/ 2>/dev/null || true
mv PROFILE_ENDPOINT_IMPROVEMENTS.md docs/ 2>/dev/null || true
echo "✅ Documentation organisée"

# 6. Vérifier la structure du .gitignore
echo ""
echo "6️⃣ Vérification du .gitignore..."
if ! grep -q "__pycache__" .gitignore 2>/dev/null; then
    echo "
# Python
__pycache__/
*.py[cod]
*\$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env
.env.local
.env.production

# Logs
*.log
logs/

# Database
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Docker
.dockerignore

# Test files
test_*.py
test_*.sh
*.test

# Backup files
*.bak
*.tmp
*~
" >> .gitignore
    echo "✅ .gitignore mis à jour"
else
    echo "✅ .gitignore déjà configuré"
fi

# 7. Vérifier les permissions des scripts
echo ""
echo "7️⃣ Correction des permissions des scripts..."
find . -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
echo "✅ Permissions des scripts corrigées"

# 8. Optimiser le docker-compose pour la production
echo ""
echo "8️⃣ Vérification de la configuration Docker..."
if [ -f "docker-compose.yml" ]; then
    echo "✅ Configuration Docker présente"
else
    echo "⚠️ Configuration Docker manquante"
fi

echo ""
echo "🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS!"
echo "=================================="
echo ""
echo "📋 Résumé des actions effectuées:"
echo "  • Fichiers Python compilés supprimés"
echo "  • Fichiers de test temporaires supprimés"
echo "  • Logs anciens nettoyés"
echo "  • Fichiers de sauvegarde supprimés"
echo "  • Documentation organisée"
echo "  • .gitignore vérifié/mis à jour"
echo "  • Permissions des scripts corrigées"
echo ""
echo "✅ Le projet est prêt pour le commit et push!"
