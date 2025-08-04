#!/bin/bash
# Script pour tester l'activation/désactivation des protocoles

echo "🔧 Script de Test des Protocoles"
echo "================================"

# Fonction pour afficher le statut actuel
show_status() {
    echo "📊 Statut actuel des protocoles :"
    curl -s "http://localhost:8000/protocols/status" | python3 -c "
import sys, json
data = json.load(sys.stdin)
protocols = data.get('protocols', {})
for proto, status in protocols.items():
    icon = '✅' if status else '❌'
    print(f'  {icon} {proto.upper()}: {'Activé' if status else 'Désactivé'}')
print(f\"Protocoles actifs: {data.get('active_protocols', 0)}/{data.get('total_protocols', 0)}\")
"
    echo ""
}

# Fonction pour tester un protocole
test_protocol() {
    local protocol=$1
    echo "🧪 Test du protocole $protocol :"
    
    response=$(curl -s -w "%{http_code}" -X POST "http://localhost:8000/verify_imei?protocol=$protocol" \
        -H "Content-Type: application/json" \
        -d '{"imei": "123456789012345"}')
    
    http_code="${response: -3}"
    body="${response%???}"
    
    if [ "$http_code" == "200" ]; then
        echo "  ✅ $protocol fonctionne"
    elif [ "$http_code" == "400" ]; then
        echo "  ❌ $protocol désactivé dans la configuration"
    else
        echo "  ⚠️  $protocol erreur (code: $http_code)"
    fi
}

# Afficher le statut
show_status

# Tester chaque protocole
echo "🧪 Tests des protocoles :"
test_protocol "rest"
test_protocol "ss7" 
test_protocol "diameter"

echo ""
echo "💡 Pour modifier la configuration :"
echo "   Éditez : config/protocols.yml"
echo "   Les changements sont automatiques !"
