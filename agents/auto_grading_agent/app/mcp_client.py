import httpx
import os
from typing import Any, Dict

ASSESSMENT_MCP_SERVER_URL = os.getenv("ASSESSMENT_MCP_SERVER_URL", "http://assessment_mcp_server:8000")

async def get_assignment(assignment_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ASSESSMENT_MCP_SERVER_URL}/tools/execute",
            json={"tool": "get_assignment", "arguments": {"assignment_id": assignment_id}}
        )
        response.raise_for_status()
        return response.json()

async def get_submission(submission_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ASSESSMENT_MCP_SERVER_URL}/tools/execute",
            json={"tool": "get_submission", "arguments": {"submission_id": submission_id}}
        )
        response.raise_for_status()
        return response.json()

async def record_grade(submission_id: str, grade_payload: Dict[str, Any]) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ASSESSMENT_MCP_SERVER_URL}/tools/execute",
            json={
                "tool": "record_grade",
                "arguments": {
                    "submission_id": submission_id,
                    "grade_payload": grade_payload
                }
            }
        )
        response.raise_for_status()
        return response.json()
