#!/bin/bash
set -euo pipefail

echo "Deploying Google API Gateway..."

GATEWAY_ID="learnsphere-gateway"
CONFIG_ID="learnsphere-config-$(date +%s)"
OPENAPI_FILE="infra/gateway/openapi_gateway.yaml"

# We need to replace backend URLs in openapi_gateway.yaml before deploying.
# For now, we assume a script or manual step does this, or we do it here.

# Example of replacing URLs:
# COURSE_SERVICE_URL=$(gcloud run services describe course-service --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
# sed -i "s|COURSE_SERVICE_URL|$COURSE_SERVICE_URL|g" "$OPENAPI_FILE"

echo "Creating API Config..."
gcloud api-gateway api-configs create "$CONFIG_ID" \
  --api="$GATEWAY_ID" \
  --openapi-spec="$OPENAPI_FILE" \
  --project="${PROJECT_ID}" \
  --backend-auth-service-account="${SERVICE_ACCOUNT}"

echo "Creating/Updating Gateway..."
if gcloud api-gateway gateways describe "$GATEWAY_ID" --location="${REGION}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud api-gateway gateways update "$GATEWAY_ID" \
    --api="$GATEWAY_ID" \
    --api-config="$CONFIG_ID" \
    --location="${REGION}" \
    --project="${PROJECT_ID}"
else
  gcloud api-gateway gateways create "$GATEWAY_ID" \
    --api="$GATEWAY_ID" \
    --api-config="$CONFIG_ID" \
    --location="${REGION}" \
    --project="${PROJECT_ID}"
fi

GATEWAY_URL=$(gcloud api-gateway gateways describe "$GATEWAY_ID" --location="${REGION}" --project="${PROJECT_ID}" --format 'value(defaultHostname)')
echo "API Gateway deployed at: https://${GATEWAY_URL}"

# Update frontend with the actual Gateway URL
echo "Updating frontend with Gateway URL..."
gcloud run deploy frontend \
  --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/frontend:latest" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --set-env-vars "API_GATEWAY_URL=https://${GATEWAY_URL}"

echo "Deployment complete."
