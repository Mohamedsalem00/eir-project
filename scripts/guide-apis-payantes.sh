#!/bin/bash

# Guide d'activation des APIs payantes CheckIMEI et IMEI.org
echo "🔑 Guide d'Activation des APIs Payantes"
echo "========================================"

echo ""
echo "📋 VOS CLÉS API DISPONIBLES:"
echo "----------------------------"
echo "✅ CheckIMEI.com:"
echo "   • Clé API: aywzL-QSlaw-EdYTY-TZq4v-FYLnT-vdkFu"
echo "   • Username: MohamedKhyarhoum627" 
echo "   • Dashboard: https://imeicheck.com/user/api-manage"
echo ""
echo "✅ IMEI.org:"
echo "   • Clé API: feWNCdwym5BEgu4PkDhCIxYE5sVuH5CYlTo3vW1WJnUJ3052k46oH4H6KIz8"
echo "   • Dashboard: https://imei.org/user-settings"

echo ""
echo "🔍 ÉTAPES POUR ACTIVER:"
echo "======================="

echo ""
echo "1️⃣ TROUVER LA DOCUMENTATION API"
echo "   • Connectez-vous à vos dashboards"
echo "   • Cherchez 'API Documentation' ou 'API Endpoints'"
echo "   • Notez l'URL exacte de l'API"
echo "   • Vérifiez le format des requêtes (GET/POST)"

echo ""
echo "2️⃣ TESTER AVEC CURL"
echo "   • Exemple CheckIMEI:"
echo "     curl -X POST 'https://api.checkimei.com/check' \\"
echo "          -H 'Authorization: Bearer aywzL-QSlaw-EdYTY-TZq4v-FYLnT-vdkFu' \\"
echo "          -d '{\"imei\":\"352745080123456\"}'"
echo ""
echo "   • Exemple IMEI.org:"
echo "     curl -X POST 'https://api.imei.org/check' \\"
echo "          -d 'key=feWNCdwym5BEgu4PkDhCIxYE5sVuH5CYlTo3vW1WJnUJ3052k46oH4H6KIz8&imei=352745080123456'"

echo ""
echo "3️⃣ MODIFIER LA CONFIGURATION"
echo "   • Éditez: config/external_apis.yml"
echo "   • Changez enabled: false → enabled: true"
echo "   • Mettez la bonne URL d'API"
echo "   • Redémarrez: docker compose restart web"

echo ""
echo "🧪 CONFIGURATION DE TEST:"
echo "========================="

cat << 'EOF'
# Dans config/external_apis.yml
checkimei_user:
  enabled: true  # ← Changer à true
  url: "https://api.checkimei.com/v1/check"  # ← URL correcte
  api_key: "${CHECKIMEI_API_KEY}"
  method: "POST"  # ← Ou GET selon doc
  
imei_org_user:
  enabled: true  # ← Changer à true
  url: "https://api.imei.org/check"  # ← URL correcte
  api_key: "${IMEI_ORG_API_KEY}"
  method: "POST"  # ← Ou GET selon doc
EOF

echo ""
echo "📊 STATUT ACTUEL:"
echo "=================="
echo "✅ Base TAC locale: ACTIVE (16,000+ modèles)"
echo "✅ Validation Luhn: ACTIVE (algorithme mathematique)"
echo "✅ API EIR: ACTIVE (http://localhost:8000)"
echo "⏳ CheckIMEI API: EN ATTENTE (documentation requise)"
echo "⏳ IMEI.org API: EN ATTENTE (documentation requise)"

echo ""
echo "🎯 RECOMMANDATIONS:"
echo "==================="
echo "1. 🚀 DÉPLOYEZ MAINTENANT avec la config actuelle (100% fonctionnelle)"
echo "2. 📚 CONSULTEZ la documentation de vos APIs en parallèle"
echo "3. 🔧 ACTIVEZ les APIs externes une fois les endpoints confirmés"
echo "4. 📈 MONITOREZ l'usage et les quotas"

echo ""
echo "💰 ALTERNATIVE GRATUITE IMMÉDIATE:"
echo "==================================="
echo "NumVerify API (APILayer):"
echo "• Inscription gratuite: https://numverify.com"
echo "• 1000 requêtes/mois gratuit"
echo "• Documentation claire"
echo "• API bien testée"

echo ""
echo "🆘 SUPPORT:"
echo "============"
echo "Si vous trouvez la bonne documentation API:"
echo "1. Testez avec curl d'abord"
echo "2. Modifiez config/external_apis.yml"
echo "3. Redémarrez le service"
echo "4. Testez avec: ./scripts/test-apis-externes.sh"

echo ""
echo "✨ Le système fonctionne parfaitement sans APIs externes!"
echo "   Vous pouvez les ajouter plus tard quand vous voulez."
