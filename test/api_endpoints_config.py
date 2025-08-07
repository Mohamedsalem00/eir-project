# 📋 Configuration des Endpoints API EIR
# Fichier central de définition de tous les endpoints de l'API
# Version: 1.0.0 - Compatible OAS 3.1

API_CONFIG = {
    "info": {
        "title": "API Projet EIR",
        "version": "1.0.0",
        "description": "API du Registre d'Identité des Équipements (EIR) pour la gestion professionnelle d'appareils mobiles",
        "contact": {
            "name": "Équipe de Développement EIR",
            "email": "contact@eir-project.com",
            "url": "https://eir-project.com"
        },
        "license": {
            "name": "Licence Propriétaire"
        },
        "terms_of_service": "https://eir-project.com/terms"
    },
    
    "servers": [
        {
            "url": "http://localhost:8000",
            "description": "Serveur de développement local"
        },
        {
            "url": "https://api.eir-project.com",
            "description": "Serveur de production"
        }
    ],
    
    "tags": [
        {
            "name": "Système",
            "description": "Informations système et vérifications d'état"
        },
        {
            "name": "Public",
            "description": "Points de terminaison publics disponibles pour tous les utilisateurs"
        },
        {
            "name": "Authentification",
            "description": "Authentification et autorisation des utilisateurs"
        },
        {
            "name": "IMEI", 
            "description": "Services de validation et recherche d'IMEI"
        },
        {
            "name": "Appareils",
            "description": "Opérations de gestion des appareils"
        },
        {
            "name": "Cartes SIM",
            "description": "Opérations de gestion des cartes SIM"
        },
        {
            "name": "Utilisateurs",
            "description": "Opérations de gestion des utilisateurs"
        },
        {
            "name": "Historique de Recherche",
            "description": "Points de terminaison d'historique et suivi des recherches"
        },
        {
            "name": "Notifications",
            "description": "Points de terminaison de gestion des notifications"
        },
        {
            "name": "Analyses",
            "description": "Points de terminaison d'analyses et rapports"
        },
        {
            "name": "Admin",
            "description": "Opérations administratives"
        },
        {
            "name": "TAC",
            "description": "Gestion de la base de données TAC (Type Allocation Code)"
        },
        {
            "name": "Gestion d'Accès",
            "description": "Contrôle d'accès granulaire et permissions"
        }
    ]
}

