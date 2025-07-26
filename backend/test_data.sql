-- Test data for EIR Project Database - Updated Schema

-- Insert test users with working passwords
-- All users have password: "password123"
-- Using fresh generated bcrypt hash
-- Removed visiteur_anonyme as anonymous users don't need database records

INSERT INTO Utilisateur (id, nom, email, mot_de_passe, type_utilisateur) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'Admin User', 'admin@eir.com', '$2b$12$/p3EJSTtw.jEreZ9hqrHHOlHqjQ.ZkdH4PIU0807wdgMOo4R6TSWC', 'administrateur'),
('550e8400-e29b-41d4-a716-446655440002', 'John Doe', 'john.doe@email.com', '$2b$12$/p3EJSTtw.jEreZ9hqrHHOlHqjQ.ZkdH4PIU0807wdgMOo4R6TSWC', 'utilisateur_authentifie'),
('550e8400-e29b-41d4-a716-446655440003', 'Jane Smith', 'jane.smith@email.com', '$2b$12$/p3EJSTtw.jEreZ9hqrHHOlHqjQ.ZkdH4PIU0807wdgMOo4R6TSWC', 'utilisateur_authentifie');

-- Insert test devices (Appareil) - WITHOUT imei field
INSERT INTO Appareil (id, marque, modele, emmc, utilisateur_id) VALUES
('660e8400-e29b-41d4-a716-446655440001', 'Apple', 'iPhone 13', 'A15_EMMC_128GB', '550e8400-e29b-41d4-a716-446655440002'),
('660e8400-e29b-41d4-a716-446655440002', 'Samsung', 'Galaxy S21', 'EXYNOS_EMMC_256GB', '550e8400-e29b-41d4-a716-446655440003'),
('660e8400-e29b-41d4-a716-446655440003', 'Google', 'Pixel 6', 'TENSOR_EMMC_128GB', '550e8400-e29b-41d4-a716-446655440002'),
('660e8400-e29b-41d4-a716-446655440004', 'OnePlus', '9 Pro', 'SNAPDRAGON_EMMC_256GB', '550e8400-e29b-41d4-a716-446655440003'),
('660e8400-e29b-41d4-a716-446655440005', 'Xiaomi', 'Mi 11', 'SNAPDRAGON_EMMC_128GB', NULL),
('660e8400-e29b-41d4-a716-446655440006', 'Unknown', 'Test Device', 'TEST_EMMC', NULL),
('660e8400-e29b-41d4-a716-446655440007', 'Blacklisted', 'Stolen Phone', 'BLOCKED_EMMC', NULL);

-- Insert IMEI records (separate table)
INSERT INTO IMEI (id, imei_number, slot_number, status, appareil_id) VALUES
-- Single SIM devices
('cc0e8400-e29b-41d4-a716-446655440001', '123456789012345', 1, 'active', '660e8400-e29b-41d4-a716-446655440001'),
('cc0e8400-e29b-41d4-a716-446655440002', '234567890123456', 1, 'active', '660e8400-e29b-41d4-a716-446655440002'),
('cc0e8400-e29b-41d4-a716-446655440003', '345678901234567', 1, 'active', '660e8400-e29b-41d4-a716-446655440003'),
-- Dual SIM device (OnePlus 9 Pro)
('cc0e8400-e29b-41d4-a716-446655440004', '456789012345678', 1, 'active', '660e8400-e29b-41d4-a716-446655440004'),
('cc0e8400-e29b-41d4-a716-446655440005', '456789012345679', 2, 'active', '660e8400-e29b-41d4-a716-446655440004'),
-- Other devices
('cc0e8400-e29b-41d4-a716-446655440006', '567890123456789', 1, 'active', '660e8400-e29b-41d4-a716-446655440005'),
('cc0e8400-e29b-41d4-a716-446655440007', '999888777666555', 1, 'unknown', '660e8400-e29b-41d4-a716-446655440006'),
('cc0e8400-e29b-41d4-a716-446655440008', '111222333444555', 1, 'blocked', '660e8400-e29b-41d4-a716-446655440007');

-- Insert test searches with more recent dates
INSERT INTO Recherche (id, date_recherche, imei_recherche, utilisateur_id) VALUES
('880e8400-e29b-41d4-a716-446655440001', '2024-12-15 10:30:00', '123456789012345', '550e8400-e29b-41d4-a716-446655440002'),
('880e8400-e29b-41d4-a716-446655440002', '2024-12-15 11:45:00', '234567890123456', '550e8400-e29b-41d4-a716-446655440003'),
('880e8400-e29b-41d4-a716-446655440003', '2024-12-15 14:20:00', '999888777666555', '550e8400-e29b-41d4-a716-446655440002'),
('880e8400-e29b-41d4-a716-446655440004', '2024-12-16 09:15:00', '345678901234567', '550e8400-e29b-41d4-a716-446655440001'),
('880e8400-e29b-41d4-a716-446655440005', '2024-12-16 16:30:00', '111222333444555', NULL), -- Anonymous search
('880e8400-e29b-41d4-a716-446655440006', '2024-12-17 10:00:00', '000000000000000', '550e8400-e29b-41d4-a716-446655440002'),
('880e8400-e29b-41d4-a716-446655440007', '2024-12-17 11:00:00', '123123123123123', NULL); -- Anonymous search

