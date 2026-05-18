from google.cloud import firestore
from .settings import settings

_db = None

def get_firestore_client():
    global _db
    if _db is None:
        _db = firestore.Client(
            project=settings.PROJECT_ID,
            database=settings.FIRESTORE_DATABASE
        )
    return _db
