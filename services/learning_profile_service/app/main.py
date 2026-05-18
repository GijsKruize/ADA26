from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from .models import LearningProfile, ProfileEvent, RecalculateResponse
from .repository import ProfileRepository
from shared.logging import logger
from shared.settings import settings
from datetime import datetime

app = FastAPI(title="Learning Profile Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repo = ProfileRepository()
router = APIRouter(prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "learning-profile-service"}

@router.get("/profiles/{learner_id}", response_model=LearningProfile)
async def get_profile(learner_id: str):
    profile = repo.get_profile(learner_id)
    if not profile:
        # Create a default profile if it doesn't exist
        profile = LearningProfile(
            learner_id=learner_id,
            mastered_concepts={},
            weak_concepts=[],
            grade_history=[],
            last_recommendations=[],
            updated_at=datetime.utcnow()
        )
        repo.update_profile(profile)
    return profile

@router.post("/profiles/{learner_id}/events")
async def inject_event(learner_id: str, event: ProfileEvent):
    logger.info(f"Injecting event for learner {learner_id}: {event.event_type}")
    # For demo purposes, we just merge the payload into the profile if it's a direct update,
    # or we could implement specific logic. The requirement says "simple Firestore updates based on the payload".
    repo.save_profile_data(learner_id, event.payload)
    return {"status": "event injected", "learner_id": learner_id}

@router.post("/profiles/{learner_id}/recalculate", response_model=RecalculateResponse)
async def recalculate_profile(learner_id: str):
    logger.info(f"Forcing recalculation for learner {learner_id}")
    # In a real system, this might trigger a background job.
    # For this demo, we just update the updated_at timestamp.
    profile = repo.get_profile(learner_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile.updated_at = datetime.utcnow()
    repo.update_profile(profile)
    
    return RecalculateResponse(
        status="success",
        message=f"Profile for {learner_id} has been recalculated (timestamp updated)."
    )

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
