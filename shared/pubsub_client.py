import json
import base64
import logging
from google.cloud import pubsub_v1
from .settings import settings

publisher = None

def get_publisher():
    global publisher
    if publisher is None and not settings.LOCAL_MODE:
        publisher = pubsub_v1.PublisherClient()
    return publisher

def publish_event(topic_id: str, envelope: dict):
    """
    Publishes an event to a Pub/Sub topic.
    In LOCAL_MODE, it logs the event to stdout instead of publishing.
    """
    data_json = json.dumps(envelope)
    data_bytes = data_json.encode("utf-8")
    
    # Attributes for routing/filtering
    attributes = {
        "event_type": str(envelope.get("event_type", "unknown")),
        "producer": str(envelope.get("producer", "unknown")),
        "version": str(envelope.get("version", "1.0"))
    }

    if settings.LOCAL_MODE:
        logging.info(f"[LOCAL_MODE] Publishing to topic {topic_id}: {data_json} with attributes {attributes}")
        return "local-msg-id"

    project_id = settings.PROJECT_ID
    topic_path = f"projects/{project_id}/topics/{topic_id}"
    
    client = get_publisher()
    future = client.publish(topic_path, data_bytes, **attributes)
    message_id = future.result()
    
    logging.info(f"Published message {message_id} to {topic_path}")
    return message_id
