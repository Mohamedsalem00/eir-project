# 🚀 EIR Multi-Protocoles - Architecture de Vérification IMEI

## 📋 Vue d'ensemble

Cette application EIR (Equipment Identity Register) moderne supporte l'intégration multi-protocoles pour la vérification des terminaux mobiles (IMEI) dans les réseaux de télécommunications.

### 🌟 Fonctionnalités Principales

- ✅ **API REST/HTTP** - Pour applications web et mobiles
- ✅ **Protocole SS7/MAP** - Pour intégration MSC/VLR/HLR (2G/3G)  
- ✅ **Protocole Diameter** - Pour intégration MME/SGSN/HSS (4G/LTE)
- ✅ **Configuration dynamique** - Activation/désactivation sans redémarrage
- ✅ **Audit complet** - Journalisation de toutes les interactions
- ✅ **Intégrations externes** - GSMA, DMS, APIs tierces

## 🏗️ Architecture

```
┌─────────────────┬─────────────────┬─────────────────┐
│   REST/HTTP     │     SS7/MAP     │    Diameter     │
│   (Web/Mobile)  │   (MSC/VLR)     │   (MME/SGSN)    │
└─────────┬───────┴─────────┬───────┴─────────┬───────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                    ┌───────▼───────┐
                    │   Dispatcher  │
                    │   Central     │
                    └───────┬───────┘
                            │
                ┌───────────▼───────────┐
                │   Business Logic     │
                │   (IMEI Validation)  │
                └───────────┬───────────┘
                            │
                ┌───────────▼───────────┐
                │    PostgreSQL DB     │
                │      + Redis         │
                └─────────────────────────┘
```

## 🚀 Démarrage Rapide

### Prérequis
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15

### Installation

1. **Cloner le projet**
```bash
git clone https://github.com/username/eir-project.git
cd eir-project
```

2. **Démarrer avec Docker**
```bash
docker compose up -d
```

3. **Vérifier le déploiement**
```bash
curl http://localhost:8000/protocols/status
```

## 🔧 Configuration

### Fichier Principal : `config/protocols.yml`

```yaml
# Activation des protocoles
enabled_protocols:
  rest: true      # API REST/HTTP
  ss7: true       # Signaling System 7
  diameter: true  # Protocole Diameter

# Timeouts (secondes)
timeouts:
  rest: 30
  ss7: 10  
  diameter: 60

# Configuration réseau
endpoints:
  ss7:
    sccp_address: "1234"        # Point Code SCCP
    gt: "33123456789"           # Global Title E.164
  diameter:
    port: 3868                  # Port standard Diameter
    realm: "eir.domain.com"     # Diameter Realm
```

### 🔄 Modification Dynamique

Les changements de configuration sont **automatiques** :

1. Éditez `config/protocols.yml`
2. Sauvegardez le fichier
3. Les changements sont appliqués instantanément !

## 📡 Utilisation des Protocoles

### 1. API REST (Recommandé pour Web/Mobile)

```bash
# Vérification IMEI standard
curl -X POST "http://localhost:8000/verify_imei?protocol=rest" \
     -H "Content-Type: application/json" \
     -d '{"imei": "123456789012345"}'

# Réponse
{
  "status": "success",
  "imei": "123456789012345", 
  "imei_status": "whitelisted",
  "action": "allow",
  "processing_time_ms": 245.67
}
```

### 2. Protocole SS7 (Pour MSC/VLR)

```bash
# Vérification SS7 (fire-and-forget)
curl -X POST "http://localhost:8000/verify_imei?protocol=ss7" \
     -H "Content-Type: application/json" \
     -d '{
       "imei": "123456789012345",
       "msisdn": "33123456789", 
       "imsi": "208011234567890"
     }'

# Réponse (confirmation)
{
  "status": "accepted",
  "message": "Requête SS7 acceptée",
  "processing_mode": "fire_and_forget",
  "request_id": "uuid-12345"
}
```

### 3. Protocole Diameter (Pour MME/SGSN)

```bash
# Vérification Diameter
curl -X POST "http://localhost:8000/verify_imei?protocol=diameter" \
     -H "Content-Type: application/json" \
     -d '{
       "imei": "123456789012345",
       "session_id": "eir.domain.com;123;abc",
       "origin_host": "mme.operator.com"
     }'

# Réponse avec AVPs
{
  "message_type": "Equipment-Status-Answer",
  "avps": {
    "Session-Id": "eir.domain.com;123;abc", 
    "Result-Code": 2001,
    "Equipment-Status": 0
  }
}
```

