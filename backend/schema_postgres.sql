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
    date_creation TIMESTAMP DEFAULT NOW(),
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
    type VARCHAR(50), -- email, sms
    destinataire VARCHAR(255), -- numéro de téléphone ou adresse email
    sujet VARCHAR(255), -- pour email
    contenu TEXT,
    statut VARCHAR(20) DEFAULT 'en_attente', -- en_attente, envoyé, échoué
    tentative INT DEFAULT 0,
    erreur TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_envoi TIMESTAMP,
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

-- Table : tac_database (Base de données des codes TAC - Type Allocation Code)
CREATE TABLE tac_database (
    tac VARCHAR(8) PRIMARY KEY,
    marque VARCHAR(100) NOT NULL,
    modele VARCHAR(100) NOT NULL,
    annee_sortie INTEGER,
    type_appareil VARCHAR(50) DEFAULT 'smartphone',
    statut VARCHAR(20) DEFAULT 'valide',
    raison VARCHAR(200),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour les performances de la table TAC
CREATE INDEX idx_tac_marque ON tac_database(marque);
CREATE INDEX idx_tac_statut ON tac_database(statut);
CREATE INDEX idx_tac_type_appareil ON tac_database(type_appareil);

-- Contraintes pour l'intégrité des données TAC
ALTER TABLE tac_database ADD CONSTRAINT chk_tac_statut 
CHECK (statut IN ('valide', 'invalide', 'bloque', 'test', 'obsolete'));

ALTER TABLE tac_database ADD CONSTRAINT chk_tac_type_appareil 
CHECK (type_appareil IN ('smartphone', 'feature_phone', 'tablet', 'iot_device', 'test_device'));

-- Fonction pour extraire le TAC d'un IMEI
CREATE OR REPLACE FUNCTION extraire_tac_depuis_imei(numero_imei VARCHAR) 
RETURNS VARCHAR AS $$
BEGIN
    -- Extraire les 8 premiers chiffres comme TAC
    RETURN SUBSTRING(numero_imei FROM 1 FOR 8);
END;
$$ LANGUAGE plpgsql;

-- Fonction pour valider un IMEI avec la base TAC
CREATE OR REPLACE FUNCTION valider_imei_avec_tac(numero_imei VARCHAR) 
RETURNS JSONB AS $$
DECLARE
    code_tac VARCHAR(8);
    info_tac RECORD;
    resultat JSONB;
    luhn_valide BOOLEAN;
BEGIN
    -- Clean and validate IMEI format
    numero_imei := REGEXP_REPLACE(numero_imei, '[^0-9]', '', 'g');
    
    -- Basic IMEI length validation
    IF LENGTH(numero_imei) NOT BETWEEN 14 AND 16 THEN
        RETURN jsonb_build_object(
            'valide', false,
            'erreur', 'IMEI doit contenir 14-16 chiffres',
            'imei', numero_imei
        );
    END IF;
    
    -- Extract TAC (first 8 digits)
    code_tac := SUBSTRING(numero_imei FROM 1 FOR 8);
    
    -- Luhn algorithm validation
    luhn_valide := valider_luhn(numero_imei);
    
    -- Search in TAC database
    SELECT * INTO info_tac FROM tac_database WHERE tac = code_tac;
    
    IF FOUND THEN
        resultat := jsonb_build_object(
            'valide', CASE 
                WHEN info_tac.statut = 'valide' AND luhn_valide THEN true 
                ELSE false 
            END,
            'marque', info_tac.marque,
            'modele', info_tac.modele,
            'tac', code_tac,
            'statut', info_tac.statut,
            'annee_sortie', info_tac.annee_sortie,
            'type_appareil', info_tac.type_appareil,
            'luhn_valide', luhn_valide,
            'source', 'tac_database'
        );
    ELSE
        resultat := jsonb_build_object(
            'valide', luhn_valide,
            'marque', 'Inconnue',
            'modele', 'Inconnu',
            'tac', code_tac,
            'statut', 'inconnu',
            'luhn_valide', luhn_valide,
            'source', 'luhn_only'
        );
    END IF;
    
    RETURN resultat;
END;
$$ LANGUAGE plpgsql;

-- Function to validate IMEI using Luhn algorithm
CREATE OR REPLACE FUNCTION valider_luhn(numero_imei VARCHAR) 
RETURNS BOOLEAN AS $$
DECLARE
    i INTEGER;
    digit INTEGER;
    sum INTEGER := 0;
    alternate BOOLEAN := false;
BEGIN
    -- Clean input
    numero_imei := REGEXP_REPLACE(numero_imei, '[^0-9]', '', 'g');
    
    -- Must be 15 digits for Luhn validation
    IF LENGTH(numero_imei) != 15 THEN
        RETURN false;
    END IF;
    
    -- Process from right to left (excluding check digit)
    -- Fixed: Use standard FOR loop instead of REVERSE
    FOR i IN 1..14 LOOP
        digit := CAST(SUBSTRING(numero_imei FROM (15 - i) FOR 1) AS INTEGER);
        
        IF alternate THEN
            digit := digit * 2;
            IF digit > 9 THEN
                digit := digit - 9;
            END IF;
        END IF;
        
        sum := sum + digit;
        alternate := NOT alternate;
    END LOOP;
    
    -- Check if sum modulo 10 equals the check digit
    RETURN (sum * 9) % 10 = CAST(SUBSTRING(numero_imei FROM 15 FOR 1) AS INTEGER);
END;
$$ LANGUAGE plpgsql;

-- Vue pour analyser la couverture TAC
CREATE VIEW vue_analyse_tac AS
SELECT 
    marque,
    COUNT(*) as nombre_modeles,
    MIN(annee_sortie) as premiere_annee,
    MAX(annee_sortie) as derniere_annee,
    COUNT(CASE WHEN statut = 'valide' THEN 1 END) as modeles_valides,
    COUNT(CASE WHEN statut = 'obsolete' THEN 1 END) as modeles_obsoletes
FROM tac_database 
GROUP BY marque 
ORDER BY nombre_modeles DESC;

-- Fonction améliorée pour importer TAC avec mapping flexible
CREATE OR REPLACE FUNCTION importer_tac_avec_mapping(
    csv_data TEXT,
    format_source VARCHAR(50) DEFAULT 'osmocom'
) RETURNS JSONB AS $$
DECLARE
    ligne TEXT;
    colonnes TEXT[];
    tac_val VARCHAR(8);
    marque_val VARCHAR(100);
    modele_val VARCHAR(100);
    statut_val VARCHAR(20) := 'valide';
    type_appareil_val VARCHAR(50) := 'smartphone';
    imported_count INTEGER := 0;
    error_count INTEGER := 0;
    resultat JSONB;
BEGIN
    -- Diviser le CSV en lignes
    FOR ligne IN SELECT unnest(string_to_array(csv_data, E'\n'))
    LOOP
        -- Ignorer les lignes vides et les en-têtes
        IF ligne IS NULL OR ligne = '' OR ligne LIKE '%tac,name%' OR ligne LIKE 'Osmocom TAC%' THEN
            CONTINUE;
        END IF;
        
        BEGIN
            -- Diviser la ligne en colonnes
            colonnes := string_to_array(ligne, ',');
            
            -- Mapping pour format Osmocom
            IF format_source = 'osmocom' AND array_length(colonnes, 1) >= 8 THEN
                tac_val := LPAD(TRIM(colonnes[1]), 8, '0');
                marque_val := TRIM(colonnes[2]);
                modele_val := TRIM(colonnes[3]);
                
                -- Si le modèle est vide, utiliser les infos depuis les autres colonnes
                IF modele_val IS NULL OR modele_val = '' THEN
                    modele_val := COALESCE(TRIM(colonnes[8]), 'Unknown Model');
                END IF;
                
                -- Valider le TAC (doit être 8 chiffres)
                IF tac_val !~ '^[0-9]{8}$' THEN
                    CONTINUE;
                END IF;
                
                -- Insérer ou mettre à jour
                INSERT INTO tac_database (tac, marque, modele, type_appareil, statut)
                VALUES (tac_val, marque_val, modele_val, type_appareil_val, statut_val)
                ON CONFLICT (tac) DO UPDATE SET
                    marque = EXCLUDED.marque,
                    modele = EXCLUDED.modele,
                    type_appareil = EXCLUDED.type_appareil,
                    statut = EXCLUDED.statut,
                    date_modification = CURRENT_TIMESTAMP;
                
                imported_count := imported_count + 1;
            END IF;
            
        EXCEPTION WHEN OTHERS THEN
            error_count := error_count + 1;
            CONTINUE;
        END;
    END LOOP;
    
    resultat := jsonb_build_object(
        'imported', imported_count,
        'errors', error_count,
        'format', format_source
    );
    
    RETURN resultat;
END;
$$ LANGUAGE plpgsql;

-- Table pour suivre les synchronisations avec les sources externes
CREATE TABLE tac_sync_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_name VARCHAR(100) NOT NULL,
    source_url TEXT,
    sync_type VARCHAR(50) NOT NULL, -- 'manual', 'automatic', 'scheduled'
    format_type VARCHAR(20) NOT NULL, -- 'csv', 'json'
    status VARCHAR(20) NOT NULL, -- 'success', 'error', 'partial'
    records_imported INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_errors INTEGER DEFAULT 0,
    sync_duration_ms INTEGER,
    error_message TEXT,
    sync_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size_bytes INTEGER,
    checksum VARCHAR(64)
);

