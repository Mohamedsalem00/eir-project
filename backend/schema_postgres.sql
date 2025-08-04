-- Table: utilisateur (Enhanced with minimal access control fields)
CREATE TABLE utilisateur (
    id UUID PRIMARY KEY,
    nom VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    mot_de_passe TEXT,
    type_utilisateur VARCHAR(50),
    -- Champs essentiels de contrôle d'accès
    niveau_acces VARCHAR(50) DEFAULT 'basique',
    portee_donnees VARCHAR(50) DEFAULT 'personnel',
    organisation VARCHAR(100),
    est_actif BOOLEAN DEFAULT TRUE,
    marques_autorisees JSONB DEFAULT '[]',
    plages_imei_autorisees JSONB DEFAULT '[]'
);

-- Table: appareil (removed imei field)
CREATE TABLE appareil (
    id UUID PRIMARY KEY,
    marque VARCHAR(50),
    modele VARCHAR(50),
    emmc VARCHAR(100),
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Table : imei (nouvelle table pour gérer plusieurs IMEIs par appareil)
CREATE TABLE imei (
    id UUID PRIMARY KEY,
    numero_imei VARCHAR(20) UNIQUE,
    numero_slot INTEGER,
    statut VARCHAR(50) DEFAULT 'actif',
    appareil_id UUID REFERENCES appareil(id) NOT NULL
);

-- Table : sim
CREATE TABLE sim (
    id UUID PRIMARY KEY,
    iccid VARCHAR(22) UNIQUE,
    operateur VARCHAR(50),
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Table : recherche
CREATE TABLE recherche (
    id UUID PRIMARY KEY,
    date_recherche TIMESTAMP,
    imei_recherche VARCHAR(20),
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Table : notification
CREATE TABLE notification (
    id UUID PRIMARY KEY,
    type VARCHAR(50),
    contenu TEXT,
    statut VARCHAR(20),
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Table : journal_audit (minuscules pour correspondre au modèle SQLAlchemy)
CREATE TABLE journal_audit (
    id UUID PRIMARY KEY,
    action TEXT,
    date TIMESTAMP,
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Table : ImportExport
CREATE TABLE importexport (
    id UUID PRIMARY KEY,
    type_operation VARCHAR(50),
    fichier TEXT,
    date TIMESTAMP,
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Créer des index pour de meilleures performances
CREATE INDEX idx_numero_imei ON imei(numero_imei);
CREATE INDEX idx_appareil_utilisateur ON appareil(utilisateur_id);
CREATE INDEX idx_recherche_imei ON recherche(imei_recherche);
CREATE INDEX idx_recherche_date ON recherche(date_recherche);

-- Index essentiels pour le contrôle d'accès
CREATE INDEX idx_utilisateur_niveau_acces ON utilisateur(niveau_acces);
CREATE INDEX idx_utilisateur_organisation ON utilisateur(organisation);
CREATE INDEX idx_utilisateur_est_actif ON utilisateur(est_actif);
CREATE INDEX idx_utilisateur_marques_autorisees ON utilisateur USING GIN(marques_autorisees) WHERE marques_autorisees != '[]';

-- Ajouter des contraintes pour l'intégrité des données
ALTER TABLE utilisateur ADD CONSTRAINT chk_niveau_acces 
CHECK (niveau_acces IN ('visiteur', 'basique', 'limite', 'standard', 'eleve', 'admin'));

ALTER TABLE utilisateur ADD CONSTRAINT chk_portee_donnees 
CHECK (portee_donnees IN ('personnel', 'organisation', 'marques', 'plages', 'tout'));

-- Mettre à jour les utilisateurs existants avec les niveaux d'accès par défaut
UPDATE utilisateur 
SET 
    niveau_acces = CASE 
        WHEN type_utilisateur = 'administrateur' THEN 'admin'
        WHEN type_utilisateur = 'utilisateur_authentifie' THEN 'standard'
        ELSE 'basique'
    END,
    portee_donnees = CASE 
        WHEN type_utilisateur = 'administrateur' THEN 'tout'
        ELSE 'personnel'
    END
WHERE niveau_acces IS NULL;
