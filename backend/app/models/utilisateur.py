from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class Utilisateur(Base):
    __tablename__ = "utilisateur"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nom = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    mot_de_passe = Column(Text)
    type_utilisateur = Column(String(50))

    # Relationships
    appareils = relationship("Appareil", back_populates="utilisateur")
    sims = relationship("SIM", back_populates="utilisateur")
    recherches = relationship("Recherche", back_populates="utilisateur")
    notifications = relationship("Notification", back_populates="utilisateur")
    audit_logs = relationship("JournalAudit", back_populates="utilisateur")
    import_exports = relationship("ImportExport", back_populates="utilisateur")
