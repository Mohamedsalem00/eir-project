from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class ImportExport(Base):
    """Modèle pour la table importexport"""
    __tablename__ = "importexport"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type_operation = Column(String(50))  # import, export
    fichier = Column(Text)
    date = Column(DateTime)
    utilisateur_id = Column(UUID(as_uuid=True), ForeignKey("utilisateur.id"))

    # Relation
    utilisateur = relationship("Utilisateur", back_populates="import_exports")
