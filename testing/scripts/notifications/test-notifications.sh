#!/bin/bash

# Script de test pour le système de notifications EIR Project
# Teste les services email, SMS et le dispatcher

echo "========================================"
echo "Test du système de notifications EIR Project"
echo "========================================"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_BASE_URL="http://localhost:8000"
ADMIN_TOKEN=""

# Fonction d'aide
print_step() {
    echo -e "${BLUE}[ÉTAPE]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCÈS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[ATTENTION]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERREUR]${NC} $1"
}

# Fonction pour obtenir un token admin
get_admin_token() {
    print_step "Obtention du token administrateur..."
    
    # Tentative de connexion avec des identifiants par défaut
    local response=$(curl -s -X POST "${API_BASE_URL}/authentification/connexion" \
        -H "Content-Type: application/json" \
        -d '{"email": "eirrproject@gmail.com", "mot_de_passe": "admin123"}')
    
    if echo "$response" | grep -q "access_token"; then
        ADMIN_TOKEN=$(echo "$response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
        print_success "Token admin obtenu"
        return 0
    else
        print_warning "Impossible d'obtenir le token admin. Certains tests seront ignorés."
        return 1
    fi
}

# Test de santé de l'API
test_api_health() {
    print_step "Test de santé de l'API..."
    
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" "${API_BASE_URL}/")
    local body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    local status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$status" -eq 200 ]; then
        print_success "API accessible"
        return 0
    else
        print_error "API non accessible (Status: $status)"
        return 1
    fi
}

# Test des connexions des services
test_service_connections() {
    print_step "Test des connexions des services de notification..."
    
    if [ -z "$ADMIN_TOKEN" ]; then
        print_warning "Token admin non disponible, test ignoré"
        return 1
    fi
    
    local response=$(curl -s -X GET "${API_BASE_URL}/admin/notifications/test-connexions" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    
    if echo "$response" | grep -q '"email"'; then
        local email_success=$(echo "$response" | grep -o '"email":{"success":[^,]*' | cut -d: -f3)
        local sms_success=$(echo "$response" | grep -o '"sms":{"success":[^,]*' | cut -d: -f3)
        
        if [ "$email_success" = "true" ]; then
            print_success "Service email opérationnel"
        else
            print_warning "Service email non opérationnel"
        fi
        
        if [ "$sms_success" = "true" ]; then
            print_success "Service SMS opérationnel"
        else
            print_warning "Service SMS non opérationnel (normal en mode console)"
        fi
        
        return 0
    else
        print_error "Impossible de tester les connexions"
        return 1
    fi
}

# Test de création de notification
test_create_notification() {
    print_step "Test de création de notification..."
    
    if [ -z "$ADMIN_TOKEN" ]; then
        print_warning "Token admin non disponible, test ignoré"
        return 1
    fi
    
    local notification_data='{
        "type": "email",
        "destinataire": "test@example.com",
        "sujet": "Test notification EIR Project",
        "contenu": "Ceci est un test du système de notifications.",
        "envoyer_immediatement": false
    }'
    
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "${API_BASE_URL}/notifications/" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$notification_data")
    
    local body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    local status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$status" -eq 201 ]; then
        local notification_id=$(echo "$body" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
        print_success "Notification créée (ID: $notification_id)"
        echo "$notification_id" > /tmp/test_notification_id
        return 0
    else
        print_error "Échec de création de notification (Status: $status)"
        echo "Réponse: $body"
        return 1
    fi
}

# Test d'envoi immédiat
test_immediate_send() {
    print_step "Test d'envoi immédiat..."
    
    if [ -z "$ADMIN_TOKEN" ]; then
        print_warning "Token admin non disponible, test ignoré"
        return 1
    fi
    
    local notification_data='{
        "type": "sms",
        "destinataire": "+33123456789",
        "contenu": "Test SMS EIR Project - Envoi immédiat"
    }'
    
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "${API_BASE_URL}/notifications/envoyer-immediatement" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d "$notification_data")
    
    local body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    local status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$status" -eq 200 ]; then
        local success=$(echo "$body" | grep -o '"success":[^,]*' | cut -d: -f2)
        if [ "$success" = "true" ]; then
            print_success "Envoi immédiat réussi"
        else
            print_warning "Envoi immédiat échoué (normal pour SMS en mode console)"
        fi
        return 0
    else
        print_error "Échec du test d'envoi immédiat (Status: $status)"
        return 1
    fi
}

