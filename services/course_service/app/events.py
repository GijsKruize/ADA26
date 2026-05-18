from shared.pubsub_client import publish_event
from shared.event_envelope import make_envelope
from shared.settings import settings

PRODUCER = "course-service"
TOPIC = settings.PUBSUB_TOPIC_COURSE_EVENTS

def publish_course_created(course_id: str, title: str, learning_objectives: list):
    payload = {
        "course_id": course_id,
        "title": title,
        "learning_objectives": learning_objectives
    }
    envelope = make_envelope("CourseCreated", PRODUCER, payload)
    publish_event(TOPIC, envelope)

def publish_course_material_updated(course_id: str, material_id: str, concepts: list, version: int):
    payload = {
        "course_id": course_id,
        "material_id": material_id,
        "concepts": concepts,
        "version": version
    }
    envelope = make_envelope("CourseMaterialUpdated", PRODUCER, payload)
    publish_event(TOPIC, envelope)
