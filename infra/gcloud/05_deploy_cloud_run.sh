#!/bin/bash
set -euo pipefail

# Services to build and deploy
SERVICES=(
  "ollama"
  "ai-proxy"
  "course-service"
  "assessment-service"
  "learning-profile-service"
  "auto-grading-agent"
  "recommender-agent"
  "assessment-mcp-server"
  "learning-course-mcp-server"
  "frontend"
)

# Base image path
IMAGE_BASE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}"

echo "Building and pushing images..."
for SERVICE in "${SERVICES[@]}"; do
  echo "Building $SERVICE..."
  # Determine context directory
  case $SERVICE in
    "ollama") CONTEXT="infra/ollama" ;;
    "ai-proxy") CONTEXT="infra/ai-proxy" ;;
    "course-service") CONTEXT="services/course_service" ;;
    "assessment-service") CONTEXT="services/assessment_service" ;;
    "learning-profile-service") CONTEXT="services/learning_profile_service" ;;
    "auto-grading-agent") CONTEXT="agents/auto_grading_agent" ;;
    "recommender-agent") CONTEXT="agents/recommender_agent" ;;
    "assessment-mcp-server") CONTEXT="mcp_servers/assessment_mcp_server" ;;
    "learning-course-mcp-server") CONTEXT="mcp_servers/learning_course_mcp_server" ;;
    "frontend") CONTEXT="frontend" ;;
  esac

  IMAGE="${IMAGE_BASE}/${SERVICE}:latest"
  
  if [ "$SERVICE" == "ollama" ] || [ "$SERVICE" == "ai-proxy" ]; then
    # Check if image already exists to avoid long builds for ollama
    if gcloud artifacts docker images list "$IMAGE" --project="${PROJECT_ID}" --limit=1 >/dev/null 2>&1; then
      echo "Image $IMAGE already exists, skipping build."
    else
      # These services don't need shared/ but need their specific context
      gcloud builds submit "$CONTEXT" --tag "$IMAGE" --project="${PROJECT_ID}"
    fi
  else
    # Submit the build from the project root but point to the specific Dockerfile
    # This allows Cloud Build to see the shared/ directory without local file moves
    gcloud builds submit . --tag "$IMAGE" --project="${PROJECT_ID}" --dockerfile="$CONTEXT/Dockerfile"
  fi
done

echo "Deploying Cloud Run services..."

# 1. Deploy Ollama
echo "Deploying ollama..."
gcloud run deploy ollama \
  --image "${IMAGE_BASE}/ollama:latest" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --memory 8Gi \
  --cpu 2 \
  --port 11434 \
  --allow-unauthenticated

OLLAMA_URL=$(gcloud run services describe ollama --region "${REGION}" --project "${PROJECT_ID}" --format='value(status.url)')

# 2. Deploy AI Proxy
echo "Deploying ai-proxy..."
gcloud run deploy ai-proxy \
  --image "${IMAGE_BASE}/ai-proxy:latest" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --set-env-vars "OLLAMA_URL=${OLLAMA_URL}" \
  --allow-unauthenticated

AI_PROXY_URL=$(gcloud run services describe ai-proxy --region "${REGION}" --project "${PROJECT_ID}" --format='value(status.url)')

# Common env vars
ENV_VARS="PROJECT_ID=${PROJECT_ID},REGION=${REGION},FIRESTORE_DATABASE=(default)"
ENV_VARS="${ENV_VARS},PUBSUB_TOPIC_COURSE_EVENTS=course-events"
ENV_VARS="${ENV_VARS},PUBSUB_TOPIC_ASSIGNMENT_CREATED=assignment-created"
ENV_VARS="${ENV_VARS},PUBSUB_TOPIC_SUBMISSION_CREATED=submission-created"
ENV_VARS="${ENV_VARS},PUBSUB_TOPIC_SUBMISSION_GRADED=submission-graded"
ENV_VARS="${ENV_VARS},OLLAMA_BASE_URL=${AI_PROXY_URL},OLLAMA_MODEL=qwen2.5:7b,LOCAL_MODE=false"

# Deploy remaining services
REMAINING_SERVICES=(
  "course-service"
  "assessment-service"
  "learning-profile-service"
  "auto-grading-agent"
  "recommender-agent"
  "assessment-mcp-server"
  "learning-course-mcp-server"
)

for SERVICE in "${REMAINING_SERVICES[@]}"; do
  echo "Deploying $SERVICE..."
  IMAGE="${IMAGE_BASE}/${SERVICE}:latest"
  
  gcloud run deploy "$SERVICE" \
    --image "$IMAGE" \
    --region "$REGION" \
    --project "${PROJECT_ID}" \
    --allow-unauthenticated \
    --set-env-vars "$ENV_VARS"
done

# Deploy Frontend (needs special handling for API Gateway URL)
echo "Deploying frontend..."
IMAGE="${IMAGE_BASE}/frontend:latest"
EXISTING_GW_URL=$(gcloud api-gateway gateways describe "${GATEWAY_ID:-learnsphere-gateway}" --location="${REGION}" --project="${PROJECT_ID}" --format='value(defaultHostname)' 2>/dev/null || echo "REPLACE_ME")

gcloud run deploy frontend \
  --image "$IMAGE" \
  --region "$REGION" \
  --project "${PROJECT_ID}" \
  --port 80 \
  --allow-unauthenticated \
  --set-env-vars "API_GATEWAY_URL=https://${EXISTING_GW_URL}"

echo "Cloud Run services deployed."
