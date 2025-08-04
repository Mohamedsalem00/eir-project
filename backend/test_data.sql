-- Test data for EIR project with proper access control
-- Run this after schema_postgres.sql and migrate_essential_access.sql

-- Clear existing data
DELETE FROM imei;
DELETE FROM appareil;
DELETE FROM recherche;
DELETE FROM sim;
DELETE FROM notification;
DELETE FROM journal_audit;
DELETE FROM importexport;
DELETE FROM utilisateur;

-- Create admin user
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, est_actif)
VALUES (
    gen_random_uuid(),
    'System Administrator',
    'admin@eir-project.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'administrateur',
    'admin',
    'tout',
    true
);

-- Create sample regular user
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, est_actif)
VALUES (
    gen_random_uuid(),
    'Regular User',
    'user@example.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'utilisateur_authentifie',
    'standard',
    'personnel',
    true
);

-- Create sample insurance company user
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, organisation, est_actif, marques_autorisees)
VALUES (
    gen_random_uuid(),
    'Insurance Agent',
    'insurance@company.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'utilisateur_authentifie',
    'limite',
    'marques',
    'SecureInsurance Corp',
    true,
    '["Samsung", "Apple", "Huawei"]'
);

-- Create sample law enforcement user  
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, organisation, est_actif, plages_imei_autorisees)
VALUES (
    gen_random_uuid(),
    'Police Officer',
    'police@cybercrime.gov',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'utilisateur_authentifie',
    'limite',
    'plages', 
    'Police Cyber Crime Unit',
    true,
    '[{"type": "prefix", "prefix": "35274508", "description": "Investigation case"}]'
);

-- Create sample tech manufacturer user
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, organisation, est_actif, marques_autorisees)
VALUES (
    gen_random_uuid(),
    'Tech Manufacturer',
    'manufacturer@techcorp.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'utilisateur_authentifie',
    'standard',
    'marques',
    'TechCorp Manufacturing',
    true,
    '["TechCorp"]'
);

-- Insert sample devices and IMEIs
-- Insert devices first, then their IMEIs

-- Insert Samsung device
INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
SELECT gen_random_uuid(), 'Samsung', 'Galaxy S21', '128GB', u.id
FROM utilisateur u WHERE u.email = 'user@example.com';

-- Insert Apple device
INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
SELECT gen_random_uuid(), 'Apple', 'iPhone 13', '256GB', u.id
FROM utilisateur u WHERE u.email = 'user@example.com';

-- Insert TechCorp device
INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
SELECT gen_random_uuid(), 'TechCorp', 'TC-Pro-2024', '512GB', u.id
FROM utilisateur u WHERE u.email = 'manufacturer@techcorp.com';

-- Insert IMEIs for the devices
INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
SELECT 
    gen_random_uuid(),
    '352745080123456',
    1,
    'active',
    a.id
FROM appareil a 
JOIN utilisateur u ON a.utilisateur_id = u.id 
WHERE u.email = 'user@example.com' AND a.marque = 'Samsung';

INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
SELECT 
    gen_random_uuid(),
    '354123456789012',
    1,
    'active',
    a.id
FROM appareil a 
JOIN utilisateur u ON a.utilisateur_id = u.id 
WHERE u.email = 'user@example.com' AND a.marque = 'Apple';

INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
SELECT 
    gen_random_uuid(),
    '352745080987654',
    1,
    'active',
    a.id
FROM appareil a 
JOIN utilisateur u ON a.utilisateur_id = u.id 
WHERE u.email = 'manufacturer@techcorp.com' AND a.marque = 'TechCorp';

-- Insert sample SIM cards
INSERT INTO sim (id, iccid, operateur, utilisateur_id)
SELECT 
    gen_random_uuid(),
    '8934051234567890123',
    'Orange',
    u.id
FROM utilisateur u WHERE u.email = 'user@example.com';

-- Insert sample search history
INSERT INTO recherche (id, date_recherche, imei_recherche, utilisateur_id)
SELECT 
    gen_random_uuid(),
    NOW() - INTERVAL '1 hour',
    '352745080123456',
    u.id
FROM utilisateur u WHERE u.email = 'user@example.com';

-- Insert sample notification
INSERT INTO notification (id, type, contenu, statut, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'system',
    'Database initialized successfully',
    'unread',
    u.id
FROM utilisateur u WHERE u.email = 'admin@eir-project.com';

-- Create audit log entry
INSERT INTO journal_audit (id, action, date, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'Database initialization completed',
    NOW(),
    u.id
FROM utilisateur u WHERE u.email = 'admin@eir-project.com';

-- Verify the data
SELECT 
    'Data Summary' as info,
    (SELECT COUNT(*) FROM utilisateur) as users,
    (SELECT COUNT(*) FROM appareil) as devices,
    (SELECT COUNT(*) FROM imei) as imeis,
    (SELECT COUNT(*) FROM sim) as sims;
