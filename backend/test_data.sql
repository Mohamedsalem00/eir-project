-- Test data for EIR project with proper access control
-- Run this after schema_postgres.sql and migrate_essential_access.sql

-- Clear existing data
DELETE FROM IMEI;
DELETE FROM Appareil;
DELETE FROM Recherche;
DELETE FROM SIM;
DELETE FROM Notification;
DELETE FROM JournalAudit;
DELETE FROM ImportExport;
DELETE FROM Utilisateur;

-- Create admin user
INSERT INTO Utilisateur (id, nom, email, mot_de_passe, type_utilisateur, access_level, data_scope, is_active)
VALUES (
    gen_random_uuid(),
    'System Administrator',
    'admin@eir-project.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'administrateur',
    'admin',
    'all',
    true
);

-- Create sample regular user
INSERT INTO Utilisateur (id, nom, email, mot_de_passe, type_utilisateur, access_level, data_scope, is_active)
VALUES (
    gen_random_uuid(),
    'Regular User',
    'user@example.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'utilisateur_authentifie',
    'standard',
    'own',
    true
);

-- Create sample insurance company user
INSERT INTO Utilisateur (id, nom, email, mot_de_passe, type_utilisateur, access_level, data_scope, organization, is_active, allowed_brands)
VALUES (
    gen_random_uuid(),
    'Insurance Agent',
    'insurance@company.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'utilisateur_authentifie',
    'limited',
    'brands',
    'SecureInsurance Corp',
    true,
    '["Samsung", "Apple", "Huawei"]'
);

-- Create sample law enforcement user  
INSERT INTO Utilisateur (id, nom, email, mot_de_passe, type_utilisateur, access_level, data_scope, organization, is_active, allowed_imei_ranges)
VALUES (
    gen_random_uuid(),
    'Police Officer',
    'police@cybercrime.gov',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'utilisateur_authentifie',
    'limited',
    'ranges', 
    'Police Cyber Crime Unit',
    true,
    '[{"type": "prefix", "prefix": "35274508", "description": "Investigation case"}]'
);

-- Create sample tech manufacturer user
INSERT INTO Utilisateur (id, nom, email, mot_de_passe, type_utilisateur, access_level, data_scope, organization, is_active, allowed_brands)
VALUES (
    gen_random_uuid(),
    'Tech Manufacturer',
    'manufacturer@techcorp.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'utilisateur_authentifie',
    'standard',
    'brands',
    'TechCorp Manufacturing',
    true,
    '["TechCorp"]'
);

-- Insert sample devices and IMEIs
-- Insert devices first, then their IMEIs
WITH regular_user AS (SELECT id FROM Utilisateur WHERE email = 'user@example.com'),
     manufacturer_user AS (SELECT id FROM Utilisateur WHERE email = 'manufacturer@techcorp.com')

-- Insert Samsung device
INSERT INTO Appareil (id, marque, modele, emmc, utilisateur_id)
SELECT gen_random_uuid(), 'Samsung', 'Galaxy S21', '128GB', regular_user.id
FROM regular_user;

-- Insert Apple device
INSERT INTO Appareil (id, marque, modele, emmc, utilisateur_id)
SELECT gen_random_uuid(), 'Apple', 'iPhone 13', '256GB', regular_user.id
FROM regular_user;

-- Insert TechCorp device
INSERT INTO Appareil (id, marque, modele, emmc, utilisateur_id)
SELECT gen_random_uuid(), 'TechCorp', 'TC-Pro-2024', '512GB', manufacturer_user.id
FROM manufacturer_user;

-- Insert IMEIs for the devices
INSERT INTO IMEI (id, imei_number, slot_number, status, appareil_id)
SELECT 
    gen_random_uuid(),
    '352745080123456',
    1,
    'active',
    a.id
FROM Appareil a 
JOIN Utilisateur u ON a.utilisateur_id = u.id 
WHERE u.email = 'user@example.com' AND a.marque = 'Samsung';

INSERT INTO IMEI (id, imei_number, slot_number, status, appareil_id)
SELECT 
    gen_random_uuid(),
    '354123456789012',
    1,
    'active',
    a.id
FROM Appareil a 
JOIN Utilisateur u ON a.utilisateur_id = u.id 
WHERE u.email = 'user@example.com' AND a.marque = 'Apple';

INSERT INTO IMEI (id, imei_number, slot_number, status, appareil_id)
SELECT 
    gen_random_uuid(),
    '352745080987654',
    1,
    'active',
    a.id
FROM Appareil a 
JOIN Utilisateur u ON a.utilisateur_id = u.id 
WHERE u.email = 'manufacturer@techcorp.com' AND a.marque = 'TechCorp';

-- Insert sample SIM cards
WITH regular_user_id AS (SELECT id FROM Utilisateur WHERE email = 'user@example.com')
INSERT INTO SIM (id, iccid, operateur, utilisateur_id)
SELECT 
    gen_random_uuid(),
    '8934051234567890123',
    'Orange',
    id
FROM regular_user_id;

-- Insert sample search history
WITH regular_user_id AS (SELECT id FROM Utilisateur WHERE email = 'user@example.com')
INSERT INTO Recherche (id, date_recherche, imei_recherche, utilisateur_id)
SELECT 
    gen_random_uuid(),
    NOW() - INTERVAL '1 hour',
    '352745080123456',
    id
FROM regular_user_id;

-- Insert sample notification
WITH admin_user_id AS (SELECT id FROM Utilisateur WHERE email = 'admin@eir-project.com')
INSERT INTO Notification (id, type, contenu, statut, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'system',
    'Database initialized successfully',
    'unread',
    id
FROM admin_user_id;

-- Create audit log entry
WITH admin_user_id AS (SELECT id FROM Utilisateur WHERE email = 'admin@eir-project.com')
INSERT INTO JournalAudit (id, action, date, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'Database initialization completed',
    NOW(),
    id
FROM admin_user_id;

-- Verify the data
SELECT 
    'Data Summary' as info,
    (SELECT COUNT(*) FROM Utilisateur) as users,
    (SELECT COUNT(*) FROM Appareil) as devices,
    (SELECT COUNT(*) FROM IMEI) as imeis,
    (SELECT COUNT(*) FROM SIM) as sims;
