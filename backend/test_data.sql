-- Test data for EIR project with proper access control
-- Run this after schema_postgres.sql

-- Clear existing data in proper order (respecting foreign keys)
DELETE FROM recherche;
DELETE FROM notification;
DELETE FROM journal_audit;
DELETE FROM importexport;
DELETE FROM imei;
DELETE FROM appareil;
DELETE FROM sim;
DELETE FROM utilisateur;
-- Clear TAC data (optional, comment out to keep existing TAC data)
-- DELETE FROM tac_sync_log;
-- DELETE FROM tac_database;

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
    'user@eir.ma',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'utilisateur_authentifie',
    'standard',
    'personnel',
    true
);

-- Create sample operator users
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, organisation, est_actif)
VALUES 
(
    gen_random_uuid(),
    'Operateur Orange',
    'orange@eir.ma',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK',
    'operateur',
    'standard',
    'organisation',
    'Orange Maroc',
    true
),
(
    gen_random_uuid(),
    'Operateur Inwi',
    'inwi@eir.ma',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK',
    'operateur',
    'standard',
    'organisation',
    'Inwi',
    true
);

-- Insert basic TAC data for testing
INSERT INTO tac_database (tac, marque, modele, type_appareil, statut) VALUES
('35326005', 'Samsung', 'Galaxy S23', 'smartphone', 'valide'),
('35692005', 'Apple', 'iPhone 14', 'smartphone', 'valide'),
('86234567', 'Huawei', 'P50 Pro', 'smartphone', 'valide'),
('35847200', 'Xiaomi', 'Mi 12', 'smartphone', 'valide'),
('35404806', 'OnePlus', '10 Pro', 'smartphone', 'valide'),
('99000000', 'TestDevice', 'Test Model', 'test_device', 'test'),
('01194800', 'Apple', 'iPhone 3GS', 'smartphone', 'obsolete')
ON CONFLICT (tac) DO UPDATE SET
    marque = EXCLUDED.marque,
    modele = EXCLUDED.modele,
    type_appareil = EXCLUDED.type_appareil,
    statut = EXCLUDED.statut,
    date_modification = CURRENT_TIMESTAMP;

-- Insert sample devices and IMEIs using a more robust approach
DO $$
DECLARE
    admin_user_id UUID;
    regular_user_id UUID;
    orange_user_id UUID;
    device_id UUID;
BEGIN
    -- Get user IDs
    SELECT id INTO admin_user_id FROM utilisateur WHERE email = 'admin@eir.ma';
    SELECT id INTO regular_user_id FROM utilisateur WHERE email = 'user@eir.ma';
    SELECT id INTO orange_user_id FROM utilisateur WHERE email = 'orange@eir.ma';
    
    -- Insert Samsung device for regular user
    device_id := gen_random_uuid();
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'Samsung', 'Galaxy S23', '256GB', regular_user_id);
    
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES (gen_random_uuid(), '353260051234567', 1, 'actif', device_id);
    
    -- Insert Apple device for Orange operator
    device_id := gen_random_uuid();
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'Apple', 'iPhone 14', '128GB', orange_user_id);
    
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES (gen_random_uuid(), '356920051234567', 1, 'actif', device_id);
    
    -- Insert Huawei device for admin testing
    device_id := gen_random_uuid();
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'Huawei', 'P50 Pro', '512GB', admin_user_id);
    
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES (gen_random_uuid(), '862345671234567', 1, 'actif', device_id);
    
    -- Insert test device with multiple IMEIs
    device_id := gen_random_uuid();
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'OnePlus', '10 Pro', '128GB', regular_user_id);
    
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES 
    (gen_random_uuid(), '354048061234567', 1, 'actif', device_id),
    (gen_random_uuid(), '354048061234568', 2, 'actif', device_id);
    
    -- Insert some test IMEIs for TAC validation testing
    device_id := gen_random_uuid();
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'TestDevice', 'Test Model', '64GB', admin_user_id);
    
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES 
    (gen_random_uuid(), '990000001234567', 1, 'suspect', device_id),
    (gen_random_uuid(), '011948001234567', 1, 'bloque', device_id);
END $$;

-- Insert sample SIM cards
INSERT INTO sim (id, iccid, operateur, utilisateur_id)
SELECT 
    gen_random_uuid(),
    '89212070000000001234',
    'Orange',
    u.id
FROM utilisateur u WHERE u.email = 'orange@eir.ma';

INSERT INTO sim (id, iccid, operateur, utilisateur_id)
SELECT 
    gen_random_uuid(),
    '89212040000000001234',
    'Inwi',
    u.id
FROM utilisateur u WHERE u.email = 'inwi@eir.ma';

-- Insert sample search history
INSERT INTO recherche (id, date_recherche, imei_recherche, utilisateur_id)
SELECT 
    gen_random_uuid(),
    NOW() - INTERVAL '1 hour',
    '353260051234567',
    u.id
FROM utilisateur u WHERE u.email = 'user@eir.ma';

INSERT INTO recherche (id, date_recherche, imei_recherche, utilisateur_id)
SELECT 
    gen_random_uuid(),
    NOW() - INTERVAL '30 minutes',
    '356920051234567',
    u.id
FROM utilisateur u WHERE u.email = 'orange@eir.ma';

-- Insert sample notifications
INSERT INTO notification (id, type, contenu, statut, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'system',
    'Base de données EIR initialisée avec succès',
    'non_lu',
    u.id
FROM utilisateur u WHERE u.email = 'admin@eir.ma';

INSERT INTO notification (id, type, contenu, statut, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'info',
    'Bienvenue dans le système EIR',
    'non_lu',
    u.id
FROM utilisateur u WHERE u.email = 'user@eir.ma';

-- Create audit log entries
INSERT INTO journal_audit (id, action, date, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'SYSTEM: Initialisation de la base de données terminée',
    NOW(),
    u.id
FROM utilisateur u WHERE u.email = 'admin@eir.ma';

-- Insert sample import/export record
INSERT INTO importexport (id, type_operation, fichier, date, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'import',
    'initial_data_setup.sql',
    NOW(),
    u.id
FROM utilisateur u WHERE u.email = 'admin@eir.ma';

-- Verify the data and show summary
SELECT 
    'Résumé des données de test' as info,
    (SELECT COUNT(*) FROM utilisateur) as utilisateurs,
    (SELECT COUNT(*) FROM appareil) as appareils,
    (SELECT COUNT(*) FROM imei) as imeis,
    (SELECT COUNT(*) FROM sim) as cartes_sim,
    (SELECT COUNT(*) FROM recherche) as recherches,
    (SELECT COUNT(*) FROM tac_database) as entries_tac,
    (SELECT COUNT(*) FROM notification) as notifications;

-- Show test accounts
SELECT 
    'Comptes de test disponibles:' as info,
    email,
    type_utilisateur,
    niveau_acces,
    organisation
FROM utilisateur 
ORDER BY type_utilisateur DESC, email;
