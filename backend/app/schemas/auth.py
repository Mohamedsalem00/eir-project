from pydantic import BaseModel, EmailStr
from typing import Optional

class ConnexionUtilisateur(BaseModel):
    """Schéma pour la connexion d'un utilisateur"""
    email: EmailStr
    mot_de_passe: str

class CreationUtilisateur(BaseModel):
    """Schéma pour la création d'un nouvel utilisateur"""
    nom: str
    email: EmailStr
    mot_de_passe: str
    type_utilisateur: Optional[str] = "utilisateur_authentifie"  # Seulement 'administrateur' ou 'utilisateur_authentifie'

class ReponseUtilisateur(BaseModel):
    """Schéma de réponse pour les informations utilisateur"""
    id: str
    nom: str
    email: str
    type_utilisateur: str

    class Config:
        from_attributes = True

class Jeton(BaseModel):
    """Schéma pour le jeton d'authentification"""
    access_token: str
    token_type: str

class DonneesJeton(BaseModel):
    """Schéma pour les données contenues dans le jeton"""
    utilisateur_id: Optional[str] = None
    email: Optional[str] = None
    type_utilisateur: Optional[str] = None
