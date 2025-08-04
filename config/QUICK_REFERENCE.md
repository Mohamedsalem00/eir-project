# Guide de Référence Rapide - Configuration Protocoles

## 🚀 Activation/Désactivation Rapide

### Fichier à modifier
```
config/protocols.yml
```

### Commandes de vérification
```bash
# Vérifier le statut
curl http://localhost:8000/protocols/status

# Tester un protocole
curl -X POST "http://localhost:8000/verify_imei?protocol=rest" \
     -H "Content-Type: application/json" \
     -d '{"imei": "123456789012345"}'
```

## 📋 Configurations Pré-définies

### 🏭 Production (Réseau Mobile Complet)
```yaml
enabled_protocols:
  rest: true      # ✅ API Web/Mobile
  ss7: true       # ✅ MSC/VLR Integration  
  diameter: true  # ✅ MME/SGSN Integration
```

### 🧪 Test/Développement
```yaml
enabled_protocols:
  rest: true      # ✅ Tests API seulement
  ss7: false      # ❌ Pas de réseau SS7
  diameter: false # ❌ Pas d'équipement Diameter
```

### 🔒 Maintenance (Tout fermé)
```yaml
enabled_protocols:
  rest: false     # ❌ Fermer API
  ss7: false      # ❌ Fermer SS7
  diameter: false # ❌ Fermer Diameter
```

### 🌐 API Seulement (Web/Mobile uniquement)
```yaml
enabled_protocols:
  rest: true      # ✅ API Web/Mobile
  ss7: false      # ❌ Pas de signalisation
  diameter: false # ❌ Pas de signalisation
```

## 🔧 Paramètres Techniques Recommandés

### Timeouts par Environnement

| Environnement | REST | SS7 | Diameter |
|---------------|------|-----|----------|
| **Production** | 30s | 10s | 60s |
| **Test** | 10s | 5s | 30s |
| **Développement** | 5s | 5s | 10s |

### Logging par Environnement

| Environnement | REST | SS7 | Diameter |
|---------------|------|-----|----------|
| **Production** | INFO | INFO | INFO |
| **Test** | DEBUG | DEBUG | DEBUG |
| **Développement** | DEBUG | DEBUG | DEBUG |

## 📡 Configuration Réseau

### SS7 (MSC/VLR Integration)
```yaml
ss7:
  sccp_address: "1234"        # Point Code local
  gt: "33123456789"           # Global Title (E.164)
```
**Valeurs à adapter selon votre réseau !**

### Diameter (MME/SGSN Integration)
```yaml
diameter:
  host: "0.0.0.0"             # Interface d'écoute
  port: 3868                  # Port standard Diameter
  realm: "eir.domain.com"     # Votre domaine Diameter
```
**Adaptez le realm à votre organisation !**

## 🆘 Dépannage Rapide

### Problème : Protocole ne répond pas
1. Vérifier l'activation : `enabled_protocols: true`
2. Vérifier les logs : `logging: enabled: true`
3. Tester : `curl .../protocols/status`

### Problème : Timeout
1. Augmenter : `timeouts: rest: 60`
2. Vérifier la connectivité réseau
3. Vérifier les logs d'application

### Problème : Erreurs SS7/Diameter
1. Vérifier les paramètres réseau (`sccp_address`, `gt`, `realm`)
2. Vérifier la connectivité avec les équipements
3. Augmenter le logging : `level: DEBUG`

## ⚡ Changements Instantanés

✅ **Les modifications sont appliquées automatiquement**
- Pas besoin de redémarrer le conteneur
- Changements pris en compte en quelques secondes
- Utiliser `/protocols/status` pour vérifier
