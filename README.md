# Proofpoint TAP API Simulator

Simulateur d'API Proofpoint TAP (Targeted Attack Protection) pour tester et développer des intégrations Cortex XSIAM sans infrastructure Proofpoint réelle.

## Caractéristiques

- ✅ Implémentation complète de tous les endpoints API Proofpoint TAP v2
- ✅ Génération de données fictives réalistes
- ✅ Authentification HTTP Basic Auth
- ✅ Structures de données conformes aux spécifications Proofpoint
- ✅ Prêt pour déploiement sur Google Cloud Platform

## Endpoints implémentés

### SIEM Events (`/v2/siem/*`)
- `GET /v2/siem/all` - Tous les événements SIEM
- `GET /v2/siem/issues` - Événements d'issues
- `GET /v2/siem/clicks/permitted` - Clics permis
- `GET /v2/siem/clicks/blocked` - Clics bloqués
- `GET /v2/siem/messages/delivered` - Messages délivrés
- `GET /v2/siem/messages/blocked` - Messages bloqués

### Forensics (`/v2/forensics`)
- `GET /v2/forensics` - Données forensiques (threat ou campaign)

### Campaigns (`/v2/campaign/*`)
- `GET /v2/campaign/ids` - Liste des IDs de campagnes
- `GET /v2/campaign/{campaign_id}` - Détails d'une campagne

### People (`/v2/people/*`)
- `GET /v2/people/vap` - Very Attacked People
- `GET /v2/people/top-clickers` - Top Clickers

### Utils (`/v2/url/*`)
- `POST /v2/url/decode` - Décodage d'URLs Proofpoint

## Installation et utilisation locale

### Prérequis
- Python 3.11+
- pip

### Installation

```bash
cd simulator
pip install -r requirements.txt
```

### Lancement

```bash
python app.py
```

Le serveur démarre sur `http://localhost:8080`

### Configuration

Variables d'environnement disponibles :

- `AUTH_USERNAME` - Nom d'utilisateur (défaut: `test-principal`)
- `AUTH_PASSWORD` - Mot de passe (défaut: `test-secret`)
- `HOST` - Adresse d'écoute (défaut: `0.0.0.0`)
- `PORT` - Port d'écoute (défaut: `8080`)
- `DEBUG` - Mode debug (défaut: `True`)
- `MIN_EVENTS_COUNT` - Nombre minimum d'événements générés (défaut: `1`)
- `MAX_EVENTS_COUNT` - Nombre maximum d'événements générés (défaut: `10`)

## Utilisation

### Test avec curl

```bash
# Tester l'endpoint /v2/siem/all
curl -u test-principal:test-secret \
  "http://localhost:8080/v2/siem/all?format=json&sinceSeconds=3600"

# Tester les messages délivrés
curl -u test-principal:test-secret \
  "http://localhost:8080/v2/siem/messages/delivered?format=json&interval=2021-04-27T09:00:00Z/2021-04-27T10:00:00Z"

# Tester les campagnes
curl -u test-principal:test-secret \
  "http://localhost:8080/v2/campaign/ids?format=json&interval=2021-04-27T09:00:00Z/2021-04-27T10:00:00Z"
```

### Configuration dans Cortex XSIAM

1. Aller dans **Settings → Integrations**
2. Rechercher **Proofpoint TAP v2**
3. Configurer l'intégration :
   - **Server URL**: URL du simulateur (ex: `http://localhost:8080` ou URL GCP)
   - **Service Principal**: `test-principal`
   - **Secret**: `test-secret`
   - **API Version**: `v2`
4. Tester la connexion
5. Activer **Fetch incidents**

## Déploiement sur Google Cloud Platform

### Avec Google App Engine

```bash
# Se placer dans le répertoire deployment
cd deployment

# Déployer
gcloud app deploy app.yaml
```

### Avec Docker et Cloud Run

```bash
# Construire l'image Docker
docker build -f deployment/Dockerfile -t proofpoint-tap-simulator .

# Tester localement
docker run -p 8080:8080 \
  -e AUTH_USERNAME=test-principal \
  -e AUTH_PASSWORD=test-secret \
  proofpoint-tap-simulator

# Tag pour GCR
docker tag proofpoint-tap-simulator gcr.io/[PROJECT-ID]/proofpoint-tap-simulator

# Push vers GCR
docker push gcr.io/[PROJECT-ID]/proofpoint-tap-simulator

# Déployer sur Cloud Run
gcloud run deploy proofpoint-tap-simulator \
  --image gcr.io/[PROJECT-ID]/proofpoint-tap-simulator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Structure du projet

```
proofpointTAP-simul/
├── simulator/
│   ├── app.py                  # Application Flask principale
│   ├── auth.py                 # Authentification Basic Auth
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Dépendances Python
│   ├── routes/                 # Endpoints API
│   │   ├── siem.py            # /v2/siem/*
│   │   ├── forensics.py       # /v2/forensics
│   │   ├── campaigns.py       # /v2/campaign/*
│   │   ├── people.py          # /v2/people/*
│   │   └── utils.py           # /v2/url/*
│   ├── generators/            # Générateurs de données
│   │   ├── base.py           # Utilitaires de base
│   │   ├── messages.py       # Génération de messages
│   │   ├── clicks.py         # Génération de clicks
│   │   ├── forensics.py      # Génération forensics
│   │   ├── campaigns.py      # Génération campagnes
│   │   └── people.py         # Génération utilisateurs
│   └── validators/           # Validation des paramètres
│       └── params.py
├── deployment/
│   ├── Dockerfile            # Image Docker
│   └── app.yaml             # Config Google App Engine
└── README.md
```

## Données générées

Le simulateur génère des données fictives mais réalistes :

### Threat Families
- Emotet, Dridex, TrickBot, Qakbot, IcedID
- Cobalt Strike, Metasploit
- Agent Tesla, FormBook, Lokibot

### Brands imités
- Microsoft, Google, Amazon, PayPal
- DHL, FedEx, Apple, LinkedIn

### Techniques MITRE ATT&CK
- T1566.001 (Spearphishing Attachment)
- T1566.002 (Spearphishing Link)
- T1204.002 (Malicious File)
- T1059.001 (PowerShell)

## Sécurité

⚠️ **IMPORTANT** : Ce simulateur est destiné uniquement à des fins de test et développement.

- Ne jamais exposer publiquement sans authentification forte
- Changer les credentials par défaut en production
- Utiliser HTTPS en production
- Ne pas utiliser avec des données réelles

## Support et contribution

Pour signaler un bug ou demander une fonctionnalité, créer une issue sur le dépôt du projet.

## Licence

Ce projet est fourni à des fins éducatives et de test.
