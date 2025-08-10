from sqlalchemy import Column, String, Text, ForeignKey, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class Notification(Base):
    __tablename__ = "notification"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type = Column(String(50))  # email, sms
    destinataire = Column(String(255))  # numéro de téléphone ou adresse email
    sujet = Column(String(255))  # pour email
    contenu = Column(Text)
    statut = Column(String(20), default='en_attente')  # en_attente, envoyé, échoué
    tentative = Column(Integer, default=0)
    erreur = Column(Text)
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    date_envoi = Column(DateTime(timezone=True))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))

    # Relationship
    utilisateur = relationship("Utilisateur", back_populates="notifications")
