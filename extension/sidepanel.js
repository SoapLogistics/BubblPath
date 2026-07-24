// sidepanel.js

const chatContainer = document.getElementById('chat-container');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

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

    try {
        const response = await fetch('http://localhost:10000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        appendMessage('Solomon', data.reply);
    } catch (error) {
        console.error("Error communicating with Solomon backend:", error);
        appendMessage('System', 'Error connecting to Solomon backend.');
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