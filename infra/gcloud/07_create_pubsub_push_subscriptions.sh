#!/bin/bash
set -euo pipefail

echo "Creating Pub/Sub push subscription for auto-grading-agent..."

# Get the URL of the auto-grading-agent service
AUTO_GRADING_AGENT_URL=$(gcloud run services describe auto-grading-agent --platform managed --region "${REGION}" --project "${PROJECT_ID}" --format 'value(status.url)')

ENDPOINT="${AUTO_GRADING_AGENT_URL}/pubsub/submission-created"

if gcloud pubsub subscriptions describe auto-grading-agent-sub --project="${PROJECT_ID}" >/dev/null 2>&1; then
  echo "Subscription auto-grading-agent-sub already exists. Updating..."
  gcloud pubsub subscriptions update auto-grading-agent-sub \
    --push-endpoint="$ENDPOINT" \
    --project="${PROJECT_ID}"
else
  echo "Creating subscription auto-grading-agent-sub..."
  gcloud pubsub subscriptions create auto-grading-agent-sub \
    --topic=submission-created \
    --push-endpoint="$ENDPOINT" \
    --project="${PROJECT_ID}"
fi

echo "Pub/Sub push subscription created/updated."