# Test du planificateur
test_scheduler() {
    print_step "Test du statut du planificateur..."
    
    if [ -z "$ADMIN_TOKEN" ]; then
        print_warning "Token admin non disponible, test ignoré"
        return 1
    fi
    
    local response=$(curl -s "${API_BASE_URL}/admin/notifications/scheduler/status" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    
    if echo "$response" | grep -q '"scheduler_running"'; then
        local scheduler_running=$(echo "$response" | grep -o '"scheduler_running":[^,]*' | cut -d: -f2)
        if [ "$scheduler_running" = "true" ]; then
            print_success "Planificateur opérationnel"
        else
            print_warning "Planificateur arrêté"
        fi
        return 0
    else
        print_error "Impossible de vérifier le statut du planificateur"
        return 1
    fi
}

# Test de déclenchement manuel
test_manual_trigger() {
    print_step "Test de déclenchement manuel du traitement..."
    
    if [ -z "$ADMIN_TOKEN" ]; then
        print_warning "Token admin non disponible, test ignoré"
        return 1
    fi
    
    local response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "${API_BASE_URL}/admin/notifications/scheduler/trigger/process_notifications" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    
    local body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    local status=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$status" -eq 200 ]; then
        print_success "Déclenchement manuel réussi"
        return 0
    else
        print_error "Échec du déclenchement manuel (Status: $status)"
        return 1
    fi
}

# Test des statistiques
test_statistics() {
    print_step "Test des statistiques..."
    
    if [ -z "$ADMIN_TOKEN" ]; then
        print_warning "Token admin non disponible, test ignoré"
        return 1
    fi
    
    local response=$(curl -s "${API_BASE_URL}/notifications/statistiques/globales" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    
    if echo "$response" | grep -q '"total_notifications"'; then
        local total=$(echo "$response" | grep -o '"total_notifications":[^,]*' | cut -d: -f2)
        print_success "Statistiques récupérées (Total: $total notifications)"
        return 0
    else
        print_error "Impossible de récupérer les statistiques"
        return 1
    fi
}

# Test de la configuration
test_configuration() {
    print_step "Test de la configuration..."
    
    if [ -z "$ADMIN_TOKEN" ]; then
        print_warning "Token admin non disponible, test ignoré"
        return 1
    fi
    
    local response=$(curl -s "${API_BASE_URL}/admin/notifications/configuration" \
        -H "Authorization: Bearer $ADMIN_TOKEN")
    
    if echo "$response" | grep -q '"email_service"'; then
        print_success "Configuration récupérée"
        return 0
    else
        print_error "Impossible de récupérer la configuration"
        return 1
    fi
}

# Test de nettoyage
cleanup_test_data() {
    print_step "Nettoyage des données de test..."
    
    if [ -f "/tmp/test_notification_id" ] && [ -n "$ADMIN_TOKEN" ]; then
        local notification_id=$(cat /tmp/test_notification_id)
        curl -s -X DELETE "${API_BASE_URL}/notifications/$notification_id" \
            -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
        rm -f /tmp/test_notification_id
        print_success "Données de test nettoyées"
    fi
}

# Fonction principale
main() {
    echo "Démarrage des tests..."
    echo ""
    
    # Vérifier si l'API est accessible
    if ! test_api_health; then
        print_error "L'API n'est pas accessible. Assurez-vous qu'elle fonctionne sur $API_BASE_URL"
        exit 1
    fi
    
    echo ""
    
    # Obtenir un token admin
    get_admin_token
    echo ""
    
    # Exécuter les tests
    test_service_connections
    echo ""
    
    test_create_notification
    echo ""
    
    test_immediate_send
    echo ""
    
    test_scheduler
    echo ""
    
    test_manual_trigger
    echo ""
    
    test_statistics
    echo ""
    
    test_configuration
    echo ""
    
    # Nettoyage
    cleanup_test_data
    
    echo "========================================"
    echo "Tests terminés!"
    echo "========================================"
    echo ""
    echo "Instructions pour tester manuellement:"
    echo "1. Configurez vos paramètres email dans config/notifications.yml"
    echo "2. Définissez les variables d'environnement dans .env"
    echo "3. Redémarrez l'application"
    echo "4. Créez une notification via l'API"
    echo "5. Vérifiez les logs dans logs/notifications.log"
    echo ""
    echo "Documentation API disponible sur: ${API_BASE_URL}/docs"
}

# Exécution du script
main "$@"