-- Index pour les logs de synchronisation
CREATE INDEX idx_tac_sync_log_date ON tac_sync_log(sync_date);
CREATE INDEX idx_tac_sync_log_source ON tac_sync_log(source_name);
CREATE INDEX idx_tac_sync_log_status ON tac_sync_log(status);

-- Fonction pour importer TAC depuis JSON Osmocom
CREATE OR REPLACE FUNCTION importer_tac_depuis_json(
    json_data JSONB,
    source_name VARCHAR(100) DEFAULT 'osmocom_json'
) RETURNS JSONB AS $$
DECLARE
    tac_entry JSONB;
    tac_val VARCHAR(8);
    marque_val VARCHAR(100);
    modele_val VARCHAR(100);
    statut_val VARCHAR(20) := 'valide';
    type_appareil_val VARCHAR(50) := 'smartphone';
    imported_count INTEGER := 0;
    updated_count INTEGER := 0;
    error_count INTEGER := 0;
    start_time TIMESTAMP := CURRENT_TIMESTAMP;
    sync_log_id UUID := gen_random_uuid();
    resultat JSONB;
BEGIN
    -- Créer une entrée de log de synchronisation
    INSERT INTO tac_sync_log (
        id, source_name, sync_type, format_type, status, sync_date
    ) VALUES (
        sync_log_id, source_name, 'automatic', 'json', 'in_progress', start_time
    );

    -- Parcourir les entrées JSON
    FOR tac_entry IN SELECT * FROM jsonb_array_elements(json_data)
    LOOP
        BEGIN
            -- Extraire les valeurs depuis le JSON
            tac_val := LPAD(TRIM(tac_entry->>'tac'), 8, '0');
            marque_val := TRIM(tac_entry->>'manufacturer');
            modele_val := TRIM(tac_entry->>'model');
            
            -- Valider les données
            IF tac_val IS NULL OR tac_val = '' OR tac_val !~ '^[0-9]{8}$' THEN
                error_count := error_count + 1;
                CONTINUE;
            END IF;
            
            IF marque_val IS NULL OR marque_val = '' THEN
                marque_val := 'Unknown';
            END IF;
            
            IF modele_val IS NULL OR modele_val = '' THEN
                modele_val := 'Unknown Model';
            END IF;
            
            -- Insérer ou mettre à jour
            INSERT INTO tac_database (tac, marque, modele, type_appareil, statut)
            VALUES (tac_val, marque_val, modele_val, type_appareil_val, statut_val)
            ON CONFLICT (tac) DO UPDATE SET
                marque = EXCLUDED.marque,
                modele = EXCLUDED.modele,
                type_appareil = EXCLUDED.type_appareil,
                statut = EXCLUDED.statut,
                date_modification = CURRENT_TIMESTAMP
            RETURNING (CASE WHEN xmax = 0 THEN 'inserted' ELSE 'updated' END) INTO statut_val;
            
            IF statut_val = 'inserted' THEN
                imported_count := imported_count + 1;
            ELSE
                updated_count := updated_count + 1;
            END IF;
            
        EXCEPTION WHEN OTHERS THEN
            error_count := error_count + 1;
            CONTINUE;
        END;
    END LOOP;
    
    -- Mettre à jour le log de synchronisation
    UPDATE tac_sync_log SET
        status = 'success',
        records_imported = imported_count,
        records_updated = updated_count,
        records_errors = error_count,
        sync_duration_ms = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - start_time)) * 1000
    WHERE id = sync_log_id;
    
    resultat := jsonb_build_object(
        'imported', imported_count,
        'updated', updated_count,
        'errors', error_count,
        'format', 'json',
        'source', source_name,
        'sync_id', sync_log_id
    );
    
    RETURN resultat;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour obtenir les statistiques de synchronisation
