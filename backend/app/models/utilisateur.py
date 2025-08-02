from sqlalchemy import Column, String, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..core.database import Base
import uuid

class Utilisateur(Base):
    """Modèle pour la table utilisateur"""
    __tablename__ = "utilisateur"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    nom = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    mot_de_passe = Column(Text)
    type_utilisateur = Column(String(50))
    
    # Champs essentiels de contrôle d'accès (noms correspondant au schéma DB)
    access_level = Column(String(50), default="basic")  # basic, limited, standard, elevated, admin
    data_scope = Column(String(50), default="own")  # own, organization, brands, ranges, all
    organization = Column(String(100))  # Affiliation organisationnelle
    is_active = Column(Boolean, default=True)  # Statut du compte
    allowed_brands = Column(JSON, default=lambda: [])  # Marques d'appareils accessibles
    allowed_imei_ranges = Column(JSON, default=lambda: [])  # Plages/préfixes IMEI spécifiques

    # Relations
    appareils = relationship("Appareil", back_populates="utilisateur")
    sims = relationship("SIM", back_populates="utilisateur")
    recherches = relationship("Recherche", back_populates="utilisateur")
    notifications = relationship("Notification", back_populates="utilisateur")
    audit_logs = relationship("JournalAudit", back_populates="utilisateur")
    import_exports = relationship("ImportExport", back_populates="utilisateur")
