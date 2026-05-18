#!/bin/bash
set -euo pipefail

TOPICS=(
  "course-events"
  "assignment-created"
  "submission-created"
  "submission-graded"
)

echo "Creating Pub/Sub topics..."
for TOPIC in "${TOPICS[@]}"; do
  if gcloud pubsub topics describe "$TOPIC" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    echo "Topic $TOPIC already exists."
  else
    echo "Creating topic $TOPIC..."
    gcloud pubsub topics create "$TOPIC" --project="${PROJECT_ID}"
  fi
done

echo "Pub/Sub topics created successfully."