CREATE OR REPLACE FUNCTION obtenir_stats_sync_tac() 
RETURNS JSONB AS $$
DECLARE
    stats JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_syncs', COUNT(*),
        'successful_syncs', COUNT(*) FILTER (WHERE status = 'success'),
        'failed_syncs', COUNT(*) FILTER (WHERE status = 'error'),
        'last_sync', MAX(sync_date),
        'total_records_imported', COALESCE(SUM(records_imported), 0),
        'total_records_updated', COALESCE(SUM(records_updated), 0),
        'average_sync_duration_ms', COALESCE(AVG(sync_duration_ms), 0),
        'sources_used', jsonb_agg(DISTINCT source_name)
    ) INTO stats
    FROM tac_sync_log
    WHERE sync_date >= CURRENT_DATE - INTERVAL '30 days';
    
    RETURN stats;
END;
$$ LANGUAGE plpgsql;

-- Vue pour monitorer les synchronisations récentes
CREATE VIEW vue_sync_tac_recent AS
SELECT 
    source_name,
    format_type,
    status,
    records_imported + records_updated as total_records,
    records_errors,
    sync_duration_ms,
    sync_date,
    CASE 
        WHEN sync_date > CURRENT_TIMESTAMP - INTERVAL '1 hour' THEN 'très récent'
        WHEN sync_date > CURRENT_TIMESTAMP - INTERVAL '1 day' THEN 'récent'
        WHEN sync_date > CURRENT_TIMESTAMP - INTERVAL '7 days' THEN 'cette semaine'
        ELSE 'plus ancien'
    END as fraicheur
