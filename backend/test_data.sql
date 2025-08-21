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
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, est_actif, email_valide, numero_telephone)
VALUES (
    gen_random_uuid(),
    'System Administrator',
    'eirrproject@gmail.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'administrateur',
    'admin',
    'tout',
    true,
    true,
    '+212600000001'
);

-- Create sample regular user
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, est_actif, email_valide, numero_telephone)
VALUES (
    gen_random_uuid(),
    'Regular User',
    'sidis9828@gmail.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK', -- admin123
    'utilisateur_authentifie',
    'standard',
    'personnel',
    true,
    false,
    '+212600000002'
);

-- Create sample operator users
INSERT INTO utilisateur (id, nom, email, mot_de_passe, type_utilisateur, niveau_acces, portee_donnees, organisation, est_actif, email_valide, numero_telephone)
VALUES 
(
    gen_random_uuid(),
    'Operateur Orange',
    'devvmrr@gmail.com',
    '$2b$12$8o8ZiuHJ8JP7QLLiKFrQUuyfErAhYSVFnuHgRnOkkvougjj1ST6yK',
    'operateur',
    'standard',
    'organisation',
    'Orange Maroc',
    true,
    false,
    '+212600000003'
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
    true,
    false,
    '+212600000004'
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
    SELECT id INTO admin_user_id FROM utilisateur WHERE email = 'eirrproject@gmail.com';
    SELECT id INTO regular_user_id FROM utilisateur WHERE email = 'sidis9828@gmail.com';
    SELECT id INTO orange_user_id FROM utilisateur WHERE email = 'devvmrr@gmail.com';
    
    -- Insert Samsung device for regular user
    -- IMEI: 353260051234567 -> TAC: 35326005, SNR: 123456, Luhn: 7
    device_id := gen_random_uuid();
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'Samsung', 'Galaxy S23', '256GB', regular_user_id);
    
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES (gen_random_uuid(), '353260051234567', 1, 'active', device_id);
    -- numero_serie '123456' will be auto-populated via trigger
    
    -- Insert Apple device for Orange operator
    -- IMEI: 356920051789012 -> TAC: 35692005, SNR: 178901, Luhn: 2
    device_id := gen_random_uuid();
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'Apple', 'iPhone 14', '128GB', orange_user_id);
    
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES (gen_random_uuid(), '356920051789012', 1, 'active', device_id);
    -- numero_serie '178901' will be auto-populated via trigger
    
    -- Insert Huawei device for admin testing
    -- IMEI: 862345673456789 -> TAC: 86234567, SNR: 345678, Luhn: 9
    device_id := gen_random_uuid();
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'Huawei', 'P50 Pro', '512GB', admin_user_id);
    
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES (gen_random_uuid(), '862345673456789', 1, 'active', device_id);
    -- numero_serie '345678' will be auto-populated via trigger
    
    -- Insert test device with multiple IMEIs (dual-SIM)
    -- IMEI1: 354048061357924 -> TAC: 35404806, SNR: 135792, Luhn: 4
    -- IMEI2: 354048061468035 -> TAC: 35404806, SNR: 146803, Luhn: 5
    device_id := gen_random_uuid();
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'OnePlus', '10 Pro', '128GB', regular_user_id);
    
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES 
    (gen_random_uuid(), '354048061357924', 1, 'active', device_id),
    (gen_random_uuid(), '354048061468035', 2, 'active', device_id);
    -- numero_serie '135792' will be auto-populated from first IMEI (slot 1)
    
    -- Insert some test IMEIs for TAC validation testing
    -- IMEI1: 990000001234567 -> TAC: 99000000, SNR: 123456, Luhn: 7 (test device)
    -- IMEI2: 011948009876543 -> TAC: 01194800, SNR: 987654, Luhn: 3 (obsolete device)
    device_id := gen_random_uuid();
    INSERT INTO appareil (id, marque, modele, emmc, utilisateur_id)
    VALUES (device_id, 'TestDevice', 'Test Model', '64GB', admin_user_id);
    
    INSERT INTO imei (id, numero_imei, numero_slot, statut, appareil_id)
    VALUES 
    (gen_random_uuid(), '990000001234567', 1, 'suspect', device_id),
    (gen_random_uuid(), '011948009876543', 2, 'bloque', device_id);
    -- numero_serie '123456' will be auto-populated from first IMEI (slot 1)
