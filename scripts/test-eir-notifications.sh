#!/bin/bash

# Script de test des notifications EIR avec des scénarios réels
# Usage: ./test-eir-notifications.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "🔔 Test des notifications EIR - Scénarios d'usage réels"
echo "===================================================="

# Vérifier que le backend est démarré
check_backend() {
    echo "🔍 Vérification du backend..."
    if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "❌ Le backend n'est pas accessible sur http://localhost:8000"
        echo "   Démarrez-le avec: cd backend && uvicorn app.main:app --reload"
        exit 1
    fi
    echo "✅ Backend accessible"
}

# Fonction pour tester un endpoint
test_endpoint() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="$3"
    local expected_status="${4:-200}"
    local description="$5"
    
    echo "📡 Test: $description"
    echo "   Endpoint: $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" = "$expected_status" ]; then
        echo "   ✅ Status: $http_code (attendu: $expected_status)"
        echo "   📄 Réponse: $(echo "$body" | jq -r '.message // .detail // .' 2>/dev/null || echo "$body")"
    else
        echo "   ❌ Status: $http_code (attendu: $expected_status)"
        echo "   📄 Erreur: $body"
    fi
    
    echo ""
}

# Test des endpoints de base
test_basic_endpoints() {
    echo "📊 Test des endpoints de base"
    echo "-----------------------------"
    
    # Statistiques
    test_endpoint "http://localhost:8000/api/notifications/stats" "GET" "" "200" "Statistiques des notifications"
    
    # Configuration actuelle
    test_endpoint "http://localhost:8000/api/notifications/config" "GET" "" "200" "Configuration des notifications"
    
    # Liste des notifications (avec pagination)
    test_endpoint "http://localhost:8000/api/notifications?limit=5" "GET" "" "200" "Liste des notifications (limite 5)"
    
    # Test de connectivité email
    test_endpoint "http://localhost:8000/api/notifications/test-email" "POST" '{}' "200" "Test de connectivité email"
    
    # Test de connectivité SMS
    test_endpoint "http://localhost:8000/api/notifications/test-sms" "POST" '{}' "200" "Test de connectivité SMS"
}

# Test de création de notifications réalistes
test_realistic_notifications() {
    echo "📱 Test de notifications réalistes EIR"
    echo "--------------------------------------"
    
    # Notification de vérification IMEI
    test_endpoint "http://localhost:8000/api/notifications/send" "POST" '{
        "user_id": "test-user-1",
        "notification_type": "email",
        "destinataire": "user@example.com",
        "sujet": "✅ Résultat vérification IMEI: 123456789012345",
        "contenu": "Votre IMEI 123456789012345 est VALIDE.\n\nMarque: Samsung\nModèle: Galaxy S21\nCode TAC: 35123456\nValidation Luhn: Oui\n\nCet IMEI est reconnu et peut être utilisé normalement.\n\n---\nEIR Project"
    }' "200" "Notification vérification IMEI valide"
    
    # Notification IMEI bloqué
    test_endpoint "http://localhost:8000/api/notifications/send" "POST" '{
        "user_id": "test-user-2", 
        "notification_type": "email",
        "destinataire": "admin@example.com",
        "sujet": "🚨 ALERTE SÉCURITÉ - IMEI Bloqué: 987654321098765",
        "contenu": "ALERTE: Un IMEI a été bloqué dans le système.\n\nIMEI: 987654321098765\nRaison: Appareil volé déclaré\nDate: 2024-01-15 14:30\n\nActions:\n- Appareil bloqué sur le réseau\n- Utilisateur notifié\n- Autorités informées\n\n---\nEIR Project - Système d'\''alerte automatique"
    }' "200" "Alerte IMEI bloqué"
    
    # Notification nouvel appareil
    test_endpoint "http://localhost:8000/api/notifications/send" "POST" '{
        "user_id": "test-user-3",
        "notification_type": "email", 
        "destinataire": "newuser@example.com",
        "sujet": "📱 Nouvel appareil enregistré: iPhone 14 Pro",
        "contenu": "Bonjour,\n\nUn nouvel appareil a été ajouté à votre compte EIR:\n\nMarque: Apple\nModèle: iPhone 14 Pro\nIMEI 1: 123456789012345\nIMEI 2: 123456789012346\nDate d'\''ajout: 2024-01-15\n\nSi vous n'\''avez pas ajouté cet appareil, contactez immédiatement le support.\n\n---\nEIR Project"
    }' "200" "Notification nouvel appareil"
    
    # Notification maintenance programmée
    test_endpoint "http://localhost:8000/api/notifications/send" "POST" '{
        "user_id": "broadcast",
        "notification_type": "email",
        "destinataire": "users@eir-project.com", 
        "sujet": "🔧 Maintenance programmée - EIR Project",
        "contenu": "Chers utilisateurs,\n\nUne maintenance du système EIR est programmée:\n\nDate: Dimanche 21 Janvier 2024\nHeure: 02h00 - 06h00 (GMT+1)\nDurée estimée: 4 heures\n\nServices affectés:\n- Vérification IMEI\n- API externe TAC\n- Synchronisation bases\n\nLe portail web restera accessible en lecture seule.\n\nMerci de votre compréhension.\n\n---\nL'\''équipe EIR Project"
    }' "200" "Notification maintenance"
    
    # Notification rapport mensuel
    test_endpoint "http://localhost:8000/api/notifications/send" "POST" '{
        "user_id": "test-user-4",
        "notification_type": "email",
        "destinataire": "premium@example.com",
        "sujet": "📊 Rapport mensuel EIR - Janvier 2024", 
        "contenu": "Votre rapport d'\''activité EIR pour Janvier 2024:\n\nVOS APPAREILS:\n- Total: 12 appareils\n- Nouveaux ce mois: 3\n- IMEI actifs: 18\n\nVÉRIFICATIONS:\n- Effectuées: 45\n- Valides: 42 (93.3%)\n- Invalides: 3\n\nSÉCURITÉ:\n- Connexions: 28\n- Alertes: 0\n\nMarque populaire: Samsung (41%)\n\nVoir le rapport détaillé sur votre tableau de bord.\n\n---\nEIR Project"
    }' "200" "Rapport mensuel utilisateur"
}

