# Déploiement GCP — ProofPoint TAP Simulator

## Procédure de déploiement

### 1. Ouvrir Cloud Shell

Dans la [console GCP](https://console.cloud.google.com/), sélectionne ton projet puis clique sur l'icône **Cloud Shell** en haut à droite.

### 2. Cloner le projet

```bash
git clone https://github.com/JCourtemanche/proofpoint-tap-simulator
```

### 3. Se déplacer dans le répertoire

```bash
cd proofpoint-tap-simulator
```

### 4. Lancer le déploiement

```bash
bash deploy-cloudrun.sh
```

Le script gère automatiquement :
- Activation des APIs GCP nécessaires
- Création du repository Artifact Registry
- Build de l'image Docker via Cloud Build
- Déploiement sur Cloud Run

À la fin, l'URL du service est affichée.

### 5. Autoriser l'accès public

Dans la [console Cloud Run](https://console.cloud.google.com/run), ouvre le service **proofpoint-tap-simulator**, va dans l'onglet **Sécurité** et vérifie que **Authentification** est réglé sur **Autoriser l'accès non authentifié**.

> Si cette option est grisée, une policy d'organisation GCP bloque l'accès public.  
> Contacte ton admin GCP pour qu'il autorise `constraints/iam.allowedPolicyMemberDomains` sur ce projet.

---

## Validation

```bash
SERVICE_URL="https://proofpoint-tap-simulator-XXXX-ew.a.run.app"  # URL affichée à l'étape 4

# Health check
curl $SERVICE_URL/health

# Test avec authentification
curl -u test-principal:test-secret \
  "$SERVICE_URL/v2/siem/all?format=json&sinceSeconds=3600"
```

## Configuration XSIAM

| Champ | Valeur |
|---|---|
| Server URL | URL Cloud Run |
| Service Principal | `test-principal` |
| Secret | `test-secret` |

## Commandes utiles

```bash
# Voir les logs
gcloud run services logs read proofpoint-tap-simulator --region europe-west1

# Redéployer après une mise à jour du code
git pull && bash deploy-cloudrun.sh

# Supprimer le service
gcloud run services delete proofpoint-tap-simulator --region europe-west1
```
