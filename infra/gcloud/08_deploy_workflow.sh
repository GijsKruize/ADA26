#!/bin/bash
set -euo pipefail

echo "Deploying Google Workflow: demo_learning_flow..."

WORKFLOW_FILE="infra/workflows/demo_learning_flow.yaml"

# Get service URLs to inject into the workflow if needed, 
# although the workflow can also use environment variables if we set them up, 
# but usually we replace placeholders in the YAML or use a config.

# For this demo, we'll assume the YAML uses placeholders like ${COURSE_SERVICE_URL}
# and we'll use env vars in the workflow.

gcloud workflows deploy demo_learning_flow \
  --source="$WORKFLOW_FILE" \
  --location="${REGION}" \
  --project="${PROJECT_ID}" \
  --service-account="${SERVICE_ACCOUNT}"

echo "Google Workflow deployed."
