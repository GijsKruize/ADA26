# LearnSphere Assignment 2 — Adaptive Learning Platform

This repository contains the implementation for Assignment 2 of the Advanced Data Architecture course. It demonstrates a simplified, event-driven microservices architecture on Google Cloud, focusing on an adaptive grading and recommendation loop.

## 1. Project overview
LearnSphere is an adaptive learning platform that automates the grading process and provides personalized learning recommendations. The system uses a mix of RESTful microservices, autonomous agents using Model Context Protocol (MCP), and serverless functions to create a responsive, event-driven experience.

## 2. Exact subset implemented
The implementation focuses on the **Adaptive Grading Feedback Loop**, covering four domains:
- **Course & Curriculum (Core):** Managing courses, modules, and materials.
- **Assessment & Grading (Supporting):** Handling assignments, student submissions, and automated grading.
- **Adaptive Learning (Core):** Managing learner profiles and providing personalized recommendations.
- **Notification (Supporting):** Simulating real-time alerts for learners when grading is complete.

## 3. Simplifications from the design report
Following the C2 requirements, several consolidations were made for this implementation:
- **Service Consolidation:** The Course Service, Curriculum Service, and Course Material Service are merged into a single `course-service` using one Firestore namespace to reduce deployment complexity.
- **FaaS for Notifications:** The Notification Service is implemented as a Cloud Run Function (`notification-function`) rather than a long-running REST service, as it is purely reactive.
- **Learning Profile Split:** The Learning Profile Service is split into a REST service (`learning-profile-service`) for query operations and a Cloud Run Function (`profile-update-function`) for idempotent, event-driven profile updates.
- **Scope Reduction:** The Tutoring Agent is excluded; the grading feedback loop sufficiently demonstrates the Adaptive Learning core domain.
- **Gateway Consolidation:** Multiple per-domain API Gateways are collapsed into a single Google API Gateway for simplicity.

## 4. Why this subset is coherent as a demo
This subset provides a complete "Day in the Life" of a learner:
1. A course is created with structured materials and assessments.
2. A learner submits an answer to an assignment.
3. An autonomous agent detects the submission and grades it (using LLM or deterministic fallback).
4. The system asynchronously updates the learner's profile and notifies them.
5. Based on the new performance data, the system recommends the next best piece of content to address weak concepts.

## 5. Mapping to Assignment 2 requirements

| Requirement | Implementation Detail |
|---|---|
| ≥ 4 Microservices/Agents | 5: `course-service`, `assessment-service`, `learning-profile-service`, `auto-grading-agent`, `recommender-agent` |
| ≥ 12 Operations | 25 operations implemented across all components |
| ≥ 2 DDD Domains | 4 domains: Course, Assessment, Adaptive Learning, Notification |
| Orchestration/Choreography | Google Workflows (Orchestration) and Pub/Sub (Choreography) |
| FaaS and RESTful mix | Cloud Run (REST) and Cloud Run Functions (FaaS) |
| MCP Server implementation | 2 servers: `assessment-mcp-server` and `learning-course-mcp-server` |

## 6. Mapping to lab technologies

| Technology | Implementation |
|---|---|
| Python + FastAPI | All REST services and agents |
| Cloud Run | Hosting for microservices and agents |
| Cloud Run Functions (2nd gen) | Event-driven functions (`profile-update`, `notification`) |
| Pub/Sub | Asynchronous event bus for choreography |
| Google Workflows | Orchestration of the demo learning flow |
| Firestore | NoSQL persistence for all domains |
| Google API Gateway | Central entry point with static token auth |
| Ollama / LLM | Used by Auto-Grading Agent with deterministic fallback |

## 7. Mapping to design report sections

| Report Section | Implementation Directory |
|---|---|
| Course Management | `services/course_service` |
| Assessment & Grading | `services/assessment_service` |
| Learning Profile | `services/learning_profile_service` |
| Grading Automation | `agents/auto_grading_agent` |
| Recommender System | `agents/recommender_agent` |
| Profile Updates | `functions/profile_update_function` |
| Notifications | `functions/notification_function` |
| Shared Logic | `shared/` |

## 8. Services/agents/functions/MCP servers table

