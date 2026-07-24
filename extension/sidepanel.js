// sidepanel.js

const chatContainer = document.getElementById('chat-container');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const contextBanner = document.getElementById('context-banner');
const pendingActionContainer = document.getElementById('pending-action-container');
const pendingActionDetails = document.getElementById('pending-action-details');
const approveBtn = document.getElementById('approve-btn');
const cancelBtn = document.getElementById('cancel-btn');

// Jules Bridge UI Elements
const julesBridgeContainer = document.getElementById('jules-bridge-container');
const julesActiveTask = document.getElementById('jules-active-task');
const julesActiveStatus = document.getElementById('jules-active-status');
const julesApproveBtn = document.getElementById('jules-approve-btn');

let activeContext = null;
let currentPendingActionSelector = null;
let activeJulesTaskId = null;
let julesPollInterval = null;

// Initialize context on load
chrome.runtime.sendMessage({ type: 'GET_CURRENT_CONTEXT' }, (response) => {
    if (response) {
        updateContextBanner(response);
    }
});

// Listen for context updates from background
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'CONTEXT_UPDATED') {
        updateContextBanner(request.payload);
    }
});

function updateContextBanner(contextPayload) {
    activeContext = contextPayload;
    if (contextPayload && contextPayload.type) {
        contextBanner.style.display = 'block';
        contextBanner.textContent = `👀 Context: ${contextPayload.type.toUpperCase()}`;
    } else {
        contextBanner.style.display = 'none';
    }
}

function appendMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    if (sender === 'User') {
        messageDiv.classList.add('user-message');
    } else {
        messageDiv.classList.add('solomon-message');
    }

    const senderSpan = document.createElement('strong');
    senderSpan.textContent = sender + ': ';

    const textSpan = document.createElement('span');
    // Using textContent provides XSS protection
    textSpan.textContent = text;

    messageDiv.appendChild(senderSpan);
    messageDiv.appendChild(textSpan);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessageToSolomon(message) {
    appendMessage('User', message);
    chatInput.value = '';

    const payload = {
        message: message,
        context: activeContext // Pass the current browser context to the backend
    };

    try {
        const response = await fetch('http://localhost:10000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        let replyText = data.reply;

        // Parse for action requests
        const actionMatch = replyText.match(/\[ACTION:\s*(.+?)\]/);
        if (actionMatch) {
            currentPendingActionSelector = actionMatch[1].trim();
            replyText = replyText.replace(actionMatch[0], '').trim();
            pendingActionContainer.style.display = 'block';
            pendingActionDetails.textContent = `Target: ${currentPendingActionSelector}`;
            chrome.runtime.sendMessage({
                type: 'HIGHLIGHT_ELEMENT',
                selector: currentPendingActionSelector
            });
        }

        // Parse for Jules Task Creation
        const julesTaskMatch = replyText.match(/\[JULES_TASK:\s*(.+?)\s*\|\s*(.+?)\]/);
        if (julesTaskMatch) {
            const repo = julesTaskMatch[1].trim();
            const obj = julesTaskMatch[2].trim();
            replyText = replyText.replace(julesTaskMatch[0], '').trim();
            triggerJulesAPI('/api/jules/task', { repository: repo, objective: obj });
        }

        // Parse for Jules Validation Request
        const julesValMatch = replyText.match(/\[JULES_VALIDATE:\s*(.+?)\]/);
        if (julesValMatch) {
            const tId = julesValMatch[1].trim();
            replyText = replyText.replace(julesValMatch[0], '').trim();
            triggerJulesAPI('/api/jules/validate', { task_id: tId });
        }

        if (replyText) {
            appendMessage('Solomon', replyText);
        }
    } catch (error) {
        console.error("Error communicating with Solomon backend:", error);
        appendMessage('System', 'Error connecting to Solomon backend. Ensure app.py is running.');
    }
}

sendBtn.addEventListener('click', () => {
    const message = chatInput.value.trim();
    if (message) {
        sendMessageToSolomon(message);
    }
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const message = chatInput.value.trim();
        if (message) {
            sendMessageToSolomon(message);
        }
    }
});

// Action Handlers
approveBtn.addEventListener('click', async () => {
    if (currentPendingActionSelector) {
        chrome.runtime.sendMessage({
            type: 'EXECUTE_ACTION',
            selector: currentPendingActionSelector
        });

        // Log action securely
        fetch('http://localhost:10000/api/browser/action-log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                selector: currentPendingActionSelector,
                url: activeContext?.url || 'unknown'
            })
        }).catch(err => console.error(err));

        appendMessage('System', `Action approved on target: ${currentPendingActionSelector}`);
        resetPendingAction();
    }
});

cancelBtn.addEventListener('click', () => {
    if (currentPendingActionSelector) {
        chrome.runtime.sendMessage({
            type: 'CLEAR_HIGHLIGHT'
        });
        appendMessage('System', 'Action cancelled by user.');
        resetPendingAction();
    }
});

function resetPendingAction() {
    pendingActionContainer.style.display = 'none';
    currentPendingActionSelector = null;
}

// --- Jules Bridge UI Flow ---
async function triggerJulesAPI(endpoint, payload) {
    julesBridgeContainer.style.display = 'block';
    julesActiveStatus.textContent = "Contacting API...";

    try {
        const response = await fetch(`http://localhost:10000${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (data.task_id) {
            activeJulesTaskId = data.task_id;
            julesActiveTask.textContent = `Task: ${data.task_id}`;
            julesActiveStatus.textContent = `Status: ${data.status}`;

            if (data.status === 'awaiting_human_approval') {
                julesApproveBtn.style.display = 'block';
            } else {
                julesApproveBtn.style.display = 'none';
            }
        }
    } catch (err) {
        console.error("Jules API Error:", err);
        julesActiveStatus.textContent = "API Error: " + err.message;
    }
}

julesApproveBtn.addEventListener('click', () => {
    if (activeJulesTaskId) {
        triggerJulesAPI('/api/jules/approve', { task_id: activeJulesTaskId });
        julesApproveBtn.style.display = 'none';
    }
});