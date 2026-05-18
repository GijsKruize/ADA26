import httpx
import os
from typing import Any, Dict

ASSESSMENT_SERVICE_URL = os.getenv("ASSESSMENT_SERVICE_URL", "http://assessment-service:8080")

async def get_assignment(assignment_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ASSESSMENT_SERVICE_URL}/assignments/{assignment_id}")
        response.raise_for_status()
        return response.json()

async def get_submission(submission_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ASSESSMENT_SERVICE_URL}/submissions/{submission_id}")
        response.raise_for_status()
        return response.json()

async def record_grade(submission_id: str, grade_payload: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ASSESSMENT_SERVICE_URL}/submissions/{submission_id}/grade",
            json=grade_payload
        )
        response.raise_for_status()
        return response.json()
