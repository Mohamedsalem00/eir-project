#!/bin/bash
# Tableau de bord des tests API EIR

echo "🎯 TABLEAU DE BORD DES TESTS API EIR"
echo "===================================="
echo ""

# Vérifier le statut de l'API
echo "🔍 STATUT DE L'API:"
if curl -s -f http://localhost:8000/verification-etat > /dev/null; then
    echo "✅ API accessible sur http://localhost:8000"
    
    # Obtenir les informations de santé
    health_data=$(curl -s http://localhost:8000/verification-etat)
    db_status=$(echo "$health_data" | jq -r '.base_donnees.statut' 2>/dev/null || echo "unknown")
    uptime=$(echo "$health_data" | jq -r '.duree_fonctionnement' 2>/dev/null || echo "unknown")
    
    echo "  📊 Base de données: $db_status"
    echo "  ⏱️  Temps de fonctionnement: $uptime"
else
    echo "❌ API non accessible"
    echo ""
    echo "💡 Pour démarrer l'API:"
    echo "   cd /home/mohamed/Documents/projects/eir-project"
    echo "   sudo docker-compose up -d"
    exit 1
fi

echo ""

# Afficher les derniers résultats de test s'ils existent
echo "📊 DERNIERS RÉSULTATS DE TEST:"
cd "$(dirname "$0")"

if ls api_test_report_*.json 1> /dev/null 2>&1; then
    latest_report=$(ls -t api_test_report_*.json | head -n1)
    
    if [ -f "$latest_report" ]; then
        echo "  📄 Dernier rapport: $latest_report"
        
        # Extraire les statistiques principales
        total=$(jq -r '.summary.total_tests' "$latest_report" 2>/dev/null || echo "0")
        passed=$(jq -r '.summary.passed' "$latest_report" 2>/dev/null || echo "0")
        failed=$(jq -r '.summary.failed' "$latest_report" 2>/dev/null || echo "0")
        warnings=$(jq -r '.summary.warnings' "$latest_report" 2>/dev/null || echo "0")
        
        # Calculer le taux de réussite
        if [ "$total" -gt 0 ]; then
            success_rate=$(echo "scale=1; $passed * 100 / $total" | bc -l 2>/dev/null || echo "0")
        else
            success_rate="0"
        fi
        
        echo "  📈 Tests totaux: $total"
        echo "  ✅ Réussis: $passed"
        echo "  ❌ Échoués: $failed"
        echo "  ⚠️  Avertissements: $warnings"
        echo "  🎯 Taux de réussite: $success_rate%"
        
        # Timestamp du dernier test
        generated_at=$(jq -r '.metadata.generated_at' "$latest_report" 2>/dev/null || echo "unknown")
        echo "  🕐 Dernier test: $generated_at"
    fi
else
    echo "  ⚠️  Aucun rapport de test trouvé"
fi

echo ""

# Menu d'actions
echo "🛠️  ACTIONS DISPONIBLES:"
echo "  1. Exécuter un test rapide"
echo "  2. Exécuter tous les tests"
echo "  3. Analyser les derniers résultats"
echo "  4. Voir les logs de l'API"
echo "  5. Redémarrer l'API"
echo "  0. Quitter"
echo ""

read -p "Choisissez une action (0-5): " choice

case $choice in
    1)
        echo "🚀 Exécution du test rapide..."
        ./quick_api_test.sh
        ;;
    2)
        echo "🧪 Exécution de tous les tests..."
        ./run_api_tests.sh
        ;;
    3)
        echo "📊 Analyse des résultats..."
        python3 analyze_test_results.py
        ;;
    4)
        echo "📝 Logs de l'API (dernières 50 lignes):"
        echo "========================================"
        sudo docker logs eir_web --tail 50
        ;;
    5)
        echo "🔄 Redémarrage de l'API..."
        cd /home/mohamed/Documents/projects/eir-project
        sudo docker-compose restart web
        echo "✅ API redémarrée"
        ;;
    0)
        echo "👋 Au revoir !"
        ;;
    *)
        echo "⚠️  Option invalide"
        ;;
esac
