from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class SIM(Base):
    __tablename__ = "sim"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    iccid = Column(String(22), unique=True, index=True, nullable=False)
    operateur = Column(String(50))
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))

    # Relationship
    utilisateur = relationship("Utilisateur", back_populates="sims")