# 🌐 Définition complète des endpoints
ENDPOINTS = {
    # ========================================
    # 🔧 SYSTÈME
    # ========================================
    "system": {
        "welcome": {
            "path": "/",
            "method": "GET",
            "summary": "Bienvenue API",
            "description": "Point d'entrée principal de l'API avec informations générales",
            "tags": ["Système"],
            "auth_required": False,
            "test_priority": "high",
            "expected_fields": ["nom_service", "version", "description"],
            "test_data": None
        },
        
        "health": {
            "path": "/health",
            "method": "GET", 
            "summary": "Vérification d'État",
            "description": "Vérification de l'état de santé du système",
            "tags": ["Système"],
            "auth_required": False,
            "test_priority": "high",
            "expected_fields": ["status", "timestamp"],
            "test_data": None
        },
        
        "health_french": {
            "path": "/verification-etat",
            "method": "GET",
            "summary": "Vérification d'État (Francisé)",
            "description": "Vérification de l'état de santé du système (version française)",
            "tags": ["Système"],
            "auth_required": False,
            "test_priority": "high",
            "expected_fields": ["statut", "base_donnees", "horodatage"],
            "test_data": None
        },
        
        "languages": {
            "path": "/languages",
            "method": "GET",
            "summary": "Langues Supportées",
            "description": "Liste des langues supportées par l'API",
            "tags": ["Système"],
            "auth_required": False,
            "test_priority": "medium",
            "expected_fields": ["langues_supportees"],
            "test_data": None
        }
    },

    # ========================================
    # 🌍 PUBLIC
    # ========================================
    "public": {
        "imei_lookup": {
            "path": "/imei/{imei}",
            "method": "GET",
            "summary": "Recherche IMEI Améliorée avec Contrôle d'Accès",
            "description": "Recherche d'informations sur un IMEI avec contrôle d'accès",
            "tags": ["Public", "IMEI"],
            "auth_required": False,
            "test_priority": "high",
            "path_params": {"imei": "352745080123456"},
            "expected_fields": ["numero_imei", "statut"],
            "test_data": None
        },
        
        "public_stats": {
            "path": "/public/statistiques",
            "method": "GET",
            "summary": "Statistiques Publiques",
            "description": "Statistiques publiques du système",
            "tags": ["Public", "Analyses"],
            "auth_required": False,
            "test_priority": "medium",
            "expected_fields": ["total_appareils", "total_recherches"],
            "test_data": None
        }
    },

    # ========================================
    # 🔐 AUTHENTIFICATION
    # ========================================
    "auth": {
        "register": {
            "path": "/authentification/inscription",
            "method": "POST",
            "summary": "Inscription",
            "description": "Créer un nouveau compte utilisateur",
            "tags": ["Authentification"],
            "auth_required": False,
            "test_priority": "medium",
            "expected_fields": ["message", "user_id"],
            "test_data": {
                "nom": "Test User",
                "email": "test_user@example.com",
                "mot_de_passe": "test123456",
                "type_utilisateur": "utilisateur_authentifie"
            }
        },
        
        "login": {
            "path": "/authentification/connexion",
            "method": "POST",
            "summary": "Connexion",
            "description": "Authentification utilisateur et obtention du token",
            "tags": ["Authentification"],
            "auth_required": False,
            "test_priority": "high",
            "expected_fields": ["access_token", "token_type"],
            "test_data": {
                "email": "admin@eir-project.com",
                "mot_de_passe": "admin123"
            }
        },
        
        "profile": {
            "path": "/authentification/profile",
            "method": "GET",
            "summary": "Profil Utilisateur",
            "description": "Obtenir les informations du profil utilisateur connecté",
            "tags": ["Authentification"],
            "auth_required": True,
            "test_priority": "medium",
            "expected_fields": ["id", "nom", "email"],
            "test_data": None
        },
        
        "logout": {
            "path": "/authentification/deconnexion",
            "method": "POST",
            "summary": "Déconnexion",
            "description": "Déconnexion utilisateur",
            "tags": ["Authentification"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["message"],
            "test_data": None
        }
    },

    # ========================================
    # 📱 IMEI
    # ========================================
    "imei": {
        "lookup": {
            "path": "/imei/{imei}",
            "method": "GET",
            "summary": "Recherche IMEI Améliorée avec Contrôle d'Accès",
            "description": "Recherche détaillée d'un IMEI avec journalisation",
            "tags": ["IMEI"],
            "auth_required": True,
            "test_priority": "high",
            "path_params": {"imei": "352745080123456"},
            "expected_fields": ["numero_imei", "appareil_info"],
            "test_data": None
        },
        
        "history": {
            "path": "/imei/{imei}/historique",
            "method": "GET",
            "summary": "Historique Recherche IMEI",
            "description": "Historique des recherches pour un IMEI spécifique",
            "tags": ["IMEI", "Historique de Recherche"],
            "auth_required": True,
            "test_priority": "medium",
            "path_params": {"imei": "352745080123456"},
            "expected_fields": ["historique", "nombre_recherches"],
            "test_data": None
        },
        
        "update_status": {
            "path": "/imeis/{imei_id}/status",
            "method": "PUT",
            "summary": "Mettre à Jour Statut IMEI",
            "description": "Modifier le statut d'un IMEI",
            "tags": ["IMEI", "Admin"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"imei_id": "test-imei-id"},
            "expected_fields": ["message"],
            "test_data": {"statut": "bloque"}
        }
    },

    # ========================================
    # 📱 APPAREILS
    # ========================================
    "devices": {
        "list": {
            "path": "/appareils",
            "method": "GET",
            "summary": "Liste des Appareils",
            "description": "Obtenir la liste des appareils de l'utilisateur",
            "tags": ["Appareils"],
            "auth_required": True,
            "test_priority": "high",
            "expected_fields": ["appareils", "total"],
            "test_data": None
        },
        
        "register": {
            "path": "/appareils",
            "method": "POST",
            "summary": "Enregistrer Appareil",
            "description": "Enregistrer un nouvel appareil",
            "tags": ["Appareils"],
            "auth_required": True,
            "test_priority": "medium",
            "expected_fields": ["message", "appareil_id"],
            "test_data": {
                "marque": "TestBrand",
                "modele": "TestModel",
                "emmc": "128GB",
                "imeis": ["123456789012345"]
            }
        },
        
        "assign": {
            "path": "/appareils/{device_id}/assigner",
            "method": "PUT",
            "summary": "Assigner Appareil",
            "description": "Assigner un appareil à un utilisateur",
            "tags": ["Appareils", "Admin"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"device_id": "test-device-id"},
            "expected_fields": ["message"],
            "test_data": {"utilisateur_id": "test-user-id"}
        },
        
        "delete": {
            "path": "/admin/appareils/{device_id}",
            "method": "DELETE",
            "summary": "Supprimer Appareil",
            "description": "Supprimer un appareil (admin uniquement)",
            "tags": ["Appareils", "Admin"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"device_id": "test-device-id"},
            "expected_fields": ["message"],
            "test_data": None
        },
        
        "bulk_import": {
            "path": "/admin/import-lot-appareils",
            "method": "POST",
            "summary": "Import en Lot d'Appareils",
            "description": "Importer plusieurs appareils en une fois",
            "tags": ["Appareils", "Admin"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["message", "nombre_importe"],
            "test_data": {
                "appareils": [
                    {
                        "marque": "BulkBrand",
                        "modele": "BulkModel",
                        "emmc": "64GB",
                        "imeis": ["111111111111111"]
                    }
                ]
            }
        },
        
        "add_imei": {
            "path": "/appareils/{appareil_id}/imeis",
            "method": "POST",
            "summary": "Ajouter IMEI à Appareil",
            "description": "Ajouter un IMEI à un appareil existant",
            "tags": ["Appareils", "IMEI"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"appareil_id": "test-device-id"},
            "expected_fields": ["message"],
            "test_data": {
                "numero_imei": "999999999999999",
                "numero_slot": 2
            }
        }
    },

    # ========================================
    # 📶 CARTES SIM
    # ========================================
    "sim": {
        "list": {
            "path": "/cartes-sim",
            "method": "GET",
            "summary": "Liste Cartes SIM",
            "description": "Obtenir la liste des cartes SIM de l'utilisateur",
            "tags": ["Cartes SIM"],
            "auth_required": True,
            "test_priority": "medium",
            "expected_fields": ["sims", "total"],
            "test_data": None
        },
        
        "register": {
            "path": "/cartes-sim",
            "method": "POST",
            "summary": "Enregistrer Carte SIM",
            "description": "Enregistrer une nouvelle carte SIM",
            "tags": ["Cartes SIM"],
            "auth_required": True,
            "test_priority": "medium",
            "expected_fields": ["message"],
            "test_data": {
                "iccid": "8934051234567890999",
                "operateur": "TestOperator"
            }
        },
        
        "check_iccid": {
            "path": "/cartes-sim/{iccid}",
            "method": "GET",
            "summary": "Vérifier ICCID",
            "description": "Vérifier les informations d'une carte SIM par ICCID",
            "tags": ["Cartes SIM"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"iccid": "8934051234567890123"},
            "expected_fields": ["iccid", "operateur"],
            "test_data": None
        }
    },

    # ========================================
    # 👤 UTILISATEURS
    # ========================================
    "users": {
        "my_permissions": {
            "path": "/mes-permissions",
            "method": "GET",
            "summary": "Mes Permissions",
            "description": "Obtenir les permissions de l'utilisateur connecté",
            "tags": ["Utilisateurs"],
            "auth_required": True,
            "test_priority": "high",
            "expected_fields": ["user_info", "permissions"],
            "test_data": None
        },
        
        "create": {
            "path": "/utilisateurs",
            "method": "POST",
            "summary": "Créer Utilisateur",
            "description": "Créer un nouvel utilisateur (admin)",
            "tags": ["Utilisateurs", "Admin"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["message", "user_id"],
            "test_data": {
                "nom": "Admin Created User",
                "email": "admin_created@example.com",
                "mot_de_passe": "admin123",
                "type_utilisateur": "utilisateur_authentifie"
            }
        },
        
        "get_user": {
            "path": "/utilisateurs/{user_id}",
            "method": "GET",
            "summary": "Obtenir Utilisateur",
            "description": "Obtenir les informations d'un utilisateur",
            "tags": ["Utilisateurs"],
            "auth_required": True,
            "test_priority": "medium",
            "path_params": {"user_id": "test-user-id"},
            "expected_fields": ["id", "nom", "email"],
            "test_data": None
        },
        
        "list_all": {
            "path": "/admin/utilisateurs",
            "method": "GET",
            "summary": "Liste Tous Utilisateurs",
            "description": "Obtenir la liste de tous les utilisateurs (admin)",
            "tags": ["Utilisateurs", "Admin"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["utilisateurs", "total"],
            "test_data": None
        }
    },

    # ========================================
    # 🔍 HISTORIQUE DE RECHERCHE
    # ========================================
    "search_history": {
        "list": {
            "path": "/recherches",
            "method": "GET",
            "summary": "Liste Recherches",
            "description": "Obtenir l'historique des recherches",
            "tags": ["Historique de Recherche"],
            "auth_required": True,
            "test_priority": "medium",
            "expected_fields": ["recherches", "total"],
            "test_data": None
        },
        
        "user_history": {
            "path": "/utilisateurs/{user_id}/recherches",
            "method": "GET", 
            "summary": "Historique Utilisateur",
            "description": "Historique des recherches d'un utilisateur spécifique",
            "tags": ["Historique de Recherche"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"user_id": "test-user-id"},
            "expected_fields": ["recherches", "utilisateur"],
            "test_data": None
        }
    },

    # ========================================
    # 🔔 NOTIFICATIONS
    # ========================================
    "notifications": {
        "list": {
            "path": "/notifications",
            "method": "GET",
            "summary": "Liste Notifications",
            "description": "Obtenir les notifications de l'utilisateur",
            "tags": ["Notifications"],
            "auth_required": True,
            "test_priority": "medium",
            "expected_fields": ["notifications", "total"],
            "test_data": None
        }
    },

    # ========================================
    # 📊 ANALYSES
    # ========================================
    "analytics": {
        "search_analytics": {
            "path": "/analyses/recherches",
            "method": "GET",
            "summary": "Analyses Recherches",
            "description": "Statistiques et analyses des recherches",
            "tags": ["Analyses"],
            "auth_required": True,
            "test_priority": "medium",
            "expected_fields": ["statistiques", "periode"],
            "test_data": None
        },
        
        "device_analytics": {
            "path": "/analyses/appareils",
            "method": "GET",
            "summary": "Analyses Appareils",
            "description": "Statistiques et analyses des appareils",
            "tags": ["Analyses"],
            "auth_required": True,
            "test_priority": "medium",
            "expected_fields": ["total_devices", "par_marque"],
            "test_data": None
        }
    },

    # ========================================
    # 🛡️ ADMIN
    # ========================================
    "admin": {
        "audit_logs": {
            "path": "/admin/journaux-audit",
            "method": "GET",
            "summary": "Journaux d'Audit",
            "description": "Obtenir les journaux d'audit système",
            "tags": ["Admin"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["logs", "total"],
            "test_data": None
        }
    },

    # ========================================
    # � TAC (Type Allocation Code)
    # ========================================
    "tac": {
        "tac_search": {
            "path": "/tac/{tac}",
            "method": "GET",
            "summary": "Recherche TAC",
            "description": "Rechercher les informations d'un code TAC",
            "tags": ["TAC"],
            "auth_required": False,
            "test_priority": "medium",
            "path_params": {"tac": "35274508"},
            "expected_fields": ["tac", "marque", "modele", "trouve"],
            "test_data": None
        },
        
        "tac_stats": {
            "path": "/admin/tac/stats",
            "method": "GET",
            "summary": "Statistiques TAC",
            "description": "Obtenir les statistiques de la base TAC",
            "tags": ["TAC", "Admin"],
            "auth_required": True,
            "test_priority": "medium",
            "expected_fields": ["statistiques_generales", "repartition_statuts"],
            "test_data": None
        },
        
        "tac_sync": {
            "path": "/admin/tac/sync",
            "method": "POST",
            "summary": "Synchronisation TAC",
            "description": "Synchroniser la base TAC depuis sources externes",
            "tags": ["TAC", "Admin"],
            "auth_required": True,
            "test_priority": "high",
            "expected_fields": ["message", "source", "result"],
            "test_data": None
        },
        
        "tac_sync_logs": {
            "path": "/admin/tac/sync/logs",
            "method": "GET",
            "summary": "Logs Synchronisation TAC",
            "description": "Obtenir l'historique des synchronisations TAC",
            "tags": ["TAC", "Admin"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["statistiques", "logs_recents"],
            "test_data": None
        },
        
        "tac_import": {
            "path": "/admin/tac/import",
            "method": "POST",
            "summary": "Import TAC",
            "description": "Importer des données TAC depuis fichier",
            "tags": ["TAC", "Admin"],
            "auth_required": True,
            "test_priority": "medium",
            "expected_fields": ["message", "filename", "result"],
            "test_data": None,
            "content_type": "multipart/form-data"
        },
        
        "imei_validate_tac": {
            "path": "/imei/{imei}/validate",
            "method": "GET",
            "summary": "Validation IMEI avec TAC",
            "description": "Valider IMEI avec base TAC et algorithme Luhn",
            "tags": ["IMEI", "TAC"],
            "auth_required": False,
            "test_priority": "medium",
            "path_params": {"imei": "352745080123456"},
            "expected_fields": ["valide", "luhn_valide", "tac_info"],
            "test_data": None
        },
        
        "imei_details": {
            "path": "/imei/{imei}/details",
            "method": "GET",
            "summary": "Détails complets IMEI",
            "description": "Détails complets IMEI avec validation TAC",
            "tags": ["IMEI", "TAC"],
            "auth_required": False,
            "test_priority": "medium",
            "path_params": {"imei": "352745080123456"},
            "expected_fields": ["imei", "recherche_locale", "validation_tac", "resume"],
            "test_data": None
        }
    },

    # ========================================
    # �🔐 GESTION D'ACCÈS
    # ========================================
    "access_management": {
        "access_levels": {
            "path": "/admin/gestion-acces/niveaux-acces",
            "method": "GET",
            "summary": "Niveaux d'Accès",
            "description": "Obtenir les niveaux d'accès disponibles",
            "tags": ["Gestion d'Accès"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["niveaux_acces"],
            "test_data": None
        },
        
        "users_with_permissions": {
            "path": "/admin/gestion-acces/utilisateurs",
            "method": "GET",
            "summary": "Utilisateurs avec Permissions",
            "description": "Liste des utilisateurs avec leurs permissions",
            "tags": ["Gestion d'Accès"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["utilisateurs"],
            "test_data": None
        },
        
        "user_permissions": {
            "path": "/admin/gestion-acces/utilisateurs/{id_utilisateur}/permissions",
            "method": "GET",
            "summary": "Permissions Utilisateur",
            "description": "Obtenir les permissions d'un utilisateur spécifique",
            "tags": ["Gestion d'Accès"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"id_utilisateur": "test-user-id"},
            "expected_fields": ["permissions", "utilisateur"],
            "test_data": None
        },
        
        "update_permissions": {
            "path": "/admin/gestion-acces/utilisateurs/{id_utilisateur}/permissions",
            "method": "PUT",
            "summary": "Mettre à Jour Permissions",
            "description": "Modifier les permissions d'un utilisateur",
            "tags": ["Gestion d'Accès"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"id_utilisateur": "test-user-id"},
            "expected_fields": ["message"],
            "test_data": {
                "niveau_acces": "standard",
                "portee_donnees": "organisation"
            }
        },
        
        "add_access_rule": {
            "path": "/admin/gestion-acces/utilisateurs/{id_utilisateur}/regles-acces",
            "method": "POST",
            "summary": "Ajouter Règle d'Accès",
            "description": "Ajouter une nouvelle règle d'accès pour un utilisateur",
            "tags": ["Gestion d'Accès"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"id_utilisateur": "test-user-id"},
            "expected_fields": ["message"],
            "test_data": {
                "type": "marque",
                "valeur": "TestBrand",
                "description": "Test access rule"
            }
        },
        
        "delete_access_rule": {
            "path": "/admin/gestion-acces/utilisateurs/{id_utilisateur}/regles-acces/{index_regle}",
            "method": "DELETE",
            "summary": "Supprimer Règle d'Accès",
            "description": "Supprimer une règle d'accès existante",
            "tags": ["Gestion d'Accès"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"id_utilisateur": "test-user-id", "index_regle": "0"},
            "expected_fields": ["message"],
            "test_data": None
        },
        
        "permissions_audit": {
            "path": "/admin/gestion-acces/audit/changements-permissions",
            "method": "GET",
            "summary": "Audit Permissions",
            "description": "Journal d'audit des changements de permissions",
            "tags": ["Gestion d'Accès"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["changements", "total"],
            "test_data": None
        },
        
        "bulk_permissions": {
            "path": "/admin/gestion-acces/mise-a-jour-lot-permissions",
            "method": "POST",
            "summary": "Mise à Jour en Lot",
            "description": "Mettre à jour les permissions de plusieurs utilisateurs",
            "tags": ["Gestion d'Accès"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["message", "utilisateurs_modifies"],
            "test_data": {
                "utilisateurs": ["user1-id", "user2-id"],
                "niveau_acces": "limite"
            }
        },
        
        "permission_templates": {
            "path": "/admin/gestion-acces/modeles",
            "method": "GET",
            "summary": "Modèles de Permissions",
            "description": "Obtenir les modèles de permissions disponibles",
            "tags": ["Gestion d'Accès"],
            "auth_required": True,
            "test_priority": "low",
            "expected_fields": ["modeles"],
            "test_data": None
        },
        
        "apply_template": {
            "path": "/admin/gestion-acces/appliquer-modele/{nom_modele}/{id_utilisateur}",
            "method": "POST",
            "summary": "Appliquer Modèle",
            "description": "Appliquer un modèle de permissions à un utilisateur",
            "tags": ["Gestion d'Accès"],
            "auth_required": True,
            "test_priority": "low",
            "path_params": {"nom_modele": "standard_user", "id_utilisateur": "test-user-id"},
            "expected_fields": ["message"],
            "test_data": None
        }
    }
}

# 📊 Métadonnées de test
TEST_CONFIG = {
    "default_timeout": 10,
    "retry_attempts": 3,
    "base_url": "http://localhost:8000",
    "auth_endpoints": {
        "login": "/authentification/connexion",
        "logout": "/authentification/deconnexion"
    },
    "test_users": {
        "admin": {
            "email": "admin@eir-project.com",
            "mot_de_passe": "admin123"
        },
        "regular": {
            "email": "user@example.com",
            "mot_de_passe": "admin123"
        }
    },
    "test_data": {
        "test_imei": "352745080123456",
        "test_iccid": "8934051234567890123",
        "test_device_id": "test-device-id",
        "test_user_id": "test-user-id"
    }
}

# 🎯 Groupes de tests pour différents scénarios
TEST_GROUPS = {
    "smoke": [
        "system.welcome",
        "system.health_french", 
        "auth.login",
        "public.imei_lookup"
    ],
    
    "core": [
        "system.welcome",
        "system.health_french",
        "system.languages",
        "auth.login",
        "auth.profile",
        "public.imei_lookup",
        "public.public_stats",
        "users.my_permissions",
        "devices.list",
        "tac.tac_search",
        "tac.imei_validate_tac"
    ],
    
    "full": "all",  # Teste tous les endpoints
    
    "authenticated": [
        endpoint_key for category in ENDPOINTS.values() 
        for endpoint_key, endpoint in category.items() 
        if endpoint.get("auth_required", False)
    ],
    
    "public": [
        endpoint_key for category in ENDPOINTS.values()
        for endpoint_key, endpoint in category.items()
        if not endpoint.get("auth_required", False)
    ],
    
    "admin": [
        endpoint_key for category in ENDPOINTS.values()
        for endpoint_key, endpoint in category.items()
        if "Admin" in endpoint.get("tags", [])
    ],
    
    "tac": [
        "tac.tac_search",
        "tac.tac_stats", 
        "tac.tac_sync",
        "tac.tac_sync_logs",
        "tac.tac_import",
        "tac.imei_validate_tac",
        "tac.imei_details"
    ]
}

def get_endpoint(category: str, name: str) -> dict:
    """Récupérer la configuration d'un endpoint spécifique"""
    return ENDPOINTS.get(category, {}).get(name, {})

def get_all_endpoints() -> dict:
    """Récupérer tous les endpoints organisés par catégorie"""
    return ENDPOINTS

def get_endpoints_by_tag(tag: str) -> list:
    """Récupérer tous les endpoints avec un tag spécifique"""
    matching_endpoints = []
    for category_name, category in ENDPOINTS.items():
        for endpoint_name, endpoint in category.items():
            if tag in endpoint.get("tags", []):
                matching_endpoints.append({
                    "category": category_name,
                    "name": endpoint_name,
                    "config": endpoint
                })
    return matching_endpoints

def get_test_group(group_name: str) -> list:
    """Récupérer les endpoints d'un groupe de test"""
    if group_name not in TEST_GROUPS:
        return []
    
    if TEST_GROUPS[group_name] == "all":
        # Retourner tous les endpoints
        all_endpoints = []
        for category_name, category in ENDPOINTS.items():
            for endpoint_name in category.keys():
                all_endpoints.append(f"{category_name}.{endpoint_name}")
        return all_endpoints
    
    return TEST_GROUPS[group_name]

def get_endpoint_by_path(path: str, method: str = "GET") -> dict:
    """Trouver un endpoint par son chemin et méthode"""
    for category in ENDPOINTS.values():
        for endpoint in category.values():
            if endpoint.get("path") == path and endpoint.get("method", "GET").upper() == method.upper():
                return endpoint
    return {}

if __name__ == "__main__":
    # Test rapide de la configuration
    print("🧪 Configuration des Endpoints API EIR")
    print(f"📊 Nombre total d'endpoints: {sum(len(cat) for cat in ENDPOINTS.values())}")
    print(f"📂 Catégories: {list(ENDPOINTS.keys())}")
    print(f"🎯 Groupes de test: {list(TEST_GROUPS.keys())}")
    
    # Afficher quelques statistiques
    auth_required = sum(
        1 for cat in ENDPOINTS.values() 
        for ep in cat.values() 
        if ep.get("auth_required", False)
    )
    print(f"🔐 Endpoints nécessitant auth: {auth_required}")
    
    high_priority = sum(
        1 for cat in ENDPOINTS.values()
        for ep in cat.values()
        if ep.get("test_priority") == "high"
    )
    print(f"⚡ Endpoints haute priorité: {high_priority}")
