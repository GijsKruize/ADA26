#!/bin/bash
set -euo pipefail

FUNCTIONS=(
  "profile_update_function"
  "notification_function"
)

for FUNC in "${FUNCTIONS[@]}"; do
  echo "Deploying function: $FUNC..."
  
  # Map name to directory (they match in this case but good to be explicit)
  DIR="functions/$FUNC"
  
  gcloud functions deploy "$FUNC" \
    --gen2 \
    --runtime=python311 \
    --region="${REGION}" \
    --project="${PROJECT_ID}" \
    --trigger-topic=submission-graded \
    --source="$DIR" \
    --entry-point="on_submission_graded" \
    --set-env-vars "PROJECT_ID=${PROJECT_ID},REGION=${REGION},FIRESTORE_DATABASE=(default)"
done

echo "Cloud Functions deployed."
