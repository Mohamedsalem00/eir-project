from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class Notification(Base):
    __tablename__ = "notification"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type = Column(String(50))  # email, sms
    contenu = Column(Text)
    statut = Column(String(20))  # envoyé, échoué, en_attente
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))

    # Relationship
    utilisateur = relationship("Utilisateur", back_populates="notifications")
