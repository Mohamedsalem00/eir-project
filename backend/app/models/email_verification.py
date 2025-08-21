from sqlalchemy import Column, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta, timezone
import uuid

from ..core.database import Base

class EmailVerification(Base):
    """
    Modèle pour gérer les tokens de vérification d'email
    """
    __tablename__ = "email_verification"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"), nullable=False)
    token = Column(Text, nullable=False, unique=True)
    date_creation = Column(DateTime, default=datetime.now)
    date_expiration = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)  # Indique si le token a été utilisé
    
    # Relations
    utilisateur = relationship("Utilisateur", back_populates="email_verifications")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.date_expiration:
            # Token valide pour 24 heures par défaut
            self.date_expiration = datetime.now(timezone.utc) + timedelta(hours=24)
    
    def is_expired(self) -> bool:
        """Vérifie si le token a expiré"""
        return datetime.now(timezone.utc) > self.date_expiration
    
    def is_valid(self) -> bool:
        """Vérifie si le token est encore valide"""
        return not self.used and not self.is_expired()
    
    def mark_as_used(self):
        """Marque le token comme utilisé"""
        self.used = True