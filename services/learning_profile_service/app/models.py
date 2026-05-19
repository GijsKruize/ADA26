from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class GradeHistoryEntry(BaseModel):
    submission_id: str
    assignment_id: str
    course_id: str
    score: float
    max_score: float
    feedback: str
    created_at: datetime

class LearningProfile(BaseModel):
    learner_id: str
    name: str
    mastered_concepts: Dict[str, float] = Field(default_factory=dict)
    weak_concepts: List[str] = Field(default_factory=list)
    grade_history: List[GradeHistoryEntry] = Field(default_factory=list)
    last_recommendations: List[Dict] = Field(default_factory=list)
    updated_at: datetime

class ProfileEvent(BaseModel):
    event_type: str
    payload: Dict

class RecalculateResponse(BaseModel):
    status: str
    message: str
