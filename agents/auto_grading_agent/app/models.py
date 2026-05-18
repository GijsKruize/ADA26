from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GradeRequest(BaseModel):
    submission_id: str
    assessment_id: str
    student_id: str
    answer_text: str

class CriterionScore(BaseModel):
    criterion: str
    score: float
    max_points: int
    reason: str

class GradeResult(BaseModel):
    score: float
    max_score: int
    feedback: str
    criteria_scores: List[CriterionScore]
    mastered_concepts: List[str]
    weak_concepts: List[str]
    trace: Dict[str, Any]