-- Insert test SIM cards
INSERT INTO SIM (id, iccid, operateur, utilisateur_id) VALUES
('770e8400-e29b-41d4-a716-446655440001', '89332402001234567890', 'Orange', '550e8400-e29b-41d4-a716-446655440002'),
('770e8400-e29b-41d4-a716-446655440002', '89332402001234567891', 'SFR', '550e8400-e29b-41d4-a716-446655440003'),
('770e8400-e29b-41d4-a716-446655440003', '89332402001234567892', 'Bouygues', '550e8400-e29b-41d4-a716-446655440002'),
('770e8400-e29b-41d4-a716-446655440004', '89332402001234567893', 'Free', '550e8400-e29b-41d4-a716-446655440003'),
('770e8400-e29b-41d4-a716-446655440005', '89332402001234567894', 'Orange', NULL);

-- Insert test notifications
INSERT INTO Notification (id, type, contenu, statut, utilisateur_id) VALUES
('990e8400-e29b-41d4-a716-446655440001', 'email', 'Bienvenue sur la plateforme EIR', 'envoyé', '550e8400-e29b-41d4-a716-446655440002'),
('990e8400-e29b-41d4-a716-446655440002', 'sms', 'Code de vérification: 123456', 'envoyé', '550e8400-e29b-41d4-a716-446655440003'),
('990e8400-e29b-41d4-a716-446655440003', 'email', 'Nouvel appareil détecté sur votre compte', 'en_attente', '550e8400-e29b-41d4-a716-446655440002'),
('990e8400-e29b-41d4-a716-446655440004', 'sms', 'Alerte sécurité: connexion suspecte', 'échoué', '550e8400-e29b-41d4-a716-446655440003'),
('990e8400-e29b-41d4-a716-446655440005', 'email', 'Rapport mensuel des recherches', 'envoyé', '550e8400-e29b-41d4-a716-446655440001');

-- Insert test audit logs with recent dates
INSERT INTO JournalAudit (id, action, date, utilisateur_id) VALUES
('aa0e8400-e29b-41d4-a716-446655440001', 'Connexion utilisateur', '2024-12-15 08:00:00', '550e8400-e29b-41d4-a716-446655440002'),
('aa0e8400-e29b-41d4-a716-446655440002', 'Recherche IMEI: 123456789012345', '2024-12-15 10:30:00', '550e8400-e29b-41d4-a716-446655440002'),
('aa0e8400-e29b-41d4-a716-446655440003', 'Ajout nouvel appareil', '2024-12-15 12:15:00', '550e8400-e29b-41d4-a716-446655440003'),
('aa0e8400-e29b-41d4-a716-446655440004', 'Modification profil utilisateur', '2024-12-16 14:45:00', '550e8400-e29b-41d4-a716-446655440002'),
('aa0e8400-e29b-41d4-a716-446655440005', 'Export données CSV', '2024-12-16 16:20:00', '550e8400-e29b-41d4-a716-446655440001');

-- Insert test import/export operations - COMPLETELY CLEAN (no duplicates at all)
INSERT INTO ImportExport (id, type_operation, fichier, date, utilisateur_id) VALUES
('bb0e8400-e29b-41d4-a716-446655440001', 'import', 'imei_batch_001.csv', '2024-12-10 09:00:00', '550e8400-e29b-41d4-a716-446655440001'),
('bb0e8400-e29b-41d4-a716-446655440002', 'export', 'recherches_decembre.json', '2024-12-15 17:30:00', '550e8400-e29b-41d4-a716-446655440001'),
('bb0e8400-e29b-41d4-a716-446655440003', 'import', 'sim_cards_batch.csv', '2024-12-12 11:20:00', '550e8400-e29b-41d4-a716-446655440001'),
('bb0e8400-e29b-41d4-a716-446655440004', 'export', 'appareils_utilisateurs.csv', '2024-12-16 10:15:00', '550e8400-e29b-41d4-a716-446655440002'),
('bb0e8400-e29b-41d4-a716-446655440005', 'import', 'users_update.json', '2024-12-14 15:45:00', '550e8400-e29b-41d4-a716-446655440001');