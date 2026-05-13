#!/bin/bash
# Script pour activer et configurer GCR (Google Container Registry)

set -e

PROJECT_ID=$(gcloud config get-value project)
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

echo "=== Configuration de Google Container Registry ==="
echo "Project ID: $PROJECT_ID"
echo "Project Number: $PROJECT_NUMBER"
echo ""

# 1. Activer l'API Container Registry (legacy mais toujours supporté)
echo "[1/3] Activation de l'API Container Registry..."
gcloud services enable containerregistry.googleapis.com

# 2. Donner les permissions au service account Cloud Build
echo ""
echo "[2/3] Configuration des permissions Cloud Build..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --quiet

# 3. Activer l'API Storage (si pas déjà fait)
echo ""
echo "[3/3] Activation de l'API Storage..."
gcloud services enable storage.googleapis.com

echo ""
echo "✓ Configuration terminée"
echo ""
echo "Vous pouvez maintenant relancer le build:"
echo "  bash deploy-cloudrun.sh"
