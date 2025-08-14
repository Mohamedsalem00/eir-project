# API d'Import Blacklist - Guide Complet

## Vue d'ensemble

L'API d'import blacklist permet d'importer des appareils et leurs IMEI depuis des fichiers CSV ou JSON avec un mapping de colonnes flexible. Cette fonctionnalité est conçue pour s'intégrer facilement avec différents systèmes externes (opérateurs télécom, solutions MDM, systèmes d'inventaire).

## Fonctionnalités Principales

### 🔄 Formats Supportés
- **CSV** : Fichiers délimités par virgules, point-virgules ou tabulations
- **JSON** : Arrays d'objets ou structures hiérarchiques avec métadonnées

### 🎯 Mapping Intelligent
- **Détection automatique** des colonnes basée sur les noms
- **Templates prédéfinis** pour systèmes courants (Orange, SFR, Intune, etc.)
- **Mapping personnalisé** pour formats spécifiques
- **Validation** en temps réel du mapping

### ✅ Validation des Données
- **Algorithme de Luhn** pour validation IMEI
- **Champs obligatoires** (marque, modèle)
- **Détection de doublons** IMEI
- **Support multi-IMEI** (principal + secondaire)

### 🛡️ Sécurité et Contrôle
- **Niveaux d'accès** configurables par endpoint
- **Audit complet** des opérations d'import
- **Validation des utilisateurs** assignés
- **Rollback automatique** en cas d'erreur

## Structure des Données

### Modèle Appareil
```sql
CREATE TABLE appareil (
    id UUID PRIMARY KEY,
    marque VARCHAR(50),           -- Fabricant (Samsung, Apple, etc.)
    modele VARCHAR(50),           -- Modèle (Galaxy S21, iPhone 13, etc.)
    emmc VARCHAR(100),            -- Capacité stockage (256GB, 128GB, etc.)
    utilisateur_id UUID           -- Propriétaire de l'appareil
);
```

### Modèle IMEI
```sql
CREATE TABLE imei (
    id UUID PRIMARY KEY,
    numero_imei VARCHAR(20),      -- IMEI 14-15 chiffres
    numero_slot INTEGER,          -- 1=principal, 2=secondaire
    statut VARCHAR(50),           -- active, blacklisted, etc.
    appareil_id UUID              -- Référence vers l'appareil
);
```

## Endpoints Disponibles

### 1. Templates de Mapping

#### `GET /import/templates`
Récupère les templates de mapping prédéfinis.

**Paramètres:**
- `category` (optionnel) : Filtrer par catégorie (`telecom`, `mdm`, `inventory`)

**Réponse:**
```json
{
    "templates": [
        {
            "name": "Orange/France Telecom",
            "description": "Format d'export Orange/France Telecom",
            "system_type": "telecom",
            "mapping": {
                "marque": "Marque",
                "modele": "Modèle",
                "emmc": "Capacité",
                "imei1": "IMEI_Principal",
                "imei2": "IMEI_Secondaire"
            },
            "example_headers": ["Marque", "Modèle", "Capacité", "IMEI_Principal"]
        }
    ],
    "categories": ["telecom", "mdm", "inventory"]
}
```

### 2. Prévisualisation d'Import

#### `POST /import/preview`
Analyse un fichier avant import pour valider la structure.

**Niveau requis:** `standard`

**Corps de la requête:**
```json
{
    "file_content": "marque,modele,imei1\nSamsung,Galaxy S21,123456789012345",
    "file_type": "csv",
    "preview_rows": 5,
    "config": {
        "column_mapping": {
            "marque": "marque",
            "modele": "modele"
        }
    }
}
```

**Réponse:**
```json
{
    "success": true,
    "file_type": "csv",
    "total_rows": 1,
    "headers": ["marque", "modele", "imei1"],
    "column_mapping_suggestions": [
        {
            "db_field": "marque",
            "suggested_columns": ["marque"],
            "is_required": true,
            "description": "Marque/fabricant de l'appareil"
        }
    ],
    "detected_mapping": {
        "marque": "marque",
        "modele": "modele",
        "imei1": "imei1"
    },
    "preview_data": [
        {
            "marque": "Samsung",
            "modele": "Galaxy S21",
            "imei1": "123456789012345"
        }
    ],
    "errors": [],
    "warnings": []
}
```

### 3. Validation de Mapping

#### `POST /import/validate-mapping`
Valide un mapping de colonnes proposé.

**Corps de la requête:**
```json
{
    "headers": ["Brand", "Model", "Storage", "IMEI"],
    "proposed_mapping": {
        "marque": "Brand",
        "modele": "Model",
        "emmc": "Storage",
        "imei1": "IMEI"
    }
}
```

**Réponse:**
```json
{
    "is_valid": true,
    "missing_required_fields": [],
    "unknown_fields": [],
    "suggestions": [],
    "validated_mapping": {
        "marque": "Brand",
        "modele": "Model",
        "emmc": "Storage",
        "imei1": "IMEI"
    }
}
```

### 4. Import CSV

#### `POST /import/csv`
Importe des appareils depuis un contenu CSV.

**Niveau requis:** `élevé` ou `admin`

**Corps de la requête:**
```json
{
    "csv_content": "marque,modele,emmc,imei1,statut\nSamsung,Galaxy S21,256GB,123456789012345,active",
    "config": {
        "column_mapping": {
            "marque": "marque",
            "modele": "modele",
            "emmc": "emmc",
            "imei1": "imei1",
            "statut": "statut"
        },
        "blacklist_only": false,
        "assign_to_user": "550e8400-e29b-41d4-a716-446655440000",
        "skip_validation": false,
        "update_existing": false
    }
}
```

### 5. Import JSON

#### `POST /import/json`
Importe des appareils depuis un contenu JSON.

**Niveau requis:** `élevé` ou `admin`

**Corps de la requête:**
```json
{
    "json_content": "{\"data\":[{\"marque\":\"Samsung\",\"modele\":\"Galaxy S21\"}]}",
    "config": {
        "blacklist_only": true,
        "assign_to_user": "550e8400-e29b-41d4-a716-446655440000"
    }
}
```

### 6. Upload de Fichier

#### `POST /import/upload`
Upload et import direct d'un fichier.

**Niveau requis:** `élevé` ou `admin`

**Format:** `multipart/form-data`

**Paramètres:**
- `file` : Fichier CSV/JSON à uploader
- `config` (optionnel) : Configuration JSON
- `blacklist_only` (optionnel) : Mode blacklist
- `assign_to_user` (optionnel) : ID utilisateur assigné

## Configuration d'Import

### Options Disponibles

```json
{
    "column_mapping": {
        "marque": "nom_colonne_fichier",
        "modele": "nom_colonne_fichier",
        "emmc": "nom_colonne_fichier",
        "imei1": "nom_colonne_fichier",
        "imei2": "nom_colonne_fichier",
        "utilisateur_id": "nom_colonne_fichier",
        "statut": "nom_colonne_fichier"
    },
    "blacklist_only": false,           // Marquer tous comme blacklistés
    "assign_to_user": "uuid",          // Assigner à un utilisateur
    "skip_validation": false,          // Ignorer validation IMEI
    "update_existing": false           // Mettre à jour existants
}
```

### Champs de Mapping

| Champ DB | Description | Obligatoire | Exemples de Colonnes |
|----------|-------------|-------------|---------------------|
| `marque` | Fabricant | ✅ | Brand, Manufacturer, Marque, Fabricant |
| `modele` | Modèle | ✅ | Model, Modèle, Device_Model |
| `emmc` | Stockage | ❌ | Storage, Capacity, Memory, Capacité |
| `imei1` | IMEI principal | ❌ | IMEI, Primary_IMEI, IMEI_Principal |
| `imei2` | IMEI secondaire | ❌ | Secondary_IMEI, IMEI_Secondaire |
| `utilisateur_id` | Propriétaire | ❌ | User_ID, Customer_ID, Owner |
| `statut` | Statut appareil | ❌ | Status, Statut, Device_Status |

## Templates Prédéfinis

### Opérateurs Télécom

#### Orange/France Telecom
```json
{
    "marque": "Marque",
    "modele": "Modèle", 
    "emmc": "Capacité",
    "imei1": "IMEI_Principal",
    "imei2": "IMEI_Secondaire",
    "utilisateur_id": "ID_Client"
}
```

#### SFR
```json
{
    "marque": "Brand",
    "modele": "Model",
    "emmc": "Storage",
    "imei1": "Primary_IMEI",
    "imei2": "Secondary_IMEI",
    "utilisateur_id": "Customer_ID"
}
```

#### Free Mobile
```json
{
    "marque": "fabricant",
    "modele": "modele_appareil",
    "emmc": "memoire",
    "imei1": "imei_1",
    "imei2": "imei_2",
    "utilisateur_id": "abonne_id"
}
```

### Solutions MDM

#### Microsoft Intune
```json
{
    "marque": "Manufacturer",
    "modele": "Model",
    "emmc": "TotalStorageSpaceInBytes",
    "imei1": "IMEI",
    "utilisateur_id": "UserPrincipalName"
}
```

#### VMware Workspace ONE
```json
{
    "marque": "DeviceManufacturer",
    "modele": "DeviceModel",
    "emmc": "DeviceCapacity",
    "imei1": "DeviceIMEI",
    "utilisateur_id": "EnrolledUserUuid"
}
```

### Systèmes d'Inventaire

#### SAP Asset Management
```json
{
    "marque": "EQUIPMENT_MANUFACTURER",
    "modele": "EQUIPMENT_MODEL",
    "emmc": "MEMORY_CAPACITY",
    "imei1": "IMEI_PRIMARY",
    "imei2": "IMEI_SECONDARY",
    "utilisateur_id": "ASSIGNED_USER"
}
```

## Réponses d'Import

### Import Réussi
```json
{
    "success": true,
    "message": "Import réussi : 5 appareils et 8 IMEI importés",
    "summary": {
        "total_rows": 5,
        "processed": 5,
        "appareils_created": 5,
        "imeis_created": 8,
        "errors_count": 0,
        "warnings_count": 1
    },
    "column_mapping_used": {
        "marque": "Brand",
        "modele": "Model"
    },
    "errors": [],
    "warnings": ["IMEI doublon ignoré: 123456789012345"],
    "import_id": "550e8400-e29b-41d4-a716-446655440000",
    "processing_time_seconds": 2.34
}
```

### Import avec Erreurs
```json
{
    "success": false,
    "message": "Import partiellement réussi avec 2 erreurs",
    "summary": {
        "total_rows": 5,
        "processed": 3,
        "appareils_created": 3,
        "imeis_created": 5,
        "errors_count": 2,
        "warnings_count": 0
    },
    "errors": [
        "Ligne 2: Marque et modèle sont obligatoires",
        "Ligne 4: IMEI invalide: 12345"
    ],
    "warnings": [],
    "processing_time_seconds": 1.87
}
```

## Codes d'Erreur

| Code | Description | Solution |
|------|-------------|----------|
| 400 | Format de fichier non supporté | Utilisez CSV ou JSON |
| 400 | Champs obligatoires manquants | Vérifiez le mapping marque/modèle |
| 400 | IMEI invalide | Vérifiez la validation Luhn |
| 401 | Non authentifié | Fournissez un token valide |
| 403 | Niveau d'accès insuffisant | Niveau 'élevé' requis pour import |
| 422 | Erreur de validation | Vérifiez le format des données |
| 500 | Erreur serveur | Contactez l'administrateur |

## Exemples d'Utilisation

### Import Simple CSV
```python
import requests

headers = {"Authorization": "Bearer YOUR_TOKEN"}

csv_data = """marque,modele,imei1
Samsung,Galaxy S21,123456789012345
Apple,iPhone 13,987654321098765"""

response = requests.post(
    "http://localhost:8000/import/csv",
    headers=headers,
    json={
        "csv_content": csv_data,
        "config": {"blacklist_only": True}
    }
)

print(response.json())
```

### Import avec Template Orange
```python
# Récupérer le template Orange
templates = requests.get("http://localhost:8000/import/templates").json()
orange_template = next(t for t in templates["templates"] if "Orange" in t["name"])

# Utiliser le mapping
csv_data = """Marque,Modèle,IMEI_Principal
Samsung,Galaxy S21,123456789012345"""

response = requests.post(
    "http://localhost:8000/import/csv",
    headers=headers,
    json={
        "csv_content": csv_data,
        "config": {"column_mapping": orange_template["mapping"]}
    }
)
```

## Bonnes Pratiques

### 1. Préparation des Données
- **Nettoyez** les IMEI (supprimez espaces et caractères spéciaux)
- **Validez** le format avant import (15 chiffres max)
- **Vérifiez** les champs obligatoires (marque, modèle)
- **Normalisez** les noms de marques (Samsung vs SAMSUNG)

### 2. Gestion des Erreurs
- **Prévisualisez** toujours avant import complet
- **Traitez** les erreurs par lots pour éviter la surcharge
- **Logguez** les opérations pour audit
- **Testez** avec des échantillons réduits

### 3. Performance
- **Limitez** les imports à 1000 lignes par batch
- **Utilisez** les transactions pour la cohérence
- **Monithez** les temps de traitement
- **Planifiez** les imports volumineux hors heures de pointe

### 4. Sécurité
- **Validez** les tokens avant import
- **Vérifiez** les permissions utilisateur
- **Auditez** toutes les opérations
- **Limitez** l'accès aux niveaux appropriés

## Monitoring et Audit

### Logs d'Import
Chaque import génère une entrée dans `journal_audit` :
```json
{
    "utilisateur_id": "uuid",
    "action": "IMPORT_CSV",
    "date": "2025-08-13T18:30:00Z",
    "details": {
        "summary": {...},
        "mapping_used": {...}
    }
}
```

### Métriques Recommandées
- **Nombre d'imports** par jour/heure
- **Taux de succès** des imports
- **Temps de traitement** moyen
- **Volume d'IMEI** traités
- **Erreurs fréquentes** par type
