from pydantic import BaseModel
from typing import Optional, List

class IMEICreate(BaseModel):
    imei_number: str
    slot_number: Optional[int] = 1
    status: Optional[str] = "active"

class IMEIResponse(BaseModel):
    id: str
    imei_number: str
    slot_number: int
    status: str
    
    class Config:
        from_attributes = True

class DeviceCreate(BaseModel):
    marque: str
    modele: str
    emmc: Optional[str] = None
    utilisateur_id: Optional[str] = None
    imeis: List[IMEICreate] = []

class DeviceResponse(BaseModel):
    id: str
    marque: str
    modele: str
    emmc: Optional[str]
    utilisateur_id: Optional[str]
    imeis: List[IMEIResponse] = []
    
    class Config:
        from_attributes = True

class DeviceAssignment(BaseModel):
    user_id: str
