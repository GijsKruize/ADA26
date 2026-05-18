#!/bin/bash
set -euo pipefail

echo "Deploying Google API Gateway..."

GATEWAY_ID="learnsphere-gateway"
CONFIG_ID="learnsphere-config-$(date +%s)"
OPENAPI_FILE="infra/gateway/openapi_gateway.yaml"

echo "Ensuring API Gateway resource exists..."
if ! gcloud api-gateway apis describe "$GATEWAY_ID" --project="${PROJECT_ID}" >/dev/null 2>&1; then
  gcloud api-gateway apis create "$GATEWAY_ID" --project="${PROJECT_ID}"
fi

# Fetch real URLs
echo "Fetching backend URLs..."
COURSE_URL=$(gcloud run services describe course-service --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
ASSESSMENT_URL=$(gcloud run services describe assessment-service --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
PROFILE_URL=$(gcloud run services describe learning-profile-service --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
AUTO_GRADING_URL=$(gcloud run services describe auto-grading-agent --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
RECOMMENDER_URL=$(gcloud run services describe recommender-agent --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')

# Create a temporary OpenAPI file with replacements
sed -e "s|COURSE_SERVICE_URL|$COURSE_URL|g" \
    -e "s|ASSESSMENT_SERVICE_URL|$ASSESSMENT_URL|g" \
    -e "s|LEARNING_PROFILE_SERVICE_URL|$PROFILE_URL|g" \
    -e "s|AUTO_GRADING_AGENT_URL|$AUTO_GRADING_URL|g" \
    -e "s|RECOMMENDER_AGENT_URL|$RECOMMENDER_URL|g" \
    "$OPENAPI_FILE" > openapi_gateway_tmp.yaml

echo "Creating API Config..."
gcloud api-gateway api-configs create "$CONFIG_ID" \
  --api="$GATEWAY_ID" \
  --openapi-spec="openapi_gateway_tmp.yaml" \
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
