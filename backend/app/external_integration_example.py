"""
Exemple d'intégration des APIs externes dans main.py
Copiez ce code dans votre endpoint /imei/{imei}
"""

# Import à ajouter en haut de main.py
# from .services.external_imei_service import external_imei_service

# Modification de l'endpoint /imei/{imei}
@app.get("/imei/{imei}")
async def verifier_imei(
    imei: str,
    request: Request,
    db: Session = Depends(get_db),
    user = Depends(get_current_user_optional),
    translator = Depends(get_current_translator),
    audit_service: AuditService = Depends(get_audit_service)
):
    # ... code existant pour vérifications d'accès ...
    
    # Search for IMEI in local database first
    imei_record = db.query(IMEI).filter(IMEI.numero_imei == imei).first()
    found = imei_record is not None
    
    # Log the search in Recherche table
    recherche = Recherche(
        id=uuid.uuid4(),
        date_recherche=datetime.now(),
        imei_recherche=imei,
        utilisateur_id=user.id if user else None
    )
    db.add(recherche)
    
    if imei_record:
        # IMEI trouvé localement - code existant
        appareil = imei_record.appareil
        
        response_data = {
            "id": str(imei_record.id),
            "imei": imei,
            "trouve": True,
            "statut": imei_record.statut,
            "source": "local_database",
            "appareil": {
                "marque": appareil.marque,
                "modele": appareil.modele
            },
            "recherche_enregistree": True,
            "id_recherche": str(recherche.id)
        }
        
        db.commit()
        return response_data
    
    else:
        # IMEI non trouvé localement - chercher via APIs externes
        try:
            external_result = await external_imei_service.check_imei_external(imei)
            
            if external_result.get('status') == 'found':
                # IMEI trouvé via API externe
                
                # Optionnel: sauvegarder en base locale pour cache permanent
                if external_result.get('source') != 'local_tac_database':
                    # Créer un nouvel appareil en base
                    new_appareil = Appareil(
                        id=uuid.uuid4(),
                        marque=external_result.get('brand', 'Unknown'),
                        modele=external_result.get('model', 'Unknown'),
                        emmc=None,
                        utilisateur_id=None
                    )
                    db.add(new_appareil)
                    db.flush()
                    
                    # Créer l'IMEI associé
                    new_imei = IMEI(
                        id=uuid.uuid4(),
                        numero_imei=imei,
                        numero_slot=1,
                        statut='active',
                        appareil_id=new_appareil.id
                    )
                    db.add(new_imei)
                
                db.commit()
                
                return {
                    "id": str(new_imei.id) if 'new_imei' in locals() else None,
                    "imei": imei,
                    "trouve": True,
                    "statut": external_result.get('device_status', 'active'),
                    "source": "external_api",
                    "provider_used": external_result.get('provider_used'),
                    "cache_hit": external_result.get('cache_hit', False),
                    "appareil": {
                        "marque": external_result.get('brand', 'Unknown'),
                        "modele": external_result.get('model', 'Unknown')
                    },
                    "external_data": external_result,
                    "recherche_enregistree": True,
                    "id_recherche": str(recherche.id)
                }
            
        except Exception as e:
            logger.error(f"Erreur APIs externes pour IMEI {imei}: {e}")
        
        # IMEI non trouvé nulle part
        db.commit()
        
        return {
            "imei": imei,
            "trouve": False,
            "source": "not_found",
            "message": translator.translate("erreur_imei_non_trouve"),
            "recherche_enregistree": True,
            "id_recherche": str(recherche.id)
        }
