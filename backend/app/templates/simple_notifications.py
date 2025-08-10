"""
📧 Gestionnaire Simple des Notifications
======================================

Ce module lit le fichier notifications_content.json pour 
charger les templates de notifications automatiques.

Usage simple:
```python
from app.templates.simple_notifications import get_notification_template

# Récupérer un template
template = get_notification_template("bienvenue", "email")
subject = template["subject"]
content = template["content"]

# Remplacer les variables
final_content = content.format(nom_utilisateur="Mohamed")
```
"""

import json
import os
from typing import Dict, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SimpleNotificationManager:
    """Gestionnaire simple pour les notifications automatiques."""
    
    def __init__(self):
        self.templates_file = Path(__file__).parent / "notifications_content.json"
        self.templates_data = None
        self.load_templates()
    
    def load_templates(self) -> bool:
        """Charge les templates depuis le fichier JSON."""
        try:
            if not self.templates_file.exists():
                logger.error(f"❌ Fichier {self.templates_file} introuvable")
                return False
            
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                self.templates_data = json.load(f)
            
            logger.info(f"✅ Templates chargés depuis {self.templates_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement templates: {e}")
            return False
    
    def get_template(self, template_key: str, notification_type: str = "email") -> Optional[Dict[str, str]]:
        """
        Récupère un template spécifique.
        
        Args:
            template_key: Clé du template (ex: "bienvenue", "verification_imei_valide")
            notification_type: Type de notification ("email" ou "sms")
        
        Returns:
            Dict avec 'subject' et 'content' ou None si introuvable
        """
        try:
            if not self.templates_data:
                self.load_templates()
            
            if not self.templates_data:
                return None
            
            template = self.templates_data.get("notifications", {}).get(template_key, {}).get(notification_type)
            
            if not template:
                logger.warning(f"⚠️ Template {template_key}/{notification_type} introuvable")
                return None
            
            return template
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération template {template_key}: {e}")
            return None
    
    def get_variable(self, variable_key: str) -> Optional[str]:
        """Récupère une variable globale."""
        try:
            if not self.templates_data:
                self.load_templates()
            
            return self.templates_data.get("variables_globales", {}).get(variable_key)
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération variable {variable_key}: {e}")
            return None
    
    def render_template(self, template_key: str, notification_type: str, variables: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Rend un template avec les variables fournies.
        
        Args:
            template_key: Clé du template
            notification_type: Type de notification
            variables: Variables à injecter
        
        Returns:
            Dict avec 'subject' et 'content' rendus ou None
        """
        try:
            template = self.get_template(template_key, notification_type)
            if not template:
                return None
            
            # Ajouter les variables globales
            global_vars = self.templates_data.get("variables_globales", {})
            all_variables = {**global_vars, **variables}
            
            # Rendre le template
            rendered = {}
            
            if "subject" in template:
                rendered["subject"] = template["subject"].format(**all_variables)
            
            rendered["content"] = template["content"].format(**all_variables)
            
            return rendered
            
        except KeyError as e:
            logger.error(f"❌ Variable manquante pour {template_key}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Erreur rendu template {template_key}: {e}")
            return None

# Instance globale
notification_manager = SimpleNotificationManager()

# 🎯 Fonctions utilitaires simples

def get_notification_template(template_key: str, notification_type: str = "email") -> Optional[Dict[str, str]]:
    """
    Fonction utilitaire pour récupérer un template.
    
    Usage:
    ```python
    template = get_notification_template("bienvenue", "email")
    if template:
        subject = template["subject"]
        content = template["content"]
    ```
    """
    return notification_manager.get_template(template_key, notification_type)

def render_notification(template_key: str, notification_type: str, **variables) -> Optional[Dict[str, str]]:
    """
    Fonction utilitaire pour rendre un template avec des variables.
    
    Usage:
    ```python
    result = render_notification(
        "bienvenue", 
        "email", 
        nom_utilisateur="Mohamed",
        date_verification="2025-08-10"
    )
    if result:
        subject = result["subject"]
        content = result["content"]
    ```
    """
    return notification_manager.render_template(template_key, notification_type, variables)

def get_available_templates() -> Dict[str, list]:
    """Retourne la liste des templates disponibles."""
    try:
        if not notification_manager.templates_data:
            notification_manager.load_templates()
        
        notifications = notification_manager.templates_data.get("notifications", {})
        
        # Organiser par type de notification
        result = {"email": [], "sms": []}
        
        for template_key, template_data in notifications.items():
            if "email" in template_data:
                result["email"].append(template_key)
            if "sms" in template_data:
                result["sms"].append(template_key)
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur liste templates: {e}")
        return {"email": [], "sms": []}

def reload_templates() -> bool:
    """Force le rechargement des templates."""
    return notification_manager.load_templates()
