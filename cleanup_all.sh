#!/bin/bash
set -euo pipefail

# This script performs a full teardown of the LearnSphere Google Cloud environment.
# Mirroring deploy_all.sh, it ensures a clean slate by removing all deployed artifacts.

export PROJECT_ID="ada2026-488110"
export REGION="us-central1"

echo "!!! WARNING: This will delete all LearnSphere resources in project ${PROJECT_ID} !!!"
echo "Starting full teardown in 5 seconds..."
sleep 5

# Call the specialized cleanup script
bash infra/gcloud/cleanup.sh

echo "Teardown sequence finished."
