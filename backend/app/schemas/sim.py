from pydantic import BaseModel
from typing import Optional

class CreationSIM(BaseModel):
    """Schéma pour la création d'une carte SIM"""
    iccid: str
    operateur: str
    utilisateur_id: Optional[str] = None

class ReponseSIM(BaseModel):
    """Schéma de réponse pour une carte SIM"""
    id: str
    iccid: str
    operateur: str
    utilisateur_id: Optional[str]
    
    class Config:
        from_attributes = True
