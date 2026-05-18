const API_BASE = window.API_BASE || 'http://localhost:8080';
const DEMO_TOKEN = 'demo-token-123'; // Matches Settings.DEMO_API_TOKEN

let state = {
    course_id: null,
    module_id: null,
    material_id: null,
    assignment_id: null,
    submission_id: null,
    learner_id: 'student_123'
};

const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${DEMO_TOKEN}`,
    'X-Demo-User': state.learner_id
};

async function callApi(path, method = 'GET', body = null) {
    const url = `${API_BASE}${path}`;
    const options = {
        method,
        headers
    };
    if (body) {
        options.body = JSON.stringify(body);
    }
    const response = await fetch(url, options);
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `API error: ${response.status}`);
    }
    return response.json();
}

// UI Helpers
function setStatus(id, text, type = 'loading') {
    const el = document.getElementById(id);
    el.textContent = text;
    el.className = `status ${type}`;
}

function displayResult(id, data) {
    const el = document.getElementById(id);
    el.textContent = JSON.stringify(data, null, 2);
}

// Step 1: Create Course
document.getElementById('btn-create-course').onclick = async () => {
    try {
        setStatus('course-status', 'Creating...');
        const data = await callApi('/api/courses', 'POST', {
            title: 'Introduction to Data Architecture',
            description: 'Learn about modern data architectures.',
            learning_objectives: ['Understand event-driven architecture', 'Understand microservices', 'Understand data products'],
            status: 'published'
        });
        state.course_id = data.course_id;
        setStatus('course-status', 'Success!', 'success');
        document.getElementById('btn-add-module').disabled = false;
    } catch (e) {
        setStatus('course-status', e.message, 'error');
    }
};

// Step 1.1: Add Module
document.getElementById('btn-add-module').onclick = async () => {
    try {
        setStatus('module-status', 'Adding...');
        const data = await callApi(`/api/courses/${state.course_id}/modules`, 'POST', {
            course_id: state.course_id,
            title: 'Event-Driven Microservices',
            learning_objectives: ['Explain Pub/Sub choreography', 'Explain service boundaries'],
            order: 1
        });
        state.module_id = data.module_id;
        setStatus('module-status', 'Success!', 'success');
        document.getElementById('btn-add-material').disabled = false;
    } catch (e) {
        setStatus('module-status', e.message, 'error');
    }
};

// Step 1.2: Add Material
document.getElementById('btn-add-material').onclick = async () => {
    try {
        setStatus('material-status', 'Adding...');
        const data = await callApi(`/api/courses/${state.course_id}/materials`, 'POST', {
            module_id: state.module_id,
            course_id: state.course_id,
            title: 'Pub/Sub and Choreography Basics',
            type: 'reading',
            concepts: ['pubsub', 'choreography', 'event-driven architecture'],
            order: 1
        });
        state.material_id = data.material_id;
        setStatus('material-status', 'Success!', 'success');
        document.getElementById('btn-create-assignment').disabled = false;
    } catch (e) {
        setStatus('material-status', e.message, 'error');
    }
};

// Step 2: Create Assignment
document.getElementById('btn-create-assignment').onclick = async () => {
    try {
        setStatus('assignment-status', 'Creating...');
        const data = await callApi('/api/assignments', 'POST', {
            course_id: state.course_id,
            title: 'Explain Event-Driven Architecture',
            instructions: 'Explain how services communicate using events and why this improves loose coupling.',
            rubric: [
                {
                    name: 'Event communication',
                    description: 'How services communicate',
                    max_points: 40,
                    keywords: ['event', 'publish', 'subscribe', 'pubsub', 'message'],
                    concepts: ['pubsub', 'event-driven architecture']
                },
                {
                    name: 'Loose coupling',
                    description: 'Why it improves loose coupling',
                    max_points: 40,
                    keywords: ['loose coupling', 'independent', 'asynchronous', 'decoupled'],
                    concepts: ['choreography', 'microservices']
                },
                {
                    name: 'Reliability',
                    description: 'System resilience',
                    max_points: 20,
                    keywords: ['retry', 'failure', 'resilience', 'eventual consistency'],
                    concepts: ['resilience']
                }
            ]
        });
        state.assignment_id = data.assignment_id;
        setStatus('assignment-status', 'Success!', 'success');
        document.getElementById('btn-submit-answer').disabled = false;
        document.getElementById('answer-text').disabled = false;
    } catch (e) {
        setStatus('assignment-status', e.message, 'error');
    }
};

// Step 2.1: Submit Answer
document.getElementById('btn-submit-answer').onclick = async () => {
    try {
        setStatus('submission-status', 'Submitting...');
        const data = await callApi('/api/submissions', 'POST', {
            assignment_id: state.assignment_id,
            learner_id: state.learner_id,
            answer_text: document.getElementById('answer-text').value
        });
        state.submission_id = data.submission_id;
        setStatus('submission-status', 'Success!', 'success');
        document.getElementById('btn-trigger-grading').disabled = false;
    } catch (e) {
        setStatus('submission-status', e.message, 'error');
    }
};

// Step 3: Trigger Grading
document.getElementById('btn-trigger-grading').onclick = async () => {
    try {
        setStatus('grading-status', 'Grading...');
        const data = await callApi('/api/agent/grade-submission', 'POST', {
            submission_id: state.submission_id
        });
        displayResult('grade-result', data);
        setStatus('grading-status', 'Success!', 'success');
        document.getElementById('btn-fetch-profile').disabled = false;
    } catch (e) {
        setStatus('grading-status', e.message, 'error');
    }
};

// Step 4: Fetch Profile
document.getElementById('btn-fetch-profile').onclick = async () => {
    try {
        setStatus('profile-status', 'Fetching...');
        const data = await callApi(`/api/profiles/${state.learner_id}`);
        displayResult('profile-result', data);
        setStatus('profile-status', 'Success!', 'success');
        document.getElementById('btn-get-recommendation').disabled = false;
    } catch (e) {
        setStatus('profile-status', e.message, 'error');
    }
};

// Step 4.1: Get Recommendation
document.getElementById('btn-get-recommendation').onclick = async () => {
    try {
        setStatus('recommendation-status', 'Getting...');
        const data = await callApi('/api/agent/recommend', 'POST', {
            learner_id: state.learner_id,
            course_id: state.course_id
        });
        displayResult('recommendation-result', data);
        setStatus('recommendation-status', 'Success!', 'success');
    } catch (e) {
        setStatus('recommendation-status', e.message, 'error');
    }
};

// Step 5: Notifications
document.getElementById('btn-fetch-notifications').onclick = async () => {
    setStatus('notification-status', 'Fetching notifications is not directly implemented in the API Gateway. Check Firestore "notifications" collection.', 'loading');
};
