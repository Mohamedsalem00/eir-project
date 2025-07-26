from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class IMEI(Base):
    __tablename__ = "imei"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    imei_number = Column(String(20), unique=True, index=True, nullable=False)
    slot_number = Column(Integer)  # 1 for primary, 2 for secondary (dual-SIM)
    status = Column(String(50), default="active")  # active, blocked, stolen, etc.
    appareil_id = Column(UUID(as_uuid=True), ForeignKey("appareil.id"), nullable=False)

    # Relationship
    appareil = relationship("Appareil", back_populates="imeis")
