from pydantic import BaseModel
from typing import Optional

class SIMCreate(BaseModel):
    iccid: str
    operateur: str
    utilisateur_id: Optional[str] = None

class SIMResponse(BaseModel):
    id: str
    iccid: str
    operateur: str
    utilisateur_id: Optional[str]
    
    class Config:
        from_attributes = True
