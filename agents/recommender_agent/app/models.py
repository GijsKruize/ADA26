from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class RecommendRequest(BaseModel):
    learner_id: str
    course_id: str

class Recommendation(BaseModel):
    material_id: str
    module_id: str
    title: str
    reason: str
    concepts: List[str]

class RecommendResponse(BaseModel):
    learner_id: str
    course_id: str
    recommendations: List[Recommendation]
