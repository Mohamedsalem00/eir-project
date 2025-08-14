"""
Exemples d'utilisation de l'API d'import blacklist
Démontre comment utiliser les différents endpoints d'import
"""

import requests
import json
import pandas as pd
import io

# Configuration
BASE_URL = "http://localhost:8000"
API_TOKEN = "votre_token_jwt_ici"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def exemple_1_templates_mapping():
    """
    Exemple 1: Récupérer les templates de mapping disponibles
    """
    print("=== Exemple 1: Templates de Mapping ===")
    
    # Récupérer tous les templates
    response = requests.get(f"{BASE_URL}/import/templates", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Nombre de templates disponibles: {len(data['templates'])}")
        print(f"Catégories: {', '.join(data['categories'])}")
        
        # Afficher les templates telecom
        print("\nTemplates Telecom:")
        for template in data['templates']:
            if template['system_type'] == 'telecom':
                print(f"  - {template['name']}: {template['description']}")
    else:
        print(f"Erreur: {response.status_code} - {response.text}")

def exemple_2_preview_csv():
    """
    Exemple 2: Prévisualiser un import CSV
    """
    print("\n=== Exemple 2: Prévisualisation CSV ===")
    
    # Données CSV d'exemple
    csv_data = """marque,modele,emmc,imei1,imei2,statut
Samsung,Galaxy S21,256GB,123456789012345,123456789012346,active
Apple,iPhone 13,128GB,987654321098765,,blacklisted
Huawei,P40 Pro,512GB,456789012345678,456789012345679,active"""
    
    request_data = {
        "file_content": csv_data,
        "file_type": "csv",
        "preview_rows": 2,
        "config": {
            "blacklist_only": False
        }
    }
    
    response = requests.post(f"{BASE_URL}/import/preview", headers=headers, json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Fichier analysé avec succès!")
        print(f"Total lignes: {data['total_rows']}")
        print(f"En-têtes détectés: {', '.join(data['headers'])}")
        print(f"Mapping détecté: {data['detected_mapping']}")
        print(f"Aperçu des données:")
        for i, row in enumerate(data['preview_data']):
            print(f"  Ligne {i+1}: {row}")
    else:
        print(f"Erreur: {response.status_code} - {response.text}")

def exemple_3_import_csv_orange():
    """
    Exemple 3: Import CSV avec mapping Orange/France Telecom
    """
    print("\n=== Exemple 3: Import CSV Orange ===")
    
    # Données au format Orange
    csv_data = """Marque,Modèle,Capacité,IMEI_Principal,IMEI_Secondaire,ID_Client
Samsung,Galaxy S21,256GB,123456789012345,123456789012346,550e8400-e29b-41d4-a716-446655440000
Apple,iPhone 13,128GB,987654321098765,,550e8400-e29b-41d4-a716-446655440001
Huawei,P40 Pro,512GB,456789012345678,456789012345679,550e8400-e29b-41d4-a716-446655440002"""
    
    # Configuration avec mapping Orange
    orange_mapping = {
        "marque": "Marque",
        "modele": "Modèle", 
        "emmc": "Capacité",
        "imei1": "IMEI_Principal",
        "imei2": "IMEI_Secondaire",
        "utilisateur_id": "ID_Client"
    }
    
    request_data = {
        "csv_content": csv_data,
        "config": {
            "column_mapping": orange_mapping,
            "blacklist_only": False,
            "skip_validation": False
        }
    }
    
    response = requests.post(f"{BASE_URL}/import/csv", headers=headers, json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("Import réussi!")
            summary = data['summary']
            print(f"  Appareils créés: {summary['appareils_created']}")
            print(f"  IMEI créés: {summary['imeis_created']}")
            print(f"  Temps de traitement: {data['processing_time_seconds']}s")
        else:
            print("Import avec erreurs:")
            for error in data['errors']:
                print(f"  - {error}")
    else:
        print(f"Erreur: {response.status_code} - {response.text}")

def exemple_4_import_json_intune():
    """
    Exemple 4: Import JSON au format Microsoft Intune
    """
    print("\n=== Exemple 4: Import JSON Intune ===")
    
    # Données au format Intune
    json_data = {
        "devices": [
            {
                "Manufacturer": "Samsung",
                "Model": "Galaxy S21",
                "TotalStorageSpaceInBytes": "274877906944",  # 256GB en bytes
                "IMEI": "123456789012345",
                "UserPrincipalName": "user1@company.com"
            },
            {
                "Manufacturer": "Apple", 
                "Model": "iPhone 13",
                "TotalStorageSpaceInBytes": "137438953472",  # 128GB en bytes
                "IMEI": "987654321098765",
                "UserPrincipalName": "user2@company.com"
            }
        ],
        "metadata": {
            "export_date": "2025-08-13",
            "source": "microsoft_intune"
        }
    }
    
    # Configuration avec mapping Intune
    intune_mapping = {
        "marque": "Manufacturer",
        "modele": "Model",
        "emmc": "TotalStorageSpaceInBytes",
        "imei1": "IMEI",
        "utilisateur_id": "UserPrincipalName"
    }
    
    request_data = {
        "json_content": json.dumps(json_data),
        "config": {
            "column_mapping": intune_mapping,
            "blacklist_only": True,  # Marquer comme blacklistés
            "skip_validation": False
        }
    }
    
    response = requests.post(f"{BASE_URL}/import/json", headers=headers, json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("Import JSON réussi!")
            summary = data['summary']
            print(f"  Appareils créés: {summary['appareils_created']}")
            print(f"  IMEI créés: {summary['imeis_created']}")
            print(f"  Mode blacklist activé")
        else:
            print("Import avec erreurs:")
            for error in data['errors']:
                print(f"  - {error}")
            for warning in data['warnings']:
                print(f"  ⚠️ {warning}")
    else:
        print(f"Erreur: {response.status_code} - {response.text}")

def exemple_5_upload_fichier():
    """
    Exemple 5: Upload et import d'un fichier
    """
    print("\n=== Exemple 5: Upload de Fichier ===")
    
    # Créer un fichier CSV temporaire
    csv_content = """marque,modele,imei1,statut
Samsung,Galaxy S22,123456789012345,active
Apple,iPhone 14,987654321098765,blacklisted"""
    
    # Préparer l'upload
    files = {
        'file': ('devices.csv', io.StringIO(csv_content), 'text/csv')
    }
    
    form_data = {
        'blacklist_only': 'false',
        'config': json.dumps({
            "column_mapping": {
                "marque": "marque",
                "modele": "modele", 
                "imei1": "imei1",
                "statut": "statut"
            }
        })
    }
    
    # Headers sans Content-Type pour multipart
    upload_headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    
    response = requests.post(
        f"{BASE_URL}/import/upload", 
        headers=upload_headers,
        files=files,
        data=form_data
    )
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("Upload et import réussis!")
            summary = data['summary']
            print(f"  Appareils créés: {summary['appareils_created']}")
            print(f"  IMEI créés: {summary['imeis_created']}")
        else:
            print("Upload avec erreurs:")
            for error in data['errors']:
                print(f"  - {error}")
    else:
        print(f"Erreur: {response.status_code} - {response.text}")

def exemple_6_validation_mapping():
    """
    Exemple 6: Validation d'un mapping personnalisé
    """
    print("\n=== Exemple 6: Validation de Mapping ===")
    
    # En-têtes d'un fichier personnalisé
    headers = ["Device_Brand", "Device_Model", "Memory_Size", "Primary_IMEI", "Owner_Email"]
    
    # Mapping proposé
    proposed_mapping = {
        "marque": "Device_Brand",
        "modele": "Device_Model",
        "emmc": "Memory_Size",
        "imei1": "Primary_IMEI"
        # Note: utilisateur_id manquant volontairement pour test
    }
    
    request_data = {
        "headers": headers,
        "proposed_mapping": proposed_mapping
    }
    
    response = requests.post(f"{BASE_URL}/import/validate-mapping", headers=headers, json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Mapping valide: {data['is_valid']}")
        
        if data['missing_required_fields']:
            print("Champs obligatoires manquants:")
            for field in data['missing_required_fields']:
                print(f"  - {field}")
        
        if data['suggestions']:
            print("Suggestions d'amélioration:")
            for suggestion in data['suggestions']:
                print(f"  - {suggestion['db_field']}: {suggestion['suggested_columns']}")
    else:
        print(f"Erreur: {response.status_code} - {response.text}")

def exemple_7_gestion_erreurs():
    """
    Exemple 7: Gestion des erreurs d'import
    """
    print("\n=== Exemple 7: Gestion des Erreurs ===")
    
    # CSV avec des erreurs volontaires
    csv_malformed = """marque,modele,imei1
Samsung,Galaxy S21,12345  # IMEI trop court
,iPhone 13,987654321098765  # Marque manquante
Huawei,P40 Pro,invalid_imei  # IMEI non numérique"""
    
    request_data = {
        "csv_content": csv_malformed,
        "config": {
            "skip_validation": False
        }
    }
    
    response = requests.post(f"{BASE_URL}/import/csv", headers=headers, json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Résultat import: {'Succès' if data['success'] else 'Échec'}")
        
        summary = data['summary']
        print(f"Total lignes: {summary['total_rows']}")
        print(f"Lignes traitées: {summary['processed']}")
        print(f"Appareils créés: {summary['appareils_created']}")
        
        if data['errors']:
            print("Erreurs détectées:")
            for error in data['errors']:
                print(f"  ❌ {error}")
        
        if data['warnings']:
            print("Avertissements:")
            for warning in data['warnings']:
                print(f"  ⚠️ {warning}")
    else:
        print(f"Erreur HTTP: {response.status_code} - {response.text}")

def guide_utilisation():
    """
    Guide d'utilisation de l'API d'import
    """
    print("🔷 Guide d'Utilisation de l'API Import Blacklist 🔷")
    print()
    print("1. 📋 Templates de Mapping")
    print("   GET /import/templates - Récupérer les templates prédéfinis")
    print("   Utilisez les templates pour des systèmes connus (Orange, Intune, etc.)")
    print()
    print("2. 👁️ Prévisualisation")
    print("   POST /import/preview - Analyser un fichier avant import")
    print("   Vérifiez le mapping automatique et les erreurs potentielles")
    print()
    print("3. ✅ Validation")
    print("   POST /import/validate-mapping - Valider un mapping personnalisé")
    print("   Assurez-vous que votre mapping est correct")
    print()
    print("4. 📊 Import CSV")
    print("   POST /import/csv - Importer depuis du contenu CSV")
    print("   Format texte avec mapping flexible")
    print()
    print("5. 🔀 Import JSON")
    print("   POST /import/json - Importer depuis du contenu JSON")
    print("   Structure hiérarchique avec métadonnées")
    print()
    print("6. 📁 Upload de Fichier")
    print("   POST /import/upload - Upload direct de fichier")
    print("   Interface multipart pour uploads web")
    print()
    print("🔐 Niveaux d'Accès Requis:")
    print("   - Templates/Validation: Utilisateur authentifié")
    print("   - Prévisualisation: Niveau 'standard'")
    print("   - Import: Niveau 'élevé' ou 'admin'")
    print()

if __name__ == "__main__":
    print("🚀 Démarrage des exemples d'import blacklist")
    print("Note: Assurez-vous que l'API est démarrée et que vous avez un token valide")
    print()
    
    # Afficher le guide d'utilisation
    guide_utilisation()
    
    # Exécuter les exemples (commenté pour éviter les erreurs sans serveur)
    """
    try:
        exemple_1_templates_mapping()
        exemple_2_preview_csv()
        exemple_3_import_csv_orange() 
        exemple_4_import_json_intune()
        exemple_5_upload_fichier()
        exemple_6_validation_mapping()
        exemple_7_gestion_erreurs()
        
        print("\n✅ Tous les exemples ont été exécutés!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API. Vérifiez que le serveur est démarré.")
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
    """
