from fastapi import FastAPI, HTTPException
from .models import Assignment, Submission, Grade
from . import repository
from . import events

app = FastAPI(title="Assessment Service")

@app.get("/health")
def health():
    return {"status": "ok", "service": "assessment-service"}

@app.post("/assignments", response_model=Assignment)
def create_assignment(assignment: Assignment):
    res = repository.create_assignment(assignment)
    events.publish_assignment_created(res.assignment_id, res.course_id, res.title)
    return res

@app.get("/assignments/{assignment_id}", response_model=Assignment)
def get_assignment(assignment_id: str):
    res = repository.get_assignment(assignment_id)
    if not res:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return res

@app.post("/submissions", response_model=Submission)
def create_submission(submission: Submission):
    res = repository.create_submission(submission)
    events.publish_submission_created(res.submission_id, res.assignment_id, res.learner_id)
    return res

@app.get("/submissions/{submission_id}", response_model=Submission)
def get_submission(submission_id: str):
    res = repository.get_submission(submission_id)
    if not res:
        raise HTTPException(status_code=404, detail="Submission not found")
    return res

@app.post("/submissions/{submission_id}/grade", response_model=Grade)
def record_grade(submission_id: str, grade: Grade):
    if grade.submission_id != submission_id:
        raise HTTPException(status_code=400, detail="submission_id mismatch")
    
    submission = repository.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    res = repository.create_grade(grade)
    repository.update_submission_status(submission_id, "graded")
    
    events.publish_submission_graded(
        submission_id=res.submission_id,
        assignment_id=res.assignment_id,
        course_id=res.course_id,
        learner_id=res.learner_id,
        score=res.score,
        max_score=res.max_score,
        feedback=res.feedback,
        weak_concepts=res.weak_concepts,
        mastered_concepts=res.mastered_concepts
    )
    return res

@app.get("/submissions/{submission_id}/grade", response_model=Grade)
def get_grade(submission_id: str):
    res = repository.get_grade_by_submission(submission_id)
    if not res:
        raise HTTPException(status_code=404, detail="Grade not found for this submission")
    return res