# Test des fonctionnalités de gestion
test_management_features() {
    echo "⚙️ Test des fonctionnalités de gestion"
    echo "--------------------------------------"
    
    # Déclenchement manuel du traitement
    test_endpoint "http://localhost:8000/api/notifications/process-pending" "POST" '{}' "200" "Traitement manuel des notifications en attente"
    
    # Test du retry automatique
    test_endpoint "http://localhost:8000/api/notifications/retry-failed" "POST" '{}' "200" "Retry des notifications échouées"
    
    # Mise à jour de la configuration
    test_endpoint "http://localhost:8000/api/notifications/config" "PUT" '{
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "use_tls": true,
            "test_mode": true
        },
        "sms": {
            "provider": "console",
            "test_mode": true
        },
        "scheduler": {
            "enabled": true,
            "interval_minutes": 2
        }
    }' "200" "Mise à jour configuration (mode test)"
}

# Test de charge (plusieurs notifications)
test_load() {
    echo "🚀 Test de charge - Notifications multiples"
    echo "-------------------------------------------"
    
    for i in {1..5}; do
        echo "📧 Envoi notification $i/5..."
        test_endpoint "http://localhost:8000/api/notifications/send" "POST" "{
            \"user_id\": \"load-test-$i\",
            \"notification_type\": \"email\",
            \"destinataire\": \"loadtest$i@example.com\",
            \"sujet\": \"Test charge #$i - Vérification IMEI\",
            \"contenu\": \"Ceci est un test de charge notification #$i\\n\\nIMEI testé: 12345678901234$i\\nRésultat: VALIDE\\n\\nTest automatisé EIR Project\"
        }" "200" "Notification charge #$i" >/dev/null
    done
    
    echo "✅ 5 notifications envoyées"
    
    # Vérifier le traitement
    sleep 2
    echo "📊 Vérification du traitement..."
    test_endpoint "http://localhost:8000/api/notifications/stats" "GET" "" "200" "Statistiques après test de charge"
}

