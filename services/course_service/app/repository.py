from shared.firestore_client import get_firestore_client
from .models import Course, Module, Material
from typing import List, Optional

db = get_firestore_client()

def create_course(course: Course) -> Course:
    db.collection("courses").document(course.course_id).set(course.dict())
    return course

def get_course(course_id: str) -> Optional[Course]:
    doc = db.collection("courses").document(course_id).get()
    if doc.exists:
        return Course(**doc.to_dict())
    return None

def create_module(module: Module) -> Module:
    db.collection("modules").document(module.module_id).set(module.dict())
    return module

def list_modules(course_id: str) -> List[Module]:
    docs = db.collection("modules").where("course_id", "==", course_id).stream()
    modules = [Module(**doc.to_dict()) for doc in docs]
    return sorted(modules, key=lambda m: m.order)

def create_material(material: Material) -> Material:
    db.collection("materials").document(material.material_id).set(material.dict())
    return material

def list_materials(course_id: str) -> List[Material]:
    docs = db.collection("materials").where("course_id", "==", course_id).stream()
    materials = [Material(**doc.to_dict()) for doc in docs]
    return sorted(materials, key=lambda m: m.order)
