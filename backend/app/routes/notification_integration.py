"""
🔧 Intégration du nouveau système de templates de notifications
=============================================================

Ce fichier montre comment intégrer les nouveaux templates dans 
les routes existantes de votre application EIR Project.

Pour l'utiliser, importez les fonctions dans vos routes existantes.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from ..core.dependencies import get_db, get_current_user
from ..models.utilisateur import Utilisateur
from ..services.eir_notifications import (
    envoyer_notification_bienvenue,
    notifier_verification_imei,
    notifier_reset_password,
    notifier_alerte_securite
)
from ..templates.simple_notifications import (
    get_notification_template,
    render_notification,
    get_available_templates
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notification-templates", tags=["Templates de Notifications"])

@router.get("/test-bienvenue")
async def test_notification_bienvenue(
    current_user: Utilisateur = Depends(get_current_user)
):
    """🧪 Test de la notification de bienvenue avec les nouveaux templates"""
    try:
        result = await envoyer_notification_bienvenue(str(current_user.id))
        return {
            "message": "Test notification bienvenue envoyée",
            "result": result,
            "user": current_user.nom
        }
    except Exception as e:
        logger.error(f"Erreur test bienvenue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-verification-imei")
async def test_verification_imei(
    statut: str = "valide",  # valide, invalide, blackliste
    current_user: Utilisateur = Depends(get_current_user)
):
    """🧪 Test de notification de vérification IMEI"""
    try:
        # IMEI de test
        test_imei = "353260051234567"
        
        result = await notifier_verification_imei(
            user_id=str(current_user.id),
            imei=test_imei,
            statut=statut,
            marque="Samsung",
            modele="Galaxy S23",
            raison="Test de vérification" if statut != "valide" else ""
        )
        
        return {
            "message": f"Test notification vérification IMEI ({statut}) envoyée",
            "result": result,
            "imei": test_imei
        }
    except Exception as e:
        logger.error(f"Erreur test vérification IMEI: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-alerte-securite")
async def test_alerte_securite(
    current_user: Utilisateur = Depends(get_current_user)
):
    """🧪 Test d'alerte de sécurité"""
    try:
        details_connexion = {
            "date_connexion": "10/08/2025 à 14:30",
            "adresse_ip": "192.168.1.100",
            "localisation": "Casablanca, Maroc",
            "navigateur": "Chrome 115.0"
        }
        
        result = await notifier_alerte_securite(
            user_id=str(current_user.id),
            details_connexion=details_connexion
        )
        
        return {
            "message": "Test alerte sécurité envoyée",
            "result": result,
            "details": details_connexion
        }
    except Exception as e:
        logger.error(f"Erreur test alerte sécurité: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates-disponibles")
async def lister_templates_disponibles():
    """📋 Liste tous les templates de notifications disponibles"""
    try:
        templates = get_available_templates()
        
        # Enrichir avec des exemples de contenu
        detailed_templates = {}
        
        for notification_type, template_keys in templates.items():
            detailed_templates[notification_type] = {}
            
            for template_key in template_keys:
                template = get_notification_template(template_key, notification_type)
                if template:
                    detailed_templates[notification_type][template_key] = {
                        "nom": template_key,
                        "type": notification_type,
                        "sujet": template.get("subject", "N/A"),
                        "preview": template["content"][:100] + "..." if len(template["content"]) > 100 else template["content"],
                        "variables_detectees": _extract_variables(template["content"])
                    }
        
        return {
            "templates": detailed_templates,
            "total_templates": sum(len(templates) for templates in templates.values()),
            "types_supportes": list(templates.keys())
        }
        
    except Exception as e:
        logger.error(f"Erreur liste templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/template/{template_key}")
