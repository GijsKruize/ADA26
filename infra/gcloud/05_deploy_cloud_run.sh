#!/bin/bash
set -euo pipefail

# Services to build and deploy
SERVICES=(
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
  
  # Copy Dockerfile to root temporarily to allow Cloud Build to see shared/
  cp "$CONTEXT/Dockerfile" ./Dockerfile
  gcloud builds submit . --tag "$IMAGE" --project="${PROJECT_ID}"
  rm ./Dockerfile
done

echo "Deploying Cloud Run services..."

# Common env vars (simplified for first pass)
# In a real scenario, we might need multiple passes to set URLs of other services.
ENV_VARS="PROJECT_ID=${PROJECT_ID},REGION=${REGION},FIRESTORE_DATABASE=(default)"
ENV_VARS="${ENV_VARS},PUBSUB_TOPIC_COURSE_EVENTS=course-events"
ENV_VARS="${ENV_VARS},PUBSUB_TOPIC_ASSIGNMENT_CREATED=assignment-created"
ENV_VARS="${ENV_VARS},PUBSUB_TOPIC_SUBMISSION_CREATED=submission-created"
ENV_VARS="${ENV_VARS},PUBSUB_TOPIC_SUBMISSION_GRADED=submission-graded"

for SERVICE in "${SERVICES[@]}"; do
  echo "Deploying $SERVICE..."
  IMAGE="${IMAGE_BASE}/${SERVICE}:latest"
  
  # Frontend needs special env var API_GATEWAY_URL (updated by 09_deploy_gateway.sh)
  if [ "$SERVICE" == "frontend" ]; then
    # Try to get existing URL if possible
    EXISTING_GW_URL=$(gcloud api-gateway gateways describe "$GATEWAY_ID" --location="${REGION}" --project="${PROJECT_ID}" --format='value(defaultHostname)' 2>/dev/null || echo "REPLACE_ME")
    
    gcloud run deploy "$SERVICE" \
      --image "$IMAGE" \
      --region "$REGION" \
      --project "${PROJECT_ID}" \
      --platform managed \
      --allow-unauthenticated \
      --port 80 \
      --set-env-vars "API_GATEWAY_URL=https://${EXISTING_GW_URL}"
  else
    gcloud run deploy "$SERVICE" \
      --image "$IMAGE" \
      --region "$REGION" \
      --project "${PROJECT_ID}" \
      --platform managed \
      --allow-unauthenticated \
      --set-env-vars "$ENV_VARS"
  fi
done

echo "Cloud Run services deployed."
