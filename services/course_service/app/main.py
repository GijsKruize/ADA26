from fastapi import FastAPI, HTTPException
from typing import List
from .models import Course, Module, Material
from . import repository
from . import events

app = FastAPI(title="Course Service")

@app.get("/health")
def health():
    return {"status": "ok", "service": "course-service"}

@app.post("/courses", response_model=Course)
def create_course(course: Course):
    res = repository.create_course(course)
    events.publish_course_created(res.course_id, res.title, res.learning_objectives)
    return res

@app.get("/courses/{course_id}", response_model=Course)
def get_course(course_id: str):
    course = repository.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.post("/courses/{course_id}/modules", response_model=Module)
def create_module(course_id: str, module: Module):
    if module.course_id != course_id:
        raise HTTPException(status_code=400, detail="course_id mismatch")
    return repository.create_module(module)

@app.get("/courses/{course_id}/modules", response_model=List[Module])
def list_modules(course_id: str):
    return repository.list_modules(course_id)

@app.post("/courses/{course_id}/materials", response_model=Material)
def create_material(course_id: str, material: Material):
    if material.course_id != course_id:
        raise HTTPException(status_code=400, detail="course_id mismatch")
    res = repository.create_material(material)
    events.publish_course_material_updated(res.course_id, res.material_id, res.concepts, res.version)
    return res

@app.get("/courses/{course_id}/materials", response_model=List[Material])
def list_materials(course_id: str):
    return repository.list_materials(course_id)
