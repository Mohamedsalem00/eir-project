#!/bin/bash

# =================================
# Script de génération données TAC d'exemple
# =================================

OUTPUT_FILE="tacdb_sample.csv"

# Vérifier l'existence du fichier tacdb.csv original
if [[ -f "tacdb.csv" ]]; then
    echo "⚠️  Attention: Fichier tacdb.csv existant trouvé"
    echo "🔒 Ne sera pas écrasé pour protéger les données originales"
    echo "📁 Création d'un nouveau fichier: $OUTPUT_FILE"
    echo ""
fi

echo "🏭 Génération de données TAC d'exemple..."

# En-tête du fichier
echo "tac,manufacturer,model" > "$OUTPUT_FILE"

# Données TAC réelles (simplifiées)
declare -A manufacturers
manufacturers=(
    ["35209301"]="Apple,iPhone 12"
    ["35209302"]="Apple,iPhone 12 Pro"
    ["35209303"]="Apple,iPhone 13"
    ["35209304"]="Apple,iPhone 13 Pro"
    ["35209305"]="Apple,iPhone 14"
    ["35100601"]="Samsung,Galaxy S21"
    ["35100602"]="Samsung,Galaxy S22"
    ["35100603"]="Samsung,Galaxy S23"
    ["35100604"]="Samsung,Galaxy Note 20"
    ["35100605"]="Samsung,Galaxy A52"
    ["86838103"]="Huawei,P30 Pro"
    ["86838104"]="Huawei,P40 Pro"
    ["86838105"]="Huawei,Mate 40"
    ["86838106"]="Huawei,Nova 7"
    ["86838107"]="Huawei,Y6 Prime"
    ["35503108"]="Xiaomi,Mi 11"
    ["35503109"]="Xiaomi,Redmi Note 10"
    ["35503110"]="Xiaomi,POCO X3"
    ["35503111"]="Xiaomi,Mi 12"
    ["35503112"]="Xiaomi,Redmi 10"
    ["49015420"]="OnePlus,9 Pro"
    ["49015421"]="OnePlus,Nord"
    ["49015422"]="OnePlus,8T"
    ["35785930"]="Oppo,Find X3"
    ["35785931"]="Oppo,Reno 6"
    ["35785932"]="Oppo,A74"
    ["35161001"]="Vivo,X60 Pro"
    ["35161002"]="Vivo,Y20"
    ["35161003"]="Vivo,V21"
    ["35043711"]="Nokia,8.3"
    ["35043712"]="Nokia,7.2"
    ["35043713"]="Nokia,6.2"
    ["35125801"]="Google,Pixel 5"
    ["35125802"]="Google,Pixel 6"
    ["35125803"]="Google,Pixel 6 Pro"
    ["35208880"]="Sony,Xperia 1 III"
    ["35208881"]="Sony,Xperia 5 II"
    ["35208882"]="Sony,Xperia 10 III"
    ["35891001"]="Realme,8 Pro"
    ["35891002"]="Realme,GT"
    ["35891003"]="Realme,C25"
    ["35675401"]="Motorola,Edge 20"
    ["35675402"]="Motorola,Moto G60"
    ["35675403"]="Motorola,One Fusion"
    ["35328004"]="Honor,50 Pro"
    ["35328005"]="Honor,20 Lite"
    ["35328006"]="Honor,X20"
    ["35555501"]="Tecno,Phantom X"
    ["35555502"]="Tecno,Camon 17"
    ["35555503"]="Tecno,Spark 7"
    ["35444401"]="Infinix,Zero 8"
    ["35444402"]="Infinix,Hot 10"
    ["35444403"]="Infinix,Note 8"
)

# Écriture des données
for tac in "${!manufacturers[@]}"; do
    IFS=',' read -r manufacturer model <<< "${manufacturers[$tac]}"
    echo "$tac,$manufacturer,$model" >> "$OUTPUT_FILE"
done

echo "✅ $(wc -l < "$OUTPUT_FILE") lignes générées dans le fichier $OUTPUT_FILE"
echo "📱 Le fichier contient des TACs pour ${#manufacturers[@]} appareils différents"

# Afficher un échantillon des données
echo ""
echo "📋 Échantillon des données générées:"
echo "===================================="
head -6 "$OUTPUT_FILE"
echo "..."
echo ""
echo "🚀 Vous pouvez maintenant exécuter le script generate_imei_blacklist_fr.sh"
