from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class Course(BaseModel):
    course_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    title: str
    description: str
    learning_objectives: List[str]
    status: str = "draft"  # draft|published
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class Module(BaseModel):
    module_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    name: str
    title: str
    learning_objectives: List[str]
    order: int
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class Material(BaseModel):
    material_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str
    module_id: str
    name: str
    title: str
    type: str  # reading|video|quiz|slides
    content_text: Optional[str] = None
    content_url: Optional[str] = None
    concepts: List[str]
    order: int
    version: int = 1
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
