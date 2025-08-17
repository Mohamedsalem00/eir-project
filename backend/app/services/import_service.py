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
import chardet

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
        Traite l'importation depuis un fichier CSV avec détection des doublons
        sur IMEI et numéro de série (SNR) extrait de l'IMEI.

        Args:
            csv_content: Contenu du fichier CSV
            custom_mapping: Mapping personnalisé des colonnes
            blacklist_only: Si True, marque tous les appareils comme blacklistés
            user_id: ID de l'utilisateur qui fait l'import

        Returns:
            Résultats de l'importation
        """
        try:
            # ===== 1. Détection intelligente du format CSV (encodage & délimiteur) =====
            try:
                # Tenter de décoder en UTF-8, la norme la plus courante
                decoded_content = csv_content
            except UnicodeDecodeError:
                # Si UTF-8 échoue, utiliser chardet pour une détection plus robuste
                raw_bytes = csv_content.encode('latin1') # Encoder dans un format sûr pour la détection
                detected = chardet.detect(raw_bytes)
                encoding = detected.get('encoding') or 'utf-8'
                decoded_content = raw_bytes.decode(encoding, errors='replace')
            
            sample = decoded_content[:2048]
            try:
                delimiter = csv.Sniffer().sniff(sample).delimiter
            except csv.Error:
                delimiter = ',' # Par défaut à la virgule si la détection échoue

            # ===== 2. Lecture du CSV en DataFrame avec Pandas =====
            # Utiliser dtype=str pour s'assurer que les IMEI ne sont pas interprétés comme des nombres
            df = pd.read_csv(io.StringIO(decoded_content), delimiter=delimiter, dtype=str, keep_default_na=False)

            if df.empty:
                return {"success": False, "error": "Le fichier CSV est vide ou n'a pas pu être lu."}

            # ===== 3. Mapping et validation des colonnes =====
            headers = df.columns.tolist()
            column_mapping = self.detect_column_mapping(headers, custom_mapping)

            # Vérifier que les colonnes essentielles sont présentes
            required_keys = ['marque', 'modele', 'imei1']
            if not all(key in column_mapping for key in required_keys):
                missing = [key for key in required_keys if key not in column_mapping]
                return {
                    "success": False, 
                    "error": f"Colonnes essentielles manquantes dans le fichier CSV. Impossible de trouver des correspondances pour : {', '.join(missing)}. Assurez-vous que les en-têtes sont corrects (ex: 'manufacturer', 'model', 'imei')."
                }

            # ===== 4. Chargement des données existantes en cache pour l'optimisation =====
            existing_imeis = {res[0] for res in self.db.query(IMEI.numero_imei).all()}
            existing_snrs = {res[0] for res in self.db.query(Appareil.numero_serie).filter(Appareil.numero_serie.isnot(None)).all()}
            
            logger.info(f"Cache chargé: {len(existing_imeis)} IMEI et {len(existing_snrs)} numéros de série existants.")

            results = {
                "total_rows": len(df),
                "processed": 0,
                "appareils_created": 0,
                "imeis_created": 0,
                "errors": [],
                "warnings": [],
                "column_mapping_used": column_mapping
            }

            # ===== 5. Traitement de chaque ligne du fichier CSV =====
            for index, row in df.iterrows():
                try:
                    # Extraire les données en utilisant le mapping détecté
                    imei_val = row.get(column_mapping['imei1'], '').strip()
                    marque = row.get(column_mapping['marque'], 'Inconnue').strip()
                    modele = row.get(column_mapping['modele'], 'Inconnu').strip()
                    statut_input = row.get(column_mapping.get('statut'), 'active').strip()
                    
                    # Validation de base
                    if not imei_val or len(imei_val) < 14:
                        results["warnings"].append(f"Ligne {index + 2}: IMEI manquant ou invalide, ligne ignorée.")
                        continue

                    # Extraire le numéro de série (SNR) de l'IMEI (positions 9-14)
                    snr = imei_val[8:14]

                    # ===== VÉRIFICATIONS DES DOUBLONS =====
                    if imei_val in existing_imeis:
                        results["warnings"].append(f"Ligne {index + 2}: L'IMEI '{imei_val}' existe déjà, ignoré.")
                        continue
                    
                    if snr in existing_snrs:
                        results["warnings"].append(f"Ligne {index + 2}: Un appareil avec le numéro de série '{snr}' existe déjà, ignoré.")
                        continue

                    # ===== Création des objets Appareil et IMEI =====
                    # Mapper le statut
                    db_status = self.map_status_to_db(statut_input, blacklist_only)
                    
                    # Créer le nouvel appareil
                    new_appareil = Appareil(
                        marque=marque,
                        modele=modele,
                        numero_serie=snr,
                        utilisateur_id=user_id
                    )
                    
                    # Créer le nouvel IMEI et l'associer à l'appareil
                    new_imei = IMEI(
                        numero_imei=imei_val,
                        statut=db_status,
                        appareil=new_appareil
                    )

                    self.db.add(new_appareil) # SQLAlchemy gère l'ajout de new_imei via la relation
                    
                    # Mettre à jour les caches pour détecter les doublons au sein du même fichier
                    existing_imeis.add(imei_val)
                    existing_snrs.add(snr)
                    
                    # Mettre à jour les statistiques
                    results["processed"] += 1
                    results["appareils_created"] += 1
                    results["imeis_created"] += 1

                except Exception as e:
                    error_msg = f"Ligne {index + 2}: Une erreur inattendue est survenue - {str(e) or 'Erreur non spécifiée'}"
                    results["errors"].append(error_msg)
                    logger.error(f"Erreur de traitement à la ligne {index + 2}: {e}", exc_info=True)

            # ===== 6. Commit ou Rollback de la transaction =====
            if not results["errors"]:
                self.db.commit()
                self._log_import_audit(user_id, "CSV", results)
            else:
                self.db.rollback()

            return results

        except pd.errors.ParserError as e:
            self.db.rollback()
            logger.error(f"Erreur de parsing CSV: {e}")
            return {"success": False, "error": f"Le fichier CSV est mal formaté. Vérifiez les délimiteurs et les guillemets. Détail: {e}"}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur critique lors de l'importation CSV: {e}", exc_info=True)
            return {"success": False, "error": f"Une erreur critique est survenue: {str(e)}"}

    
    def process_json_import(self, 
                        json_content: str, 
                        custom_mapping: Optional[Dict] = None,
                        blacklist_only: bool = False,
                        user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Traite l'importation depuis un fichier JSON avec détection des doublons
        sur IMEI et numéro de série (SNR) extrait de l'IMEI.

        Args:
            json_content: Contenu du fichier JSON
            custom_mapping: Mapping personnalisé des colonnes
            blacklist_only: Si True, marque tous les appareils comme blacklistés
            user_id: ID de l'utilisateur qui fait l'import
            
        Returns:
            Résultats de l'importation
        """
        try:
            # ===== 1. Chargement et validation du JSON =====
            data = json.loads(json_content)
            
            # Déterminer la liste des enregistrements (appareils)
            if isinstance(data, dict):
                # Accepte les formats comme {"data": [...]}, {"devices": [...]}, etc.
                for key in ['data', 'devices', 'appareils', 'records']:
                    if key in data and isinstance(data[key], list):
                        records = data[key]
                        break
                else:
                    # Si aucune clé standard n'est trouvée, considérer le dictionnaire comme un seul enregistrement
                    records = [data]
            elif isinstance(data, list):
                records = data
            else:
                return {"success": False, "error": "Format JSON non supporté. Attendu: une liste d'objets ou un objet contenant une liste."}
            
            if not records:
                return {"success": False, "error": "Aucun enregistrement (appareil) trouvé dans le fichier JSON."}

            # ===== 2. Mapping et validation des colonnes (clés JSON) =====
            headers = list(records[0].keys())
            column_mapping = self.detect_column_mapping(headers, custom_mapping)
            
            required_keys = ['marque', 'modele', 'imei1']
            if not all(key in column_mapping for key in required_keys):
                missing = [key for key in required_keys if key not in column_mapping]
                return {
                    "success": False, 
                    "error": f"Clés essentielles manquantes dans le JSON. Impossible de trouver des correspondances pour : {', '.join(missing)}. Assurez-vous que les clés sont correctes (ex: 'manufacturer', 'model', 'imei')."
                }

            # ===== 3. Chargement des données existantes en cache pour l'optimisation =====
            existing_imeis = {res[0] for res in self.db.query(IMEI.numero_imei).all()}
            existing_snrs = {res[0] for res in self.db.query(Appareil.numero_serie).filter(Appareil.numero_serie.isnot(None)).all()}
            
            logger.info(f"Cache chargé: {len(existing_imeis)} IMEI et {len(existing_snrs)} numéros de série existants.")
            
            results = {
                "total_rows": len(records),
                "processed": 0,
                "appareils_created": 0,
                "imeis_created": 0,
                "errors": [],
                "warnings": [],
                "column_mapping_used": column_mapping
            }

            # ===== 4. Traitement de chaque enregistrement JSON =====
            for index, record in enumerate(records):
                try:
                    # Extraire les données en utilisant le mapping
                    imei_val = str(record.get(column_mapping['imei1'], '')).strip()
                    marque = str(record.get(column_mapping['marque'], 'Inconnue')).strip()
                    modele = str(record.get(column_mapping['modele'], 'Inconnu')).strip()
                    statut_input = str(record.get(column_mapping.get('statut'), 'active')).strip()
                    
                    if not imei_val or len(imei_val) < 14:
                        results["warnings"].append(f"Enregistrement {index + 1}: IMEI manquant ou invalide, ignoré.")
                        continue
                    
                    # Extraire le numéro de série (SNR) de l'IMEI
                    snr = imei_val[8:14]

                    # ===== VÉRIFICATIONS DES DOUBLONS =====
                    if imei_val in existing_imeis:
                        results["warnings"].append(f"Enregistrement {index + 1}: L'IMEI '{imei_val}' existe déjà, ignoré.")
                        continue
                    
                    if snr in existing_snrs:
                        results["warnings"].append(f"Enregistrement {index + 1}: Un appareil avec le numéro de série '{snr}' existe déjà, ignoré.")
                        continue

                    # ===== Création des objets Appareil et IMEI =====
                    db_status = self.map_status_to_db(statut_input, blacklist_only)
                    
                    new_appareil = Appareil(
                        marque=marque,
                        modele=modele,
                        numero_serie=snr,
                        utilisateur_id=user_id
                    )
                    
                    new_imei = IMEI(
                        numero_imei=imei_val,
                        statut=db_status,
                        appareil=new_appareil
                    )
                    
                    self.db.add(new_appareil)
                    
                    # Mettre à jour les caches pour éviter les doublons dans le même fichier
                    existing_imeis.add(imei_val)
                    existing_snrs.add(snr)
                    
                    # Mettre à jour les statistiques
                    results["processed"] += 1
                    results["appareils_created"] += 1
                    results["imeis_created"] += 1

                except Exception as e:
                    error_msg = f"Enregistrement {index + 1}: Erreur - {str(e)}"
                    results["errors"].append(error_msg)
                    logger.error(f"Erreur de traitement de l'enregistrement {index + 1}: {e}", exc_info=True)

            # ===== 5. Commit ou Rollback de la transaction =====
            if not results["errors"]:
                self.db.commit()
                self._log_import_audit(user_id, "JSON", results)
            else:
                self.db.rollback()
                
            return results

        except json.JSONDecodeError as e:
            self.db.rollback()
            return {"success": False, "error": f"Erreur de format JSON: Le fichier n'est pas un JSON valide. Détail: {e}"}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Erreur critique lors de l'importation JSON: {e}", exc_info=True)
            return {"success": False, "error": f"Une erreur critique est survenue: {str(e)}"}
    
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
                                        existing_imeis: set) -> Dict[str, Any]:
        """
        Version optimisée qui utilise des caches en mémoire au lieu de requêtes SQL
        Chaque appareil est maintenant créé de façon unique grâce au numero_serie
        
        Args:
            row: Données de la ligne
            column_mapping: Mapping des colonnes
            blacklist_only: Si True, marque comme blacklisté
            user_id: ID de l'utilisateur
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
        
        # Créer un nouvel appareil (pas de vérification de duplication, le SNR assure l'unicité)
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
