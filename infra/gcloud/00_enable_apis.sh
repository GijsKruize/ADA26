#!/bin/bash
set -euo pipefail

# Required APIs
APIS=(
  "run.googleapis.com"
  "cloudfunctions.googleapis.com"
  "cloudbuild.googleapis.com"
  "artifactregistry.googleapis.com"
  "pubsub.googleapis.com"
  "firestore.googleapis.com"
  "workflows.googleapis.com"
  "eventarc.googleapis.com"
  "storage.googleapis.com"
  "apigateway.googleapis.com"
)

echo "Enabling Google Cloud APIs..."
for API in "${APIS[@]}"; do
  echo "Enabling $API..."
  gcloud services enable "$API" --project="${PROJECT_ID}"
done

echo "APIs enabled successfully."
