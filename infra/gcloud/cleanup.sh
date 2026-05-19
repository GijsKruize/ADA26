#!/bin/bash
set -euo pipefail

# Use environment variables if set, otherwise try to fetch from gcloud config
PROJECT_ID=${PROJECT_ID:-$(gcloud config get-value project)}
REGION=${REGION:-$(gcloud config get-value compute/region)}
REGION=${REGION:-"us-central1"}

echo "--- Starting full cleanup of Google Cloud resources in project: ${PROJECT_ID} ---"

echo "1. Cleaning up API Gateway..."
# Gateways must be deleted before configs and APIs
for gateway in $(gcloud api-gateway gateways list --project="${PROJECT_ID}" --location="${REGION}" --format="value(name)"); do
    echo "Deleting API Gateway: $gateway"
    gcloud api-gateway gateways delete "$gateway" --project="${PROJECT_ID}" --location="${REGION}" --quiet
done

# We must find the API ID for each config to delete it. Configs are nested under APIs.
for api in $(gcloud api-gateway apis list --project="${PROJECT_ID}" --format="value(name)"); do
    echo "Processing API for config cleanup: $api"
    for config in $(gcloud api-gateway api-configs list --api="$api" --project="${PROJECT_ID}" --format="value(name)"); do
        echo "Deleting API Config: $config from API: $api"
        gcloud api-gateway api-configs delete "$config" --api="$api" --project="${PROJECT_ID}" --quiet
    done
    echo "Deleting API: $api"
    gcloud api-gateway apis delete "$api" --project="${PROJECT_ID}" --quiet
done

echo "2. Cleaning up Google Workflows..."
for workflow in $(gcloud workflows list --project="${PROJECT_ID}" --location="${REGION}" --format="value(name)"); do
    echo "Deleting Workflow: $workflow"
    gcloud workflows delete "$workflow" --project="${PROJECT_ID}" --location="${REGION}" --quiet
done

echo "3. Cleaning up Cloud Run services..."
for service in $(gcloud run services list --project="${PROJECT_ID}" --region="${REGION}" --format="value(name)"); do
    echo "Deleting Cloud Run service: $service"
    gcloud run services delete "$service" --project="${PROJECT_ID}" --region="${REGION}" --quiet
done

echo "4. Cleaning up Cloud Functions..."
for function in $(gcloud functions list --project="${PROJECT_ID}" --regions="${REGION}" --format="value(name)"); do
    echo "Deleting Cloud Function: $function"
    gcloud functions delete "$function" --project="${PROJECT_ID}" --region="${REGION}" --quiet
done

echo "5. Cleaning up Pub/Sub..."
# Subscriptions first
for sub in $(gcloud pubsub subscriptions list --project="${PROJECT_ID}" --format="value(name)"); do
    echo "Deleting Pub/Sub subscription: $sub"
    gcloud pubsub subscriptions delete "$sub" --project="${PROJECT_ID}" --quiet
done
# Then topics
for topic in $(gcloud pubsub topics list --project="${PROJECT_ID}" --format="value(name)"); do
    echo "Deleting Pub/Sub topic: $topic"
    gcloud pubsub topics delete "$topic" --project="${PROJECT_ID}" --quiet
done

echo "6. Cleaning up Cloud Storage..."
# Attempt to delete the specific demo bucket. Firestore is left intact as it's harder to re-provision via script once deleted.
BUCKET_NAME="learnsphere-submissions-${PROJECT_ID}"
if gsutil ls -b "gs://${BUCKET_NAME}" >/dev/null 2>&1; then
    echo "Deleting Cloud Storage bucket: ${BUCKET_NAME}"
    gsutil rm -r "gs://${BUCKET_NAME}"
fi

echo "7. Cleaning up Artifact Registry..."
for repo in $(gcloud artifacts repositories list --project="${PROJECT_ID}" --location="${REGION}" --format="value(name)"); do
    echo "Deleting Artifact Registry repository: $repo"
    gcloud artifacts repositories delete "$repo" --project="${PROJECT_ID}" --location="${REGION}" --quiet
done

echo "--- Cleanup complete! ---"
