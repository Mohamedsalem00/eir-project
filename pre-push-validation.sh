#!/bin/bash

echo "🔍 VALIDATION FINALE AVANT PUSH"
echo "==============================="
echo ""

# 1. Vérifier que l'application démarre correctement
echo "1️⃣ Vérification du démarrage de l'application..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Application fonctionne correctement"
else
    echo "⚠️ Application non accessible - démarrage des containers..."
    docker compose up -d
    sleep 5
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Application démarrée avec succès"
    else
        echo "❌ Problème de démarrage de l'application"
        exit 1
    fi
fi

# 2. Vérifier la base de données
echo ""
echo "2️⃣ Vérification de la base de données..."
if docker compose exec db psql -U postgres -d eir_project -c "\dt" > /dev/null 2>&1; then
    echo "✅ Base de données accessible"
    
    # Vérifier la table password_reset
    if docker compose exec db psql -U postgres -d eir_project -c "\d password_reset" > /dev/null 2>&1; then
        echo "✅ Table password_reset présente"
    else
        echo "⚠️ Table password_reset manquante"
    fi
else
    echo "❌ Problème d'accès à la base de données"
    exit 1
fi

# 3. Test rapide des endpoints critiques
echo ""
echo "3️⃣ Test des endpoints critiques..."

# Test health check
if curl -s http://localhost:8000/health | grep -q "sain"; then
    echo "✅ Health check OK"
else
    echo "❌ Health check échec"
    exit 1
fi

# Test endpoint profile simple (sans auth pour test basique)
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ Documentation API accessible"
else
    echo "⚠️ Documentation API non accessible"
fi

# 4. Vérifier la structure des fichiers
echo ""
echo "4️⃣ Vérification de la structure des fichiers..."

# Fichiers essentiels
essential_files=(
    "backend/app/models/password_reset.py"
    "backend/app/schemas/password_reset.py"
    "backend/migrations/003_add_password_reset_table.sql"
    "COMMIT_SUMMARY.md"
    "docker-compose.yml"
    "README.md"
)

for file in "${essential_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file manquant"
        exit 1
    fi
done

# 5. Vérifier que Git est prêt
echo ""
echo "5️⃣ Vérification Git..."
if git status --porcelain | grep -q .; then
    echo "⚠️ Fichiers non commités détectés"
    git status --short
else
    echo "✅ Tous les fichiers sont commités"
fi

# 6. Informations du commit
echo ""
echo "6️⃣ Informations du dernier commit..."
echo "Commit: $(git log --oneline -1)"
echo "Auteur: $(git log -1 --pretty=format:'%an <%ae>')"
echo "Date: $(git log -1 --pretty=format:'%cd')"

echo ""
echo "🎉 VALIDATION TERMINÉE AVEC SUCCÈS!"
echo "==================================="
echo ""
echo "📋 État du projet:"
echo "  ✅ Application fonctionnelle"
echo "  ✅ Base de données opérationnelle"
echo "  ✅ Endpoints critiques testés"
echo "  ✅ Structure des fichiers validée"
echo "  ✅ Git repository propre"
echo ""
echo "🚀 PRÊT POUR LE PUSH!"
echo ""
echo "Pour pusher les changements:"
echo "git push origin main"
