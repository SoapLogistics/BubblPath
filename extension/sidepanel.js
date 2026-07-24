// sidepanel.js

const chatContainer = document.getElementById('chat-container');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const contextBanner = document.getElementById('context-banner');
const pendingActionContainer = document.getElementById('pending-action-container');
const pendingActionDetails = document.getElementById('pending-action-details');
const approveBtn = document.getElementById('approve-btn');
const cancelBtn = document.getElementById('cancel-btn');

let activeContext = null;
let currentPendingActionSelector = null;

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
            // Remove the raw action tag from the user-visible message
            replyText = replyText.replace(actionMatch[0], '').trim();

            // Show approval UI
            pendingActionContainer.style.display = 'block';
            pendingActionDetails.textContent = `Target: ${currentPendingActionSelector}`;

            // Highlight element on page
            chrome.runtime.sendMessage({
                type: 'HIGHLIGHT_ELEMENT',
                selector: currentPendingActionSelector
            });
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