FROM tac_sync_log
ORDER BY sync_date DESC
LIMIT 20;

-- Trigger pour mettre à jour automatiquement date_modification
CREATE OR REPLACE FUNCTION update_tac_modification_date()
RETURNS TRIGGER AS $$
BEGIN
    NEW.date_modification = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tac_update_modification_date
    BEFORE UPDATE ON tac_database
    FOR EACH ROW
    EXECUTE FUNCTION update_tac_modification_date();

-- Fonctions pour synchroniser depuis les APIs externes Osmocom
CREATE OR REPLACE FUNCTION sync_osmocom_csv() 
RETURNS JSONB AS $$
DECLARE
    start_time TIMESTAMP := CURRENT_TIMESTAMP;
    sync_log_id UUID := gen_random_uuid();
    imported_count INTEGER := 0;
    updated_count INTEGER := 0;
    error_count INTEGER := 0;
    resultat JSONB;
    error_message TEXT := NULL;
BEGIN
    -- Créer une entrée de log de synchronisation
    INSERT INTO tac_sync_log (
        id, source_name, source_url, sync_type, format_type, status, sync_date
    ) VALUES (
        sync_log_id, 'osmocom_csv_api', 'https://tacdb.osmocom.org/export/tacdb.csv', 
        'automatic', 'csv', 'in_progress', start_time
    );

    BEGIN
        -- Note: Cette fonction simule la synchronisation
        -- Dans un environnement réel, vous utiliseriez une extension comme http ou un script externe
        
        -- Pour le moment, retourner un résultat simulé
        imported_count := 0;
        updated_count := 0;
        error_count := 0;
        error_message := 'Synchronisation API non implémentée - utilisez le script externe ./scripts/alimenter-base-donnees.sh --sync-osmocom-csv';
        
        -- Mettre à jour le log de synchronisation
        UPDATE tac_sync_log SET
            status = 'partial',
            records_imported = imported_count,
            records_updated = updated_count,
            records_errors = error_count,
            error_message = error_message,
            sync_duration_ms = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - start_time)) * 1000
        WHERE id = sync_log_id;
        
    EXCEPTION WHEN OTHERS THEN
        error_message := SQLERRM;
        error_count := 1;
        
        -- Mettre à jour le log avec l'erreur
        UPDATE tac_sync_log SET
            status = 'error',
            records_imported = 0,
            records_updated = 0,
            records_errors = error_count,
            error_message = error_message,
            sync_duration_ms = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - start_time)) * 1000
        WHERE id = sync_log_id;
    END;
    
    resultat := jsonb_build_object(
        'imported', imported_count,
        'updated', updated_count,
        'errors', error_count,
        'format', 'csv',
        'source', 'osmocom_csv_api',
        'sync_id', sync_log_id,
        'error_message', error_message,
        'note', 'Utilisez les scripts externes pour la synchronisation réelle'
    );
    
    RETURN resultat;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour synchroniser depuis l'API JSON Osmocom
