const API_BASE = window.API_BASE || 'http://localhost:8080';
const DEMO_TOKEN = 'demo-token-123'; // Matches Settings.DEMO_API_TOKEN

let state = {
    course_id: null,
    module_id: null,
    material_id: null,
    assignment_id: null,
    submission_id: null
};

function getLearnerId() {
    return document.getElementById('learner-id').value;
}

function getLearnerName() {
    return document.getElementById('learner-name').value;
}

function getLearnerEmail() {
    return document.getElementById('learner-email').value;
}

async function callApi(path, method = 'GET', body = null) {
    const url = `${API_BASE}${path}`;
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${DEMO_TOKEN}`,
            'X-Demo-User': getLearnerId()
        }
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
            name: document.getElementById('course-name').value,
            title: document.getElementById('course-title').value,
            description: document.getElementById('course-desc').value,
            learning_objectives: ['Understand event-driven architecture', 'Understand microservices', 'Understand data products'],
            status: 'published'
        });
        state.course_id = data.course_id;
        setStatus('course-status', 'Success!', 'success');
        document.getElementById('btn-add-module').disabled = false;
        document.getElementById('module-name').disabled = false;
        document.getElementById('module-title').disabled = false;
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
            name: document.getElementById('module-name').value,
            title: document.getElementById('module-title').value,
            learning_objectives: ['Explain Pub/Sub choreography', 'Explain service boundaries'],
            order: 1
        });
        state.module_id = data.module_id;
        setStatus('module-status', 'Success!', 'success');
        document.getElementById('btn-add-material').disabled = false;
        document.getElementById('material-name').disabled = false;
        document.getElementById('material-title').disabled = false;
        document.getElementById('material-concepts').disabled = false;
    } catch (e) {
        setStatus('module-status', e.message, 'error');
    }
};

// Step 1.2: Add Material
document.getElementById('btn-add-material').onclick = async () => {
    try {
        setStatus('material-status', 'Adding...');
        const concepts = document.getElementById('material-concepts').value.split(',').map(s => s.trim());
        const data = await callApi(`/api/courses/${state.course_id}/materials`, 'POST', {
            module_id: state.module_id,
            course_id: state.course_id,
            name: document.getElementById('material-name').value,
            title: document.getElementById('material-title').value,
            type: 'reading',
            concepts: concepts,
            order: 1
        });
        state.material_id = data.material_id;
        setStatus('material-status', 'Success!', 'success');
        document.getElementById('btn-create-assignment').disabled = false;
        document.getElementById('assignment-name').disabled = false;
        document.getElementById('assignment-title').disabled = false;
        document.getElementById('assignment-instr').disabled = false;
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
            name: document.getElementById('assignment-name').value,
            title: document.getElementById('assignment-title').value,
            instructions: document.getElementById('assignment-instr').value,
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
        setStatus('submission-status', 'Submitting (this triggers auto-grading)...');
        const data = await callApi('/api/submissions', 'POST', {
            assignment_id: state.assignment_id,
            learner_id: getLearnerId(),
            learner_email: getLearnerEmail(),
            answer_text: document.getElementById('answer-text').value
        });
        state.submission_id = data.submission_id;
        setStatus('submission-status', 'Success! Grading triggered automatically.', 'success');
        document.getElementById('btn-trigger-grading').disabled = false;
    } catch (e) {
        setStatus('submission-status', e.message, 'error');
    }
};

// Step 3: Fetch Grade Result (Polling)
document.getElementById('btn-trigger-grading').onclick = async () => {
    try {
        setStatus('grading-status', 'Polling for LLM grade (Ollama is thinking)...');
        
        let attempts = 0;
        const maxAttempts = 20; // Increase polling time for slower LLMs
        const delay = 5000; // 5 seconds

        while (attempts < maxAttempts) {
            try {
                const data = await callApi(`/api/submissions/${state.submission_id}/grade`);
                displayResult('grade-result', data);
                
                const provider = data.trace && data.trace.llm_provider ? data.trace.llm_provider : 'unknown';
                if (provider === 'deterministic-fallback') {
                    setStatus('grading-status', 'Warning: Fallback used. Ollama might still be loading or timed out.', 'error');
                } else {
                    setStatus('grading-status', `Success! Graded by LLM (${provider})`, 'success');
                }
                
                document.getElementById('btn-fetch-profile').disabled = false;
                return;
            } catch (e) {
                if (e.message.includes('404')) {
                    attempts++;
                    setStatus('grading-status', `LLM is still grading... (attempt ${attempts}/${maxAttempts}, waiting 5s)`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                } else {
                    throw e;
                }
            }
        }
        throw new Error('LLM grading is taking longer than expected. Please wait another minute and click again.');
    } catch (e) {
        setStatus('grading-status', e.message, 'error');
    }
};

// Step 4: Fetch Profile
document.getElementById('btn-fetch-profile').onclick = async () => {
    try {
        setStatus('profile-status', 'Fetching...');
        const data = await callApi(`/api/profiles/${getLearnerId()}`);
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
            learner_id: getLearnerId(),
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
