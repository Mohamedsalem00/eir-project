from sqlalchemy import Column, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
import uuid

from ..core.database import Base

class PasswordReset(Base):
    """
    Modèle pour gérer les tokens de réinitialisation de mot de passe
    """
    __tablename__ = "password_reset"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    token = Column(Text, nullable=False, unique=True)
    methode_verification = Column(Text, nullable=False)  # "email" ou "sms"
    code_verification = Column(Text, nullable=True)  # Code à 6 chiffres pour SMS/email
    email = Column(Text, nullable=True)  # Email de vérification si différent de l'utilisateur
    telephone = Column(Text, nullable=True)  # Numéro de téléphone pour SMS
    utilise = Column(Boolean, default=False)
    date_creation = Column(DateTime, default=datetime.now)
    date_expiration = Column(DateTime, nullable=False)
    date_utilisation = Column(DateTime, nullable=True)
    adresse_ip = Column(Text, nullable=True)
    
    # Relations
    utilisateur = relationship("Utilisateur", back_populates="password_resets")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.date_expiration:
            # Token valide pour 1 heure par défaut
            self.date_expiration = datetime.now(timezone.utc) + timedelta(hours=1)
    
    def is_expired(self) -> bool:
        """Vérifie si le token a expiré"""
        return datetime.now(timezone.utc) > self.date_expiration
    
    def is_valid(self) -> bool:
        """Vérifie si le token est encore valide"""
        return not self.utilise and not self.is_expired()
    
    def mark_as_used(self):
        """Marque le token comme utilisé"""
        self.utilise = True
        self.date_utilisation = datetime.now()
