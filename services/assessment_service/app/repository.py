from shared.firestore_client import get_firestore_client
from .models import Assignment, Submission, Grade
from typing import Optional

db = get_firestore_client()

def create_assignment(assignment: Assignment) -> Assignment:
    db.collection("assignments").document(assignment.assignment_id).set(assignment.dict())
    return assignment

def get_assignment(assignment_id: str) -> Optional[Assignment]:
    doc = db.collection("assignments").document(assignment_id).get()
    if doc.exists:
        return Assignment(**doc.to_dict())
    return None

def create_submission(submission: Submission) -> Submission:
    db.collection("submissions").document(submission.submission_id).set(submission.dict())
    return submission

def get_submission(submission_id: str) -> Optional[Submission]:
    doc = db.collection("submissions").document(submission_id).get()
    if doc.exists:
        return Submission(**doc.to_dict())
    return None

def update_submission_status(submission_id: str, status: str):
    db.collection("submissions").document(submission_id).update({"status": status})

def create_grade(grade: Grade) -> Grade:
    db.collection("grades").document(grade.grade_id).set(grade.dict())
    return grade

def get_grade_by_submission(submission_id: str) -> Optional[Grade]:
    docs = db.collection("grades").where("submission_id", "==", submission_id).limit(1).stream()
    for doc in docs:
        return Grade(**doc.to_dict())
    return None
