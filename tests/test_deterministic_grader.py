import pytest
from shared.deterministic_llm import run_deterministic_grader

def test_deterministic_grader_demo():
    # Demo data from gemini.md
    rubric = [
        {
            "name": "Event communication",
            "max_points": 40,
            "keywords": ["event", "publish", "subscribe", "pubsub", "message"],
            "concepts": ["pubsub", "event-driven architecture"]
        },
        {
            "name": "Loose coupling",
            "max_points": 40,
            "keywords": ["loose coupling", "independent", "asynchronous", "decoupled"],
            "concepts": ["choreography", "microservices"]
        },
        {
            "name": "Reliability",
            "max_points": 20,
            "keywords": ["retry", "failure", "resilience", "eventual consistency"],
            "concepts": ["resilience"]
        }
    ]
    
    answer_text = (
        "In an event-driven architecture, services publish events when something important happens. "
        "Other services subscribe to those messages through a Pub/Sub system. "
        "This means the sender does not need to know who receives the event. "
        "The services become more independent and decoupled. "
        "Communication is asynchronous, so one service can continue even if another service is temporarily unavailable. "
        "This improves loose coupling and supports microservices. "
        "With retries and eventual consistency, the system can also become more resilient to failure."
    )
    
    result = run_deterministic_grader(answer_text, rubric)
    
    # Assert total score is in range 60-95
    assert 60 <= result["score"] <= 95
    
    # Assert mastered_concepts is a list
    assert isinstance(result["mastered_concepts"], list)
    
    # Assert weak_concepts is a list
    assert isinstance(result["weak_concepts"], list)
    
    # Assert feedback is a non-empty string
    assert isinstance(result["feedback"], str)
    assert len(result["feedback"]) > 0
    
    # Debugging print (optional, but good for local verification if needed)
    print(f"Score: {result['score']}")
    print(f"Mastered: {result['mastered_concepts']}")
    print(f"Weak: {result['weak_concepts']}")
    print(f"Feedback: {result['feedback']}")