# Test des scénarios d'erreur
test_error_scenarios() {
    echo "🔥 Test des scénarios d'erreur"
    echo "------------------------------"
    
    # Notification sans destinataire
    test_endpoint "http://localhost:8000/api/notifications/send" "POST" '{
        "user_id": "error-test-1",
        "notification_type": "email",
        "destinataire": "",
        "sujet": "Test erreur",
        "contenu": "Test"
    }' "422" "Validation - destinataire vide"
    
    # Type de notification invalide
    test_endpoint "http://localhost:8000/api/notifications/send" "POST" '{
        "user_id": "error-test-2",
        "notification_type": "carrier_pigeon",
        "destinataire": "test@example.com",
        "sujet": "Test",
        "contenu": "Test"
    }' "422" "Validation - type invalide"
    
    # Email invalide
    test_endpoint "http://localhost:8000/api/notifications/send" "POST" '{
        "user_id": "error-test-3", 
        "notification_type": "email",
        "destinataire": "email-invalide",
        "sujet": "Test",
        "contenu": "Test"
    }' "422" "Validation - email invalide"
}

# Affichage des logs récents
show_recent_logs() {
    echo "📜 Logs récents du système"
    echo "-------------------------"
    
    if [ -f "$BACKEND_DIR/logs/notifications.log" ]; then
        echo "🔍 10 dernières entrées du log des notifications:"
        tail -n 10 "$BACKEND_DIR/logs/notifications.log" | while read line; do
            echo "   $line"
        done
    else
        echo "ℹ️ Aucun fichier de log trouvé"
    fi
    
    echo ""
}

# Résumé final
show_summary() {
    echo "📋 Résumé du test"
    echo "=================="
    
    # Statistiques finales
    echo "📊 Statistiques finales:"
    curl -s "http://localhost:8000/api/notifications/stats" | jq '.' 2>/dev/null || echo "Impossible de récupérer les statistiques"
    
    echo ""
    echo "✅ Tests terminés!"
    echo ""
    echo "🔗 Liens utiles:"
    echo "   - Swagger UI: http://localhost:8000/docs"
    echo "   - ReDoc: http://localhost:8000/redoc"
    echo "   - Logs: tail -f $BACKEND_DIR/logs/notifications.log"
    echo ""
    echo "📧 Configuration email recommandée pour la production:"
    echo "   - SMTP_SERVER=smtp.gmail.com"
    echo "   - SMTP_PORT=587"
    echo "   - EMAIL_USER=votre-email@gmail.com"
    echo "   - EMAIL_PASSWORD=votre-mot-de-passe-app"
    echo ""
    echo "📱 Pour activer les SMS en production:"
    echo "   - Configurez un provider (Twilio, AWS SNS, etc.)"
    echo "   - Mettez à jour notifications.yml"
    echo "   - Définissez les variables d'environnement appropriées"
}

# Fonction principale
main() {
    echo "🚀 Démarrage des tests EIR Notifications"
    echo "========================================"
    echo ""
    
    # Vérifications préliminaires
    check_backend
    
    echo "📝 Ordre des tests:"
    echo "   1. Endpoints de base"
    echo "   2. Notifications réalistes EIR"
    echo "   3. Fonctionnalités de gestion"
    echo "   4. Test de charge"
    echo "   5. Scénarios d'erreur"
    echo ""
    
    read -p "Appuyez sur Entrée pour continuer..."
    echo ""
    
    # Exécution des tests
    test_basic_endpoints
    test_realistic_notifications
    test_management_features
    test_load
    test_error_scenarios
    
    # Logs et résumé
    show_recent_logs
    show_summary
}

# Aide
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Test des notifications EIR avec scénarios réels"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h     Afficher cette aide"
    echo "  --basic        Tester uniquement les endpoints de base"
    echo "  --realistic    Tester uniquement les notifications réalistes"
    echo "  --load         Tester uniquement la charge"
    echo "  --errors       Tester uniquement les erreurs"
    echo ""
    echo "Exemples:"
    echo "  $0                    # Test complet"
    echo "  $0 --basic           # Test des endpoints de base uniquement"
    echo "  $0 --realistic       # Test des notifications EIR uniquement"
    echo ""
    exit 0
fi

# Gestion des arguments
case "$1" in
    --basic)
        check_backend
        test_basic_endpoints
        ;;
    --realistic)
        check_backend
        test_realistic_notifications
        ;;
    --load)
        check_backend
        test_load
        ;;
    --errors)
        check_backend
        test_error_scenarios
        ;;
    *)
        main
        ;;
esac
