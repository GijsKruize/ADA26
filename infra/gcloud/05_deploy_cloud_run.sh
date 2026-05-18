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
    "course-service"|"assessment-service"|"learning-profile-service")
      CONTEXT="services/$SERVICE"
      ;;
    "auto-grading-agent"|"recommender-agent")
      CONTEXT="agents/$SERVICE"
      ;;
    "assessment-mcp-server"|"learning-course-mcp-server")
      CONTEXT="mcp_servers/$SERVICE"
      ;;
    "frontend")
      CONTEXT="frontend"
      ;;
  esac

  IMAGE="${IMAGE_BASE}/${SERVICE}:latest"
  
  # Use Cloud Build to build and push
  gcloud builds submit "$CONTEXT" --tag "$IMAGE" --project="${PROJECT_ID}"
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
  
  # Frontend needs special env var API_GATEWAY_URL (will be updated later)
  if [ "$SERVICE" == "frontend" ]; then
    gcloud run deploy "$SERVICE" \
      --image "$IMAGE" \
      --region "$REGION" \
      --project "${PROJECT_ID}" \
      --platform managed \
      --allow-unauthenticated \
      --set-env-vars "API_GATEWAY_URL=REPLACE_ME"
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
