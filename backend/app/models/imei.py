from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class IMEI(Base):
    __tablename__ = "imei"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    numero_imei = Column(String(20), unique=True, index=True, nullable=False)
    numero_slot = Column(Integer)  # 1 pour principal, 2 pour secondaire (dual-SIM)
    statut = Column(String(50), default="actif")  # actif, bloque, vole, etc.
    appareil_id = Column(UUID(as_uuid=True), ForeignKey("appareil.id"), nullable=False)

    # Relationship
    appareil = relationship("Appareil", back_populates="imeis")
