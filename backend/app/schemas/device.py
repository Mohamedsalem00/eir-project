from pydantic import BaseModel
from typing import Optional, List

class CreationIMEI(BaseModel):
    """Schéma pour la création d'un IMEI"""
    numero_imei: str
    numero_slot: Optional[int] = 1
    statut: Optional[str] = "actif"

class ReponseIMEI(BaseModel):
    """Schéma de réponse pour un IMEI"""
    id: str
    numero_imei: str
    numero_slot: int
    statut: str
    
    class Config:
        from_attributes = True

class CreationAppareil(BaseModel):
    """Schéma pour la création d'un appareil"""
    marque: str
    modele: str
    emmc: Optional[str] = None
    utilisateur_id: Optional[str] = None
    imeis: List[CreationIMEI] = []

class ReponseAppareil(BaseModel):
    """Schéma de réponse pour un appareil"""
    id: str
    marque: str
    modele: str
    emmc: Optional[str]
    utilisateur_id: Optional[str]
    imeis: List[ReponseIMEI] = []
    
    class Config:
        from_attributes = True

class AssignationAppareil(BaseModel):
    """Schéma pour l'assignation d'un appareil à un utilisateur"""
    utilisateur_id: str