| Component | Type | Domain | Runtime |
|---|---|---|---|
| `course-service` | REST Service | Course & Curriculum | Cloud Run (FastAPI) |
| `assessment-service` | REST Service | Assessment & Grading | Cloud Run (FastAPI) |
| `learning-profile-service` | REST Service | Adaptive Learning | Cloud Run (FastAPI) |
| `auto-grading-agent` | Agent | Assessment & Grading | Cloud Run (FastAPI) |
| `recommender-agent` | Agent | Adaptive Learning | Cloud Run (FastAPI) |
| `assessment-mcp-server` | MCP Server | Assessment & Grading | Docker / Cloud Run |
| `learning-course-mcp-server` | MCP Server | Course & Profile | Docker / Cloud Run |
| `profile-update-function` | FaaS | Adaptive Learning | Cloud Run Function (Gen 2) |
| `notification-function` | FaaS | Notification | Cloud Run Function (Gen 2) |

## 9. Operations table

| # | Component | Method | Path / Trigger | Description |
|---|---|---|---|---|
| 1 | `course-service` | GET | `/health` | Health check |
| 2 | `course-service` | POST | `/courses` | Create a course |
| 3 | `course-service` | GET | `/courses/{course_id}` | Get a course |
| 4 | `course-service` | POST | `/courses/{course_id}/modules` | Add a module to a course |
| 5 | `course-service` | GET | `/courses/{course_id}/modules` | List modules for a course |
| 6 | `course-service` | POST | `/courses/{course_id}/materials` | Add learning material |
| 7 | `course-service` | GET | `/courses/{course_id}/materials` | List course materials |
| 8 | `assessment-service` | GET | `/health` | Health check |
| 9 | `assessment-service` | POST | `/assignments` | Create an assignment |
| 10 | `assessment-service` | GET | `/assignments/{assignment_id}` | Get assignment details |
| 11 | `assessment-service` | POST | `/submissions` | Submit learner answer (Publishes `SubmissionCreated`) |
| 12 | `assessment-service` | GET | `/submissions/{submission_id}` | Get submission details |
| 13 | `assessment-service` | POST | `/submissions/{submission_id}/grade` | Record a grade (Publishes `SubmissionGraded`) |
| 14 | `assessment-service` | GET | `/submissions/{submission_id}/grade` | Get grade for a submission |
| 15 | `learning-profile-service`| GET | `/health` | Health check |
| 16 | `learning-profile-service`| GET | `/profiles/{learner_id}` | Get learner profile |
| 17 | `learning-profile-service`| POST | `/profiles/{learner_id}/events` | Inject profile event (debug) |
| 18 | `learning-profile-service`| POST | `/profiles/{learner_id}/recalculate` | Force recalculation (debug) |
| 19 | `auto-grading-agent` | GET | `/health` | Health check |
| 20 | `auto-grading-agent` | POST | `/agent/grade-submission` | Explicitly trigger grading |
| 21 | `auto-grading-agent` | POST | `/pubsub/submission-created` | Pub/Sub push endpoint for submissions |
| 22 | `recommender-agent` | GET | `/health` | Health check |
| 23 | `recommender-agent` | POST | `/agent/recommend` | Get personalized recommendation |
| 24 | `profile-update-function` | Pub/Sub| `submission-graded` | Update learner profile (Choreography) |
| 25 | `notification-function` | Pub/Sub| `submission-graded` | Send notification (Choreography) |

## 10. MCP tools table

| Tool ID | MCP Server | Tool Name | Description |
|---|---|---|---|
| T1 | `assessment-mcp-server` | `get_assignment` | Retrieve assignment by ID |
| T2 | `assessment-mcp-server` | `get_submission` | Retrieve submission by ID |
| T3 | `assessment-mcp-server` | `record_grade` | Post grade payload |
| T4 | `learning-course-mcp-server`| `get_course` | Retrieve course details |
| T5 | `learning-course-mcp-server`| `list_modules` | List modules for a course |
| T6 | `learning-course-mcp-server`| `list_materials` | List materials for a course |
| T7 | `learning-course-mcp-server`| `get_learning_profile` | Retrieve learner profile |

## 11. Event table

| Event | Topic | Producer | Consumers |
|---|---|---|---|
| `CourseCreated` | `course-events` | `course-service` | None (Audit) |
| `CourseMaterialUpdated` | `course-events` | `course-service` | None (Audit) |
| `AssignmentCreated` | `assignment-created` | `assessment-service` | None (Audit) |
| `SubmissionCreated` | `submission-created` | `assessment-service` | `auto-grading-agent` (Push) |
| `SubmissionGraded` | `submission-graded` | `assessment-service` | `profile-update-function`, `notification-function` |

## 12. Firestore collections

- **`courses`**: Course metadata and objectives.
- **`modules`**: Modular structure within courses.
- **`materials`**: Content items with concept tags and sequence order.
- **`assignments`**: Assessment tasks with rubrics.
- **`submissions`**: Student answers and submission status.
- **`grades`**: Grading results, feedback, and concept mastery metadata.
- **`learner_profiles`**: Aggregated concept mastery and history per learner.
- **`notifications`**: Log of simulated notifications sent to learners.
- **`llm_traces`**: Detailed logs of LLM interactions for the grading agent.

