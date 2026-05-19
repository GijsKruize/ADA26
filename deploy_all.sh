#!/bin/bash
set -euo pipefail

export PROJECT_ID="ada2026-488110"
export REGION="us-central1"
export REPOSITORY="learnsphere-repo"
export SERVICE_ACCOUNT="479923065661-compute@developer.gserviceaccount.com"

echo "Starting deployment sequence..."

cd infra/gcloud
bash 00_enable_apis.sh
bash 01_create_artifact_registry.sh
bash 02_create_firestore.sh || echo "Firestore might already exist, continuing."
bash 03_create_pubsub.sh
bash 04_create_storage.sh || echo "Storage bucket might already exist, continuing."

# We need to build from project root
cd ../../
bash infra/gcloud/05_deploy_cloud_run.sh
bash infra/gcloud/06_deploy_functions.sh
bash infra/gcloud/07_create_pubsub_push_subscriptions.sh
bash infra/gcloud/08_deploy_workflow.sh
bash infra/gcloud/09_deploy_gateway.sh
bash infra/gcloud/10_update_urls.sh

echo "Full deployment complete!"
