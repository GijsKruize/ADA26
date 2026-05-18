#!/bin/bash
set -euo pipefail

BUCKET_NAME="learnsphere-submissions-${PROJECT_ID}"

echo "Creating Cloud Storage bucket: ${BUCKET_NAME} in ${REGION}..."

if gcloud storage buckets describe "gs://${BUCKET_NAME}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  echo "Bucket gs://${BUCKET_NAME} already exists."
else
  gcloud storage buckets create "gs://${BUCKET_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --uniform-bucket-level-access
fi

echo "Cloud Storage bucket created successfully."
