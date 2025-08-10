from sqlalchemy import Column, String, Text, JSON, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
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
    date_creation = Column(DateTime, default=datetime.now, nullable=False)
    
    # Champs essentiels de contrôle d'accès (noms français correspondant au schéma DB)
    niveau_acces = Column(String(50), default="basique")  # basique, limite, standard, eleve, admin
    portee_donnees = Column(String(50), default="personnel")  # personnel, organisation, marques, plages, tout
    organisation = Column(String(100))  # Affiliation organisationnelle
    est_actif = Column(Boolean, default=True)  # Statut du compte
    marques_autorisees = Column(JSON, default=lambda: [])  # Marques d'appareils accessibles
    plages_imei_autorisees = Column(JSON, default=lambda: [])  # Plages/préfixes IMEI spécifiques

    # Relations
    appareils = relationship("Appareil", back_populates="utilisateur")
    sims = relationship("SIM", back_populates="utilisateur")
    recherches = relationship("Recherche", back_populates="utilisateur")
    notifications = relationship("Notification", back_populates="utilisateur")
    audit_logs = relationship("JournalAudit", back_populates="utilisateur")
    import_exports = relationship("ImportExport", back_populates="utilisateur")
    password_resets = relationship("PasswordReset", back_populates="utilisateur")
