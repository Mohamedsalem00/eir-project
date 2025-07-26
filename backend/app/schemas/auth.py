from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str

class UserCreate(BaseModel):
    nom: str
    email: EmailStr
    mot_de_passe: str
    type_utilisateur: Optional[str] = "utilisateur_authentifie"  # Only 'administrateur' or 'utilisateur_authentifie'

class UserResponse(BaseModel):
    id: str
    nom: str
    email: str
    type_utilisateur: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    user_type: Optional[str] = None
