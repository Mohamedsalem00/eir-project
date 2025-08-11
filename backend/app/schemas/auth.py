from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

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

class ProfilUtilisateurDetaille(BaseModel):
    """Schéma de réponse détaillé pour le profil utilisateur"""
    id: str = Field(..., description="Identifiant unique de l'utilisateur")
    nom: str = Field(..., description="Nom complet de l'utilisateur")
    email: str = Field(..., description="Adresse email de l'utilisateur")
    type_utilisateur: str = Field(..., description="Type d'utilisateur (administrateur, utilisateur_authentifie)")
    date_creation: Optional[datetime] = Field(None, description="Date de création du compte")
    derniere_connexion: Optional[datetime] = Field(None, description="Date et heure de la dernière connexion")
    statut_compte: str = Field(default="active", description="Statut du compte (active, suspendu, etc.)")
    permissions: list[str] = Field(default_factory=list, description="Liste des permissions accordées")
    statistiques: dict = Field(default_factory=dict, description="Statistiques d'utilisation")
    
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
