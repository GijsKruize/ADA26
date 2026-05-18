import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any

from .circuit_breaker import ollama_circuit_breaker
from .mcp_client import get_assignment, get_submission, record_grade
from shared.ollama_client import call_ollama
from shared.deterministic_llm import run_deterministic_grader
from shared.firestore_client import get_firestore_client

logger = logging.getLogger(__name__)

@ollama_circuit_breaker
def call_ollama_with_breaker(prompt: str) -> str:
    return call_ollama(prompt)

async def grade_submission(submission_id: str) -> Dict[str, Any]:
    # 1. Fetch submission and assignment details via MCP
    submission = await get_submission(submission_id)
    assignment_id = submission["assignment_id"]
    assignment = await get_assignment(assignment_id)
    
    answer_text = submission["answer_text"]
    rubric = assignment["rubric"]
    
    # 2. Try grading with Ollama
    prompt = f"""
    Grade the following student answer based on the provided rubric.
    Return a JSON object only.
    
    Student Answer: {answer_text}
    
    Rubric: {json.dumps(rubric)}
    
    The JSON should have:
    - score: total score (float)
    - max_score: total possible score (int)
    - feedback: general feedback (string)
    - criteria_scores: list of objects with {{criterion, score, max_points, reason}}
    - mastered_concepts: list of concepts the student mastered (strings)
    - weak_concepts: list of concepts the student needs to improve on (strings)
    """
    
    grading_result = None
    llm_provider = "ollama"
    
    try:
        response = call_ollama_with_breaker(prompt)
        # Parse JSON from response (handling potential markdown blocks)
        json_match = response.strip()
        if json_match.startswith("```json"):
            json_match = json_match[7:-3].strip()
        elif json_match.startswith("```"):
            json_match = json_match[3:-3].strip()
            
        grading_result = json.loads(json_match)
        grading_result["trace"] = {
            "llm_provider": "ollama",
            "model": "llama3", # Assuming default
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.warning(f"Ollama grading failed or circuit breaker open: {e}. Falling back to deterministic grader.")
        grading_result = run_deterministic_grader(answer_text, rubric)
        llm_provider = "deterministic-fallback"

    # 3. Store trace in Firestore
    db = get_firestore_client()
    trace_id = str(uuid.uuid4())
    trace_data = {
        "id": trace_id,
        "submission_id": submission_id,
        "llm_provider": llm_provider,
        "result": grading_result,
        "timestamp": datetime.utcnow().isoformat()
    }
    db.collection("llm_traces").document(trace_id).set(trace_data)
    
    # 4. Record grade via MCP
    grade_payload = {
        "submission_id": submission_id,
        "assignment_id": assignment_id,
        "course_id": assignment["course_id"],
        "learner_id": submission["learner_id"],
        "score": grading_result["score"],
        "max_score": grading_result["max_score"],
        "feedback": grading_result["feedback"],
        "criteria_scores": grading_result.get("criteria_scores", []),
        "mastered_concepts": grading_result.get("mastered_concepts", []),
        "weak_concepts": grading_result.get("weak_concepts", []),
        "graded_by": f"auto-grading-agent ({llm_provider})",
        "trace": grading_result.get("trace", {"provider": llm_provider})
    }
    await record_grade(submission_id, grade_payload)
    
    return grading_result
