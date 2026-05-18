#!/bin/bash
set -euo pipefail

echo "Creating Artifact Registry repository: ${REPOSITORY} in ${REGION}..."

# Check if repository already exists
if gcloud artifacts repositories describe "${REPOSITORY}" --project="${PROJECT_ID}" --location="${REGION}" >/dev/null 2>&1; then
  echo "Repository ${REPOSITORY} already exists."
else
  gcloud artifacts repositories create "${REPOSITORY}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --repository-format=docker \
    --description="Docker repository for LearnSphere Assignment 2"
fi

echo "Artifact Registry repository created successfully."
