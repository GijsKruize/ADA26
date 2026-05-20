#!/bin/bash
set -euo pipefail

echo "Fetching service URLs..."

COURSE_URL=$(gcloud run services describe course-service --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')/api
ASSESSMENT_URL=$(gcloud run services describe assessment-service --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')/api
PROFILE_URL=$(gcloud run services describe learning-profile-service --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')/api
AUTO_GRADING_URL=$(gcloud run services describe auto-grading-agent --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')/api
RECOMMENDER_URL=$(gcloud run services describe recommender-agent --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')/api
ASSESSMENT_MCP_URL=$(gcloud run services describe assessment-mcp-server --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
LEARNING_COURSE_MCP_URL=$(gcloud run services describe learning-course-mcp-server --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
AI_PROXY_URL=$(gcloud run services describe ai-proxy --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')

echo "Updating Cloud Run services with real URLs..."

SERVICES=(
  "course-service"
  "assessment-service"
  "learning-profile-service"
  "auto-grading-agent"
  "recommender-agent"
  "assessment-mcp-server"
  "learning-course-mcp-server"
)

# Build the env var string
ENV_VARS="COURSE_SERVICE_URL=${COURSE_URL}"
ENV_VARS="${ENV_VARS},ASSESSMENT_SERVICE_URL=${ASSESSMENT_URL}"
ENV_VARS="${ENV_VARS},LEARNING_PROFILE_SERVICE_URL=${PROFILE_URL}"
ENV_VARS="${ENV_VARS},AUTO_GRADING_AGENT_URL=${AUTO_GRADING_URL}"
ENV_VARS="${ENV_VARS},RECOMMENDER_AGENT_URL=${RECOMMENDER_URL}"
ENV_VARS="${ENV_VARS},ASSESSMENT_MCP_SERVER_URL=${ASSESSMENT_MCP_URL}"
ENV_VARS="${ENV_VARS},LEARNING_COURSE_MCP_SERVER_URL=${LEARNING_COURSE_MCP_URL}"
ENV_VARS="${ENV_VARS},OLLAMA_BASE_URL=${AI_PROXY_URL}"
ENV_VARS="${ENV_VARS},OLLAMA_MODEL=llama3.1"
ENV_VARS="${ENV_VARS},LOCAL_MODE=false"

for SERVICE in "${SERVICES[@]}"; do
  echo "Updating $SERVICE..."
  gcloud run services update "$SERVICE" \
    --region "${REGION}" \
    --project "${PROJECT_ID}" \
    --update-env-vars "$ENV_VARS"
done

echo "Updating Frontend with API Gateway URL..."
GW_URL=$(gcloud api-gateway gateways describe "${GATEWAY_ID:-learnsphere-gateway}" --location="${REGION}" --project="${PROJECT_ID}" --format='value(defaultHostname)' 2>/dev/null || echo "ERROR_GETTING_GW_URL")

if [ "$GW_URL" != "ERROR_GETTING_GW_URL" ]; then
  gcloud run services update frontend \
    --region "${REGION}" \
    --project "${PROJECT_ID}" \
    --update-env-vars "API_GATEWAY_URL=https://${GW_URL}"
fi

echo "URLs updated successfully."
