-- Table: Utilisateur
CREATE TABLE Utilisateur (
    id UUID PRIMARY KEY,
    nom VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    mot_de_passe TEXT,
    type_utilisateur VARCHAR(50)
);

-- Table: Appareil (removed imei field)
CREATE TABLE Appareil (
    id UUID PRIMARY KEY,
    marque VARCHAR(50),
    modele VARCHAR(50),
    emmc VARCHAR(100),
    utilisateur_id UUID REFERENCES Utilisateur(id)
);

-- Table: IMEI (new table for handling multiple IMEIs per device)
CREATE TABLE IMEI (
    id UUID PRIMARY KEY,
    imei_number VARCHAR(20) UNIQUE,
    slot_number INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    appareil_id UUID REFERENCES Appareil(id) NOT NULL
);

-- Table: SIM
CREATE TABLE SIM (
    id UUID PRIMARY KEY,
    iccid VARCHAR(22) UNIQUE,
    operateur VARCHAR(50),
    utilisateur_id UUID REFERENCES Utilisateur(id)
);

-- Table: Recherche
CREATE TABLE Recherche (
    id UUID PRIMARY KEY,
    date_recherche TIMESTAMP,
    imei_recherche VARCHAR(20),
    utilisateur_id UUID REFERENCES Utilisateur(id)
);

-- Table: Notification
CREATE TABLE Notification (
    id UUID PRIMARY KEY,
    type VARCHAR(50),
    contenu TEXT,
    statut VARCHAR(20),
    utilisateur_id UUID REFERENCES Utilisateur(id)
);

-- Table: JournalAudit
CREATE TABLE JournalAudit (
    id UUID PRIMARY KEY,
    action TEXT,
    date TIMESTAMP,
    utilisateur_id UUID REFERENCES Utilisateur(id)
);

-- Table: ImportExport
CREATE TABLE ImportExport (
    id UUID PRIMARY KEY,
    type_operation VARCHAR(50),
    fichier TEXT,
    date TIMESTAMP,
    utilisateur_id UUID REFERENCES Utilisateur(id)
);

-- Create indexes for better performance
CREATE INDEX idx_imei_number ON IMEI(imei_number);
CREATE INDEX idx_appareil_user ON Appareil(utilisateur_id);
CREATE INDEX idx_recherche_imei ON Recherche(imei_recherche);
CREATE INDEX idx_recherche_date ON Recherche(date_recherche);