async def obtenir_template_details(
    template_key: str,
    notification_type: str = "email"
):
    """ℹ️ Détails d'un template spécifique"""
    try:
        template = get_notification_template(template_key, notification_type)
        
        if not template:
            raise HTTPException(
                status_code=404, 
                detail=f"Template '{template_key}' introuvable pour le type '{notification_type}'"
            )
        
        variables = _extract_variables(template["content"])
        if template.get("subject"):
            variables.extend(_extract_variables(template["subject"]))
        
        return {
            "template_key": template_key,
            "notification_type": notification_type,
            "template": template,
            "variables_requises": list(set(variables)),
            "exemple_utilisation": _generate_example_usage(template_key, notification_type, variables)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur détails template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-template/{template_key}")
async def tester_template_avec_variables(
    template_key: str,
    variables: Dict[str, str],
    notification_type: str = "email"
):
    """🧪 Teste le rendu d'un template avec des variables personnalisées"""
    try:
        result = render_notification(template_key, notification_type, **variables)
        
        if not result:
            raise HTTPException(
                status_code=400,
                detail=f"Impossible de rendre le template '{template_key}' avec ces variables"
            )
        
        return {
            "template_key": template_key,
            "notification_type": notification_type,
            "variables_utilisees": variables,
            "resultat": result,
            "preview": {
                "sujet": result.get("subject", "N/A"),
                "contenu_debut": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur test template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 🔧 Fonctions utilitaires

def _extract_variables(text: str) -> list:
    """Extrait les variables {variable} d'un texte"""
    import re
    return re.findall(r'\{([^}]+)\}', text)

def _generate_example_usage(template_key: str, notification_type: str, variables: list) -> str:
    """Génère un exemple d'utilisation du template"""
    variables_example = ", ".join([f'{var}="exemple_{var}"' for var in variables[:3]])
    
    return f"""
# Exemple d'utilisation:
from app.templates.simple_notifications import render_notification

result = render_notification(
    "{template_key}", 
    "{notification_type}", 
    {variables_example}
)

if result:
    subject = result["subject"]  # Pour email
    content = result["content"]
    """.strip()

# 🎯 Guide d'intégration pour les développeurs

"""
📚 GUIDE D'INTÉGRATION RAPIDE
============================

1. 📧 NOTIFICATION DE BIENVENUE
   Dans routes/auth.py après inscription:
   
   from ..services.eir_notifications import envoyer_notification_bienvenue
   
   @router.post("/register")
   async def register(user_data: UserCreate):
       # ... création utilisateur ...
       await envoyer_notification_bienvenue(str(new_user.id))

2. 📱 VÉRIFICATION IMEI
   Dans routes/imei.py après vérification:
   
   from ..services.eir_notifications import notifier_verification_imei
   
   @router.post("/verify/{imei}")
   async def verify_imei(imei: str, current_user: Utilisateur = Depends(get_current_user)):
       # ... vérification ...
       await notifier_verification_imei(
           str(current_user.id), 
           imei, 
           statut_verification,
           marque=device_info.get("marque"),
           modele=device_info.get("modele")
       )

3. 🔑 RESET PASSWORD
   Dans routes/auth.py:
   
   from ..services.eir_notifications import notifier_reset_password
   
   @router.post("/reset-password")
   async def reset_password(email: str):
       # ... génération token ...
       reset_link = f"https://app.com/reset/{token}"
       await notifier_reset_password(str(user.id), reset_link)

4. 🚨 ALERTE SÉCURITÉ
   Dans middleware de sécurité:
   
   from ..services.eir_notifications import notifier_alerte_securite
   
   await notifier_alerte_securite(user_id, {
       "date_connexion": datetime.now().strftime('%d/%m/%Y à %H:%M'),
       "adresse_ip": request.client.host,
       "localisation": "Casablanca, Maroc",
       "navigateur": request.headers.get("user-agent")
   })

✅ AVANTAGES DU NOUVEAU SYSTÈME:
- Templates centralisés dans JSON
- Facile à modifier sans toucher au code
- Support multilingue prêt
- Variables automatiques
- Rendu sécurisé
"""
