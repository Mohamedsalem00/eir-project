-- Table: utilisateur (Enhanced with minimal access control fields)
CREATE TABLE utilisateur (
    id UUID PRIMARY KEY,
    nom VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    mot_de_passe TEXT,
    type_utilisateur VARCHAR(50),
    -- Essential access control fields
    access_level VARCHAR(50) DEFAULT 'basic',
    data_scope VARCHAR(50) DEFAULT 'own',
    organization VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    allowed_brands JSONB DEFAULT '[]',
    allowed_imei_ranges JSONB DEFAULT '[]'
);

-- Table: appareil (removed imei field)
CREATE TABLE appareil (
    id UUID PRIMARY KEY,
    marque VARCHAR(50),
    modele VARCHAR(50),
    emmc VARCHAR(100),
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Table: imei (new table for handling multiple IMEIs per device)
CREATE TABLE imei (
    id UUID PRIMARY KEY,
    imei_number VARCHAR(20) UNIQUE,
    slot_number INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    appareil_id UUID REFERENCES appareil(id) NOT NULL
);

-- Table: sim
CREATE TABLE sim (
    id UUID PRIMARY KEY,
    iccid VARCHAR(22) UNIQUE,
    operateur VARCHAR(50),
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Table: recherche
CREATE TABLE recherche (
    id UUID PRIMARY KEY,
    date_recherche TIMESTAMP,
    imei_recherche VARCHAR(20),
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Table: Notification
CREATE TABLE notification (
    id UUID PRIMARY KEY,
    type VARCHAR(50),
    contenu TEXT,
    statut VARCHAR(20),
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Table: journal_audit (lowercase to match SQLAlchemy model)
CREATE TABLE journal_audit (
    id UUID PRIMARY KEY,
    action TEXT,
    date TIMESTAMP,
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Table: ImportExport
CREATE TABLE importexport (
    id UUID PRIMARY KEY,
    type_operation VARCHAR(50),
    fichier TEXT,
    date TIMESTAMP,
    utilisateur_id UUID REFERENCES utilisateur(id)
);

-- Create indexes for better performance
CREATE INDEX idx_imei_number ON imei(imei_number);
CREATE INDEX idx_appareil_user ON appareil(utilisateur_id);
CREATE INDEX idx_recherche_imei ON recherche(imei_recherche);
CREATE INDEX idx_recherche_date ON recherche(date_recherche);

-- Essential indexes for access control
CREATE INDEX idx_utilisateur_access_level ON utilisateur(access_level);
CREATE INDEX idx_utilisateur_organization ON utilisateur(organization);
CREATE INDEX idx_utilisateur_is_active ON utilisateur(is_active);
CREATE INDEX idx_utilisateur_allowed_brands ON utilisateur USING GIN(allowed_brands) WHERE allowed_brands != '[]';

-- Add constraints for data integrity
ALTER TABLE utilisateur ADD CONSTRAINT chk_access_level 
CHECK (access_level IN ('visitor', 'basic', 'limited', 'standard', 'elevated', 'admin'));

ALTER TABLE utilisateur ADD CONSTRAINT chk_data_scope 
CHECK (data_scope IN ('own', 'organization', 'brands', 'ranges', 'all'));

-- Update existing users with default access levels
UPDATE utilisateur 
SET 
    access_level = CASE 
        WHEN type_utilisateur = 'administrateur' THEN 'admin'
        WHEN type_utilisateur = 'utilisateur_authentifie' THEN 'standard'
        ELSE 'basic'
    END,
    data_scope = CASE 
        WHEN type_utilisateur = 'administrateur' THEN 'all'
        ELSE 'own'
    END
WHERE access_level IS NULL;
