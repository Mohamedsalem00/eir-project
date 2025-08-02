from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class Appareil(Base):
    """Modèle pour la table appareil"""
    __tablename__ = "appareil"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    marque = Column(String(50))
    modele = Column(String(50))
    emmc = Column(String(100))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))

    # Relations
    utilisateur = relationship("Utilisateur", back_populates="appareils")
    imeis = relationship("IMEI", back_populates="appareil", cascade="all, delete-orphan")
