#!/bin/bash

# =================================
# Script d'estimation taille données générées
# =================================

INPUT_FILE="tacdb.csv"
IMEIS_PER_TAC=2

echo "🔍 Analyse du fichier TAC..."

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "❌ Fichier $INPUT_FILE non trouvé"
    exit 1
fi

# Calculer le nombre de TACs
total_lines=$(wc -l < "$INPUT_FILE")
total_tacs=$((total_lines - 1))  # Exclure l'en-tête

# Estimer les données générées
estimated_imeis=$((total_tacs * IMEIS_PER_TAC))
estimated_file_size_mb=$(echo "scale=2; $estimated_imeis * 60 / 1024 / 1024" | bc)
estimated_time_minutes=$(echo "scale=1; $total_tacs / 1000" | bc)

echo ""
echo "📊 Analyse des données:"
echo "   📁 Fichier d'entrée: $INPUT_FILE"
echo "   📱 Nombre de TACs: $total_tacs"
echo "   🔢 IMEI par TAC: $IMEIS_PER_TAC"
echo ""
echo "📈 Estimations:"
echo "   📱 Total IMEI attendu: $estimated_imeis"
echo "   💾 Taille fichier attendue: ~${estimated_file_size_mb}MB"
echo "   ⏱️  Temps estimé: ~${estimated_time_minutes} minute(s)"
echo ""

# Afficher un échantillon des données
echo "📋 Échantillon des données TAC:"
echo "=============================="
head -6 "$INPUT_FILE"
echo "..."

echo ""
echo "❓ Voulez-vous continuer? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "🚀 Lancement du script de génération IMEI..."
    ./generate_imei_blacklist.sh
else
    echo "🛑 Annulé"
fi
