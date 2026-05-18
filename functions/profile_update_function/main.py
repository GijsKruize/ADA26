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
    Update learner profile from grade event.
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

    payload = envelope.get("payload", {})
    submission_id = payload.get("submission_id")
    learner_id = payload.get("learner_id")
    assignment_id = payload.get("assignment_id")
    course_id = payload.get("course_id")
    score = payload.get("score")
    max_score = payload.get("max_score")
    feedback = payload.get("feedback")
    weak_concepts = payload.get("weak_concepts", [])
    mastered_concepts = payload.get("mastered_concepts", [])

    if not learner_id or not submission_id:
        print(f"Missing required fields: learner_id={learner_id}, submission_id={submission_id}")
        return

    # Idempotency check (C5): check whether learner_profiles/{learner_id}/grade_history 
    # already contains an entry with this submission_id.
    profile_ref = db.collection("learner_profiles").document(learner_id)
    profile_doc = profile_ref.get()

    if profile_doc.exists:
        profile_data = profile_doc.to_dict()
        grade_history = profile_data.get("grade_history", [])
        if any(g.get("submission_id") == submission_id for g in grade_history):
            print(f"Submission {submission_id} already processed for learner {learner_id}. Skipping.")
            return
    else:
        # Initialize new profile if it doesn't exist
        profile_data = {
            "learner_id": learner_id,
            "mastered_concepts": {},
            "weak_concepts": [],
            "grade_history": [],
            "last_recommendations": [],
            "updated_at": datetime.utcnow().isoformat()
        }

    # Update Logic (as per gemini.md)
    ratio = score / max_score if max_score > 0 else 0
    
    # 1. mastered_concepts: If score / max_score >= 0.80, increase mastery score
    if ratio >= 0.80:
        current_mastery = profile_data.get("mastered_concepts", {})
        for concept in mastered_concepts:
            # Set to max(existing, current_ratio)
            current_mastery[concept] = max(current_mastery.get(concept, 0), ratio)
        profile_data["mastered_concepts"] = current_mastery

    # 2. weak_concepts: If score / max_score < 0.70, add to weak_concepts (deduplicated)
    if ratio < 0.70:
        current_weak = set(profile_data.get("weak_concepts", []))
        for concept in weak_concepts:
            current_weak.add(concept)
        profile_data["weak_concepts"] = list(current_weak)
    
    # 3. Append to grade_history
    grade_entry = {
        "submission_id": submission_id,
        "assignment_id": assignment_id,
        "course_id": course_id,
        "score": score,
        "max_score": max_score,
        "feedback": feedback,
        "created_at": datetime.utcnow().isoformat()
    }
    profile_data.setdefault("grade_history", []).append(grade_entry)
    profile_data["updated_at"] = datetime.utcnow().isoformat()

    # Save to Firestore
    profile_ref.set(profile_data)
    print(f"Successfully updated profile for learner {learner_id} from submission {submission_id}")
