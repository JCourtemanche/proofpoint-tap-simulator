#!/bin/bash
# Script pour résoudre le problème de bucket de staging App Engine

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Résolution du problème de bucket App Engine ===${NC}\n"

# 1. Récupérer les informations du projet
PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
BUCKET_NAME="staging.${PROJECT_ID}.appspot.com"

echo -e "${GREEN}Project ID:${NC} $PROJECT_ID"
echo -e "${GREEN}Project Number:${NC} $PROJECT_NUMBER"
echo -e "${GREEN}Bucket de staging:${NC} $BUCKET_NAME"
echo ""

# 2. Vérifier si le bucket existe
echo -e "${YELLOW}Vérification de l'existence du bucket...${NC}"
if gsutil ls -b gs://$BUCKET_NAME 2>/dev/null; then
    echo -e "${GREEN}✓ Le bucket existe déjà${NC}"
else
    echo -e "${YELLOW}Le bucket n'existe pas, création...${NC}"
    # Créer le bucket dans la même région que App Engine
    REGION=$(gcloud app describe --format="value(locationId)")
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME
    echo -e "${GREEN}✓ Bucket créé${NC}"
fi
echo ""

# 3. Donner les permissions au service account App Engine
echo -e "${YELLOW}Configuration des permissions du bucket...${NC}"

# Donner objectAdmin au service account App Engine
gsutil iam ch \
  serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com:objectAdmin \
  gs://$BUCKET_NAME

# Donner admin au service account Cloud Build
gsutil iam ch \
  serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com:admin \
  gs://$BUCKET_NAME

echo -e "${GREEN}✓ Permissions configurées${NC}"
echo ""

# 4. Donner les permissions IAM au niveau projet (si pas déjà fait)
echo -e "${YELLOW}Configuration des permissions IAM du projet...${NC}"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --quiet

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --quiet

echo -e "${GREEN}✓ Permissions IAM configurées${NC}"
echo ""

# 5. Attendre la propagation
echo -e "${YELLOW}Attente de 30 secondes pour la propagation des permissions...${NC}"
sleep 30
echo -e "${GREEN}✓ Délai écoulé${NC}"
echo ""

# 6. Afficher les permissions du bucket
echo -e "${YELLOW}Permissions actuelles du bucket:${NC}"
gsutil iam get gs://$BUCKET_NAME
echo ""

echo -e "${GREEN}=== Configuration terminée ===${NC}"
echo -e "${YELLOW}Vous pouvez maintenant relancer le déploiement avec:${NC}"
echo -e "  cd ~/proofpoint-tap-simulator/deployment"
echo -e "  gcloud app deploy app.yaml --quiet"
