"""
Service d'importation pour les appareils et IMEI en blacklist
Supporte les formats CSV et JSON avec mapping de colonnes flexible
"""

import csv
import json
import io
import uuid
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import pandas as pd
import logging

from ..models.appareil import Appareil
from ..models.imei import IMEI
from ..models.utilisateur import Utilisateur
from ..models.journal_audit import JournalAudit

logger = logging.getLogger(__name__)

class ImportService:
    """Service pour l'importation d'appareils et IMEI"""
    
    # Mapping par défaut des colonnes
    DEFAULT_COLUMN_MAPPING = {
        # Champs appareil
        'marque': ['marque', 'brand', 'manufacturer', 'fabricant', 'marca'],
        'modele': ['modele', 'model', 'modelo', 'modèle', 'device_model'],
        'emmc': ['emmc', 'storage', 'capacity', 'capacité', 'memoire', 'memory'],
        
        # Champs IMEI
        'imei1': ['imei1', 'imei_1', 'imei', 'primary_imei', 'imei_principal', 'main_imei', 'numero_imei'],
        'imei2': ['imei2', 'imei_2', 'secondary_imei', 'imei_secondaire', 'second_imei'],
        
        # Champs utilisateur
        'utilisateur_id': ['utilisateur_id', 'user_id', 'customer_id', 'assigned_to', 'owner_id'],
        
        # Champs de statut pour blacklist
        'statut': ['statut', 'status', 'estado', 'état', 'device_status']
    }
    
    # Mapping des statuts d'entrée vers les statuts de la base de données
    STATUS_MAPPING = {
        # Statuts blacklist/blocked -> bloque
        'blacklisted': 'bloque',
        'blocked': 'bloque',
        'bloque': 'bloque',
        'blacklist': 'bloque',
        'banned': 'bloque',
        'interdite': 'bloque',
        
        # Statuts suspect/graylist -> suspect
        'suspect': 'suspect',
        'suspicious': 'suspect',
        'graylist': 'suspect',
        'graylisted': 'suspect',
        'warning': 'suspect',
        'attention': 'suspect',
        'douteux': 'suspect',
        
        # Statuts actif/whitelist -> active
        'active': 'active',
        'actif': 'active',
        'allowed': 'active',
        'autorise': 'active',
        'whitelist': 'active',
        'whitelisted': 'active',
        'valid': 'active',
        'valide': 'active',
        'ok': 'active',
        'clean': 'active'
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def map_status_to_db(self, input_status: str, blacklist_only: bool = False) -> str:
        """
        Mappe un statut d'entrée vers le statut correspondant dans la base de données.
        
        Args:
            input_status: Statut depuis le fichier d'import
            blacklist_only: Si True, force le statut vers 'bloque' par défaut
            
        Returns:
            str: Statut compatible avec la base de données ('active', 'suspect', 'bloque')
        """
        if blacklist_only:
            return 'bloque'
        
        if not input_status:
            return 'active'  # Statut par défaut
        
        # Nettoyer et normaliser l'entrée
        clean_status = str(input_status).lower().strip()
        
        # Chercher dans le mapping
        mapped_status = self.STATUS_MAPPING.get(clean_status)
        
        if mapped_status:
            return mapped_status
        
        # Si pas trouvé, essayer de détecter par mots-clés
        if any(keyword in clean_status for keyword in ['black', 'block', 'ban', 'interdite']):
            return 'bloque'
        elif any(keyword in clean_status for keyword in ['suspect', 'gray', 'warning', 'attention']):
            return 'suspect'
        elif any(keyword in clean_status for keyword in ['active', 'white', 'allow', 'valid', 'ok']):
            return 'active'
        
        # Par défaut, retourner 'active' si on ne peut pas déterminer
        logger.warning(f"Statut inconnu '{input_status}', utilisation de 'active' par défaut")
        return 'active'
    
    def detect_column_mapping(self, headers: List[str], custom_mapping: Optional[Dict] = None) -> Dict[str, str]:
        """
        Détecte automatiquement le mapping des colonnes basé sur les en-têtes
        
        Args:
            headers: Liste des en-têtes du fichier
            custom_mapping: Mapping personnalisé fourni par l'utilisateur
            
        Returns:
            Dictionnaire de mapping {champ_db: nom_colonne_fichier}
        """
        mapping = {}
        headers_lower = [h.lower().strip() for h in headers]
        
        # Utiliser le mapping personnalisé en priorité
        if custom_mapping:
            for db_field, file_column in custom_mapping.items():
                if file_column in headers:
                    mapping[db_field] = file_column
        
        # Compléter avec la détection automatique
        for db_field, possible_names in self.DEFAULT_COLUMN_MAPPING.items():
            if db_field not in mapping:
                for possible_name in possible_names:
                    if possible_name.lower() in headers_lower:
                        original_header = headers[headers_lower.index(possible_name.lower())]
                        mapping[db_field] = original_header
                        break
        
        return mapping
    
    def validate_imei(self, imei: str) -> bool:
        """Valide un numéro IMEI avec l'algorithme de Luhn"""
        if not imei or not imei.isdigit():
            return False
        
        if len(imei) not in [14, 15]:
            return False
        
        # Algorithme de Luhn pour validation
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10
        
        return luhn_checksum(imei) == 0
    
    def process_csv_import(self, 
                          csv_content: str, 
                          custom_mapping: Optional[Dict] = None,
                          blacklist_only: bool = False,
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Traite l'importation depuis un fichier CSV
        
        Args:
            csv_content: Contenu du fichier CSV
            custom_mapping: Mapping personnalisé des colonnes
            blacklist_only: Si True, marque tous les appareils comme blacklistés
            user_id: ID de l'utilisateur qui fait l'import
            
        Returns:
            Résultats de l'importation
        """
        try:
            # Lecture du CSV avec pandas pour une meilleure gestion
            df = pd.read_csv(io.StringIO(csv_content))
            
            if df.empty:
                return {"success": False, "error": "Fichier CSV vide"}
            
            headers = df.columns.tolist()
            column_mapping = self.detect_column_mapping(headers, custom_mapping)
            
            # OPTIMISATION: Charger tous les appareils et IMEI existants en mémoire
            existing_appareils = {}  # {(marque, modele): appareil_obj}
            existing_imeis = set()   # {imei_numero}
            
            # Charger tous les appareils existants
            all_appareils = self.db.query(Appareil).all()
            for app in all_appareils:
                key = (app.marque, app.modele)
                existing_appareils[key] = app
            
            # Charger tous les IMEI existants
            all_imeis = self.db.query(IMEI.numero_imei).all()
            existing_imeis = {imei[0] for imei in all_imeis}
            
            logger.info(f"Cache chargé: {len(existing_appareils)} appareils, {len(existing_imeis)} IMEI")
            
            results = {
                "total_rows": len(df),
                "processed": 0,
                "appareils_created": 0,
                "imeis_created": 0,
                "errors": [],
                "warnings": [],
                "column_mapping_used": column_mapping
            }
            
            for index, row in df.iterrows():
                try:
                    result = self._process_single_record_optimized(
                        row, column_mapping, blacklist_only, user_id,
                        existing_appareils, existing_imeis
                    )
                    results["processed"] += 1
                    
                    if result.get("appareil_created"):
                        results["appareils_created"] += 1
                    
                    results["imeis_created"] += result.get("imeis_created", 0)
                    
                    if result.get("warnings"):
                        results["warnings"].extend(result["warnings"])
                        
                except Exception as e:
                    error_msg = f"Ligne {index + 2}: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(f"Erreur lors du traitement de la ligne {index + 2}: {e}")
            
            # Commit des changements si tout s'est bien passé
            if not results["errors"]:
                self.db.commit()
                self._log_import_audit(user_id, "CSV", results)
            else:
                self.db.rollback()
            
            return results
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur lors de l'importation CSV: {e}")
            return {"success": False, "error": f"Erreur lors de l'importation CSV: {str(e)}"}
    
    def process_json_import(self, 
                           json_content: str, 
                           custom_mapping: Optional[Dict] = None,
                           blacklist_only: bool = False,
                           user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Traite l'importation depuis un fichier JSON
        
        Args:
            json_content: Contenu du fichier JSON
            custom_mapping: Mapping personnalisé des colonnes
            blacklist_only: Si True, marque tous les appareils comme blacklistés
            user_id: ID de l'utilisateur qui fait l'import
            
        Returns:
            Résultats de l'importation
        """
        try:
            data = json.loads(json_content)
            
            # Support pour différents formats JSON
            if isinstance(data, dict):
                if 'data' in data:
                    records = data['data']
                elif 'devices' in data:
                    records = data['devices']
                elif 'appareils' in data:
                    records = data['appareils']
                else:
                    # Traiter le dict comme un seul enregistrement
                    records = [data]
            elif isinstance(data, list):
                records = data
            else:
                return {"success": False, "error": "Format JSON non supporté"}
            
            if not records:
                return {"success": False, "error": "Aucune donnée trouvée dans le JSON"}
            
            # Détecter le mapping basé sur le premier enregistrement
            if records:
                headers = list(records[0].keys())
                column_mapping = self.detect_column_mapping(headers, custom_mapping)
            
            # OPTIMISATION: Charger tous les appareils et IMEI existants en mémoire
            existing_appareils = {}  # {(marque, modele): appareil_obj}
            existing_imeis = set()   # {imei_numero}
            
            # Charger tous les appareils existants
            all_appareils = self.db.query(Appareil).all()
            for app in all_appareils:
                key = (app.marque, app.modele)
                existing_appareils[key] = app
            
            # Charger tous les IMEI existants
            all_imeis = self.db.query(IMEI.numero_imei).all()
            existing_imeis = {imei[0] for imei in all_imeis}
            
            logger.info(f"Cache chargé: {len(existing_appareils)} appareils, {len(existing_imeis)} IMEI")
            
            results = {
                "total_rows": len(records),
                "processed": 0,
                "appareils_created": 0,
                "imeis_created": 0,
                "errors": [],
                "warnings": [],
                "column_mapping_used": column_mapping
            }
            
            for index, record in enumerate(records):
                try:
                    # Convertir le dict en Series pour compatibilité
                    row = pd.Series(record)
                    result = self._process_single_record_optimized(
                        row, column_mapping, blacklist_only, user_id,
                        existing_appareils, existing_imeis
                    )
                    results["processed"] += 1
                    
                    if result.get("appareil_created"):
                        results["appareils_created"] += 1
                    
                    results["imeis_created"] += result.get("imeis_created", 0)
                    
                    if result.get("warnings"):
                        results["warnings"].extend(result["warnings"])
                        
                except Exception as e:
                    error_msg = f"Enregistrement {index + 1}: {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(f"Erreur lors du traitement de l'enregistrement {index + 1}: {e}")
            
            # Commit des changements si tout s'est bien passé
            if not results["errors"]:
                self.db.commit()
                self._log_import_audit(user_id, "JSON", results)
            else:
                self.db.rollback()
            
            return results
            
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Erreur de format JSON: {str(e)}"}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur lors de l'importation JSON: {e}")
            return {"success": False, "error": f"Erreur lors de l'importation JSON: {str(e)}"}
    
    def _process_single_record(self, 
                              row: pd.Series, 
                              column_mapping: Dict[str, str], 
                              blacklist_only: bool,
                              user_id: Optional[str]) -> Dict[str, Any]:
        """
        Traite un seul enregistrement d'appareil avec ses IMEI
        
        Args:
            row: Données de la ligne
            column_mapping: Mapping des colonnes
            blacklist_only: Si True, marque comme blacklisté
            user_id: ID de l'utilisateur
            
        Returns:
            Résultats du traitement
        """
        result = {
            "appareil_created": False,
            "imeis_created": 0,
            "warnings": []
        }
        
        # Extraire les données mappées
        appareil_data = {}
        for db_field in ['marque', 'modele', 'emmc']:
            if db_field in column_mapping and column_mapping[db_field] in row:
                value = row[column_mapping[db_field]]
                if pd.notna(value):
                    appareil_data[db_field] = str(value).strip()
        
        # Vérifier les champs obligatoires
        if not appareil_data.get('marque') or not appareil_data.get('modele'):
            raise ValueError("Marque et modèle sont obligatoires")
        
        # Récupérer l'utilisateur assigné
        assigned_user_id = None
        if 'utilisateur_id' in column_mapping and column_mapping['utilisateur_id'] in row:
            user_value = row[column_mapping['utilisateur_id']]
            if pd.notna(user_value):
                assigned_user_id = str(user_value).strip()
        
        # Vérifier si l'appareil existe déjà (même marque et modèle)
        existing_appareil = self.db.query(Appareil).filter(
            Appareil.marque == appareil_data['marque'],
            Appareil.modele == appareil_data['modele']
        ).first()
        
        if existing_appareil:
            # Utiliser l'appareil existant
            appareil = existing_appareil
            result["warnings"].append(f"Appareil {appareil_data['marque']} {appareil_data['modele']} existe déjà, réutilisation")
        else:
            # Créer un nouvel appareil
            appareil = Appareil(
                id=uuid.uuid4(),
                marque=appareil_data['marque'],
                modele=appareil_data['modele'],
                emmc=appareil_data.get('emmc'),
                utilisateur_id=assigned_user_id if assigned_user_id else user_id
            )
            
            self.db.add(appareil)
            result["appareil_created"] = True
        
        # Traiter les IMEI
        imeis_to_process = []
        
        # IMEI principal
        if 'imei1' in column_mapping and column_mapping['imei1'] in row:
            imei1 = row[column_mapping['imei1']]
            if pd.notna(imei1):
                imei1_str = str(imei1).strip()
                if imei1_str:
                    imeis_to_process.append((imei1_str, 1))
        
        # IMEI secondaire
        if 'imei2' in column_mapping and column_mapping['imei2'] in row:
            imei2 = row[column_mapping['imei2']]
            if pd.notna(imei2):
                imei2_str = str(imei2).strip()
                if imei2_str:
                    imeis_to_process.append((imei2_str, 2))
        
        # Déterminer le statut avec le nouveau mapping
        statut = self.map_status_to_db(None, blacklist_only)  # Statut par défaut
        
        if 'statut' in column_mapping and column_mapping['statut'] in row:
            status_value = row[column_mapping['statut']]
            if pd.notna(status_value):
                statut = self.map_status_to_db(str(status_value), blacklist_only)
        
        # Créer les IMEI - NOTE: Cette méthode non-optimisée utilise des requêtes SQL
        # Pour de meilleures performances, utilisez _process_single_record_optimized
        for imei_numero, slot in imeis_to_process:
            # Nettoyer l'IMEI
            imei_clean = ''.join(filter(str.isdigit, imei_numero))
            
            if not self.validate_imei(imei_clean):
                result["warnings"].append(f"IMEI invalide ignoré: {imei_numero}")
                continue
            
            # Vérifier si l'IMEI existe déjà (requête SQL - non optimisé)
            existing_imei = self.db.query(IMEI).filter(IMEI.numero_imei == imei_clean).first()
            if existing_imei:
                result["warnings"].append(f"IMEI {imei_clean} existe déjà, ignoré")
                continue
            
            # Créer l'IMEI
            imei_obj = IMEI(
                id=uuid.uuid4(),
                numero_imei=imei_clean,
                numero_slot=slot,
                statut=statut,
                appareil_id=appareil.id
            )
            
            self.db.add(imei_obj)
            result["imeis_created"] += 1
        
        return result
    
    def _process_single_record_optimized(self, 
                                        row: pd.Series, 
                                        column_mapping: Dict[str, str], 
                                        blacklist_only: bool,
                                        user_id: Optional[str],
                                        existing_appareils: Dict[Tuple[str, str], Appareil],
                                        existing_imeis: set) -> Dict[str, Any]:
        """
        Version optimisée qui utilise des caches en mémoire au lieu de requêtes SQL
        
        Args:
            row: Données de la ligne
            column_mapping: Mapping des colonnes
            blacklist_only: Si True, marque comme blacklisté
            user_id: ID de l'utilisateur
            existing_appareils: Cache des appareils existants {(marque, modele): appareil}
            existing_imeis: Cache des IMEI existants {imei_numero}
            
        Returns:
            Résultats du traitement
        """
        result = {
            "appareil_created": False,
            "imeis_created": 0,
            "warnings": []
        }
        
        # Extraire les données mappées
        appareil_data = {}
        for db_field in ['marque', 'modele', 'emmc']:
            if db_field in column_mapping and column_mapping[db_field] in row:
                value = row[column_mapping[db_field]]
                if pd.notna(value):
                    appareil_data[db_field] = str(value).strip()
        
        # Vérifier les champs obligatoires
        if not appareil_data.get('marque') or not appareil_data.get('modele'):
            raise ValueError("Marque et modèle sont obligatoires")
        
        # Récupérer l'utilisateur assigné
        assigned_user_id = None
        if 'utilisateur_id' in column_mapping and column_mapping['utilisateur_id'] in row:
            user_value = row[column_mapping['utilisateur_id']]
            if pd.notna(user_value):
                assigned_user_id = str(user_value).strip()
        
        # Vérifier si l'appareil existe déjà (vérification en mémoire)
        appareil_key = (appareil_data['marque'], appareil_data['modele'])
        if appareil_key in existing_appareils:
            # Utiliser l'appareil existant
            appareil = existing_appareils[appareil_key]
            result["warnings"].append(f"Appareil {appareil_data['marque']} {appareil_data['modele']} existe déjà, réutilisation")
        else:
            # Créer un nouvel appareil
            appareil = Appareil(
                id=uuid.uuid4(),
                marque=appareil_data['marque'],
                modele=appareil_data['modele'],
                emmc=appareil_data.get('emmc'),
                utilisateur_id=assigned_user_id if assigned_user_id else user_id
            )
            
            self.db.add(appareil)
            result["appareil_created"] = True
            
            # Ajouter au cache pour éviter les doublons dans le même batch
            existing_appareils[appareil_key] = appareil
        
        # Traiter les IMEI
        imeis_to_process = []
        
        # IMEI principal
        if 'imei1' in column_mapping and column_mapping['imei1'] in row:
            imei1 = row[column_mapping['imei1']]
            if pd.notna(imei1):
                imei1_str = str(imei1).strip()
                if imei1_str:
                    imeis_to_process.append((imei1_str, 1))
        
        # IMEI secondaire
        if 'imei2' in column_mapping and column_mapping['imei2'] in row:
            imei2 = row[column_mapping['imei2']]
            if pd.notna(imei2):
                imei2_str = str(imei2).strip()
                if imei2_str:
                    imeis_to_process.append((imei2_str, 2))
        
        # Déterminer le statut avec le nouveau mapping
        statut = self.map_status_to_db(None, blacklist_only)  # Statut par défaut
        
        if 'statut' in column_mapping and column_mapping['statut'] in row:
            status_value = row[column_mapping['statut']]
            if pd.notna(status_value):
                statut = self.map_status_to_db(str(status_value), blacklist_only)
        
        # Créer les IMEI
        for imei_numero, slot in imeis_to_process:
            # Nettoyer l'IMEI
            imei_clean = ''.join(filter(str.isdigit, imei_numero))
            
            if not self.validate_imei(imei_clean):
                result["warnings"].append(f"IMEI invalide ignoré: {imei_numero}")
                continue
            
            # Vérifier si l'IMEI existe déjà (vérification en mémoire)
            if imei_clean in existing_imeis:
                result["warnings"].append(f"IMEI {imei_clean} existe déjà, ignoré")
                continue
            
            # Créer l'IMEI
            imei_obj = IMEI(
                id=uuid.uuid4(),
                numero_imei=imei_clean,
                numero_slot=slot,
                statut=statut,
                appareil_id=appareil.id
            )
            
            self.db.add(imei_obj)
            result["imeis_created"] += 1
            
            # Ajouter au cache pour éviter les doublons dans le même batch
            existing_imeis.add(imei_clean)
        
        return result
    
    def _log_import_audit(self, user_id: Optional[str], import_type: str, results: Dict):
        """Enregistre l'opération d'import dans le journal d'audit"""
        try:
            if user_id:
                audit_entry = JournalAudit(
                    id=uuid.uuid4(),
                    utilisateur_id=user_id,
                    action=f"IMPORT_{import_type}",
                    date=datetime.utcnow()
                )
                # Note: Le modèle JournalAudit pourrait avoir besoin d'un champ 'details' pour stocker les résultats
                self.db.add(audit_entry)
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'audit: {e}")
    
    def get_column_mapping_suggestions(self, headers: List[str]) -> Dict[str, List[str]]:
        """
        Retourne des suggestions de mapping basées sur les en-têtes fournis
        
        Args:
            headers: Liste des en-têtes du fichier
            
        Returns:
            Dictionnaire avec suggestions de mapping
        """
        suggestions = {}
        headers_lower = [h.lower().strip() for h in headers]
        
        for db_field, possible_names in self.DEFAULT_COLUMN_MAPPING.items():
            matches = []
            for header in headers:
                if header.lower() in possible_names:
                    matches.append(header)
            
            # Recherche partielle pour des correspondances proches
            if not matches:
                for header in headers:
                    for possible_name in possible_names:
                        if possible_name in header.lower() or header.lower() in possible_name:
                            matches.append(header)
                            break
            
            if matches:
                suggestions[db_field] = matches
        
        return suggestions
    
    def _analyze_csv_preview(self, 
                            csv_content: str, 
                            custom_mapping: Optional[Dict] = None, 
                            preview_rows: int = 5) -> Dict[str, Any]:
        """
        Analyse un CSV pour prévisualisation
        
        Args:
            csv_content: Contenu du CSV
            custom_mapping: Mapping personnalisé
            preview_rows: Nombre de lignes à prévisualiser
            
        Returns:
            Résultats de l'analyse
        """
        try:
            # Lecture du CSV
            df = pd.read_csv(io.StringIO(csv_content))
            
            if df.empty:
                return {
                    "success": False,
                    "file_type": "csv",
                    "errors": ["Fichier CSV vide"],
                    "total_rows": 0,
                    "headers": [],
                    "column_mapping_suggestions": [],
                    "detected_mapping": {},
                    "preview_data": []
                }
            
            headers = df.columns.tolist()
            detected_mapping = self.detect_column_mapping(headers, custom_mapping)
            
            # Créer les suggestions de mapping
            suggestions_dict = self.get_column_mapping_suggestions(headers)
            suggestions = []
            
            required_fields = ['marque', 'modele']
            for db_field, matches in suggestions_dict.items():
                if matches:
                    suggestions.append({
                        "db_field": db_field,
                        "suggested_columns": matches,
                        "is_required": db_field in required_fields,
                        "description": _get_field_description_service(db_field)
                    })
            
            # Prévisualisation des données
            preview_data = []
            for _, row in df.head(preview_rows).iterrows():
                row_dict = {}
                for col in headers:
                    value = row[col]
                    if pd.notna(value):
                        row_dict[col] = str(value)
                    else:
                        row_dict[col] = None
                preview_data.append(row_dict)
            
            # Validation préliminaire
            errors = []
            warnings = []
            
            # Vérifier les champs obligatoires dans le mapping détecté
            for required_field in required_fields:
                if required_field not in detected_mapping:
                    errors.append(f"Champ obligatoire '{required_field}' non détecté")
            
            # Vérifier les IMEI dans l'échantillon
            imei_fields = ['imei1', 'imei2']
            for imei_field in imei_fields:
                if imei_field in detected_mapping:
                    col_name = detected_mapping[imei_field]
                    if col_name in df.columns:
                        for _, row in df.head(preview_rows).iterrows():
                            imei_value = row[col_name]
                            if pd.notna(imei_value):
                                imei_str = str(imei_value).strip()
                                if imei_str and not self.validate_imei(imei_str):
                                    warnings.append(f"IMEI potentiellement invalide détecté: {imei_str}")
            
            return {
                "success": True,
                "file_type": "csv",
                "total_rows": len(df),
                "headers": headers,
                "column_mapping_suggestions": suggestions,
                "detected_mapping": detected_mapping,
                "preview_data": preview_data,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            return {
                "success": False,
                "file_type": "csv",
                "errors": [f"Erreur lors de l'analyse CSV: {str(e)}"],
                "total_rows": 0,
                "headers": [],
                "column_mapping_suggestions": [],
                "detected_mapping": {},
                "preview_data": []
            }
    
    def _analyze_json_preview(self, 
                             json_content: str, 
                             custom_mapping: Optional[Dict] = None, 
                             preview_rows: int = 5) -> Dict[str, Any]:
        """
        Analyse un JSON pour prévisualisation
        
        Args:
            json_content: Contenu du JSON
            custom_mapping: Mapping personnalisé
            preview_rows: Nombre de lignes à prévisualiser
            
        Returns:
            Résultats de l'analyse
        """
        try:
            data = json.loads(json_content)
            
            # Support pour différents formats JSON
            if isinstance(data, dict):
                if 'data' in data:
                    records = data['data']
                elif 'devices' in data:
                    records = data['devices']
                elif 'appareils' in data:
                    records = data['appareils']
                else:
                    records = [data]
            elif isinstance(data, list):
                records = data
            else:
                return {
                    "success": False,
                    "file_type": "json",
                    "errors": ["Format JSON non supporté"],
                    "total_rows": 0,
                    "headers": [],
                    "column_mapping_suggestions": [],
                    "detected_mapping": {},
                    "preview_data": []
                }
            
            if not records:
                return {
                    "success": False,
                    "file_type": "json",
                    "errors": ["Aucune donnée trouvée dans le JSON"],
                    "total_rows": 0,
                    "headers": [],
                    "column_mapping_suggestions": [],
                    "detected_mapping": {},
                    "preview_data": []
                }
            
            # Extraire les en-têtes du premier enregistrement
            headers = list(records[0].keys()) if records else []
            detected_mapping = self.detect_column_mapping(headers, custom_mapping)
            
            # Créer les suggestions de mapping
            suggestions_dict = self.get_column_mapping_suggestions(headers)
            suggestions = []
            
            required_fields = ['marque', 'modele']
            for db_field, matches in suggestions_dict.items():
                if matches:
                    suggestions.append({
                        "db_field": db_field,
                        "suggested_columns": matches,
                        "is_required": db_field in required_fields,
                        "description": _get_field_description_service(db_field)
                    })
            
            # Prévisualisation des données
            preview_data = records[:preview_rows]
            
            # Validation préliminaire
            errors = []
            warnings = []
            
            # Vérifier les champs obligatoires
            for required_field in required_fields:
                if required_field not in detected_mapping:
                    errors.append(f"Champ obligatoire '{required_field}' non détecté")
            
            # Vérifier les IMEI dans l'échantillon
            imei_fields = ['imei1', 'imei2']
            for imei_field in imei_fields:
                if imei_field in detected_mapping:
                    col_name = detected_mapping[imei_field]
                    for record in preview_data:
                        if col_name in record and record[col_name]:
                            imei_str = str(record[col_name]).strip()
                            if imei_str and not self.validate_imei(imei_str):
                                warnings.append(f"IMEI potentiellement invalide détecté: {imei_str}")
            
            return {
                "success": True,
                "file_type": "json",
                "total_rows": len(records),
                "headers": headers,
                "column_mapping_suggestions": suggestions,
                "detected_mapping": detected_mapping,
                "preview_data": preview_data,
                "errors": errors,
                "warnings": warnings
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "file_type": "json",
                "errors": [f"Erreur de format JSON: {str(e)}"],
                "total_rows": 0,
                "headers": [],
                "column_mapping_suggestions": [],
                "detected_mapping": {},
                "preview_data": []
            }
        except Exception as e:
            return {
                "success": False,
                "file_type": "json",
                "errors": [f"Erreur lors de l'analyse JSON: {str(e)}"],
                "total_rows": 0,
                "headers": [],
                "column_mapping_suggestions": [],
                "detected_mapping": {},
                "preview_data": []
            }

def _get_field_description_service(field: str) -> str:
    """Retourne la description d'un champ de base de données"""
    descriptions = {
        'marque': 'Marque/fabricant de l\'appareil (Samsung, Apple, etc.)',
        'modele': 'Modèle de l\'appareil (Galaxy S21, iPhone 13, etc.)',
        'emmc': 'Capacité de stockage (128GB, 256GB, etc.)',
        'imei1': 'IMEI principal (14-15 chiffres)',
        'imei2': 'IMEI secondaire pour dual-SIM (14-15 chiffres)',
        'utilisateur_id': 'ID de l\'utilisateur propriétaire (UUID)',
        'statut': 'Statut de l\'appareil (active, blacklisted, etc.)'
    }
    return descriptions.get(field, f'Champ {field}')
