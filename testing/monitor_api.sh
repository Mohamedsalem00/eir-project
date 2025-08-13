#!/bin/bash

# 📊 Monitoring Continu de l'API EIR
# Surveille l'API en temps réel et alerte en cas de problème

set -e

# Configuration
API_URL="${1:-http://localhost:8000}"
CHECK_INTERVAL="${2:-30}"  # Secondes entre chaque vérification
LOG_FILE="monitoring.log"
ALERT_THRESHOLD=3  # Nombre d'échecs avant alerte

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Compteurs
TOTAL_CHECKS=0
FAILED_CHECKS=0
CONSECUTIVE_FAILURES=0
START_TIME=$(date)

# Fonction de log
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Fonction d'affichage avec couleur
print_status() {
    local color="$1"
    local message="$2"
    echo -e "${color}$message${NC}"
}

# Fonction de test de l'API
test_api() {
    local start_time=$(date +%s.%3N)
    
    # Test de base
    if response=$(curl -s -w "%{http_code}" "$API_URL/" 2>/dev/null); then
        local http_code="${response: -3}"
        local response_body="${response%???}"
        local end_time=$(date +%s.%3N)
        local response_time=$(echo "$end_time - $start_time" | bc -l)
        
        if [[ "$http_code" == "200" ]]; then
            return 0
        else
            echo "HTTP_ERROR:$http_code"
            return 1
        fi
    else
        echo "CONNECTION_ERROR"
        return 1
    fi
}

# Fonction d'alerte
send_alert() {
    local message="$1"
    print_status "$RED" "🚨 ALERTE: $message"
    log_message "ALERT" "$message"
    
    # Ici on pourrait ajouter des notifications (email, Slack, etc.)
    echo "$(date): ALERTE - $message" >> alerts.log
}

# Fonction de récupération
recovery_detected() {
    print_status "$GREEN" "✅ RÉCUPÉRATION: API de nouveau accessible"
    log_message "RECOVERY" "API récupérée après $CONSECUTIVE_FAILURES échecs"
    CONSECUTIVE_FAILURES=0
}

# Fonction d'affichage du statut
show_status() {
    clear
    echo -e "${BLUE}📊 MONITORING API EIR - $(date)${NC}"
    echo "=============================================="
    echo "🌐 URL surveillée: $API_URL"
    echo "⏱️  Intervalle: ${CHECK_INTERVAL}s"
    echo "📅 Démarré: $START_TIME"
    echo ""
    echo "📈 STATISTIQUES:"
    echo "   Total vérifications: $TOTAL_CHECKS"
    echo "   Échecs: $FAILED_CHECKS"
    if [[ $TOTAL_CHECKS -gt 0 ]]; then
        local success_rate=$(echo "scale=2; ($TOTAL_CHECKS - $FAILED_CHECKS) * 100 / $TOTAL_CHECKS" | bc -l)
        echo "   Taux de succès: ${success_rate}%"
    fi
    echo "   Échecs consécutifs: $CONSECUTIVE_FAILURES"
    echo ""
    
    if [[ $CONSECUTIVE_FAILURES -eq 0 ]]; then
        print_status "$GREEN" "🟢 STATUT: API FONCTIONNELLE"
    elif [[ $CONSECUTIVE_FAILURES -lt $ALERT_THRESHOLD ]]; then
        print_status "$YELLOW" "🟡 STATUT: PROBLÈMES INTERMITTENTS"
    else
        print_status "$RED" "🔴 STATUT: API EN PANNE"
    fi
    
    echo ""
    echo "Appuyez sur Ctrl+C pour arrêter le monitoring"
    echo "Logs: $LOG_FILE"
}

# Fonction de nettoyage à l'arrêt
cleanup() {
    echo ""
    print_status "$BLUE" "📊 RAPPORT FINAL"
    echo "=============================================="
    echo "Durée du monitoring: $(date)"
    echo "Total vérifications: $TOTAL_CHECKS"
    echo "Échecs: $FAILED_CHECKS"
    if [[ $TOTAL_CHECKS -gt 0 ]]; then
        local success_rate=$(echo "scale=2; ($TOTAL_CHECKS - $FAILED_CHECKS) * 100 / $TOTAL_CHECKS" | bc -l)
        echo "Taux de succès: ${success_rate}%"
    fi
    echo "Logs sauvegardés dans: $LOG_FILE"
    exit 0
}

# Capture Ctrl+C
trap cleanup INT

# Initialisation
echo -e "${BLUE}🚀 Démarrage du monitoring de l'API EIR${NC}"
log_message "INFO" "Monitoring démarré pour $API_URL"

# Vérification initiale
print_status "$BLUE" "🔍 Test initial de connectivité..."
if test_api > /dev/null 2>&1; then
    print_status "$GREEN" "✅ API accessible - monitoring en cours..."
else
    print_status "$YELLOW" "⚠️  API non accessible au démarrage - monitoring quand même..."
fi

# Boucle principale de monitoring
while true; do
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    # Test de l'API
    if error_info=$(test_api 2>&1); then
        # Succès
        if [[ $CONSECUTIVE_FAILURES -gt 0 ]]; then
            recovery_detected
        fi
        log_message "SUCCESS" "API accessible"
    else
        # Échec
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
        
        log_message "FAILURE" "API inaccessible: $error_info"
        
        # Alerte si seuil atteint
        if [[ $CONSECUTIVE_FAILURES -eq $ALERT_THRESHOLD ]]; then
            send_alert "API inaccessible depuis $ALERT_THRESHOLD vérifications"
        fi
    fi
    
    # Affichage du statut
    show_status
    
    # Attente avant le prochain test
    sleep "$CHECK_INTERVAL"
done
