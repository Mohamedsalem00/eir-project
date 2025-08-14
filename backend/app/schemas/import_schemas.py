"""
Schémas Pydantic pour l'import d'appareils et IMEI
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any, Union
from datetime import datetime
import uuid

class ImportConfigRequest(BaseModel):
    """Configuration pour l'import"""
    column_mapping: Optional[Dict[str, str]] = Field(
        None, 
        description="Mapping personnalisé des colonnes {champ_db: nom_colonne_fichier}"
    )
    blacklist_only: bool = Field(
        False, 
        description="Si True, marque tous les appareils comme blacklistés"
    )
    assign_to_user: Optional[str] = Field(
        None, 
        description="ID de l'utilisateur à qui assigner les appareils (UUID)"
    )
    skip_validation: bool = Field(
        False, 
        description="Si True, ignore la validation IMEI (non recommandé)"
    )
    update_existing: bool = Field(
        False, 
        description="Si True, met à jour les appareils existants"
    )

    @validator('assign_to_user')
    def validate_user_id(cls, v):
        if v is not None:
            try:
                uuid.UUID(v)
            except ValueError:
                raise ValueError('assign_to_user doit être un UUID valide')
        return v

class ImportPreviewRequest(BaseModel):
    """Requête pour prévisualiser l'import"""
    file_content: str = Field(..., description="Contenu du fichier")
    file_type: str = Field(..., description="Type de fichier: 'csv' ou 'json'")
    config: Optional[ImportConfigRequest] = Field(None, description="Configuration d'import")
    preview_rows: int = Field(5, ge=1, le=20, description="Nombre de lignes à prévisualiser")

class ColumnMappingSuggestion(BaseModel):
    """Suggestion de mapping de colonne"""
    db_field: str = Field(..., description="Nom du champ dans la base de données")
    suggested_columns: List[str] = Field(..., description="Colonnes suggérées du fichier")
    is_required: bool = Field(..., description="Si ce champ est obligatoire")
    description: str = Field(..., description="Description du champ")

class ImportPreviewResponse(BaseModel):
    """Réponse de prévisualisation d'import"""
    success: bool
    file_type: str
    total_rows: int
    headers: List[str]
    column_mapping_suggestions: List[ColumnMappingSuggestion]
    detected_mapping: Dict[str, str]
    preview_data: List[Dict[str, Any]]
    errors: List[str] = []
    warnings: List[str] = []

class ImportResultSummary(BaseModel):
    """Résumé des résultats d'import"""
    total_rows: int
    processed: int
    appareils_created: int
    imeis_created: int
    errors_count: int
    warnings_count: int

class ImportResponse(BaseModel):
    """Réponse d'import"""
    success: bool
    message: str
    summary: Optional[ImportResultSummary] = None
    column_mapping_used: Dict[str, str] = {}
    errors: List[str] = []
    warnings: List[str] = []
    import_id: Optional[str] = None
    processing_time_seconds: Optional[float] = None

class CSVImportRequest(BaseModel):
    """Requête d'import CSV"""
    csv_content: str = Field(..., description="Contenu du fichier CSV")
    config: Optional[ImportConfigRequest] = Field(None, description="Configuration d'import")

class JSONImportRequest(BaseModel):
    """Requête d'import JSON"""
    json_content: str = Field(..., description="Contenu du fichier JSON")
    config: Optional[ImportConfigRequest] = Field(None, description="Configuration d'import")

class MappingValidationRequest(BaseModel):
    """Requête de validation de mapping"""
    headers: List[str] = Field(..., description="En-têtes du fichier")
    proposed_mapping: Dict[str, str] = Field(..., description="Mapping proposé")

class MappingValidationResponse(BaseModel):
    """Réponse de validation de mapping"""
    is_valid: bool
    missing_required_fields: List[str] = []
    unknown_fields: List[str] = []
    suggestions: List[ColumnMappingSuggestion] = []
    validated_mapping: Dict[str, str] = {}

