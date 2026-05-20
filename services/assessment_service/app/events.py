from shared.pubsub_client import publish_event
from shared.event_envelope import make_envelope
from shared.settings import settings

PRODUCER = "assessment-service"

def publish_assignment_created(assignment_id: str, course_id: str, title: str):
    payload = {
        "assignment_id": assignment_id,
        "course_id": course_id,
        "title": title
    }
    envelope = make_envelope("AssignmentCreated", PRODUCER, payload)
    publish_event(settings.PUBSUB_TOPIC_ASSIGNMENT_CREATED, envelope)

def publish_submission_created(submission_id: str, assignment_id: str, learner_id: str, learner_email: str = "demo@example.com"):
    payload = {
        "submission_id": submission_id,
        "assignment_id": assignment_id,
        "learner_id": learner_id,
        "learner_email": learner_email
    }
    envelope = make_envelope("SubmissionCreated", PRODUCER, payload)
    publish_event(settings.PUBSUB_TOPIC_SUBMISSION_CREATED, envelope)

def publish_submission_graded(submission_id: str, assignment_id: str, course_id: str, learner_id: str, score: float, max_score: int, feedback: str, weak_concepts: list, mastered_concepts: list, learner_email: str = "demo@example.com"):
    payload = {
        "submission_id": submission_id,
        "assignment_id": assignment_id,
        "course_id": course_id,
        "learner_id": learner_id,
        "learner_email": learner_email,
        "score": score,
        "max_score": max_score,
        "feedback": feedback,
        "weak_concepts": weak_concepts,
        "mastered_concepts": mastered_concepts
    }
    envelope = make_envelope("SubmissionGraded", PRODUCER, payload)
    publish_event(settings.PUBSUB_TOPIC_SUBMISSION_GRADED, envelope)
