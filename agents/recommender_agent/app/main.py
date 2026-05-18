from fastapi import FastAPI, HTTPException, APIRouter
from .models import RecommendRequest, RecommendResponse
from .recommender import get_recommendations
import uvicorn

app = FastAPI(title="Recommender Agent")
router = APIRouter(prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "recommender-agent"}

@router.post("/agent/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    try:
        return await get_recommendations(request.learner_id, request.course_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