## 13. Google Cloud architecture diagram

```text
      [ Learner Browser ]
              |
      [ Google API Gateway ]
              |
     ---------------------------------------------------------
     |                |                    |                 |
[ Course Svc ] [ Assessment Svc ] [ Profile Svc ] [ Agents ]
     |                |                    |          |      |
     |          (Publishes)           (Queries)   (Uses MCP) |
     |                |                    |          |      |
     |          [ Pub/Sub Bus ] <----------------------      |
     |                |                                      |
     |      -------------------------                        |
     |      |                       |                        |
     | [ Profile Update Fn ] [ Notification Fn ]             |
     |      |                       |                        |
     ---------------------------------------------------------
              |
      [ Firestore (NoSQL) ]
```

## 14. Local setup instructions

1.  **Environment:** Copy `.env.example` to `.env` and fill in required variables (use `LOCAL_MODE=true`).
2.  **Dependencies:** Ensure Docker and Docker Compose are installed.
3.  **Launch:** Run `docker-compose up --build` to start all services, agents, and MCP servers locally.
4.  **Ollama (Optional):** If you wish to use LLM grading locally, ensure Ollama is running and the `OLLAMA_BASE_URL` is accessible from the containers.

## 15. Cloud deployment steps

Deploy the infrastructure using the provided scripts in `infra/gcloud/` in the following sequence:

1.  `./infra/gcloud/00_enable_apis.sh`: Enable required Google Cloud APIs.
2.  `./infra/gcloud/01_create_artifact_registry.sh`: Create the Docker repository.
3.  `./infra/gcloud/02_create_firestore.sh`: Provision the Firestore database.
4.  `./infra/gcloud/03_create_pubsub.sh`: Create topics and subscriptions.
5.  `./infra/gcloud/04_create_storage.sh`: Create the Cloud Storage bucket for submissions.
6.  `./infra/gcloud/05_deploy_cloud_run.sh`: Build and deploy the 5 microservices/agents.
7.  `./infra/gcloud/06_deploy_functions.sh`: Deploy the 2nd Gen Cloud Run Functions.
8.  `./infra/gcloud/07_create_pubsub_push_subscriptions.sh`: Configure push triggers for the grading agent.
9.  `./infra/gcloud/08_deploy_workflow.sh`: Deploy the Google Workflow orchestration.
10. `./infra/gcloud/09_deploy_gateway.sh`: Deploy the API Gateway.

## 16. Demo script instructions

-   **Local Demo:** Run `./scripts/run_local_demo.sh` to execute a full end-to-end flow using the local Docker environment.
-   **Cloud Demo:** Run `./scripts/run_cloud_demo.sh` to execute the same flow against the deployed Google Cloud infrastructure.

## 17. Workflow execution instructions

To trigger the orchestrated demo flow in Google Workflows:
1.  Ensure you have `gcloud` authenticated.
2.  Run `./scripts/call_workflow.sh`.
3.  The script will trigger the workflow and wait for the final JSON result, which consolidates all created resources and grading results.

## 18. Assumptions

-   **Security:** `DEMO_API_TOKEN` is a static token for demo purposes. In production, this would be replaced by Identity Platform (Firebase Auth).
-   **Identity:** `X-Demo-User` header is used to simulate different learners without a full auth provider.
-   **Persistence:** Firestore is used in Datastore mode or Native mode with the `(default)` database.
-   **LLM Availability:** The system assumes Ollama might be unavailable and provides a robust deterministic fallback based on keyword matching and length heuristics.

## 19. Known limitations

-   **Manual Grading:** The system is focused on auto-grading; manual override workflows are defined in the API but not implemented in the frontend demo.
-   **Storage:** While Cloud Storage is provisioned, files are currently passed as base64 or text for demo simplicity in the `run_local_demo` scripts.
-   **LLM Latency:** LLM grading via Ollama can take several seconds; the system uses a push-based asynchronous model to handle this gracefully.

## 20. Troubleshooting

-   **Grading Stuck:** Check the `auto-grading-agent` logs. If Ollama is timing out, the circuit breaker should trigger the deterministic fallback.
-   **Profile Not Updating:** Verify that the `SubmissionGraded` event was published and check the `profile-update-function` logs for idempotency skips.
-   **API Gateway 403:** Ensure the `Authorization: Bearer <token>` header matches the `DEMO_API_TOKEN` set during deployment.