END $$;

-- Insert sample SIM cards
INSERT INTO sim (id, iccid, operateur, utilisateur_id)
SELECT 
    gen_random_uuid(),
    '89212070000000001234',
    'Orange',
    u.id
FROM utilisateur u WHERE u.email = 'devvmrr@gmail.com';

INSERT INTO sim (id, iccid, operateur, utilisateur_id)
SELECT 
    gen_random_uuid(),
    '89212040000000001234',
    'Inwi',
    u.id
FROM utilisateur u WHERE u.email = 'inwi@eir.ma';

-- Insert sample search history with updated IMEI numbers
INSERT INTO recherche (id, date_recherche, imei_recherche, utilisateur_id)
SELECT 
    gen_random_uuid(),
    NOW() - INTERVAL '1 hour',
    '353260051234567', -- Samsung Galaxy S23 - SNR: 123456
    u.id
FROM utilisateur u WHERE u.email = 'sidis9828@gmail.com';

INSERT INTO recherche (id, date_recherche, imei_recherche, utilisateur_id)
SELECT 
    gen_random_uuid(),
    NOW() - INTERVAL '30 minutes',
    '356920051789012', -- Apple iPhone 14 - SNR: 178901
    u.id
FROM utilisateur u WHERE u.email = 'devvmrr@gmail.com';

-- Insert sample notifications using new notification system structure
INSERT INTO notification (id, type, destinataire, sujet, contenu, statut, source, utilisateur_id, date_creation)
SELECT 
    gen_random_uuid(),
    'email',
    'eirrproject@gmail.com',
    '🔧 Système EIR - Base de données initialisée',
    'Bonjour Administrator,

La base de données EIR a été initialisée avec succès.

📊 RÉSUMÉ DE L''INITIALISATION:
- Utilisateurs créés: 4
- Appareils de test: 5
- IMEI de test: 7
- Données TAC: 7 entrées

Le système est maintenant prêt à être utilisé.

🔗 Accès: http://localhost:8000
📚 Documentation: ./NOTIFICATIONS_QUICK_START.md

---
EIR Project - Système d''initialisation automatique',
    'en_attente',
    'system',
    u.id,
    NOW()
FROM utilisateur u WHERE u.email = 'eirrproject@gmail.com';

INSERT INTO notification (id, type, destinataire, sujet, contenu, statut, source, utilisateur_id, date_creation)
SELECT 
    gen_random_uuid(),
    'email',
    'sidis9828@gmail.com',
    '🎉 Bienvenue dans EIR Project',
    'Bonjour Regular User,

Bienvenue dans le système EIR Project !

📱 VOS APPAREILS:
Vous avez 2 appareils enregistrés dans le système :
- Samsung Galaxy S23 (IMEI: 353260051234567, SNR: 123456)
- OnePlus 10 Pro (IMEI: 354048061357924, 354048061468035, SNR: 135792)

🔍 FONCTIONNALITÉS DISPONIBLES:
- Vérification d''IMEI en temps réel avec extraction automatique du SNR
- Gestion de vos appareils avec numéros de série uniques
- Historique des recherches
- Notifications automatiques

🆕 NOUVELLES FONCTIONNALITÉS:
- Extraction automatique du Serial Number (SNR) depuis l''IMEI
- Identification unique de chaque appareil physique
- Validation TAC + SNR pour sécurité renforcée

🌐 Portail: http://localhost:8000
📞 Support: contact@eir-project.com

---
L''équipe EIR Project',
    'en_attente',
    'system',
    u.id,
    NOW()
FROM utilisateur u WHERE u.email = 'sidis9828@gmail.com';

-- Notification pour l'opérateur Orange
INSERT INTO notification (id, type, destinataire, sujet, contenu, statut, source, utilisateur_id, date_creation)
SELECT 
    gen_random_uuid(),
    'email',
    'devvmrr@gmail.com',
    '📊 Rapport d''activité EIR - Orange Maroc',
    'Bonjour Operateur Orange,

Votre rapport d''activité EIR pour votre organisation Orange Maroc.

📱 VOS APPAREILS ENREGISTRÉS:
- Apple iPhone 14 (IMEI: 356920051789012, SNR: 178901)
- Statut: active et validé
- TAC: 35692005 (Apple iPhone 14 validé)

