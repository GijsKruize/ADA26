import httpx
import os
from typing import Any, Dict, List

LEARNING_COURSE_MCP_SERVER_URL = os.getenv("LEARNING_COURSE_MCP_SERVER_URL", "http://learning_course_mcp_server:8000")

async def get_course(course_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LEARNING_COURSE_MCP_SERVER_URL}/tools/execute",
            json={"tool": "get_course", "arguments": {"course_id": course_id}}
        )
        response.raise_for_status()
        return response.json()

async def list_modules(course_id: str) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LEARNING_COURSE_MCP_SERVER_URL}/tools/execute",
            json={"tool": "list_modules", "arguments": {"course_id": course_id}}
        )
        response.raise_for_status()
        return response.json()

async def list_materials(course_id: str) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LEARNING_COURSE_MCP_SERVER_URL}/tools/execute",
            json={"tool": "list_materials", "arguments": {"course_id": course_id}}
        )
        response.raise_for_status()
        return response.json()

async def get_learning_profile(learner_id: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LEARNING_COURSE_MCP_SERVER_URL}/tools/execute",
            json={"tool": "get_learning_profile", "arguments": {"learner_id": learner_id}}
        )
        response.raise_for_status()
        return response.json()
