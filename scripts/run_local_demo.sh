#!/bin/bash
set -euo pipefail

# Local URLs
export COURSE_SERVICE_URL="http://localhost:8001"
export ASSESSMENT_SERVICE_URL="http://localhost:8002"
export LEARNING_PROFILE_SERVICE_URL="http://localhost:8003"
export AUTO_GRADING_AGENT_URL="http://localhost:8004"
export RECOMMENDER_AGENT_URL="http://localhost:8005"

LEARNER_ID="local-demo-learner"

echo "=== RUNNING LOCAL DEMO ==="

# 1. Seed data and get IDs
echo "Seeding data..."
# Use python3 to run the seed script
python3 scripts/seed_demo_data.py > /tmp/seed_output.txt
cat /tmp/seed_output.txt

COURSE_ID=$(grep "Created course:" /tmp/seed_output.txt | awk '{print $NF}')
ASSIGNMENT_ID=$(grep "Created assignment:" /tmp/seed_output.txt | awk '{print $NF}')

# 2. Submit answer
echo "Submitting answer..."
SUBMISSION_DATA=$(cat <<EOF
{
  "assignment_id": "$ASSIGNMENT_ID",
  "learner_id": "$LEARNER_ID",
  "answer_text": "In an event-driven architecture, services publish events when something important happens. Other services subscribe to those messages through a Pub/Sub system. This means the sender does not need to know who receives the event. The services become more independent and decoupled. Communication is asynchronous, so one service can continue even if another service is temporarily unavailable. This improves loose coupling and supports microservices. With retries and eventual consistency, the system can also become more resilient to failure."
}
EOF
)

SUBMISSION_RES=$(curl -s -X POST "${ASSESSMENT_SERVICE_URL}/submissions" \
  -H "Content-Type: application/json" \
  -d "$SUBMISSION_DATA")
SUBMISSION_ID=$(echo "$SUBMISSION_RES" | python3 -c "import sys, json; print(json.load(sys.stdin)['submission_id'])")
echo "Submission created: $SUBMISSION_ID"

# 3. Trigger grading
echo "Triggering grading..."
curl -s -X POST "${AUTO_GRADING_AGENT_URL}/agent/grade-submission" \
  -H "Content-Type: application/json" \
  -d "{\"submission_id\": \"$SUBMISSION_ID\"}"

# 4. Wait for grade (Pub/Sub is local so it should be fast or handled by the agent)
echo "Waiting for grade..."
for i in {1..10}; do
  GRADE_RES=$(curl -s "${ASSESSMENT_SERVICE_URL}/submissions/${SUBMISSION_ID}/grade")
  if [[ "$GRADE_RES" == *"grade_id"* ]]; then
    echo "Grade found!"
    echo "$GRADE_RES" | python3 -m json.tool
    break
  fi
  echo "Polling... ($i)"
  sleep 2
done

# 5. Get Profile
echo "Fetching learner profile..."
curl -s "${LEARNING_PROFILE_SERVICE_URL}/profiles/${LEARNER_ID}" | python3 -m json.tool

# 6. Get Recommendation
echo "Fetching recommendation..."
curl -s -X POST "${RECOMMENDER_AGENT_URL}/agent/recommend" \
  -H "Content-Type: application/json" \
  -d "{\"learner_id\": \"$LEARNER_ID\", \"course_id\": \"$COURSE_ID\"}" | python3 -m json.tool

echo "=== LOCAL DEMO COMPLETE ==="
