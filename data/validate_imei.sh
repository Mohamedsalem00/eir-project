#!/bin/bash

# =================================
# Script de validation IMEI
# =================================

# Fonction pour vérifier la validité IMEI avec l'algorithme Luhn
validate_imei_luhn() {
    local imei="$1"
    
    # Vérifier la longueur IMEI (doit être 15 chiffres)
    if [[ ${#imei} -ne 15 ]]; then
        echo "❌ Longueur IMEI incorrecte: ${#imei} (doit être 15)"
        return 1
    fi
    
    # Vérifier que tous les caractères sont des chiffres
    if [[ ! "$imei" =~ ^[0-9]+$ ]]; then
        echo "❌ IMEI contient des caractères non numériques"
        return 1
    fi
    
    # Appliquer l'algorithme Luhn
    local sum=0
    local len=${#imei}
    
    # Commencer de la droite, chaque chiffre en position paire (de la droite) multiplié par 2
    for ((i=0; i<$len; i++)); do
        local digit=${imei:$((len-1-i)):1}
        
        # Si la position est paire de la droite (commençant à 0: 0, 2, 4...)
        if (( (i % 2) == 1 )); then
            ((digit *= 2))
            if ((digit > 9)); then
                ((digit = digit - 9))
            fi
        fi
        ((sum += digit))
    done
    
    if (( sum % 10 == 0 )); then
        echo "✅ IMEI valide (Luhn valid)"
        return 0
    else
        echo "❌ IMEI invalide (Luhn invalid) - Checksum: $((sum % 10))"
        return 1
    fi
}

# Fonction pour analyser l'IMEI
analyze_imei() {
    local imei="$1"
    echo "🔍 Analyse IMEI: $imei"
    echo "   📱 TAC: ${imei:0:8}"
    echo "   🔢 Numéro de série: ${imei:8:6}"
    echo "   ✔️  Chiffre de contrôle: ${imei:14:1}"
}

# Fonction pour tester le fichier IMEI
test_imei_file() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo "❌ Fichier non trouvé: $file"
        return 1
    fi
    
    echo "📂 Test du fichier: $file"
    echo "=================================="
    
    local total=0
    local valid=0
    local invalid=0
    
    # Ignorer l'en-tête et lire les IMEI
    tail -n +2 "$file" | while IFS=',' read -r imei rest; do
        ((total++))
        echo ""
        echo "📱 IMEI #$total: $imei"
        analyze_imei "$imei"
        
        if validate_imei_luhn "$imei"; then
            ((valid++))
        else
            ((invalid++))
        fi
        
        # Arrêter après 10 échantillons pour test rapide
        if (( total >= 10 )); then
            echo ""
            echo "🛑 10 échantillons testés (pour test rapide)"
            break
        fi
    done
    
    echo ""
    echo "📊 Résultats du test:"
    echo "   📱 Total testé: $total"
    echo "   ✅ Valide: $valid"
    echo "   ❌ Invalide: $invalid"
}

# Fonction principale
main() {
    echo "🔧 Vérificateur de validité IMEI"
    echo "================================="
    
    # Si un paramètre est passé, le tester comme IMEI unique
    if [[ $# -eq 1 ]]; then
        if [[ -f "$1" ]]; then
            test_imei_file "$1"
        else
            echo "🔍 Test IMEI unique"
            analyze_imei "$1"
            validate_imei_luhn "$1"
        fi
    else
        # Tester le fichier par défaut
        if [[ -f "imei_blacklist.csv" ]]; then
            test_imei_file "imei_blacklist.csv"
        else
            echo "❌ Fichier imei_blacklist.csv non trouvé"
            echo "💡 Utilisation: $0 <imei> ou $0 <file.csv>"
            echo "💡 Exemples:"
            echo "   $0 123456789012345"
            echo "   $0 imei_blacklist.csv"
        fi
    fi
}

# Exécuter la fonction principale
main "$@"
