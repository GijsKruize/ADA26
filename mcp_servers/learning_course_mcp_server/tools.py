import httpx
import os
from typing import Any, Dict, List

COURSE_SERVICE_URL = os.getenv("COURSE_SERVICE_URL", "http://course-service:8080")
LEARNING_PROFILE_SERVICE_URL = os.getenv("LEARNING_PROFILE_SERVICE_URL", "http://learning-profile-service:8080")

async def get_course(course_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{COURSE_SERVICE_URL}/courses/{course_id}")
        response.raise_for_status()
        return response.json()

async def list_modules(course_id: str) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{COURSE_SERVICE_URL}/courses/{course_id}/modules")
        response.raise_for_status()
        return response.json()

async def list_materials(course_id: str) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{COURSE_SERVICE_URL}/courses/{course_id}/materials")
        response.raise_for_status()
        return response.json()

async def get_learning_profile(learner_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{LEARNING_PROFILE_SERVICE_URL}/profiles/{learner_id}")
        response.raise_for_status()
        return response.json()
