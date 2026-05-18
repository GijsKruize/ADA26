from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class RubricCriterion(BaseModel):
    name: str
    description: str
    max_points: int
    keywords: List[str]
    concepts: List[str]

class Assignment(BaseModel):
    assignment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    title: str
    instructions: str
    rubric: List[RubricCriterion]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class Submission(BaseModel):
    submission_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assignment_id: str
    learner_id: str
    answer_text: str
    file_url: Optional[str] = None
    status: str = "submitted"  # submitted|graded|manual_review
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class CriterionScore(BaseModel):
    criterion: str
    score: float
    max_points: int
    reason: str

class Grade(BaseModel):
    grade_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    submission_id: str
    assignment_id: str
    course_id: str
    learner_id: str
    score: float
    max_score: int
    feedback: str
    criteria_scores: List[CriterionScore]
    weak_concepts: List[str]
    mastered_concepts: List[str]
    graded_by: str = "auto-grading-agent"
    trace: Dict[str, Any]
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
