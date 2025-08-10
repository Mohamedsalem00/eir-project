from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class UtilisateurBase(BaseModel):
    """Base schema for Utilisateur"""
    nom: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    type_utilisateur: Optional[str] = Field(None, max_length=50)
    niveau_acces: Optional[str] = Field("basique", max_length=50)
    portee_donnees: Optional[str] = Field("personnel", max_length=50)
    organisation: Optional[str] = Field(None, max_length=100)
    est_actif: bool = True
    marques_autorisees: Optional[List[str]] = Field(default_factory=list)
    plages_imei_autorisees: Optional[List[str]] = Field(default_factory=list)


class UtilisateurCreate(UtilisateurBase):
    """Schema for creating a new user"""
    mot_de_passe: str = Field(..., min_length=6)


class UtilisateurUpdate(BaseModel):
    """Schema for updating a user"""
    nom: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    type_utilisateur: Optional[str] = Field(None, max_length=50)
    niveau_acces: Optional[str] = Field(None, max_length=50)
    portee_donnees: Optional[str] = Field(None, max_length=50)
    organisation: Optional[str] = Field(None, max_length=100)
    est_actif: Optional[bool] = None
    marques_autorisees: Optional[List[str]] = None
    plages_imei_autorisees: Optional[List[str]] = None


class UtilisateurResponse(UtilisateurBase):
    """Schema for user response (without password)"""
    id: str = Field(..., description="User ID")
    
    class Config:
        from_attributes = True


class UtilisateurPermissions(BaseModel):
    """Schema for user permissions summary"""
    id: str
    nom: Optional[str]
    email: Optional[str]
    niveau_acces: str
    portee_donnees: str
    organisation: Optional[str]
    est_actif: bool
    marques_autorisees: List[str]
    plages_imei_autorisees: List[str]
    
    class Config:
        from_attributes = True
