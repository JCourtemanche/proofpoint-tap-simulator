#!/bin/bash
# Script de déploiement Cloud Run pour le simulateur Proofpoint TAP
# Usage: bash deploy-cloudrun.sh

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
REGION="europe-west1"
SERVICE_NAME="proofpoint-tap-simulator"

echo -e "${GREEN}=== Déploiement Cloud Run - Simulateur Proofpoint TAP ===${NC}\n"
echo -e "${YELLOW}Project:${NC} $PROJECT_ID"
echo -e "${YELLOW}Region:${NC} $REGION"
echo -e "${YELLOW}Service:${NC} $SERVICE_NAME"
echo ""

# 1. Activer les APIs nécessaires et configurer les permissions
echo -e "${YELLOW}[1/6] Activation des APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable storage.googleapis.com
echo -e "${GREEN}✓ APIs activées${NC}\n"

# 1b. Créer le repository Artifact Registry
echo -e "${YELLOW}[2/6] Configuration d'Artifact Registry...${NC}"
REPO_EXISTS=$(gcloud artifacts repositories list \
  --location=$REGION \
  --filter="name:proofpoint-simulator" \
  --format="value(name)" 2>/dev/null)

if [ -z "$REPO_EXISTS" ]; then
  echo "Création du repository Artifact Registry..."
  gcloud artifacts repositories create proofpoint-simulator \
    --repository-format=docker \
    --location=$REGION \
    --description="Proofpoint TAP Simulator images" \
    --quiet
  echo -e "${GREEN}✓ Repository créé${NC}"
else
  echo -e "${GREEN}✓ Repository existe déjà${NC}"
fi
echo ""

# 2. Se placer dans le bon répertoire
echo -e "${YELLOW}[3/6] Vérification du répertoire...${NC}"
if [ ! -f "deployment/Dockerfile" ]; then
    echo -e "${RED}ERREUR: Dockerfile non trouvé${NC}"
    echo "Assurez-vous d'être dans le répertoire proofpoint-tap-simulator"
    exit 1
fi
echo -e "${GREEN}✓ Dockerfile trouvé${NC}\n"

# 3. Construire l'image Docker
echo -e "${YELLOW}[4/6] Construction de l'image Docker...${NC}"
echo "Cela peut prendre 2-3 minutes..."
gcloud builds submit --config cloudbuild.yaml

if [ $? -ne 0 ]; then
    echo -e "${RED}ERREUR: La construction de l'image a échoué${NC}"
    exit 1
fi
IMAGE_PATH="${REGION}-docker.pkg.dev/$PROJECT_ID/proofpoint-simulator/tap-simulator:latest"
echo -e "${GREEN}✓ Image construite: $IMAGE_PATH${NC}\n"

# 4. Déployer sur Cloud Run
echo -e "${YELLOW}[5/6] Déploiement sur Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_PATH \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 2 \
  --set-env-vars AUTH_USERNAME=test-principal,AUTH_PASSWORD=test-secret,DEBUG=False

if [ $? -ne 0 ]; then
    echo -e "${RED}ERREUR: Le déploiement a échoué${NC}"
    exit 1
fi

# 5b. Autoriser l'accès public (si la policy d'organisation le permet)
echo -e "${YELLOW}[6/6] Configuration de l'accès public...${NC}"
gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --region=$REGION \
  --member=allUsers \
  --role=roles/run.invoker \
  --project=$PROJECT_ID \
  --quiet 2>/dev/null

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Accès public activé${NC}\n"
  PUBLIC_ACCESS=true
else
  echo -e "${YELLOW}⚠ L'accès public a été bloqué par une policy d'organisation${NC}"
  echo -e "${YELLOW}  Le service nécessite une authentification GCP en plus de Basic Auth${NC}\n"
  PUBLIC_ACCESS=false
fi

# 6. Récupérer l'URL du service
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(status.url)')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Déploiement réussi !${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}URL du service:${NC}"
echo -e "${GREEN}$SERVICE_URL${NC}"
echo ""
echo -e "${YELLOW}Tests de validation:${NC}"
echo ""

if [ "$PUBLIC_ACCESS" = true ]; then
  echo "1. Health check:"
  echo -e "   ${GREEN}curl $SERVICE_URL/health${NC}"
  echo ""
  echo "2. Test avec authentification:"
  echo -e "   ${GREEN}curl -u test-principal:test-secret \\${NC}"
  echo -e "     ${GREEN}\"$SERVICE_URL/v2/siem/all?format=json&sinceSeconds=3600\"${NC}"
  echo ""
else
  echo "⚠ Accès public désactivé par policy d'organisation"
  echo ""
  echo "Pour permettre l'accès depuis XSIAM, demandez à votre admin GCP de:"
  echo "1. Modifier la policy d'organisation pour autoriser 'allUsers', OU"
  echo "2. Créer un service account XSIAM et l'autoriser avec:"
  echo -e "   ${GREEN}gcloud run services add-iam-policy-binding $SERVICE_NAME \\${NC}"
  echo -e "   ${GREEN}  --region=$REGION \\${NC}"
  echo -e "   ${GREEN}  --member='serviceAccount:XSIAM_SA@PROJECT.iam.gserviceaccount.com' \\${NC}"
  echo -e "   ${GREEN}  --role='roles/run.invoker' \\${NC}"
  echo -e "   ${GREEN}  --project=$PROJECT_ID${NC}"
  echo ""
  echo "Pour tester avec votre compte GCP:"
  echo -e "   ${GREEN}curl -H \"Authorization: Bearer \$(gcloud auth print-identity-token)\" \\${NC}"
  echo -e "   ${GREEN}  -u test-principal:test-secret \\${NC}"
  echo -e "   ${GREEN}  \"$SERVICE_URL/v2/siem/all?format=json&sinceSeconds=3600\"${NC}"
  echo ""
fi
echo -e "${YELLOW}Configuration XSIAM:${NC}"
echo "   Server URL: $SERVICE_URL"
echo "   Service Principal: test-principal"
echo "   Secret: test-secret"
echo ""
echo -e "${YELLOW}Commandes utiles:${NC}"
echo "   Voir les logs:  gcloud run services logs read $SERVICE_NAME --region $REGION"
echo "   Supprimer:      gcloud run services delete $SERVICE_NAME --region $REGION"
echo ""
