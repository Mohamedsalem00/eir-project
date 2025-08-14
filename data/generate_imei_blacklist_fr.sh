#!/bin/bash

# =================================
# Script de génération IMEI Blacklist
# =================================

# Fichier TAC DB
INPUT_FILE="tacdb.csv"
# Fichier de sortie
OUTPUT_FILE="imei_blacklist.csv"

# Pourcentage d'appareils blacklistés (0.0 - 1.0)
BLACKLIST_RATIO=0.15

# Nombre d'IMEI par TAC (avec fichier volumineux, réduire le nombre)
IMEIS_PER_TAC=2

# Taille de lot pour afficher le progrès
BATCH_SIZE=1000

echo "🔧 Début de génération IMEI Blacklist..."
echo "📁 Fichier d'entrée: $INPUT_FILE"
echo "📁 Fichier de sortie: $OUTPUT_FILE"
echo "📊 Pourcentage blacklist: $(echo "$BLACKLIST_RATIO * 100" | bc)%"
echo "🔢 IMEI par TAC: $IMEIS_PER_TAC"

# Calcul du nombre attendu
total_lines=$(wc -l < "$INPUT_FILE")
expected_imeis=$((($total_lines - 1) * IMEIS_PER_TAC))
echo "📊 Attendu génération ~$expected_imeis IMEI de $((total_lines - 1)) TAC"
echo "💾 Taille fichier attendue: ~$(echo "scale=1; $expected_imeis * 80 / 1024 / 1024" | bc) MB"
echo ""

# Fonction pour calculer le chiffre de vérification Luhn
luhn_check_digit() {
    local imei_without_check="$1"
    local sum=0
    local len=${#imei_without_check}
    
    # Commencer de la droite, chaque chiffre en position paire (de la droite) multiplié par 2
    for ((i=0; i<$len; i++)); do
        local digit=${imei_without_check:$((len-1-i)):1}
        
        # Si la position est paire de la droite (1, 3, 5...)
        if (( (i % 2) == 1 )); then
            ((digit *= 2))
            if ((digit > 9)); then
                ((digit = digit - 9))
            fi
        fi
        ((sum += digit))
    done
    
    # Calcul du chiffre de vérification
    local check_digit=$(( (10 - (sum % 10)) % 10 ))
    echo "$check_digit"
}

# Fonction pour vérifier l'existence du fichier
check_input_file() {
    if [[ ! -f "$INPUT_FILE" ]]; then
        echo "❌ Erreur: Fichier $INPUT_FILE non trouvé"
        echo "💡 Assurez-vous que le fichier tacdb.csv existe dans le même dossier"
        exit 1
    fi
    echo "✅ Fichier d'entrée trouvé"
}

# Fonction pour générer un IMEI valide
generate_valid_imei() {
    local tac="$1"
    local serial_number=$(printf "%06d" $((RANDOM % 1000000)))
    local imei_without_check="${tac}${serial_number}"
    local check_digit=$(luhn_check_digit "$imei_without_check")
    echo "${imei_without_check}${check_digit}"
}

# Vérifier l'existence du fichier
check_input_file

# En-tête du fichier de sortie
echo "imei,tac,manufacturer,model,status,generated_date" > "$OUTPUT_FILE"

echo "📝 Début du traitement des données..."

# Compteur pour les statistiques
total_imeis=0
blacklisted_count=0
allowed_count=0

# Lire TAC DB et générer plusieurs IMEI pour chaque TAC
while IFS=',' read -r tac manufacturer model rest; do
    # Ignorer l'en-tête
    if [[ "$tac" == "tac" ]] || [[ "$tac" == "TAC" ]]; then
        continue
    fi
    
    # Nettoyer les données
    tac=$(echo "$tac" | tr -d '[:space:]' | tr -d '"')
    manufacturer=$(echo "$manufacturer" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"')
    model=$(echo "$model" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"')
    
    # Vérifier la validité du TAC (doit être 8 chiffres)
    if [[ ! "$tac" =~ ^[0-9]{8}$ ]]; then
        echo "⚠️  Ignorer TAC invalide: $tac"
        continue
    fi
    
    # Générer plusieurs IMEI pour chaque TAC
    for ((i=1; i<=IMEIS_PER_TAC; i++)); do
        # Générer IMEI valide
        imei=$(generate_valid_imei "$tac")
        
        # Déterminer le statut (blacklist ou autorisé)
        if (( $(echo "$RANDOM/32767 < $BLACKLIST_RATIO" | bc -l) )); then
            status="blacklisted"
            ((blacklisted_count++))
        else
            status="allowed"
            ((allowed_count++))
        fi
        
        # Date actuelle
        current_date=$(date '+%Y-%m-%d %H:%M:%S')
        
        # Écrire la ligne
        echo "$imei,$tac,$manufacturer,$model,$status,$current_date" >> "$OUTPUT_FILE"
        ((total_imeis++))
    done
    
    # Afficher le progrès tous les BATCH_SIZE TACs
    if (( total_imeis % BATCH_SIZE == 0 )); then
        echo "📊 $total_imeis IMEI générés jusqu'à présent..."
    fi
    
done < "$INPUT_FILE"

# Afficher les statistiques finales
echo ""
echo "✅ Génération de données terminée!"
echo "📊 Statistiques finales:"
echo "   📱 Total IMEI: $total_imeis"
echo "   🚫 Blacklistés: $blacklisted_count ($(echo "scale=1; $blacklisted_count*100/$total_imeis" | bc)%)"
echo "   ✅ Autorisés: $allowed_count ($(echo "scale=1; $allowed_count*100/$total_imeis" | bc)%)"
echo "   📁 Fichier de sortie: $OUTPUT_FILE"
echo ""
echo "🎉 Données sauvegardées avec succès!"
