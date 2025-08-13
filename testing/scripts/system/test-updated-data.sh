#!/bin/bash

# Script pour tester les données avec le nouveau système de notifications
# Usage: ./test-updated-data.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "🔄 Test des données mises à jour avec le nouveau système de notifications"
echo "====================================================================="

# Fonction pour exécuter SQL et afficher les résultats
run_sql() {
    local query="$1"
    local description="$2"
    
    echo "📊 $description"
    echo "Query: $query"
    
    if command -v psql &> /dev/null; then
        echo "Résultat:"
        psql -d eir_project -c "$query" 2>/dev/null || {
            echo "❌ Erreur lors de l'exécution de la requête"
            echo "   Assurez-vous que la base de données 'eir_project' existe et est accessible"
            return 1
        }
    else
        echo "❌ psql non trouvé - impossible d'exécuter la requête"
        return 1
    fi
    
    echo ""
}

# Vérifier la structure de la table notification
echo "🔍 Vérification de la structure mise à jour"
echo "==========================================="

run_sql "SELECT column_name, data_type, is_nullable, column_default 
         FROM information_schema.columns 
         WHERE table_name = 'notification' 
         ORDER BY ordinal_position;" \
        "Structure actuelle de la table notification"

# Vérifier les utilisateurs créés
run_sql "SELECT email, nom, type_utilisateur, niveau_acces, portee_donnees, est_actif 
         FROM utilisateur 
         ORDER BY type_utilisateur DESC;" \
        "Utilisateurs de test créés"

# Vérifier les notifications avec les nouveaux champs
run_sql "SELECT 
            id,
            type,
            destinataire,
            LEFT(sujet, 50) || '...' as sujet_court,
            statut,
            tentative,
            date_creation,
            date_envoi,
            CASE WHEN erreur IS NOT NULL THEN 'Oui' ELSE 'Non' END as a_erreur
         FROM notification 
         ORDER BY date_creation DESC;" \
        "Notifications créées avec les nouveaux champs"

# Vérifier les appareils et IMEI
run_sql "SELECT 
            a.marque,
            a.modele,
            i.numero_imei,
            i.statut as statut_imei,
            u.email as proprietaire
         FROM appareil a
         JOIN imei i ON i.appareil_id = a.id
         JOIN utilisateur u ON u.id = a.utilisateur_id
         ORDER BY a.marque, i.numero_imei;" \
        "Appareils et IMEI de test"

# Vérifier les données TAC
run_sql "SELECT tac, marque, modele, type_appareil, statut 
         FROM tac_database 
         ORDER BY marque;" \
        "Données TAC pour les tests"

# Statistiques générales
run_sql "SELECT 
            'Statistiques générales' as info,
            (SELECT COUNT(*) FROM utilisateur) as utilisateurs,
            (SELECT COUNT(*) FROM appareil) as appareils,
            (SELECT COUNT(*) FROM imei) as imeis,
            (SELECT COUNT(*) FROM notification) as notifications,
            (SELECT COUNT(*) FROM notification WHERE statut = 'en_attente') as notifications_en_attente,
            (SELECT COUNT(*) FROM tac_database) as entries_tac;" \
        "Résumé des données de test"

# Test de validation IMEI avec TAC
echo "🧪 Test de validation IMEI avec la base TAC"
echo "=========================================="

run_sql "SELECT valider_imei_avec_tac('353260051234567');" \
        "Validation IMEI Samsung Galaxy S23"

run_sql "SELECT valider_imei_avec_tac('356920051234567');" \
        "Validation IMEI Apple iPhone 14"

run_sql "SELECT valider_imei_avec_tac('990000001234567');" \
        "Validation IMEI de test (devrait être détecté comme test)"

# Test des notifications spécifiques EIR
echo "📧 Exemples de notifications EIR créées"
echo "======================================="

run_sql "SELECT 
            destinataire,
            LEFT(sujet, 60) as sujet,
            statut,
            date_creation
         FROM notification 
         WHERE type = 'email' 
         ORDER BY date_creation;" \
        "Notifications email créées"

run_sql "SELECT 
            destinataire,
            LEFT(contenu, 100) || '...' as contenu_extrait,
            statut,
            date_creation
         FROM notification 
         WHERE type = 'sms';" \
        "Notifications SMS créées"

echo "✅ Test des données terminé"
echo ""
echo "📝 Prochaines étapes:"
echo "  1. Démarrez le backend: cd $BACKEND_DIR && uvicorn app.main:app --reload"
echo "  2. Testez les notifications: $PROJECT_ROOT/scripts/test-eir-notifications.sh"
echo "  3. Accédez à l'API: http://localhost:8000/docs"
echo ""
echo "💡 Les données de test incluent maintenant:"
echo "  - 4 utilisateurs (admin, user, orange, inwi)"
echo "  - 5 appareils avec 7 IMEI"
echo "  - 5 notifications avec les nouveaux champs"
echo "  - 7 entrées TAC pour les tests de validation"
echo "  - Données cohérentes pour tester le système complet"
