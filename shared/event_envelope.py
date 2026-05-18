from pydantic import BaseModel, Field
from typing import Any, Dict
from datetime import datetime
import uuid

class EventEnvelope(BaseModel):
    event_id: str
    event_type: str
    occurred_at: str
    producer: str
    version: str = "1.0"
    payload: Dict[str, Any]

def make_envelope(event_type: str, producer: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Factory function to create a validated event envelope.
    """
    envelope = EventEnvelope(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        occurred_at=datetime.utcnow().isoformat(),
        producer=producer,
        payload=payload
    )
    return envelope.dict()
