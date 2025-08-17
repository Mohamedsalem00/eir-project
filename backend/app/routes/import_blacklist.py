"""
Routeur pour l'import d'appareils et IMEI en blacklist
Supporte les formats CSV et JSON avec mapping de colonnes flexible
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import time
import uuid
import json
import logging

from ..core.dependencies import get_db, get_current_user, get_admin_user
from ..core.permissions import require_niveau_acces, AccessLevel
from ..models.utilisateur import Utilisateur
from ..services.import_service import ImportService
from ..schemas.import_schemas import (
    ImportConfigRequest,
    ImportPreviewRequest,
    ImportPreviewResponse,
    ImportResponse,
    MappingValidationRequest,
    MappingValidationResponse,
    AvailableTemplatesResponse,
    ImportHistoryResponse,
    ColumnMappingSuggestion,
    ImportResultSummary,
    PREDEFINED_TEMPLATES
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/import", tags=["Import"])

@router.get(
    "/aide",
    summary="Guide d'utilisation",
    description="Comment utiliser les endpoints d'import simplement"
)
async def guide_utilisation():
    """Guide simple pour utiliser l'import"""
    return {
        "message": "Guide d'utilisation de l'import",
        "etapes": [
            "1. Préparez votre fichier CSV avec les colonnes : marque,modele,imei1,statut",
            "2. Utilisez l'endpoint /import/simple-upload pour uploader votre fichier",
            "3. Le système détectera automatiquement le format et importera les données",
            "4. Les numéros de série (SNR) seront extraits automatiquement des IMEI",
            "5. Les statuts supportés sont : active, suspect, bloque"
        ],
        "exemple_csv": "marque,modele,imei1,statut\nSamsung,Galaxy S21,353260051234567,active\nApple,iPhone 13,356920051789012,bloque",
        "endpoints_disponibles": {
            "/simple-upload": "Upload simple depuis votre appareil",
            "/templates": "Templates de mapping prédéfinis",
            "/preview": "Prévisualiser avant import"
        }
    }

@router.get(
    "/templates",
    response_model=AvailableTemplatesResponse,
    summary="Templates de mapping",
    description="Obtenir les templates de mapping prédéfinis pour faciliter l'import de fichiers."
)
async def get_mapping_templates(
    category: Optional[str] = Query(None, description="Filtrer par catégorie de système"),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Obtenir les templates de mapping prédéfinis"""
    try:
        templates = PREDEFINED_TEMPLATES
        
        if category:
            templates = [t for t in templates if t.system_type == category]
        
        categories = list(set(t.system_type for t in PREDEFINED_TEMPLATES))
        
        logger.info(f"Templates de mapping consultés par utilisateur {current_user.id} ({current_user.nom})")
        
        return AvailableTemplatesResponse(
            templates=templates,
            categories=categories
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération des templates"
        )

@router.post(
    "/preview",
    response_model=ImportPreviewResponse,
    summary="Prévisualiser un fichier",
    description="Analyser un fichier CSV ou JSON avant l'import pour vérifier la structure et détecter les erreurs."
)
async def preview_import(
    request: ImportPreviewRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Prévisualiser un import de fichier"""
    try:
        # Vérifier le niveau d'accès minimum pour la prévisualisation
        if hasattr(current_user, 'niveau_acces'):
            user_level = AccessLevel.from_french(current_user.niveau_acces or "basique")
            if user_level.value not in ['standard', 'elevated', 'admin']:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Niveau d'accès insuffisant. Niveau 'standard' ou plus élevé requis."
                )
        
        import_service = ImportService(db)
        
        if request.file_type.lower() not in ['csv', 'json']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Type de fichier non supporté. Utilisez 'csv' ou 'json'."
            )
        
        # Analyser le contenu selon le type
        if request.file_type.lower() == 'csv':
            result = import_service._analyze_csv_preview(
                request.file_content, 
                request.config.column_mapping if request.config else None,
                request.preview_rows
            )
        else:  # json
            result = import_service._analyze_json_preview(
                request.file_content,
                request.config.column_mapping if request.config else None,
                request.preview_rows
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de la prévisualisation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la prévisualisation: {str(e)}"
        )

