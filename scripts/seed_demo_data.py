import requests
import os
import json
import time

# Get base URLs from env
COURSE_URL = os.getenv("COURSE_SERVICE_URL", "http://localhost:8001")
ASSESSMENT_URL = os.getenv("ASSESSMENT_SERVICE_URL", "http://localhost:8002")

def seed():
    print("Seeding demo data...")

    # 1. Create Course
    course_data = {
        "name": "IntroDataArch",
        "title": "Introduction to Data Architecture",
        "description": "Learn about EDA, microservices, and data products.",
        "learning_objectives": ["Understand event-driven architecture", "Understand microservices", "Understand data products"]
    }
    res = requests.post(f"{COURSE_URL}/courses", json=course_data)
    res.raise_for_status()
    course = res.json()
    course_id = course["course_id"]
    print(f"Created course: {course_id}")

    # 2. Add Module
    module_data = {
        "name": "EDM",
        "title": "Event-Driven Microservices",
        "learning_objectives": ["Explain Pub/Sub choreography", "Explain service boundaries"],
        "order": 1
    }
    res = requests.post(f"{COURSE_URL}/courses/{course_id}/modules", json=module_data)
    res.raise_for_status()
    module = res.json()
    module_id = module["module_id"]
    print(f"Added module: {module_id}")

    # 3. Add Material
    material_data = {
        "module_id": module_id,
        "name": "PubSubBasics",
        "title": "Pub/Sub and Choreography Basics",
        "type": "reading",
        "concepts": ["pubsub", "choreography", "event-driven architecture"],
        "order": 1
    }
    res = requests.post(f"{COURSE_URL}/courses/{course_id}/materials", json=material_data)
    res.raise_for_status()
    print(f"Added material")

    # 4. Create Assignment
    assignment_data = {
        "course_id": course_id,
        "name": "EDAExplain",
        "title": "Explain Event-Driven Architecture",
        "instructions": "Explain how services communicate using events and why this improves loose coupling.",
        "rubric": [
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
    }
    res = requests.post(f"{ASSESSMENT_URL}/assignments", json=assignment_data)
    res.raise_for_status()
    assignment = res.json()
    print(f"Created assignment: {assignment['assignment_id']}")

    print("Seeding complete.")
    return {
        "course_id": course_id,
        "assignment_id": assignment["assignment_id"]
    }

if __name__ == "__main__":
    seed()
