-- Migration pour ajouter la table password_reset
-- Date: 2025-08-10

CREATE TABLE password_reset (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    utilisateur_id UUID NOT NULL REFERENCES utilisateur(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    methode_verification TEXT NOT NULL CHECK (methode_verification IN ('email', 'sms')),
    code_verification TEXT,
    email TEXT,
    telephone TEXT,
    utilise BOOLEAN DEFAULT FALSE,
    date_creation TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date_expiration TIMESTAMP WITH TIME ZONE NOT NULL,
    date_utilisation TIMESTAMP WITH TIME ZONE,
    adresse_ip TEXT
);

-- Index pour optimiser les requêtes
CREATE INDEX idx_password_reset_token ON password_reset(token);
CREATE INDEX idx_password_reset_utilisateur_id ON password_reset(utilisateur_id);
CREATE INDEX idx_password_reset_expiration ON password_reset(date_expiration);
CREATE INDEX idx_password_reset_utilise ON password_reset(utilise);

-- Commentaires pour documenter la table
COMMENT ON TABLE password_reset IS 'Table pour gérer les tokens de réinitialisation de mot de passe';
COMMENT ON COLUMN password_reset.token IS 'Token unique pour la réinitialisation';
COMMENT ON COLUMN password_reset.methode_verification IS 'Méthode de vérification: email ou sms';
COMMENT ON COLUMN password_reset.code_verification IS 'Code à 6 chiffres envoyé par email/SMS';
COMMENT ON COLUMN password_reset.utilise IS 'Indique si le token a été utilisé';
COMMENT ON COLUMN password_reset.date_expiration IS 'Date d''expiration du token';