@router.post(
    "/validate-mapping",
    response_model=MappingValidationResponse,
    summary="Valider le Mapping de Colonnes",
    description="""
    ## Validation de Mapping de Colonnes
    
    Valider un mapping de colonnes proposé avant l'import :
    
    ### Validations Effectuées :
    - **Champs obligatoires** : Vérification que marque et modèle sont mappés
    - **Cohérence** : Validation que les colonnes existent dans le fichier
    - **Suggestions** : Propositions alternatives pour les champs non mappés
    - **Optimisation** : Détection de mappings potentiellement meilleurs
    
    ### Retour :
    - **is_valid** : True si le mapping est valide
    - **missing_required_fields** : Champs obligatoires manquants
    - **suggestions** : Améliorations suggérées
    - **validated_mapping** : Mapping validé et optimisé
    
    Accessible à tous les utilisateurs authentifiés.
    """
)
async def validate_mapping(
    request: MappingValidationRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    """Valider un mapping de colonnes"""
    try:
        import_service = ImportService(db)
        
        # Vérifier que les colonnes du mapping existent
        unknown_fields = []
        for db_field, file_column in request.proposed_mapping.items():
            if file_column not in request.headers:
                unknown_fields.append(file_column)
        
        # Vérifier les champs obligatoires
        required_fields = ['marque', 'modele']
        missing_required = []
        for field in required_fields:
            if field not in request.proposed_mapping:
                missing_required.append(field)
        
        # Obtenir des suggestions pour améliorer le mapping
        suggestions_dict = import_service.get_column_mapping_suggestions(request.headers)
        suggestions = []
        
        for db_field, matches in suggestions_dict.items():
            if db_field not in request.proposed_mapping and matches:
                suggestions.append(ColumnMappingSuggestion(
                    db_field=db_field,
                    suggested_columns=matches,
                    is_required=db_field in required_fields,
                    description=_get_field_description(db_field)
                ))
        
        is_valid = len(missing_required) == 0 and len(unknown_fields) == 0
        
        return MappingValidationResponse(
            is_valid=is_valid,
            missing_required_fields=missing_required,
            unknown_fields=unknown_fields,
            suggestions=suggestions,
            validated_mapping=request.proposed_mapping if is_valid else {}
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la validation du mapping: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la validation: {str(e)}"
        )

@router.post(
    "/csv",
    response_model=ImportResponse,
    summary="Importer un fichier CSV",
    description="Importer des appareils et IMEI depuis un fichier CSV. Format attendu : marque,modele,imei1,imei2,statut (active/suspect/bloque). Les numéros de série (SNR) sont extraits automatiquement des IMEI (positions 9-14)."
)
async def import_csv(
    file: UploadFile = File(..., description="Sélectionner un fichier CSV depuis votre appareil"),
    blacklist_only: bool = Form(False, description="Marquer tous les appareils comme blacklistés"),
    assign_to_user: Optional[str] = Form(None, description="ID utilisateur pour assigner les appareils"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """Importer des appareils depuis un fichier CSV"""
    try:
        # Double vérification - s'assurer que l'utilisateur est admin
        if current_user.type_utilisateur != "administrateur":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilèges administrateur requis pour l'import de données"
            )
        
        start_time = time.time()
        
        # Vérifier l'extension du fichier
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nom de fichier requis"
            )
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['csv', 'txt']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de fichier non supporté. Utilisez CSV ou TXT."
            )
        
        # Lire le contenu du fichier
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        import_service = ImportService(db)
        
        # Configuration
        config = ImportConfigRequest()
        config.blacklist_only = blacklist_only
        
        # Traiter l'import
        results = import_service.process_csv_import(
            csv_content=csv_content,
            custom_mapping=config.column_mapping,
            blacklist_only=config.blacklist_only,
            user_id=assign_to_user or str(current_user.id)
        )
        
        processing_time = time.time() - start_time
        
        # Déterminer le succès
        success = len(results.get('errors', [])) == 0
        
        # Créer le résumé
        summary = ImportResultSummary(
            total_rows=results.get('total_rows', 0),
            processed=results.get('processed', 0),
            appareils_created=results.get('appareils_created', 0),
            imeis_created=results.get('imeis_created', 0),
            errors_count=len(results.get('errors', [])),
            warnings_count=len(results.get('warnings', []))
        )
        
        # Message de résultat
        if success:
            message = f"Import CSV réussi : {summary.appareils_created} appareils et {summary.imeis_created} IMEI importés avec extraction automatique des numéros de série"
        else:
            message = f"Import CSV partiellement réussi avec {summary.errors_count} erreurs"
        
        return ImportResponse(
            success=success,
            message=message,
            summary=summary,
            column_mapping_used=results.get('column_mapping_used', {}),
            errors=results.get('errors', []),
            warnings=results.get('warnings', []),
            import_id=str(uuid.uuid4()),
            processing_time_seconds=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'import CSV: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import CSV: {str(e)}"
        )

