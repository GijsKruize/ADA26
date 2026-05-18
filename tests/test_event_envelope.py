import pytest
from pydantic import ValidationError
from shared.event_envelope import make_envelope, EventEnvelope

def test_make_envelope_success():
    event_type = "SubmissionCreated"
    producer = "assessment-service"
    payload = {"submission_id": "123"}
    
    envelope = make_envelope(event_type, producer, payload)
    
    assert "event_id" in envelope
    assert envelope["event_type"] == event_type
    assert envelope["producer"] == producer
    assert envelope["payload"] == payload
    assert "occurred_at" in envelope
    assert envelope["version"] == "1.0"
    
    # Verify it can be parsed back into EventEnvelope
    parsed = EventEnvelope(**envelope)
    assert parsed.event_id == envelope["event_id"]

def test_event_envelope_missing_event_id_fails():
    # Instruction: "Assert that an envelope with a missing event_id fails Pydantic validation."
    with pytest.raises(ValidationError) as excinfo:
        EventEnvelope(
            # event_id missing
            event_type="SubmissionCreated",
            occurred_at="2023-01-01T00:00:00",
            producer="assessment-service",
            payload={}
        )
    assert "event_id" in str(excinfo.value)

def test_event_envelope_missing_other_required_fields_fails():
    with pytest.raises(ValidationError):
        EventEnvelope(
            event_id="uuid",
            # event_type missing
            occurred_at="2023-01-01T00:00:00",
            producer="assessment-service",
            payload={}
        )
