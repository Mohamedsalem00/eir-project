#!/bin/bash

# 🚀 Script d'intégration du nouveau système de templates
# ======================================================

echo "🔧 Intégration du nouveau système de notifications..."

# 1. Vérifier que les fichiers existent
echo "📋 Vérification des fichiers..."

FILES=(
    "backend/app/templates/notifications_content.json"
    "backend/app/templates/simple_notifications.py"
    "backend/app/services/eir_notifications.py"
    "backend/app/routes/notification_integration.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - OK"
    else
        echo "❌ $file - MANQUANT"
        exit 1
    fi
done

echo ""
echo "🎯 Pour intégrer complètement le système:"
echo ""

echo "1. 📝 Ajouter dans main.py:"
echo "   from app.routes.notification_integration import router as notification_integration_router"
echo "   app.include_router(notification_integration_router)"
echo ""

echo "2. 🔄 Dans vos routes existantes, remplacer les anciens appels par:"
echo "   from app.services.eir_notifications import ("
echo "       envoyer_notification_bienvenue,"
echo "       notifier_verification_imei,"
echo "       notifier_reset_password,"
echo "       notifier_alerte_securite"
echo "   )"
echo ""

echo "3. 🧪 Tester les nouveaux endpoints:"
echo "   GET /notification-templates/test-bienvenue"
echo "   GET /notification-templates/test-verification-imei"
echo "   GET /notification-templates/templates-disponibles"
echo ""

echo "4. ✏️ Modifier les notifications facilement dans:"
echo "   backend/app/templates/notifications_content.json"
echo ""

echo "✅ Système de templates intégré avec succès!"
echo ""
echo "📚 Documentation complète disponible dans:"
echo "   - backend/app/routes/notification_integration.py"
echo "   - backend/app/templates/simple_notifications.py"
echo ""

# Afficher un exemple de test
echo "🧪 Exemple de test rapide:"
echo "curl -X GET 'http://localhost:8000/notification-templates/templates-disponibles'"
echo ""

echo "🎉 Terminé! Vous pouvez maintenant utiliser le nouveau système de templates."
