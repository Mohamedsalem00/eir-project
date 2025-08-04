# Documentation Technique - Configuration des Protocoles

## Vue d'ensemble

Ce fichier documente en détail tous les paramètres de configuration du système d'intégration multi-protocoles du projet EIR.

## Structure du Fichier `config/protocols.yml`

### 1. Section `enabled_protocols`

Cette section contrôle l'activation/désactivation des protocoles d'intégration.

```yaml
enabled_protocols:
  rest: true      # API REST/HTTP
  ss7: true       # Signaling System 7  
  diameter: true  # Protocole Diameter
```

**Valeurs possibles :** `true` (activé) ou `false` (désactivé)

**Impact :** 
- Si `false` : Le protocole refuse toutes les requêtes avec une erreur 400
- Si `true` : Le protocole traite les requêtes selon sa logique

### 2. Section `timeouts`

Configure les temps d'attente maximum pour chaque protocole.

```yaml
timeouts:
  rest: 30        # 30 secondes
  ss7: 10         # 10 secondes  
  diameter: 60    # 60 secondes
```

**Recommandations :**
- **REST :** 30s - Suffisant pour requêtes web/mobile
- **SS7 :** 10s - Réseau temps réel, réponse rapide requise
- **Diameter :** 60s - Sessions plus longues, authentification complexe

### 3. Section `logging`

Configure le niveau de journalisation pour chaque protocole.

```yaml
logging:
  rest:
    level: INFO     # Niveau de log
    enabled: true   # Activation du logging
```

**Niveaux disponibles :**
- `DEBUG` : Très détaillé (développement)
- `INFO` : Informations importantes (production)
- `WARNING` : Avertissements seulement
- `ERROR` : Erreurs seulement
- `CRITICAL` : Erreurs critiques seulement

### 4. Section `endpoints`

#### 4.1 Configuration REST

```yaml
rest:
  host: "0.0.0.0"    # Interface d'écoute
  port: 8000         # Port HTTP
```

**Paramètres :**
- `host` : Interface réseau (`0.0.0.0` = toutes, `127.0.0.1` = local seulement)
- `port` : Port TCP pour l'API HTTP

#### 4.2 Configuration SS7 (Signaling System 7)

```yaml
ss7:
  sccp_address: "1234"        # SCCP Address
  gt: "33123456789"           # Global Title
```

**Explication détaillée :**

##### `sccp_address` - SCCP Address (Signaling Connection Control Part)
- **Format :** Point Code décimal ou format ITU
- **Exemple :** `"1234"` représente le Point Code 1-2-3-4
- **Usage :** Identifie le nœud SS7 local dans le réseau
- **Importance :** Utilisé pour le routage des messages MAP

##### `gt` - Global Title
- **Format :** E.164 (numéro de téléphone international)
- **Exemple :** `"33123456789"` (33 = code pays France, 123456789 = numéro)
- **Usage :** Identifiant global unique pour le routage SS7
- **Importance :** Permet aux autres nœuds SS7 de nous identifier

**Contexte réseau SS7 :**
- Utilisé pour intégration avec MSC (Mobile Switching Center)
- Communication avec VLR (Visitor Location Register)
- Échange avec HLR (Home Location Register)

#### 4.3 Configuration Diameter

```yaml
diameter:
  host: "0.0.0.0"             # Interface d'écoute
  port: 3868                  # Port Diameter standard
  realm: "eir.domain.com"     # Diameter Realm
```

**Explication détaillée :**

##### `host` et `port`
- `host` : Interface réseau pour écouter les connexions Diameter
- `port` : `3868` est le port officiel IANA pour Diameter

##### `realm` - Diameter Realm
- **Format :** FQDN (Fully Qualified Domain Name)
- **Exemple :** `"eir.domain.com"`
- **Usage :** Identifie le domaine administratif Diameter
- **Importance :** Utilisé pour :
  - Authentification mutuelle
  - Routage des messages
  - Établissement des sessions

**Contexte réseau Diameter :**
- Utilisé pour intégration avec MME (Mobility Management Entity)
- Communication avec SGSN (Serving GPRS Support Node)
- Échange avec HSS (Home Subscriber Server)
- Support des applications 3GPP (S6a, S6d, etc.)

## Exemples de Configuration par Environnement

### Environnement de Production

```yaml
enabled_protocols:
  rest: true      # API pour applications
  ss7: true       # Intégration réseau mobile
  diameter: true  # Support LTE/4G

timeouts:
  rest: 30
  ss7: 10
  diameter: 60

logging:
  rest:
    level: INFO
    enabled: true
  ss7:
    level: INFO     # Production : moins de détails
    enabled: true
  diameter:
    level: INFO
    enabled: true
```

### Environnement de Test

```yaml
enabled_protocols:
  rest: true      # Tests API
  ss7: false      # Pas de réseau SS7 en test
  diameter: false # Pas d'équipement Diameter

timeouts:
  rest: 10        # Plus rapide en test

logging:
  rest:
    level: DEBUG    # Plus de détails pour débuggage
    enabled: true
```

### Environnement de Développement

```yaml
enabled_protocols:
  rest: true
  ss7: true       # Simulation
  diameter: true  # Simulation

timeouts:
  rest: 5         # Très rapide
  ss7: 5
  diameter: 10

logging:
  rest:
    level: DEBUG
    enabled: true
  ss7:
    level: DEBUG    # Maximum de détails
    enabled: true
  diameter:
    level: DEBUG
    enabled: true
```

## Modification Dynamique

Les modifications du fichier `protocols.yml` sont prises en compte **automatiquement** sans redémarrage grâce au système de rechargement de configuration.

**Pour vérifier les changements :**
```bash
curl http://localhost:8000/protocols/status
```

**Pour tester un protocole :**
```bash
curl -X POST "http://localhost:8000/verify_imei?protocol=rest" \
     -H "Content-Type: application/json" \
     -d '{"imei": "123456789012345"}'
```