## 🔍 Monitoring et Debug

### Vérification du Statut

```bash
# Statut des protocoles
curl http://localhost:8000/protocols/status

# Santé du système
curl http://localhost:8000/health

# Logs en temps réel
docker logs -f eir_web
```

### Script de Test Intégré

```bash
# Test complet de tous les protocoles
./test_protocol_toggle.sh

# Test d'un protocole spécifique
python3 test_multi_protocol.py
```

## 🔐 Sécurité

### Authentification

- **JWT Bearer Tokens** pour REST
- **Mutual TLS** pour SS7/Diameter
- **API Keys** pour intégrations système

### Audit et Conformité

- Journalisation complète de toutes les requêtes
- Traçabilité end-to-end
- Conformité RGPD
- Standards GSMA

## 🌍 Cas d'Usage par Protocole

### REST/HTTP
- ✅ Applications web d'administration
- ✅ Apps mobiles de vérification  
- ✅ Portails self-service
- ✅ Intégrations API tierces

### SS7/MAP
- ✅ Centres de commutation (MSC)
- ✅ Registres visiteurs (VLR)
- ✅ Registres nominaux (HLR)
- ✅ Réseaux 2G/3G legacy

### Diameter
- ✅ Entités de mobilité (MME)
- ✅ Nœuds GPRS (SGSN)
- ✅ Serveurs d'abonnés (HSS)
- ✅ Réseaux 4G/LTE

## 📊 Métriques et Performance

### Métriques Collectées

- **Par protocole** : Latence, throughput, erreurs
- **Par endpoint** : Temps de réponse, volumétrie
- **Système** : CPU, mémoire, disque
- **Business** : IMEI autorisés/bloqués

### Dashboards

- **Operational** : Vue temps réel des protocoles
- **Business** : Statistiques de vérification IMEI
- **Technical** : Métriques infrastructure
- **Security** : Audit et conformité

## 🔄 CI/CD et Déploiement

### Environnements

```yaml
# Développement
enabled_protocols:
  rest: true
  ss7: true    # Simulation
  diameter: true   # Simulation

# Production
enabled_protocols: 
  rest: true
  ss7: true    # Réseau réel
  diameter: true   # Réseau réel
```

### Pipeline de Déploiement

1. **Tests unitaires** - Couverture > 80%
2. **Tests d'intégration** - Tous les protocoles
3. **Tests de performance** - Charge et stress
4. **Déploiement Blue/Green** - Zero downtime

## 📚 Documentation

### Fichiers Principaux

- `docs/architecture_multi_protocoles.tex` - Architecture complète
- `config/PROTOCOLS_DOCUMENTATION.md` - Config détaillée
- `config/QUICK_REFERENCE.md` - Guide de référence rapide
- `docs/uml/` - Diagrammes PlantUML

### APIs

- **Interactive** : http://localhost:8000/docs
- **OpenAPI** : http://localhost:8000/openapi.json
- **ReDoc** : http://localhost:8000/redoc

## 🆘 Support et Dépannage

### Problèmes Courants

1. **Protocole ne répond pas**
   - Vérifier `enabled_protocols: true`
   - Consulter les logs : `docker logs eir_web`

2. **Timeout errors** 
   - Augmenter `timeouts` dans la config
   - Vérifier la connectivité réseau

3. **Erreurs SS7/Diameter**
   - Valider les paramètres réseau
   - Augmenter logging : `level: DEBUG`

### Contacts

- **Développeur** : Mohamed Salem Khyarhoum
- **Organisation** : Moov Mauritel
- **Email** : support@eir-project.com
- **Documentation** : https://eir-project.com/docs

---

## 🎯 Avantages Multi-Protocoles

✅ **Flexibilité** - Support tous types d'équipements  
✅ **Évolutivité** - Ajout facile de nouveaux protocoles  
✅ **Rétrocompatibilité** - Intégration systems legacy  
✅ **Future-proof** - Prêt pour 5G et au-delà  
✅ **Coûts réduits** - Infrastructure unifiée  
✅ **Maintenance simplifiée** - Un seul système à gérer  

> **🚀 Un seul système EIR pour tous vos besoins d'intégration !**
