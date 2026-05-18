import base64
import json
import os
from datetime import datetime
import functions_framework
from google.cloud import firestore

# Initialize Firestore
db = firestore.Client(
    project=os.environ.get("PROJECT_ID"),
    database=os.environ.get("FIRESTORE_DATABASE", "(default)")
)

@functions_framework.cloud_event
def on_submission_graded(cloud_event):
    """
    Create simulated notification from grade event.
    Triggered by Pub/Sub topic 'submission-graded'.
    """
    # Decode Pub/Sub message
    try:
        data_base64 = cloud_event.data["message"]["data"]
        data_json = base64.b64decode(data_base64).decode("utf-8")
        envelope = json.loads(data_json)
    except Exception as e:
        print(f"Error decoding Pub/Sub message: {e}")
        return

    event_id = envelope.get("event_id")
    payload = envelope.get("payload", {})
    
    submission_id = payload.get("submission_id")
    learner_id = payload.get("learner_id")
    assignment_id = payload.get("assignment_id")
    score = payload.get("score")
    max_score = payload.get("max_score")
    feedback = payload.get("feedback")

    if not event_id or not learner_id:
        print(f"Missing required fields: event_id={event_id}, learner_id={learner_id}")
        return

    # Idempotency check (C5): use event_id as the Firestore document ID.
    notification_ref = db.collection("notifications").document(event_id)
    notification_doc = notification_ref.get()

    if notification_doc.exists:
        print(f"Notification for event {event_id} already exists. Skipping.")
        return

    # Write notification document (as per gemini.md)
    notification_data = {
        "notification_id": event_id,
        "learner_id": learner_id,
        "type": "submission_graded",
        "title": "Submission graded",
        "message": f"Your submission for assignment {assignment_id} has been graded. Score: {score}/{max_score}. Feedback: {feedback}",
        "status": "simulated_sent",
        "created_at": datetime.utcnow().isoformat()
    }

    notification_ref.set(notification_data)
    print(f"Created notification for learner {learner_id} from event {event_id}")