# Modèles pour les templates de mapping prédéfinis
class MappingTemplate(BaseModel):
    """Template de mapping prédéfini"""
    name: str = Field(..., description="Nom du template")
    description: str = Field(..., description="Description du template")
    system_type: str = Field(..., description="Type de système (telecom, mdm, inventory, etc.)")
    mapping: Dict[str, str] = Field(..., description="Mapping des colonnes")
    example_headers: List[str] = Field(..., description="Exemples d'en-têtes")

class AvailableTemplatesResponse(BaseModel):
    """Réponse avec les templates disponibles"""
    templates: List[MappingTemplate]
    categories: List[str]

# Modèles pour les statistiques d'import
class ImportStatistics(BaseModel):
    """Statistiques d'import"""
    total_imports: int
    successful_imports: int
    failed_imports: int
    total_devices_imported: int
    total_imeis_imported: int
    last_import_date: Optional[datetime] = None
    average_processing_time: Optional[float] = None

class ImportHistoryItem(BaseModel):
    """Élément de l'historique d'import"""
    import_id: str
    user_id: Optional[str] = None
    file_type: str
    import_date: datetime
    summary: ImportResultSummary
    status: str  # success, failed, partial
    processing_time_seconds: float

class ImportHistoryResponse(BaseModel):
    """Réponse de l'historique d'import"""
    history: List[ImportHistoryItem]
    statistics: ImportStatistics
    pagination: Dict[str, Any]

# Configuration des templates prédéfinis
PREDEFINED_TEMPLATES = [
    MappingTemplate(
        name="Orange/France Telecom",
        description="Format d'export Orange/France Telecom",
        system_type="telecom",
        mapping={
            "marque": "Marque",
            "modele": "Modèle", 
            "emmc": "Capacité",
            "imei1": "IMEI_Principal",
            "imei2": "IMEI_Secondaire",
            "utilisateur_id": "ID_Client"
        },
        example_headers=["Marque", "Modèle", "Capacité", "IMEI_Principal", "IMEI_Secondaire", "ID_Client"]
    ),
    MappingTemplate(
        name="SFR Export",
        description="Format d'export SFR",
        system_type="telecom",
        mapping={
            "marque": "Brand",
            "modele": "Model",
            "emmc": "Storage",
            "imei1": "Primary_IMEI", 
            "imei2": "Secondary_IMEI",
            "utilisateur_id": "Customer_ID"
        },
        example_headers=["Brand", "Model", "Storage", "Primary_IMEI", "Secondary_IMEI", "Customer_ID"]
    ),
    MappingTemplate(
        name="Microsoft Intune",
        description="Export Microsoft Intune",
        system_type="mdm",
        mapping={
            "marque": "Manufacturer",
            "modele": "Model",
            "emmc": "TotalStorageSpaceInBytes",
            "imei1": "IMEI",
            "utilisateur_id": "UserPrincipalName"
        },
        example_headers=["Manufacturer", "Model", "TotalStorageSpaceInBytes", "IMEI", "UserPrincipalName"]
    ),
    MappingTemplate(
        name="VMware Workspace ONE",
        description="Export VMware Workspace ONE",
        system_type="mdm",
        mapping={
            "marque": "DeviceManufacturer",
            "modele": "DeviceModel",
            "emmc": "DeviceCapacity", 
            "imei1": "DeviceIMEI",
            "utilisateur_id": "EnrolledUserUuid"
        },
        example_headers=["DeviceManufacturer", "DeviceModel", "DeviceCapacity", "DeviceIMEI", "EnrolledUserUuid"]
    ),
    MappingTemplate(
        name="SAP Asset Management",
        description="Export SAP Asset Management",
        system_type="inventory",
        mapping={
            "marque": "EQUIPMENT_MANUFACTURER",
            "modele": "EQUIPMENT_MODEL",
            "emmc": "MEMORY_CAPACITY",
            "imei1": "IMEI_PRIMARY",
            "imei2": "IMEI_SECONDARY",
            "utilisateur_id": "ASSIGNED_USER"
        },
        example_headers=["EQUIPMENT_MANUFACTURER", "EQUIPMENT_MODEL", "MEMORY_CAPACITY", "IMEI_PRIMARY", "IMEI_SECONDARY", "ASSIGNED_USER"]
    )
]