🔍 ACTIVITÉ RÉCENTE:
- 1 recherche IMEI effectuée
- 1 appareil vérifié avec succès
- Taux de validité: 100%

📈 STATISTIQUES ORGANISATION:
- Appareils total: 1
- IMEI actifs: 1
- Dernière activité: Il y a 30 minutes

🔒 SÉCURITÉ:
Aucune alerte de sécurité détectée.

---
EIR Project - Rapport automatique',
    'en_attente',
    'system',
    u.id,
    NOW() - INTERVAL '15 minutes'
FROM utilisateur u WHERE u.email = 'devvmrr@gmail.com';

-- Notification de test pour SMS (sera traitée en mode console)
INSERT INTO notification (id, type, destinataire, contenu, statut, source, utilisateur_id, date_creation, tentative)
SELECT 
    gen_random_uuid(),
    'sms',
    '+33123456789',
    '🔔 EIR Project: Votre IMEI 353260051234567 (SNR: 123456) a été vérifié avec succès. Appareil: Samsung Galaxy S23. Plus d''infos: http://eir.ma/v/353260051234567',
    'en_attente',
    'system',
    u.id,
    NOW() - INTERVAL '5 minutes',
    0
FROM utilisateur u WHERE u.email = 'sidis9828@gmail.com';

-- Notification d'alerte sécurité (exemple)
INSERT INTO notification (id, type, destinataire, sujet, contenu, statut, source, utilisateur_id, date_creation, tentative)
SELECT 
    gen_random_uuid(),
    'email',
    'eirrproject@gmail.com',
    '🚨 ALERTE SÉCURITÉ EIR - IMEI Suspect Détecté',
    'ALERTE SÉCURITÉ URGENTE

Un IMEI suspect a été détecté dans le système.

🚨 DÉTAILS DE L''INCIDENT:
- IMEI: 990000001234567
- Statut: Suspect
- TAC: 99000000 (Code de test)
- Appareil: TestDevice Test Model
- Utilisateur: System Administrator
- Détection: Validation automatique

⚠️ ACTIONS REQUISES:
1. Vérifier l''origine de cet IMEI
2. Confirmer qu''il s''agit d''un appareil de test
3. Mettre à jour le statut si nécessaire

🔍 Ce message a été généré automatiquement par le système de détection EIR.

---
EIR Project - Système d''alerte automatique',
    'en_attente',
    'system',
    u.id,
    NOW() - INTERVAL '1 hour',
    0
FROM utilisateur u WHERE u.email = 'eirrproject@gmail.com';

-- Create audit log entries
INSERT INTO journal_audit (id, action, date, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'SYSTEM: Initialisation de la base de données terminée',
    NOW(),
    u.id
FROM utilisateur u WHERE u.email = 'eirrproject@gmail.com';

-- Insert sample import/export record
INSERT INTO importexport (id, type_operation, fichier, date, utilisateur_id)
SELECT 
    gen_random_uuid(),
    'import',
    'initial_data_setup.sql',
    NOW(),
    u.id
FROM utilisateur u WHERE u.email = 'eirrproject@gmail.com';

-- Verify the data and show summary with auto-populated serial numbers
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

-- Verify auto-populated serial numbers from IMEI
SELECT 
    'Vérification auto-population SNR:' as info,
    a.marque,
    a.modele,
    a.numero_serie as snr_auto_extrait,
    i.numero_imei,
    SUBSTRING(i.numero_imei FROM 9 FOR 6) as snr_from_imei,
    CASE 
        WHEN a.numero_serie = SUBSTRING(i.numero_imei FROM 9 FOR 6) THEN '✅ Correct'
        ELSE '❌ Erreur'
    END as verification_status
FROM appareil a
JOIN imei i ON a.id = i.appareil_id AND i.numero_slot = 1
ORDER BY a.marque, a.modele;

-- Show IMEI structure breakdown for educational purposes
SELECT 
    'Structure IMEI de test:' as info,
    i.numero_imei,
    SUBSTRING(i.numero_imei FROM 1 FOR 8) as tac_code,
    SUBSTRING(i.numero_imei FROM 9 FOR 6) as snr_serial,
    SUBSTRING(i.numero_imei FROM 15 FOR 1) as luhn_check,
    a.marque || ' ' || a.modele as appareil,
    a.numero_serie as snr_stored
FROM imei i
JOIN appareil a ON i.appareil_id = a.id
ORDER BY i.numero_imei;
