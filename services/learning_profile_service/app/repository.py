from shared.firestore_client import get_firestore_client
from .models import LearningProfile
from datetime import datetime
from typing import Optional

class ProfileRepository:
    def __init__(self):
        self.db = get_firestore_client()
        self.collection = "learner_profiles"

    def get_profile(self, learner_id: str) -> Optional[LearningProfile]:
        doc = self.db.collection(self.collection).document(learner_id).get()
        if doc.exists:
            data = doc.to_dict()
            return LearningProfile(**data)
        return None

    def update_profile(self, profile: LearningProfile):
        data = profile.model_dump()
        # Convert datetime to Firestore format if necessary, 
        # but Firestore client usually handles datetime objects.
        self.db.collection(self.collection).document(profile.learner_id).set(data)

    def save_profile_data(self, learner_id: str, data: dict):
        # Direct update for demo purposes
        data["updated_at"] = datetime.utcnow()
        self.db.collection(self.collection).document(learner_id).set(data, merge=True)
