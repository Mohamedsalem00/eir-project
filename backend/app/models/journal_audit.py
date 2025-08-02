from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class JournalAudit(Base):
    """Modèle pour la table journal_audit"""
    __tablename__ = "journal_audit"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    action = Column(Text)
    date = Column(DateTime)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))

    # Relation
    utilisateur = relationship("Utilisateur", back_populates="audit_logs")