@router.post(
    "/json", 
    response_model=ImportResponse,
    summary="Importer un fichier JSON",
    description="Importer des appareils et IMEI depuis un fichier JSON. Les numéros de série (SNR) sont extraits automatiquement des IMEI (positions 9-14)."
)
async def import_json(
    file: UploadFile = File(..., description="Sélectionner un fichier JSON depuis votre appareil"),
    blacklist_only: bool = Form(False, description="Marquer tous les appareils comme blacklistés"),
    assign_to_user: Optional[str] = Form(None, description="ID utilisateur pour assigner les appareils"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """Importer des appareils depuis un fichier JSON"""
    try:
        # Double vérification - s'assurer que l'utilisateur est admin
        if current_user.type_utilisateur != "administrateur":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilèges administrateur requis pour l'import de données"
            )
        
        start_time = time.time()
        
        # Vérifier l'extension du fichier
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nom de fichier requis"
            )
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['json']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de fichier non supporté. Utilisez JSON."
            )
        
        # Lire le contenu du fichier
        content = await file.read()
        json_content = content.decode('utf-8')
        
        import_service = ImportService(db)
        
        # Configuration
        config = ImportConfigRequest()
        config.blacklist_only = blacklist_only
        
        # Traiter l'import
        results = import_service.process_json_import(
            json_content=json_content,
            custom_mapping=config.column_mapping,
            blacklist_only=config.blacklist_only,
            user_id=assign_to_user or str(current_user.id)
        )
        
        processing_time = time.time() - start_time
        
        # Déterminer le succès
        success = len(results.get('errors', [])) == 0
        
        # Créer le résumé
        summary = ImportResultSummary(
            total_rows=results.get('total_rows', 0),
            processed=results.get('processed', 0),
            appareils_created=results.get('appareils_created', 0),
            imeis_created=results.get('imeis_created', 0),
            errors_count=len(results.get('errors', [])),
            warnings_count=len(results.get('warnings', []))
        )
        
        # Message de résultat
        if success:
            message = f"Import JSON réussi : {summary.appareils_created} appareils et {summary.imeis_created} IMEI importés avec extraction automatique des numéros de série"
        else:
            message = f"Import JSON partiellement réussi avec {summary.errors_count} erreurs"
        
        return ImportResponse(
            success=success,
            message=message,
            summary=summary,
            column_mapping_used=results.get('column_mapping_used', {}),
            errors=results.get('errors', []),
            warnings=results.get('warnings', []),
            import_id=str(uuid.uuid4()),
            processing_time_seconds=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'import JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import JSON: {str(e)}"
        )

@router.post(
    "/upload",
    response_model=ImportResponse,
    summary="Uploader et importer un fichier",
    description="Uploader un fichier CSV ou JSON depuis votre appareil et l'importer directement. Les numéros de série (SNR) sont extraits automatiquement des IMEI."
)
async def import_file_upload(
    file: UploadFile = File(..., description="Fichier CSV ou JSON à importer"),
    blacklist_only: bool = Form(False, description="Marquer tous les appareils comme blacklistés"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """Importer un fichier uploadé"""
    try:
        # Double vérification - s'assurer que l'utilisateur est admin
        if current_user.type_utilisateur != "administrateur":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilèges administrateur requis pour l'import de données"
            )
        
        start_time = time.time()
        
        # Vérifier l'extension du fichier
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nom de fichier requis"
            )
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['csv', 'json', 'txt']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de fichier non supporté. Utilisez CSV, JSON ou TXT."
            )
        
        # Lire le contenu du fichier
        content = await file.read()
        file_content = content.decode('utf-8')
        
        # Configuration par défaut simplifiée
        import_config = ImportConfigRequest()
        import_config.blacklist_only = blacklist_only
        
        # Déterminer le type de fichier et traiter
        import_service = ImportService(db)
        
        if file_extension in ['csv', 'txt']:
            results = import_service.process_csv_import(
                csv_content=file_content,
                custom_mapping=import_config.column_mapping,
                blacklist_only=import_config.blacklist_only,
                user_id=str(current_user.id)
            )
        else:  # json
            results = import_service.process_json_import(
                json_content=file_content,
                custom_mapping=import_config.column_mapping,
                blacklist_only=import_config.blacklist_only,
                user_id=str(current_user.id)
            )
        
        processing_time = time.time() - start_time
        
        # Déterminer le succès
        success = len(results.get('errors', [])) == 0
        
        # Créer le résumé
        summary = ImportResultSummary(
            total_rows=results.get('total_rows', 0),
            processed=results.get('processed', 0),
            appareils_created=results.get('appareils_created', 0),
            imeis_created=results.get('imeis_created', 0),
            errors_count=len(results.get('errors', [])),
            warnings_count=len(results.get('warnings', []))
        )
        
        # Message de résultat
        if success:
            message = f"Import du fichier '{file.filename}' réussi : {summary.appareils_created} appareils et {summary.imeis_created} IMEI importés avec SNR automatique"
        else:
            message = f"Import du fichier '{file.filename}' partiellement réussi avec {summary.errors_count} erreurs"
        
        return ImportResponse(
            success=success,
            message=message,
            summary=summary,
            column_mapping_used=results.get('column_mapping_used', {}),
            errors=results.get('errors', []),
            warnings=results.get('warnings', []),
            import_id=str(uuid.uuid4()),
            processing_time_seconds=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de l'import de fichier: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import de fichier: {str(e)}"
        )