CREATE OR REPLACE FUNCTION sync_osmocom_json() 
RETURNS JSONB AS $$
DECLARE
    start_time TIMESTAMP := CURRENT_TIMESTAMP;
    sync_log_id UUID := gen_random_uuid();
    imported_count INTEGER := 0;
    updated_count INTEGER := 0;
    error_count INTEGER := 0;
    resultat JSONB;
    error_message TEXT := NULL;
BEGIN
    -- Créer une entrée de log de synchronisation
    INSERT INTO tac_sync_log (
        id, source_name, source_url, sync_type, format_type, status, sync_date
    ) VALUES (
        sync_log_id, 'osmocom_json_api', 'https://tacdb.osmocom.org/export/tacdb.json', 
        'automatic', 'json', 'in_progress', start_time
    );

    BEGIN
        -- Note: Cette fonction simule la synchronisation
        -- Dans un environnement réel, vous utiliseriez une extension comme http ou un script externe
        
        imported_count := 0;
        updated_count := 0;
        error_count := 0;
        error_message := 'Synchronisation API non implémentée - utilisez le script externe ./scripts/alimenter-base-donnees.sh --sync-osmocom-json';
        
        -- Mettre à jour le log de synchronisation
        UPDATE tac_sync_log SET
            status = 'partial',
            records_imported = imported_count,
            records_updated = updated_count,
            records_errors = error_count,
            error_message = error_message,
            sync_duration_ms = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - start_time)) * 1000
        WHERE id = sync_log_id;
        
    EXCEPTION WHEN OTHERS THEN
        error_message := SQLERRM;
        error_count := 1;
        
        UPDATE tac_sync_log SET
            status = 'error',
            records_imported = 0,
            records_updated = 0,
            records_errors = error_count,
            error_message = error_message,
            sync_duration_ms = EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - start_time)) * 1000
        WHERE id = sync_log_id;
    END;
    
    resultat := jsonb_build_object(
        'imported', imported_count,
        'updated', updated_count,
        'errors', error_count,
        'format', 'json',
        'source', 'osmocom_json_api',
        'sync_id', sync_log_id,
        'error_message', error_message,
        'note', 'Utilisez les scripts externes pour la synchronisation réelle'
    );
    
    RETURN resultat;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour obtenir les dernières statistiques TAC en temps réel
CREATE OR REPLACE FUNCTION obtenir_stats_tac_temps_reel() 
RETURNS JSONB AS $$
DECLARE
    stats JSONB;
