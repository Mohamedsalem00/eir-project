"""
Service de notifications EIR Project utilisant le nouveau système de templates
Intègre les templates JSON pour les notifications automatiques
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from ..tasks.notification_dispatcher import send_notification_now
from ..models.notification import Notification
from ..models.utilisateur import Utilisateur
from ..core.database import get_db_session
from ..templates.simple_notifications import render_notification, get_notification_template

logger = logging.getLogger(__name__)

class EIRNotificationService:
    """
    Service de notifications spécifique à l'application EIR
    Utilise le nouveau système de templates JSON
    """
    
    @staticmethod
    async def envoyer_notification_bienvenue(user_id: str) -> Dict[str, Any]:
        """
        Envoie une notification de bienvenue à un nouvel utilisateur
        
        Args:
            user_id: ID de l'utilisateur à notifier
            
        Returns:
            Résultat de l'envoi de la notification
        """
        db = next(get_db_session())
        
        try:
            # Récupérer les infos utilisateur
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            if not user:
                return {"success": False, "error": "Utilisateur introuvable"}
            
            # Utiliser le template de bienvenue
            template_result = render_notification(
                "bienvenue", 
                "email", 
                nom_utilisateur=user.nom
            )
            
            if not template_result:
                return {"success": False, "error": "Template de bienvenue introuvable"}
            
            # Envoyer la notification
            return await send_notification_now(
                user_id=user_id,
                notification_type="email",
                destinataire=user.email,
                sujet=template_result["subject"],
                contenu=template_result["content"]
            )
            
        except Exception as e:
            logger.error(f"Erreur notification bienvenue: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def notifier_verification_imei(user_id: str, imei: str, statut: str, marque: str = "", modele: str = "", raison: str = "") -> Dict[str, Any]:
        """
        Notifie le résultat d'une vérification IMEI
        
        Args:
            user_id: ID de l'utilisateur
            imei: IMEI vérifié
            statut: Statut de la vérification (valide, invalide, blackliste)
            marque: Marque de l'appareil
            modele: Modèle de l'appareil
            raison: Raison en cas d'invalidité
            
        Returns:
            Résultat de l'envoi
        """
        db = next(get_db_session())
        
        try:
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            if not user:
                return {"success": False, "error": "Utilisateur introuvable"}
            
            # Déterminer le template selon le statut
            template_key = f"verification_imei_{statut}"
            
            # Variables pour le template
            variables = {
                "nom_utilisateur": user.nom,
                "imei": imei,
                "marque": marque or "Inconnue",
                "modele": modele or "Inconnu",
                "date_verification": datetime.now().strftime('%d/%m/%Y à %H:%M'),
                "raison": raison or "Non spécifiée"
            }
            
            # Rendu du template email
            template_result = render_notification(template_key, "email", **variables)
            
            if not template_result:
                return {"success": False, "error": f"Template {template_key} introuvable"}
            
            # Envoyer l'email
            email_result = await send_notification_now(
                user_id=user_id,
                notification_type="email",
                destinataire=user.email,
                sujet=template_result["subject"],
                contenu=template_result["content"]
            )
            
            # Envoyer aussi un SMS si le template existe
            sms_template = render_notification(template_key, "sms", **variables)
            if sms_template and hasattr(user, 'telephone') and user.telephone:
                await send_notification_now(
                    user_id=user_id,
                    notification_type="sms",
                    destinataire=user.telephone,
                    sujet=None,
                    contenu=sms_template["content"]
                )
            
            return email_result
            
        except Exception as e:
            logger.error(f"Erreur notification vérification IMEI: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def notifier_reset_password(user_id: str, lien_reset: str) -> Dict[str, Any]:
        """
        Envoie un email de réinitialisation de mot de passe
        
        Args:
            user_id: ID de l'utilisateur
            lien_reset: Lien de réinitialisation
            
        Returns:
            Résultat de l'envoi
        """
        db = next(get_db_session())
        
        try:
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            if not user:
                return {"success": False, "error": "Utilisateur introuvable"}
            
            # Utiliser le template de reset password
            template_result = render_notification(
                "reset_password", 
                "email", 
                nom_utilisateur=user.nom,
                lien_reset=lien_reset
            )
            
            if not template_result:
                return {"success": False, "error": "Template reset password introuvable"}
            
            # Envoyer la notification
            return await send_notification_now(
                user_id=user_id,
                notification_type="email",
                destinataire=user.email,
                sujet=template_result["subject"],
                contenu=template_result["content"]
            )
            
        except Exception as e:
            logger.error(f"Erreur notification reset password: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def notifier_alerte_securite(user_id: str, details_connexion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notifie une alerte de sécurité (connexion suspecte)
        
        Args:
            user_id: ID de l'utilisateur
            details_connexion: Détails de la connexion suspecte
            
        Returns:
            Résultat de l'envoi
        """
        db = next(get_db_session())
        
        try:
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            if not user:
                return {"success": False, "error": "Utilisateur introuvable"}
            
            # Variables pour le template
            variables = {
                "nom_utilisateur": user.nom,
                "date_connexion": details_connexion.get("date_connexion", datetime.now().strftime('%d/%m/%Y à %H:%M')),
                "adresse_ip": details_connexion.get("adresse_ip", "Inconnue"),
                "localisation": details_connexion.get("localisation", "Inconnue"),
                "navigateur": details_connexion.get("navigateur", "Inconnu")
            }
            
            # Rendu du template email
            template_result = render_notification("alerte_securite", "email", **variables)
            
            if not template_result:
                return {"success": False, "error": "Template alerte sécurité introuvable"}
            
            # Envoyer l'email
            email_result = await send_notification_now(
                user_id=user_id,
                notification_type="email",
                destinataire=user.email,
                sujet=template_result["subject"],
                contenu=template_result["content"]
            )
            
            # Envoyer aussi un SMS si disponible
            sms_template = render_notification("alerte_securite", "sms", **variables)
            if sms_template and hasattr(user, 'telephone') and user.telephone:
                await send_notification_now(
                    user_id=user_id,
                    notification_type="sms",
                    destinataire=user.telephone,
                    sujet=None,
                    contenu=sms_template["content"]
                )
            
            return email_result
            
        except Exception as e:
            logger.error(f"Erreur notification alerte sécurité: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def notifier_nouvel_appareil(user_id: str, appareil_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notifie l'ajout d'un nouvel appareil en utilisant les templates JSON
        
        Args:
            user_id: ID de l'utilisateur
            appareil_details: Détails de l'appareil
            
        Returns:
            Résultat de l'envoi
        """
        db = next(get_db_session())
        
        try:
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            if not user:
                return {"success": False, "error": "Utilisateur introuvable"}
            
            # Variables pour le template
            variables = {
                "nom_utilisateur": user.nom,
                "marque": appareil_details.get('marque', 'Inconnue'),
                "modele": appareil_details.get('modele', 'Inconnu'),
                "emmc": appareil_details.get('emmc', 'Non spécifié'),
                "date_verification": datetime.now().strftime('%d/%m/%Y à %H:%M'),
                "imeis": _format_imei_list(appareil_details.get('imeis', []))
            }
            
            # Utiliser le template nouvel_appareil
            template_result = render_notification("nouvel_appareil", "email", **variables)
            
            if not template_result:
                return {"success": False, "error": "Template nouvel appareil introuvable"}
            
            # Envoyer l'email
            email_result = await send_notification_now(
                user_id=user_id,
                notification_type="email",
                destinataire=user.email,
                sujet=template_result["subject"],
                contenu=template_result["content"]
            )
            
            # Envoyer aussi un SMS si le template existe
            sms_template = render_notification("nouvel_appareil", "sms", **variables)
            if sms_template and hasattr(user, 'telephone') and user.telephone:
                await send_notification_now(
                    user_id=user_id,
                    notification_type="sms",
                    destinataire=user.telephone,
                    sujet=None,
                    contenu=sms_template["content"]
                )
            
            return email_result
            
        except Exception as e:
            logger.error(f"Erreur notification nouvel appareil: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def notifier_activite_suspecte(user_id: str, activite: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Notifie une activité suspecte en utilisant le template d'alerte sécurité
        
        Args:
            user_id: ID de l'utilisateur
            activite: Type d'activité suspecte
            details: Détails de l'activité
            
        Returns:
            Résultat de l'envoi
        """
        # Réutiliser le template d'alerte sécurité existant
        details_connexion = {
            "date_connexion": datetime.now().strftime('%d/%m/%Y à %H:%M'),
            "adresse_ip": details.get('ip_address', 'Inconnue'),
            "localisation": details.get('localisation', 'Inconnue'),
            "navigateur": details.get('user_agent', 'Inconnu')
        }
        
        return await EIRNotificationService.notifier_alerte_securite(user_id, details_connexion)
    
    @staticmethod
    async def notifier_rapport_mensuel(user_id: str, rapport: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envoie le rapport mensuel d'activité
        
        Args:
            user_id: ID de l'utilisateur
            rapport: Données du rapport mensuel
            
        Returns:
            Résultat de l'envoi
        """
        db = next(get_db_session())
        
        try:
            user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
            if not user:
                return {"success": False, "error": "Utilisateur introuvable"}
            
            mois = rapport.get('mois', datetime.now().strftime('%B %Y'))
            
            sujet = f"📊 Rapport mensuel EIR - {mois}"
            contenu = f"""Bonjour {user.nom},

📊 **Votre rapport d'activité EIR pour {mois}**

📱 **VOS APPAREILS :**
• Nombre total d'appareils : {rapport.get('total_appareils', 0)}
• Nouveaux appareils ce mois : {rapport.get('nouveaux_appareils', 0)}
• IMEI actifs : {rapport.get('imei_actifs', 0)}

🔍 **ACTIVITÉ DE VÉRIFICATION :**
• Vérifications effectuées : {rapport.get('total_verifications', 0)}
• IMEI valides : {rapport.get('imei_valides', 0)}
• IMEI invalides : {rapport.get('imei_invalides', 0)}

📈 **STATISTIQUES :**
• Taux de validité : {rapport.get('taux_validite', 0):.1f}%
• Marque la plus fréquente : {rapport.get('marque_populaire', 'N/A')}
• Dernière connexion : {rapport.get('derniere_connexion', 'N/A')}

🛡️ **SÉCURITÉ :**
• Tentatives de connexion : {rapport.get('tentatives_connexion', 0)}
• Alertes sécurité : {rapport.get('alertes_securite', 0)}

🌐 Voir le rapport détaillé : https://eir-project.com/rapports

Merci de votre confiance !

L'équipe EIR Project

---
🔒 EIR Project - Système de gestion des équipements mobiles
📧 Email automatique généré par le système"""
            
            return await send_notification_now(
                user_id=user_id,
                notification_type="email",
                destinataire=user.email,
                sujet=sujet,
                contenu=contenu
            )
            
        except Exception as e:
            logger.error(f"Erreur notification rapport mensuel: {e}")
            return {"success": False, "error": str(e)}


def _format_imei_list(imeis: list) -> str:
    """Formate une liste d'IMEI pour l'affichage"""
    if not imeis:
        return "• Aucun IMEI associé"
    
    formatted = []
    for i, imei in enumerate(imeis, 1):
        if isinstance(imei, dict):
            numero = imei.get('numero', 'N/A')
            slot = imei.get('slot', i)
            formatted.append(f"• Slot {slot}: {numero}")
        else:
            formatted.append(f"• IMEI {i}: {imei}")
    
    return "\n".join(formatted)


# 🎯 Fonctions utilitaires pour l'intégration dans d'autres modules

async def envoyer_notification_bienvenue(user_id: str) -> Dict[str, Any]:
    """
    Envoie une notification de bienvenue à un nouvel utilisateur
    """
    return await EIRNotificationService.envoyer_notification_bienvenue(user_id)

async def notifier_verification_imei(user_id: str, imei: str, statut: str, **kwargs) -> Dict[str, Any]:
    """
    Notifie le résultat d'une vérification IMEI
    """
    return await EIRNotificationService.notifier_verification_imei(user_id, imei, statut, **kwargs)

async def notifier_reset_password(user_id: str, lien_reset: str) -> Dict[str, Any]:
    """
    Envoie un email de réinitialisation de mot de passe
    """
    return await EIRNotificationService.notifier_reset_password(user_id, lien_reset)

async def notifier_alerte_securite(user_id: str, details_connexion: Dict[str, Any]) -> Dict[str, Any]:
    """
    Notifie une alerte de sécurité
    """
    return await EIRNotificationService.notifier_alerte_securite(user_id, details_connexion)

async def notifier_nouvel_appareil(user_id: str, appareil_details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Notifie l'ajout d'un nouvel appareil
    """
    return await EIRNotificationService.notifier_nouvel_appareil(user_id, appareil_details)

async def notifier_activite_suspecte(user_id: str, activite: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Notifie une activité suspecte
    """
    return await EIRNotificationService.notifier_activite_suspecte(user_id, activite, details)

async def notifier_rapport_mensuel(user_id: str, rapport: Dict[str, Any]) -> Dict[str, Any]:
    """
    Envoie le rapport mensuel d'activité
    """
    return await EIRNotificationService.notifier_rapport_mensuel(user_id, rapport)


# 📚 Exemples d'utilisation dans les routes API

"""
# Dans routes/imei.py, après une vérification d'IMEI:

@router.post("/imei/{imei}/verifier")
async def verifier_imei(
    imei: str,
    current_user: Utilisateur = Depends(get_current_user)
):
    # ... logique de vérification ...
    
    # Envoyer la notification du résultat
    await notifier_verification_imei(
        user_id=str(current_user.id),
        imei=imei,
        statut=resultat_verification,  # "valide", "invalide", "blackliste"
        marque=details.get("marque", ""),
        modele=details.get("modele", ""),
        raison=details.get("raison", "")
    )
    
    return resultat

# Dans routes/auth.py, après inscription:

@router.post("/auth/register")
async def register_user(user_data: UserCreate):
    # ... logique de création ...
    
    # Envoyer l'email de bienvenue
    await envoyer_notification_bienvenue(str(new_user.id))
    
    return new_user

# Dans routes/auth.py, pour reset password:

@router.post("/auth/reset-password")
async def reset_password(email: str):
    # ... génération du token de reset ...
    
    # Envoyer l'email de reset
    reset_link = f"https://eir-project.com/reset/{reset_token}"
    await notifier_reset_password(str(user.id), reset_link)
    
    return {"message": "Email envoyé"}

# Dans routes/appareils.py, après ajout d'un appareil:

@router.post("/appareils/")
async def creer_appareil(
    appareil_data: CreationAppareil,
    current_user: Utilisateur = Depends(get_current_user)
):
    # ... logique de création ...
    
    # Notifier l'ajout
    await notifier_nouvel_appareil(
        user_id=str(current_user.id),
        appareil_details={
            "marque": appareil.marque,
            "modele": appareil.modele,
            "emmc": appareil.emmc,
            "imeis": [imei.numero_imei for imei in appareil.imeis]
        }
    )
    
    return appareil

# Dans un middleware de sécurité:

async def detecter_activite_suspecte(request: Request, user_id: str):
    # ... logique de détection ...
    
    if activite_suspecte:
        await notifier_alerte_securite(
            user_id=user_id,
            details_connexion={
                "date_connexion": datetime.now().strftime('%d/%m/%Y à %H:%M'),
                "adresse_ip": request.client.host,
                "localisation": "Casablanca, Maroc",
                "navigateur": request.headers.get("user-agent", "Inconnu")
            }
        )
"""
