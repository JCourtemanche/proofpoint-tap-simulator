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
echo -e "${YELLOW}[1/5] Activation des APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable storage.googleapis.com
echo -e "${GREEN}✓ APIs activées${NC}\n"

# 1b. Configurer les permissions pour GCR
echo -e "${YELLOW}[2/5] Configuration des permissions GCR...${NC}"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --quiet > /dev/null 2>&1
echo -e "${GREEN}✓ Permissions configurées${NC}\n"

# 2. Se placer dans le bon répertoire
echo -e "${YELLOW}[3/5] Vérification du répertoire...${NC}"
if [ ! -f "deployment/Dockerfile" ]; then
    echo -e "${RED}ERREUR: Dockerfile non trouvé${NC}"
    echo "Assurez-vous d'être dans le répertoire proofpoint-tap-simulator"
    exit 1
fi
echo -e "${GREEN}✓ Dockerfile trouvé${NC}\n"

# 3. Construire l'image Docker
echo -e "${YELLOW}[4/5] Construction de l'image Docker...${NC}"
echo "Cela peut prendre 2-3 minutes..."
gcloud builds submit --config cloudbuild.yaml

if [ $? -ne 0 ]; then
    echo -e "${RED}ERREUR: La construction de l'image a échoué${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Image construite: gcr.io/$PROJECT_ID/$SERVICE_NAME${NC}\n"

# 4. Déployer sur Cloud Run
echo -e "${YELLOW}[5/5] Déploiement sur Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
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

# 5. Récupérer l'URL du service
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
echo "1. Health check:"
echo -e "   ${GREEN}curl $SERVICE_URL/health${NC}"
echo ""
echo "2. Test avec authentification:"
echo -e "   ${GREEN}curl -u test-principal:test-secret \\${NC}"
echo -e "     ${GREEN}\"$SERVICE_URL/v2/siem/all?format=json&sinceSeconds=3600\"${NC}"
echo ""
echo -e "${YELLOW}Configuration XSIAM:${NC}"
echo "   Server URL: $SERVICE_URL"
echo "   Service Principal: test-principal"
echo "   Secret: test-secret"
echo ""
echo -e "${YELLOW}Commandes utiles:${NC}"
echo "   Voir les logs:  gcloud run services logs read $SERVICE_NAME --region $REGION"
echo "   Supprimer:      gcloud run services delete $SERVICE_NAME --region $REGION"
echo ""