BEGIN
    SELECT jsonb_build_object(
        'total_tacs', (SELECT COUNT(*) FROM tac_database),
        'total_marques', (SELECT COUNT(DISTINCT marque) FROM tac_database),
        'tacs_valides', (SELECT COUNT(*) FROM tac_database WHERE statut = 'valide'),
        'tacs_obsoletes', (SELECT COUNT(*) FROM tac_database WHERE statut = 'obsolete'),
        'derniere_modification', (SELECT MAX(date_modification) FROM tac_database),
        'top_5_marques', (
            SELECT jsonb_agg(
                jsonb_build_object('marque', marque, 'count', count)
            ) FROM (
                SELECT marque, COUNT(*) as count 
                FROM tac_database 
                GROUP BY marque 
                ORDER BY COUNT(*) DESC 
                LIMIT 5
            ) top_brands
        ),
        'repartition_types', (
            SELECT jsonb_agg(
                jsonb_build_object('type', type_appareil, 'count', count)
            ) FROM (
                SELECT type_appareil, COUNT(*) as count 
                FROM tac_database 
                GROUP BY type_appareil 
                ORDER BY COUNT(*) DESC
            ) device_types
        ),
        'timestamp', CURRENT_TIMESTAMP
    ) INTO stats;
    
    RETURN stats;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour nettoyer les anciens logs de synchronisation
CREATE OR REPLACE FUNCTION nettoyer_logs_sync_tac(retention_days INTEGER DEFAULT 90) 
RETURNS JSONB AS $$
DECLARE
    deleted_count INTEGER;
    cutoff_date TIMESTAMP;
BEGIN
    cutoff_date := CURRENT_TIMESTAMP - (retention_days || ' days')::INTERVAL;
    
    DELETE FROM tac_sync_log 
    WHERE sync_date < cutoff_date;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN jsonb_build_object(
        'deleted_logs', deleted_count,
        'retention_days', retention_days,
        'cutoff_date', cutoff_date,
        'cleanup_date', CURRENT_TIMESTAMP
    );
END;
$$ LANGUAGE plpgsql;

-- Vue améliorée pour la surveillance des synchronisations
CREATE OR REPLACE VIEW vue_monitoring_sync_tac AS
SELECT 
    sl.source_name,
    sl.format_type,
    sl.status,
    sl.records_imported,
    sl.records_updated,
    sl.records_errors,
    sl.sync_duration_ms,
    sl.error_message,
    sl.sync_date,
    CASE 
        WHEN sl.sync_date > CURRENT_TIMESTAMP - INTERVAL '1 hour' THEN 'critical'
        WHEN sl.sync_date > CURRENT_TIMESTAMP - INTERVAL '6 hours' THEN 'warning'
        WHEN sl.sync_date > CURRENT_TIMESTAMP - INTERVAL '24 hours' THEN 'info'
        ELSE 'outdated'
    END as urgence_niveau,
    CASE 
        WHEN sl.status = 'success' AND sl.records_imported > 0 THEN 'healthy'
        WHEN sl.status = 'partial' THEN 'warning'
        WHEN sl.status = 'error' THEN 'critical'
        ELSE 'unknown'
    END as health_status
FROM tac_sync_log sl
WHERE sl.sync_date >= CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY sl.sync_date DESC;

-- Fonction pour valider un lot d'IMEIs avec TAC
CREATE OR REPLACE FUNCTION valider_lot_imeis_avec_tac(imeis_list TEXT[]) 
RETURNS JSONB AS $$
DECLARE
    imei_item TEXT;
    validation_results JSONB[];
    validation_result JSONB;
    total_count INTEGER := 0;
    valid_count INTEGER := 0;
    invalid_count INTEGER := 0;
BEGIN
    -- Valider chaque IMEI dans la liste
    FOREACH imei_item IN ARRAY imeis_list
    LOOP
        total_count := total_count + 1;
        
        -- Utiliser la fonction existante de validation
        SELECT valider_imei_avec_tac(imei_item) INTO validation_result;
        
        -- Compter les résultats
        IF (validation_result->>'valide')::BOOLEAN THEN
            valid_count := valid_count + 1;
        ELSE
            invalid_count := invalid_count + 1;
        END IF;
        
        -- Ajouter au tableau des résultats
        validation_results := validation_results || validation_result;
        
        -- Limiter à 100 IMEIs pour éviter les timeouts
        IF total_count >= 100 THEN
            EXIT;
        END IF;
    END LOOP;
    
    RETURN jsonb_build_object(
        'total_processed', total_count,
        'valid_imeis', valid_count,
        'invalid_imeis', invalid_count,
        'success_rate', ROUND((valid_count::DECIMAL / total_count * 100), 2),
        'results', validation_results,
        'processing_date', CURRENT_TIMESTAMP
    );
END;
$$ LANGUAGE plpgsql;
