from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_ID: str = "your-project-id"
    REGION: str = "us-central1"
    FIRESTORE_DATABASE: str = "(default)"
    
    COURSE_SERVICE_URL: str = "http://localhost:8001"
    ASSESSMENT_SERVICE_URL: str = "http://localhost:8002"
    LEARNING_PROFILE_SERVICE_URL: str = "http://localhost:8003"
    AUTO_GRADING_AGENT_URL: str = "http://localhost:8004"
    RECOMMENDER_AGENT_URL: str = "http://localhost:8005"
    ASSESSMENT_MCP_SERVER_URL: str = "http://localhost:8006"
    LEARNING_COURSE_MCP_SERVER_URL: str = "http://localhost:8007"
    
    OLLAMA_BASE_URL: Optional[str] = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    
    PUBSUB_TOPIC_COURSE_EVENTS: str = "course-events"
    PUBSUB_TOPIC_ASSIGNMENT_CREATED: str = "assignment-created"
    PUBSUB_TOPIC_SUBMISSION_CREATED: str = "submission-created"
    PUBSUB_TOPIC_SUBMISSION_GRADED: str = "submission-graded"
    
    DEMO_API_TOKEN: str = "demo-token-123"
    LOCAL_MODE: bool = True
    API_GATEWAY_URL: str = "http://localhost:8080"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
