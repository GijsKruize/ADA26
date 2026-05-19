#!/bin/bash
set -euo pipefail

# API_GATEWAY_URL and DEMO_API_TOKEN must be set
if [[ -z "${API_GATEWAY_URL:-}" ]]; then
  echo "API_GATEWAY_URL is not set"
  exit 1
fi

if [[ -z "${DEMO_API_TOKEN:-}" ]]; then
  echo "DEMO_API_TOKEN is not set"
  exit 1
fi

LEARNER_ID="cloud-demo-learner"
AUTH_HEADER="Authorization: Bearer ${DEMO_API_TOKEN}"

echo "=== RUNNING CLOUD DEMO ==="

# 1. Create Course
echo "Creating course..."
COURSE_RES=$(curl -s -X POST "${API_GATEWAY_URL}/api/courses" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d '{
    "name": "Course DA",
    "title": "Introduction to Data Architecture",
    "description": "Learn about EDA, microservices, and data products.",
    "learning_objectives": ["Understand event-driven architecture", "Understand microservices", "Understand data products"]
  }')
COURSE_ID=$(echo "$COURSE_RES" | python3 -c "import sys, json; print(json.load(sys.stdin)['course_id'])")
echo "Course created: $COURSE_ID"

# 2. Add Module
echo "Adding module..."
MODULE_RES=$(curl -s -X POST "${API_GATEWAY_URL}/api/courses/${COURSE_ID}/modules" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "{
    \"course_id\": \"$COURSE_ID\",
    \"name\": \"Module EDA\",
    \"title\": \"Event-Driven Microservices\",
    \"learning_objectives\": [\"Explain Pub/Sub choreography\", \"Explain service boundaries\"],
    \"order\": 1
  }")
MODULE_ID=$(echo "$MODULE_RES" | python3 -c "import sys, json; print(json.load(sys.stdin)['module_id'])")
echo "Module created: $MODULE_ID"

# 3. Add Material
echo "Adding material..."
curl -s -X POST "${API_GATEWAY_URL}/api/courses/${COURSE_ID}/materials" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "{
    \"course_id\": \"$COURSE_ID\",
    \"module_id\": \"$MODULE_ID\",
    \"name\": \"Material Basics\",
    \"title\": \"Pub/Sub and Choreography Basics\",
    \"type\": \"reading\",
    \"concepts\": [\"pubsub\", \"choreography\", \"event-driven architecture\"],
    \"order\": 1
  }" > /dev/null

# 4. Create Assignment
echo "Creating assignment..."
ASSIGNMENT_RES=$(curl -s -X POST "${API_GATEWAY_URL}/api/assignments" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "{
    \"course_id\": \"$COURSE_ID\",
    \"name\": \"Assignment EDA\",
    \"title\": \"Explain Event-Driven Architecture\",
    \"instructions\": \"Explain how services communicate using events and why this improves loose coupling.\",
    \"rubric\": [
      {\"name\": \"Event communication\", \"description\": \"Checks for keywords related to Pub/Sub\", \"max_points\": 40, \"keywords\": [\"event\", \"publish\", \"subscribe\", \"pubsub\", \"message\"], \"concepts\": [\"pubsub\", \"event-driven architecture\"]},
      {\"name\": \"Loose coupling\", \"description\": \"Checks for keywords related to decoupling\", \"max_points\": 40, \"keywords\": [\"loose coupling\", \"independent\", \"asynchronous\", \"decoupled\"], \"concepts\": [\"choreography\", \"microservices\"]},
      {\"name\": \"Reliability\", \"description\": \"Checks for keywords related to resilience\", \"max_points\": 20, \"keywords\": [\"retry\", \"failure\", \"resilience\", \"eventual consistency\"], \"concepts\": [\"resilience\"]}
    ]
  }")
ASSIGNMENT_ID=$(echo "$ASSIGNMENT_RES" | python3 -c "import sys, json; print(json.load(sys.stdin)['assignment_id'])")

# 5. Submit answer
echo "Submitting answer..."
SUBMISSION_RES=$(curl -s -X POST "${API_GATEWAY_URL}/api/submissions" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "{
    \"assignment_id\": \"$ASSIGNMENT_ID\",
    \"learner_id\": \"$LEARNER_ID\",
    \"answer_text\": \"In an event-driven architecture, services publish events when something important happens. Other services subscribe to those messages through a Pub/Sub system. This means the sender does not need to know who receives the event. The services become more independent and decoupled. Communication is asynchronous, so one service can continue even if another service is temporarily unavailable. This improves loose coupling and supports microservices. With retries and eventual consistency, the system can also become more resilient to failure.\"
  }")
SUBMISSION_ID=$(echo "$SUBMISSION_RES" | python3 -c "import sys, json; print(json.load(sys.stdin)['submission_id'])")

# 6. Trigger grading
echo "Triggering grading..."
curl -s -X POST "${API_GATEWAY_URL}/api/agent/grade-submission" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "{\"submission_id\": \"$SUBMISSION_ID\"}"

# 7. Wait for grade
echo "Waiting for grade..."
for i in {1..15}; do
  GRADE_RES=$(curl -s -H "$AUTH_HEADER" "${API_GATEWAY_URL}/api/submissions/${SUBMISSION_ID}/grade")
  if [[ "$GRADE_RES" == *"grade_id"* ]]; then
    echo "Grade found!"
    echo "$GRADE_RES" | python3 -m json.tool
    break
  fi
  echo "Polling... ($i)"
  sleep 5
done

# 8. Get Profile
echo "Fetching learner profile..."
curl -s -H "$AUTH_HEADER" "${API_GATEWAY_URL}/api/profiles/${LEARNER_ID}" | python3 -m json.tool

# 9. Get Recommendation
echo "Fetching recommendation..."
curl -s -X POST "${API_GATEWAY_URL}/api/agent/recommend" \
  -H "Content-Type: application/json" \
  -H "$AUTH_HEADER" \
  -d "{\"learner_id\": \"$LEARNER_ID\", \"course_id\": \"$COURSE_ID\"}" | python3 -m json.tool

echo "=== CLOUD DEMO COMPLETE ==="
