from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class Recherche(Base):
    __tablename__ = "recherche"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    date_recherche = Column(DateTime)
    imei_recherche = Column(String(20))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))

    # Relationship
    utilisateur = relationship("Utilisateur", back_populates="recherches")
