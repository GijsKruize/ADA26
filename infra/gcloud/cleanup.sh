#!/bin/bash
PROJECT_ID=$(gcloud config get-value project)
REGION=$(gcloud config get-value compute/region)

if [ -z "$REGION" ]; then
    REGION="us-central1"
fi

echo "Cleaning up Cloud Run services..."
for service in $(gcloud run services list --project="${PROJECT_ID}" --region="${REGION}" --format="value(name)"); do
    echo "Deleting Cloud Run service: $service"
    gcloud run services delete "$service" --project="${PROJECT_ID}" --region="${REGION}" --quiet
done

echo "Cleaning up API Gateway..."
for gateway in $(gcloud api-gateway gateways list --project="${PROJECT_ID}" --location="${REGION}" --format="value(name)"); do
    echo "Deleting API Gateway: $gateway"
    gcloud api-gateway gateways delete "$gateway" --project="${PROJECT_ID}" --location="${REGION}" --quiet
done

for config in $(gcloud api-gateway api-configs list --project="${PROJECT_ID}" --format="value(name)"); do
    echo "Deleting API Config: $config"
    gcloud api-gateway api-configs delete "$config" --project="${PROJECT_ID}" --quiet || true
done

for api in $(gcloud api-gateway apis list --project="${PROJECT_ID}" --format="value(name)"); do
    echo "Deleting API: $api"
    gcloud api-gateway apis delete "$api" --project="${PROJECT_ID}" --quiet
done

echo "Cleaning up Cloud Functions..."
for function in $(gcloud functions list --project="${PROJECT_ID}" --regions="${REGION}" --format="value(name)"); do
    echo "Deleting Cloud Function: $function"
    gcloud functions delete "$function" --project="${PROJECT_ID}" --region="${REGION}" --quiet
done

echo "Cleaning up Pub/Sub subscriptions..."
for sub in $(gcloud pubsub subscriptions list --project="${PROJECT_ID}" --format="value(name)"); do
    echo "Deleting Pub/Sub subscription: $sub"
    gcloud pubsub subscriptions delete "$sub" --project="${PROJECT_ID}" --quiet
done

echo "Cleaning up Pub/Sub topics..."
for topic in $(gcloud pubsub topics list --project="${PROJECT_ID}" --format="value(name)"); do
    echo "Deleting Pub/Sub topic: $topic"
    gcloud pubsub topics delete "$topic" --project="${PROJECT_ID}" --quiet
done

echo "Cleaning up Artifact Registry repositories..."
for repo in $(gcloud artifacts repositories list --project="${PROJECT_ID}" --location="${REGION}" --format="value(name)"); do
    echo "Deleting Artifact Registry repository: $repo"
    gcloud artifacts repositories delete "$repo" --project="${PROJECT_ID}" --location="${REGION}" --quiet
done

echo "Cleanup complete."