def _get_field_description(field: str) -> str:
    """Retourne la description d'un champ de base de données"""
    descriptions = {
        'marque': 'Marque/fabricant de l\'appareil (Samsung, Apple, etc.)',
        'modele': 'Modèle de l\'appareil (Galaxy S21, iPhone 13, etc.)',
        'emmc': 'Capacité de stockage (128GB, 256GB, etc.)',
        'imei1': 'IMEI principal (15 chiffres) - Le SNR sera extrait automatiquement',
        'imei2': 'IMEI secondaire pour dual-SIM (15 chiffres) - Le SNR sera extrait automatiquement',
        'utilisateur_id': 'ID de l\'utilisateur propriétaire (UUID)',
        'statut': 'Statut de l\'appareil (active, suspect, bloque)',
        'numero_serie': 'Numéro de série (extrait automatiquement de l\'IMEI positions 9-14)'
    }
    return descriptions.get(field, f'Champ {field}')

@router.post(
    "/simple-upload",
    response_model=ImportResponse,
    summary="Upload simple de fichier",
    description="Uploader simplement un fichier CSV ou JSON et l'importer. Extraction automatique des numéros de série depuis les IMEI. Idéal pour utilisation mobile."
)
async def simple_file_upload(
    file: UploadFile = File(..., description="Sélectionner un fichier CSV ou JSON depuis votre appareil"),
    force_status: Optional[str] = Form(None, description="Forcer un statut pour tous les appareils (active/suspect/bloque)"),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_admin_user)
):
    """Upload et import simple d'un fichier"""
    try:
        if current_user.type_utilisateur != "administrateur":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privilèges administrateur requis pour l'import"
            )
        
        # Vérifier l'extension du fichier
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Veuillez sélectionner un fichier"
            )
        
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['csv', 'json']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de fichier non supporté. Utilisez CSV ou JSON seulement."
            )
        
        # Lire le contenu
        content = await file.read()
        file_content = content.decode('utf-8')
        
        # Traitement simple
        import_service = ImportService(db)
        start_time = time.time()
        
        # Déterminer si on force un statut particulier
        blacklist_only = False
        if force_status and force_status.lower() in ['bloque', 'blocked', 'blacklisted']:
            blacklist_only = True
        
        if file_extension == 'csv':
            results = import_service.process_csv_import(
                csv_content=file_content,
                custom_mapping=None,  # Mapping automatique
                blacklist_only=blacklist_only,
                user_id=str(current_user.id)
            )
        else:  # json
            results = import_service.process_json_import(
                json_content=file_content,
                custom_mapping=None,  # Mapping automatique
                blacklist_only=blacklist_only,
                user_id=str(current_user.id)
            )
        
        processing_time = time.time() - start_time
        success = len(results.get('errors', [])) == 0
        
        summary = ImportResultSummary(
            total_rows=results.get('total_rows', 0),
            processed=results.get('processed', 0),
            appareils_created=results.get('appareils_created', 0),
            imeis_created=results.get('imeis_created', 0),
            errors_count=len(results.get('errors', [])),
            warnings_count=len(results.get('warnings', []))
        )
        
        if success:
            message = f"✅ Import réussi : {summary.appareils_created} appareils importés avec SNR automatique"
        else:
            message = f"⚠️ Import avec {summary.errors_count} erreurs"
        
        return ImportResponse(
            success=success,
            message=message,
            summary=summary,
            column_mapping_used=results.get('column_mapping_used', {}),
            errors=results.get('errors', []),
            warnings=results.get('warnings', []),
            import_id=str(uuid.uuid4()),
            processing_time_seconds=round(processing_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Erreur upload simple: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'import: {str(e)}"
        )
