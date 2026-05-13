# Guide de déploiement sur Google Cloud Platform (GCP)

Ce guide vous accompagne étape par étape pour déployer le simulateur Proofpoint TAP sur Google Cloud Platform.

## Table des matières

1. [Prérequis](#prérequis)
2. [Préparation de l'environnement GCP](#préparation-de-lenvironnement-gcp)
3. [Option 1 : Déploiement avec App Engine (Recommandé)](#option-1--déploiement-avec-app-engine-recommandé)
4. [Option 2 : Déploiement avec Cloud Run](#option-2--déploiement-avec-cloud-run)
5. [Configuration post-déploiement](#configuration-post-déploiement)
6. [Tests et validation](#tests-et-validation)
7. [Gestion et monitoring](#gestion-et-monitoring)
8. [Dépannage](#dépannage)

---

## Prérequis

### 1. Compte Google Cloud Platform

- **Compte GCP actif** : https://console.cloud.google.com/
- **Billing activé** : Un compte de facturation doit être configuré
  - Les nouveaux comptes bénéficient de 300$ de crédits gratuits
  - Le simulateur coûte environ 1-5$/mois avec App Engine (selon l'utilisation)

### 2. Outils à installer sur votre machine locale

#### Installation de Google Cloud CLI (gcloud)

**Windows :**
```powershell
# Télécharger l'installateur
https://cloud.google.com/sdk/docs/install#windows

# Ou avec Chocolatey
choco install gcloudsdk
```

**Linux/Mac :**
```bash
# Télécharger et installer
curl https://sdk.cloud.google.com | bash

# Redémarrer le shell
exec -l $SHELL
```

**Vérification :**
```bash
gcloud --version
```

Vous devriez voir quelque chose comme :
```
Google Cloud SDK 460.0.0
bq 2.0.101
core 2024.01.12
gcloud-crc32c 1.0.0
gsutil 5.27
```

#### Installation de Git (si pas déjà installé)

```bash
# Vérifier si Git est installé
git --version

# Si non installé :
# Windows: https://git-scm.com/download/win
# Linux: sudo apt-get install git
# Mac: brew install git
```

---

## Préparation de l'environnement GCP

### Étape 1 : Initialiser gcloud CLI

```bash
# Authentification
gcloud auth login
```
→ Une fenêtre de navigateur s'ouvre pour vous connecter à votre compte Google.

### Étape 2 : Créer un nouveau projet GCP

```bash
# Définir les variables (modifier selon vos besoins)
export PROJECT_ID="proofpoint-tap-sim"
export PROJECT_NAME="Proofpoint TAP Simulator"
export REGION="europe-west1"  # ou us-central1, asia-east1, etc.

# Créer le projet
gcloud projects create $PROJECT_ID \
  --name="$PROJECT_NAME" \
  --set-as-default

# Vérifier que le projet est bien créé
gcloud projects list
```

**Note :** Le PROJECT_ID doit être unique globalement sur GCP. Si celui-ci est pris, essayez :
- `proofpoint-tap-sim-VOTRENOM`
- `pps-simulator-2024`
- `tap-api-simulator-xyz`

### Étape 3 : Lier le projet à votre compte de facturation

**Via Console Web :**
1. Aller sur https://console.cloud.google.com/billing
2. Sélectionner votre projet
3. Lier à un compte de facturation

**Via CLI :**
```bash
# Lister les comptes de facturation
gcloud billing accounts list

# Lier le projet (remplacer BILLING_ACCOUNT_ID)
gcloud billing projects link $PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID
```

### Étape 4 : Configurer le projet par défaut

```bash
# Définir le projet par défaut
gcloud config set project $PROJECT_ID

# Définir la région par défaut
gcloud config set compute/region $REGION
```

---

## Option 1 : Déploiement avec App Engine (Recommandé)

App Engine est la solution la plus simple pour déployer le simulateur. Pas besoin de gérer les conteneurs ou l'infrastructure.

### Étape 1 : Activer les APIs nécessaires

```bash
# Activer App Engine API
gcloud services enable appengine.googleapis.com

# Activer Cloud Build API (IMPORTANT pour le déploiement)
gcloud services enable cloudbuild.googleapis.com

# Activer Storage API
gcloud services enable storage.googleapis.com

# Créer l'application App Engine
gcloud app create --region=$REGION
```

**Régions disponibles :** `europe-west1`, `us-central1`, `asia-northeast1`, etc.
⚠️ **Attention :** La région ne peut pas être changée après création !

### Étape 1b : Configurer les permissions Cloud Build

App Engine utilise Cloud Build pour construire votre application. Le service account doit avoir les bonnes permissions :

```bash
# Récupérer le numéro du projet
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Donner les permissions au service account Cloud Build
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin"

# Donner les permissions au service account App Engine
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/storage.objectViewer"
```

> ⚠️ **Note :** Ces commandes peuvent prendre 30-60 secondes pour que les permissions soient propagées.

### Étape 2 : Cloner le projet (si pas déjà fait)

```bash
# Cloner depuis GitHub
git clone https://github.com/JCourtemanche/proofpoint-tap-simulator.git
cd proofpoint-tap-simulator
```

### Étape 3 : Configurer les credentials (IMPORTANT)

**Option A : Modifier le fichier app.yaml (Simple mais moins sécurisé)**

Éditer `deployment/app.yaml` :

```yaml
runtime: python311
service: default  # IMPORTANT: Le premier service DOIT être "default"

env_variables:
  AUTH_USERNAME: "votre-username"      # CHANGEZ ICI
  AUTH_PASSWORD: "votre-mot-de-passe"  # CHANGEZ ICI
  DEBUG: "False"

automatic_scaling:
  min_instances: 0
  max_instances: 2
  target_cpu_utilization: 0.65
```

> ⚠️ **IMPORTANT** : App Engine exige que le **premier service déployé** soit nommé `default`. Vous ne pouvez pas utiliser un nom personnalisé comme `proofpoint-tap-simulator` pour le premier déploiement. Une fois le service `default` déployé, vous pourrez créer d'autres services avec des noms personnalisés.

**Option B : Utiliser Secret Manager (Recommandé pour production)**

```bash
# Activer Secret Manager API
gcloud services enable secretmanager.googleapis.com

# Créer les secrets
echo -n "votre-username" | gcloud secrets create tap-username --data-file=-
echo -n "votre-mot-de-passe-securise" | gcloud secrets create tap-password --data-file=-

# Donner accès à App Engine
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding tap-username \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding tap-password \
  --member="serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

Puis modifier `deployment/app.yaml` :

```yaml
runtime: python311
service: default  # IMPORTANT: Le premier service DOIT être "default"

env_variables:
  DEBUG: "False"

# Secrets depuis Secret Manager
secrets:
  - name: AUTH_USERNAME
    version: latest
    secret: tap-username
  - name: AUTH_PASSWORD
    version: latest
    secret: tap-password
```

### Étape 4 : Déployer l'application

```bash
# Se placer dans le répertoire deployment
cd deployment

# Déployer (première fois : ~3-5 minutes)
gcloud app deploy app.yaml --quiet
```

Vous verrez :
```
Beginning deployment of service [default]...
╔════════════════════════════════════════════════════════════╗
╠═ Uploading 15 files to Google Cloud Storage              ═╣
╚════════════════════════════════════════════════════════════╝
File upload done.
Updating service [default]...done.
Setting traffic split for service [default]...done.
Deployed service [default] to [https://PROJECT_ID.ew.r.appspot.com]
```

### Étape 5 : Obtenir l'URL de l'application

```bash
# Afficher l'URL
gcloud app browse
```

Votre simulateur sera accessible à : `https://PROJECT_ID.ew.r.appspot.com`

---

## Option 2 : Déploiement avec Cloud Run

Cloud Run offre plus de flexibilité et une tarification à l'utilisation (vous payez uniquement quand le service est sollicité).

### Étape 1 : Activer les APIs nécessaires

```bash
# Activer Cloud Run et Artifact Registry
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Étape 2 : Créer un repository Artifact Registry

```bash
# Créer le repository pour les images Docker
gcloud artifacts repositories create proofpoint-simulator \
  --repository-format=docker \
  --location=$REGION \
  --description="Proofpoint TAP Simulator Docker images"
```

### Étape 3 : Construire l'image Docker

```bash
# Se placer à la racine du projet
cd /path/to/proofpoint-tap-simulator

# Construire et pousser l'image avec Cloud Build
gcloud builds submit \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/proofpoint-simulator/tap-simulator:latest \
  --file deployment/Dockerfile \
  .
```

### Étape 4 : Configurer les secrets (recommandé)

```bash
# Créer les secrets (si pas déjà fait)
echo -n "votre-username" | gcloud secrets create tap-username --data-file=-
echo -n "votre-mot-de-passe" | gcloud secrets create tap-password --data-file=-
```

### Étape 5 : Déployer sur Cloud Run

**Avec secrets (recommandé) :**

```bash
gcloud run deploy proofpoint-tap-simulator \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/proofpoint-simulator/tap-simulator:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 2 \
  --set-secrets=AUTH_USERNAME=tap-username:latest,AUTH_PASSWORD=tap-password:latest \
  --set-env-vars DEBUG=False
```

**Avec variables d'environnement (moins sécurisé) :**

```bash
gcloud run deploy proofpoint-tap-simulator \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/proofpoint-simulator/tap-simulator:latest \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars AUTH_USERNAME=votre-username,AUTH_PASSWORD=votre-password,DEBUG=False
```

### Étape 6 : Obtenir l'URL du service

```bash
# Récupérer l'URL
gcloud run services describe proofpoint-tap-simulator \
  --region $REGION \
  --format 'value(status.url)'
```

L'URL sera du type : `https://proofpoint-tap-simulator-xxx-ew.a.run.app`

---

## Configuration post-déploiement

### 1. Tester le déploiement

```bash
# Définir l'URL de votre service
export SERVICE_URL="https://VOTRE-URL.appspot.com"  # ou .run.app

# Test du health check
curl $SERVICE_URL/health

# Test avec authentification
curl -u votre-username:votre-password \
  "$SERVICE_URL/v2/siem/all?format=json&sinceSeconds=3600"
```

### 2. Configurer un nom de domaine personnalisé (Optionnel)

**Pour App Engine :**

```bash
# Mapper un domaine personnalisé
gcloud app domain-mappings create api.votre-domaine.com
```

Suivez les instructions pour configurer les DNS.

**Pour Cloud Run :**

```bash
# Mapper un domaine
gcloud run domain-mappings create \
  --service proofpoint-tap-simulator \
  --domain api.votre-domaine.com \
  --region $REGION
```

### 3. Activer HTTPS (automatique)

Les deux plateformes (App Engine et Cloud Run) fournissent automatiquement un certificat SSL/TLS.
Vos URLs sont déjà en HTTPS par défaut.

---

## Tests et validation

### 1. Tester tous les endpoints

```bash
# Variables
export SERVICE_URL="https://votre-url"
export USERNAME="votre-username"
export PASSWORD="votre-password"

# Test SIEM all
curl -u $USERNAME:$PASSWORD \
  "$SERVICE_URL/v2/siem/all?format=json&sinceSeconds=3600"

# Test campaigns
curl -u $USERNAME:$PASSWORD \
  "$SERVICE_URL/v2/campaign/ids?format=json&interval=2024-01-01T00:00:00Z/2024-01-01T01:00:00Z"

# Test forensics
curl -u $USERNAME:$PASSWORD \
  "$SERVICE_URL/v2/forensics?threatId=test123"

# Test VAP
curl -u $USERNAME:$PASSWORD \
  "$SERVICE_URL/v2/people/vap?window=30"

# Test URL decode
curl -u $USERNAME:$PASSWORD \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://urldefense.proofpoint.com/v2/url?u=http-3A__example.com&d=abc"]}' \
  "$SERVICE_URL/v2/url/decode"
```

### 2. Configuration dans Cortex XSIAM

1. **Accéder à XSIAM** : Settings → Integrations
2. **Rechercher** : "Proofpoint TAP v2"
3. **Configurer** :
   - **Server URL** : `https://votre-url` (URL complète du service déployé)
   - **Service Principal** : `votre-username`
   - **Secret** : `votre-password`
   - **API Version** : `v2`
   - **Trust any certificate** : Décoché (vous utilisez HTTPS)
4. **Test Connection** : Cliquer sur "Test"
5. **Activer Fetch Incidents** : Cocher "Fetches incidents"
6. **Sauvegarder**

### 3. Vérifier la collecte d'incidents

Après 5-10 minutes, vérifier dans XSIAM :
- **Incidents** → Filtrer par source "Proofpoint TAP"
- Vous devriez voir des incidents générés par le simulateur

---

## Gestion et monitoring

### Visualiser les logs

**App Engine :**
```bash
# Logs en temps réel
gcloud app logs tail -s default

# Logs des 10 dernières minutes
gcloud app logs read --limit=50
```

**Cloud Run :**
```bash
# Logs en temps réel
gcloud run services logs read proofpoint-tap-simulator \
  --region $REGION \
  --tail

# Logs avec filtre
gcloud run services logs read proofpoint-tap-simulator \
  --region $REGION \
  --filter="severity>=ERROR"
```

**Via Console Web :**
- Aller sur https://console.cloud.google.com/logs
- Sélectionner votre projet
- Filtrer par service (App Engine ou Cloud Run)

### Monitoring et métriques

**Via Console :**
1. Aller sur https://console.cloud.google.com/monitoring
2. Créer un dashboard personnalisé
3. Ajouter des métriques :
   - Nombre de requêtes
   - Latence
   - Erreurs HTTP
   - Utilisation CPU/Mémoire

**Alertes recommandées :**

```bash
# Créer une alerte pour les erreurs 5xx
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="Proofpoint Simulator - Erreurs 5xx" \
  --condition-display-name="Taux d'erreur > 5%" \
  --condition-threshold-value=5 \
  --condition-threshold-duration=300s
```

### Mise à jour du simulateur

**App Engine :**
```bash
# Récupérer les dernières modifications
git pull origin main

# Redéployer
cd deployment
gcloud app deploy app.yaml --quiet
```

**Cloud Run :**
```bash
# Récupérer les modifications
git pull origin main

# Reconstruire et redéployer
gcloud builds submit \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/proofpoint-simulator/tap-simulator:latest \
  --file deployment/Dockerfile .

gcloud run deploy proofpoint-tap-simulator \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/proofpoint-simulator/tap-simulator:latest \
  --region $REGION
```

### Gestion des versions (Cloud Run uniquement)

```bash
# Déployer une nouvelle version sans traffic
gcloud run deploy proofpoint-tap-simulator \
  --image ${REGION}-docker.pkg.dev/${PROJECT_ID}/proofpoint-simulator/tap-simulator:v2 \
  --no-traffic \
  --tag v2 \
  --region $REGION

# Tester la nouvelle version
curl https://v2---proofpoint-tap-simulator-xxx.run.app/health

# Basculer progressivement le traffic
gcloud run services update-traffic proofpoint-tap-simulator \
  --to-revisions LATEST=50,PREVIOUS=50 \
  --region $REGION

# Basculer tout le traffic
gcloud run services update-traffic proofpoint-tap-simulator \
  --to-latest \
  --region $REGION
```

---

## Dépannage

### Problème : Le déploiement échoue

**Erreur : Billing not enabled**
```
Solution :
1. Aller sur https://console.cloud.google.com/billing
2. Activer la facturation pour le projet
```

**Erreur : Permission denied**
```bash
# Vérifier les permissions
gcloud projects get-iam-policy $PROJECT_ID

# Vous devez avoir le rôle Owner ou Editor
```

**Erreur : App Engine region cannot be changed**
```
Solution : Vous ne pouvez pas changer la région App Engine après création.
Créez un nouveau projet si vous devez changer de région.
```

**Erreur : The first service must be 'default'**
```
ERROR: INVALID_ARGUMENT: The first service (module) you upload to a new 
application must be the 'default' service (module).
```

**Solution :**
```bash
# Modifier deployment/app.yaml
# Changer la ligne:
#   service: proofpoint-tap-simulator
# En:
#   service: default

# Puis redéployer
cd deployment
gcloud app deploy app.yaml --quiet
```

**Explication :** App Engine exige que le premier service déployé soit nommé `default`. Une fois ce service déployé, vous pourrez créer d'autres services avec des noms personnalisés.

**Erreur : Service account does not have access to the bucket**
```
ERROR: an internal error has occurred
Details: invalid bucket "staging.PROJECT_ID.appspot.com"; 
service account PROJECT_ID@appspot.gserviceaccount.com does not have 
access to the bucket
```

**Solution :**

Cette erreur signifie que le bucket de staging n'existe pas ou que les service accounts n'ont pas les permissions nécessaires. Le bucket de staging est automatiquement créé par App Engine mais les permissions peuvent manquer.

**Solution complète (copier-coller dans Cloud Shell) :**

```bash
# === Script de résolution du problème de bucket App Engine ===

# 1. Récupérer les informations du projet
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
BUCKET_NAME="staging.${PROJECT_ID}.appspot.com"

echo "Project ID: $PROJECT_ID"
echo "Bucket de staging: $BUCKET_NAME"

# 2. Activer les APIs nécessaires
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com

# 3. Vérifier/Créer le bucket de staging
if gsutil ls -b gs://$BUCKET_NAME 2>/dev/null; then
    echo "✓ Le bucket existe déjà"
else
    echo "Création du bucket de staging..."
    REGION=$(gcloud app describe --format="value(locationId)")
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
    echo "✓ Bucket créé"
fi

# 4. Donner les permissions sur le bucket spécifique
echo "Configuration des permissions du bucket..."
gsutil iam ch \
  serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com:objectAdmin \
  gs://$BUCKET_NAME

gsutil iam ch \
  serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com:admin \
  gs://$BUCKET_NAME

# 5. Donner les permissions IAM au niveau projet
echo "Configuration des permissions IAM..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --quiet

# 6. Attendre la propagation des permissions
echo "Attente de 30 secondes pour la propagation des permissions..."
sleep 30

# 7. Relancer le déploiement
echo "✓ Configuration terminée. Lancement du déploiement..."
cd ~/proofpoint-tap-simulator/deployment
gcloud app deploy app.yaml --quiet
```

**Explication détaillée :**

1. **Bucket de staging** : App Engine utilise un bucket nommé `staging.PROJECT_ID.appspot.com` pour stocker les fichiers temporaires pendant le build
2. **Permissions bucket** : Les service accounts ont besoin d'accès direct au bucket (objectAdmin pour App Engine, admin pour Cloud Build)
3. **Permissions IAM** : Les service accounts ont aussi besoin de `roles/storage.admin` au niveau projet
4. **Propagation** : Les permissions IAM peuvent prendre jusqu'à 60 secondes pour se propager dans GCP

**Alternative : Utiliser Cloud Run**

Si App Engine continue à poser problème, Cloud Run est une alternative plus simple :

```bash
# Cloud Run ne nécessite pas de bucket de staging
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# Construire et déployer directement
cd ~/proofpoint-tap-simulator
gcloud builds submit --tag gcr.io/$PROJECT_ID/proofpoint-tap-simulator

gcloud run deploy proofpoint-tap-simulator \
  --image gcr.io/$PROJECT_ID/proofpoint-tap-simulator \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars AUTH_USERNAME=test-principal,AUTH_PASSWORD=test-secret
```

### Problème : Authentification échoue (401)

**Vérifier les credentials :**

```bash
# App Engine - vérifier les variables d'environnement
gcloud app describe --format="value(env_variables)"

# Cloud Run - vérifier les variables
gcloud run services describe proofpoint-tap-simulator \
  --region $REGION \
  --format="value(spec.template.spec.containers[0].env)"
```

**Tester directement :**
```bash
# Test sans auth (doit retourner 401)
curl -v $SERVICE_URL/v2/siem/all?format=json&sinceSeconds=3600

# Test avec mauvais credentials (doit retourner 401)
curl -v -u wrong:credentials \
  $SERVICE_URL/v2/siem/all?format=json&sinceSeconds=3600

# Test avec bons credentials (doit retourner 200)
curl -v -u $USERNAME:$PASSWORD \
  $SERVICE_URL/v2/siem/all?format=json&sinceSeconds=3600
```

### Problème : Erreurs 500 dans les logs

**Consulter les logs détaillés :**

```bash
# App Engine
gcloud app logs read --limit=100 --format=json

# Cloud Run
gcloud run services logs read proofpoint-tap-simulator \
  --region $REGION \
  --limit=100 \
  --format=json
```

**Erreurs Python courantes :**
- `ModuleNotFoundError` : Vérifier requirements.txt
- `ImportError` : Problème de structure de fichiers
- `AttributeError` : Bug dans le code

**Activer le mode debug temporairement :**

```bash
# App Engine - modifier app.yaml
env_variables:
  DEBUG: "True"

# Redéployer
gcloud app deploy

# Cloud Run
gcloud run services update proofpoint-tap-simulator \
  --set-env-vars DEBUG=True \
  --region $REGION
```

### Problème : Performance lente

**Augmenter les ressources (Cloud Run) :**

```bash
gcloud run services update proofpoint-tap-simulator \
  --memory 1Gi \
  --cpu 2 \
  --region $REGION
```

**Activer min instances pour éviter cold start :**

```bash
# Cloud Run
gcloud run services update proofpoint-tap-simulator \
  --min-instances 1 \
  --region $REGION
```

⚠️ **Note :** min-instances > 0 engendre des coûts même sans traffic !

### Problème : Coûts élevés

**Vérifier la consommation :**
```bash
# Consulter les coûts
https://console.cloud.google.com/billing/
```

**Optimisations :**

1. **Réduire les instances min** :
   ```bash
   gcloud run services update proofpoint-tap-simulator \
     --min-instances 0 \
     --region $REGION
   ```

2. **Limiter le scaling** :
   ```bash
   gcloud run services update proofpoint-tap-simulator \
     --max-instances 1 \
     --region $REGION
   ```

3. **Supprimer les anciennes révisions** (Cloud Run) :
   ```bash
   # Lister les révisions
   gcloud run revisions list --service proofpoint-tap-simulator --region $REGION
   
   # Supprimer les anciennes
   gcloud run revisions delete REVISION_NAME --region $REGION
   ```

---

## Coûts estimés

### App Engine (Standard Environment)

- **Instance gratuite** : 28 heures/jour (F1 instance)
- **Au-delà** : ~0.05$/heure
- **Trafic sortant** : Gratuit jusqu'à 1GB/jour

**Estimation mensuelle :**
- Utilisation légère (< 10 requêtes/min) : **GRATUIT**
- Utilisation modérée (< 100 requêtes/min) : **1-5$/mois**

### Cloud Run

- **Requêtes** : 2 millions gratuites/mois
- **CPU** : 180,000 vCPU-secondes gratuits/mois
- **Mémoire** : 360,000 GiB-secondes gratuits/mois

**Estimation mensuelle :**
- Utilisation test/dev (< 1000 requêtes/jour) : **GRATUIT**
- Utilisation modérée (< 10,000 requêtes/jour) : **< 1$/mois**

---

## Nettoyage et suppression

### Supprimer le service uniquement

**App Engine :**
```bash
# Supprimer une version spécifique
gcloud app versions delete VERSION_ID --service=default

# Note : On ne peut pas supprimer complètement App Engine une fois créé
```

**Cloud Run :**
```bash
gcloud run services delete proofpoint-tap-simulator \
  --region $REGION
```

### Supprimer tout le projet

⚠️ **ATTENTION : Cela supprime TOUTES les ressources du projet !**

```bash
# Lister vos projets
gcloud projects list

# Supprimer le projet (30 jours pour annuler)
gcloud projects delete $PROJECT_ID
```

---

## Ressources utiles

- **Documentation GCP** : https://cloud.google.com/docs
- **App Engine Python** : https://cloud.google.com/appengine/docs/standard/python3
- **Cloud Run** : https://cloud.google.com/run/docs
- **Calculateur de prix** : https://cloud.google.com/products/calculator
- **Console GCP** : https://console.cloud.google.com
- **Support GCP** : https://cloud.google.com/support

---

## Support

Pour toute question :
- **Issues GitHub** : https://github.com/JCourtemanche/proofpoint-tap-simulator/issues
- **Documentation Proofpoint TAP** : https://help.proofpoint.com/
- **Documentation XSIAM** : https://docs-cortex.paloaltonetworks.com/

---

**Bon déploiement ! 🚀**
