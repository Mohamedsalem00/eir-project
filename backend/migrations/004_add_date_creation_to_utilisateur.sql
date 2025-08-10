-- Migration pour ajouter le champ date_creation à la table utilisateur
-- Date: 2025-08-10

-- Ajouter la colonne date_creation avec une valeur par défaut
ALTER TABLE utilisateur 
ADD COLUMN date_creation TIMESTAMP DEFAULT NOW();

-- Mettre à jour les utilisateurs existants avec la date actuelle
UPDATE utilisateur 
SET date_creation = NOW() 
WHERE date_creation IS NULL;

-- Rendre la colonne non-nullable après la mise à jour
ALTER TABLE utilisateur 
ALTER COLUMN date_creation SET NOT NULL;

-- Ajouter un index pour optimiser les requêtes sur la date de création
CREATE INDEX idx_utilisateur_date_creation ON utilisateur(date_creation);

-- Commentaire pour documenter le champ
COMMENT ON COLUMN utilisateur.date_creation IS 'Date et heure de création du compte utilisateur';
