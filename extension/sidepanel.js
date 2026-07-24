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

// Optimization UI Elements
const clearBtn = document.getElementById('clear-btn');
const haltBtn = document.getElementById('halt-btn');

let activeContext = null;
let currentPendingActionSelector = null;
let currentPendingFillValue = null;
let activeJulesTaskId = null;
let julesPollInterval = null;
let pollDelay = 2000;

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

// Load persistent chat
chrome.storage.local.get(['solomonChatHistory'], (result) => {
    if (result.solomonChatHistory) {
        chatContainer.innerHTML = result.solomonChatHistory;
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});

function saveChatToStorage() {
    chrome.storage.local.set({ solomonChatHistory: chatContainer.innerHTML });
}

function updateContextBanner(contextPayload) {
    activeContext = contextPayload;
    if (contextPayload && contextPayload.type) {
        contextBanner.style.display = 'block';
        contextBanner.textContent = `👀 Context: ${contextPayload.type.toUpperCase()}`;
        // Add pulse animation
        contextBanner.classList.add('context-pulse');
        setTimeout(() => contextBanner.classList.remove('context-pulse'), 500);
    } else {
        contextBanner.style.display = 'none';
    }
}

function formatMarkdown(text) {
    let html = text.replace(/`([^`]+)`/g, '<code style="background:#eee;padding:2px 4px;border-radius:3px;">$1</code>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    return html;
}

function appendMessage(sender, text, isTyping = false) {
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

    if (isTyping) {
        messageDiv.id = 'typing-indicator';
        textSpan.classList.add('typing');
        textSpan.textContent = text;
    } else {
        // Safe innerHTML assignment for our simple markdown (bold/code)
        // In prod, use DOMPurify
        const safeText = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        textSpan.innerHTML = formatMarkdown(safeText);
    }

    const timeSpan = document.createElement('span');
    timeSpan.classList.add('msg-time');
    timeSpan.textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

    messageDiv.appendChild(senderSpan);
    messageDiv.appendChild(textSpan);
    if (!isTyping) messageDiv.appendChild(timeSpan);
    chatContainer.appendChild(messageDiv);

    // Scroll to bottom if we're near the bottom
    if (chatContainer.scrollHeight - chatContainer.scrollTop - chatContainer.clientHeight < 150) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    if (!isTyping) saveChatToStorage();
}

function removeTypingIndicator() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

async function sendMessageToSolomon(message) {
    appendMessage('User', message);
    chatInput.value = '';
    chatInput.disabled = true;
    sendBtn.disabled = true;
    appendMessage('Solomon', 'Thinking...', true);

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

        removeTypingIndicator();
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        let replyText = data.reply;

        // Parse for Click Action requests
        const actionMatch = replyText.match(/\[ACTION:\s*(.+?)\]/);
        if (actionMatch) {
            currentPendingActionSelector = actionMatch[1].trim();
            currentPendingFillValue = null;
            replyText = replyText.replace(actionMatch[0], '').trim();
            pendingActionContainer.style.display = 'block';
            pendingActionDetails.textContent = `Click Target: ${currentPendingActionSelector}`;
            chrome.runtime.sendMessage({
                type: 'HIGHLIGHT_ELEMENT',
                selector: currentPendingActionSelector
            });
        }

        // Parse for Form Fill requests
        const fillMatch = replyText.match(/\[FILL:\s*(.+?)\s*\|\s*(.+?)\]/);
        if (fillMatch) {
            currentPendingActionSelector = fillMatch[1].trim();
            currentPendingFillValue = fillMatch[2].trim();
            replyText = replyText.replace(fillMatch[0], '').trim();
            pendingActionContainer.style.display = 'block';
            pendingActionDetails.textContent = `Fill: ${currentPendingActionSelector} \nWith: "${currentPendingFillValue}"`;
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
        removeTypingIndicator();
        chatInput.disabled = false;
        sendBtn.disabled = false;
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

// Tool Action Handlers
clearBtn.addEventListener('click', () => {
    chatContainer.innerHTML = '';
    saveChatToStorage();
});

haltBtn.addEventListener('click', () => {
    // 1. Send halt to backend
    fetch('http://localhost:10000/api/browser/halt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: true })
    }).catch(e => console.log(e));

    // 2. Clear UI states
    resetPendingAction();
    julesBridgeContainer.style.display = 'none';
    if (julesPollInterval) {
        clearTimeout(julesPollInterval);
        julesPollInterval = null;
    }
    removeTypingIndicator();
    chatInput.disabled = false;
    sendBtn.disabled = false;
    appendMessage('System', '🛑 ALL OPERATIONS HALTED.');
});

// Action Handlers
approveBtn.addEventListener('click', async () => {
    if (currentPendingActionSelector) {
        chrome.runtime.sendMessage({
            type: 'EXECUTE_ACTION',
            selector: currentPendingActionSelector,
            actionType: currentPendingFillValue ? 'FILL' : 'CLICK',
            fillValue: currentPendingFillValue
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
    currentPendingFillValue = null;
    chrome.runtime.sendMessage({ type: 'CLEAR_HIGHLIGHT' });
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

            // Color Coding
            if (data.status === 'validated_ss3' || data.status === 'promoted_to_ss1') {
                julesActiveStatus.style.borderColor = '#4caf50';
                julesActiveStatus.style.color = '#4caf50';
            } else if (data.status.includes('error') || data.status === 'cancelled') {
                julesActiveStatus.style.borderColor = '#f44336';
                julesActiveStatus.style.color = '#f44336';
            } else {
                julesActiveStatus.style.borderColor = '#ff9800';
                julesActiveStatus.style.color = '#ff9800';
            }

            if (data.status === 'awaiting_human_approval') {
                julesApproveBtn.style.display = 'block';
            } else {
                julesApproveBtn.style.display = 'none';
            }

            // Exponential Backoff Polling
            if (data.status !== 'promoted_to_ss1' && data.status !== 'cancelled' && !data.status.includes('error')) {
                if (julesPollInterval) clearTimeout(julesPollInterval);
                julesPollInterval = setTimeout(() => {
                    pollDelay = Math.min(pollDelay * 1.5, 15000); // Max 15s delay
                    triggerJulesAPI(`/api/jules/status/${activeJulesTaskId}`, {});
                }, pollDelay);
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