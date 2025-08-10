from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from enum import Enum

class MethodeVerification(str, Enum):
    """Méthodes de vérification disponibles"""
    EMAIL = "email"
    SMS = "sms"

class DemandeResetPassword(BaseModel):
    """Schema pour demander un reset de mot de passe"""
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    methode_verification: MethodeVerification = Field(
        default=MethodeVerification.EMAIL,
        description="Méthode de vérification (email ou sms)"
    )
    telephone: Optional[str] = Field(
        None,
        description="Numéro de téléphone pour la vérification par SMS",
        pattern=r'^(\+?[1-9]\d{1,14})$'
    )

class VerificationCodeReset(BaseModel):
    """Schema pour vérifier le code de reset"""
    token: str = Field(..., description="Token de reset reçu")
    code_verification: str = Field(
        ...,
        description="Code de vérification à 6 chiffres",
        min_length=6,
        max_length=6
    )

class NouveauMotDePasse(BaseModel):
    """Schema pour définir un nouveau mot de passe"""
    token: str = Field(..., description="Token de reset validé")
    nouveau_mot_de_passe: str = Field(
        ...,
        min_length=8,
        description="Nouveau mot de passe (minimum 8 caractères)"
    )
    confirmer_mot_de_passe: str = Field(
        ...,
        description="Confirmation du nouveau mot de passe"
    )

    def validate_passwords_match(self):
        """Valide que les mots de passe correspondent"""
        if self.nouveau_mot_de_passe != self.confirmer_mot_de_passe:
            raise ValueError("Les mots de passe ne correspondent pas")
        return True

class ReponseResetPassword(BaseModel):
    """Schema de réponse pour les opérations de reset password"""
    success: bool
    message: str
    token: Optional[str] = None
    methode_verification: Optional[str] = None
    expires_in_minutes: Optional[int] = None
