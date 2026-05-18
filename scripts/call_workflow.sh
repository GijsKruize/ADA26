#!/bin/bash
set -euo pipefail

# Required env vars: PROJECT_ID, REGION
if [[ -z "${PROJECT_ID:-}" ]]; then
  echo "PROJECT_ID is not set"
  exit 1
fi

if [[ -z "${REGION:-}" ]]; then
  echo "REGION is not set"
  exit 1
fi

# Get service URLs to pass to the workflow
echo "Getting service URLs..."
COURSE_URL=$(gcloud run services describe course-service --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
ASSESSMENT_URL=$(gcloud run services describe assessment-service --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
PROFILE_URL=$(gcloud run services describe learning-profile-service --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
GRADER_URL=$(gcloud run services describe auto-grading-agent --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')
RECOMMENDER_URL=$(gcloud run services describe recommender-agent --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')

DATA=$(cat <<EOF
{
  "course_service_url": "$COURSE_URL",
  "assessment_service_url": "$ASSESSMENT_URL",
  "learning_profile_service_url": "$PROFILE_URL",
  "auto_grading_agent_url": "$GRADER_URL",
  "recommender_agent_url": "$RECOMMENDER_URL",
  "learner_id": "workflow-demo-learner-$(date +%s)"
}
EOF
)

echo "Executing workflow demo_learning_flow..."
gcloud workflows run demo_learning_flow \
  --location="${REGION}" \
  --project="${PROJECT_ID}" \
  --data="$DATA"
