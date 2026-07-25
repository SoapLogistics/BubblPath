async function getConfig() {
    return new Promise((resolve) => {
        chrome.storage.local.get(['backendUrl', 'authKey'], (result) => {
            resolve({
                backendUrl: result.backendUrl || "http://localhost:10000",
                authKey: result.authKey || ""
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    refreshContext();

    document.getElementById('btn-refresh-context').addEventListener('click', refreshContext);

    document.getElementById('chat-btn').addEventListener('click', sendChatMessage);
});

let currentContext = null;
let currentTabId = null;

function refreshContext() {
    const display = document.getElementById('context-display');
    display.textContent = "Fetching context...";

    chrome.runtime.sendMessage({ action: "GET_CURRENT_TAB_CONTEXT" }, (response) => {
        if (chrome.runtime.lastError) {
            display.textContent = "Error: Cannot access tab. " + chrome.runtime.lastError.message;
            return;
        }

        if (response && response.context) {
            currentContext = response.context;

            // Get active tab ID safely
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                if (tabs.length > 0) currentTabId = tabs[0].id;
            });

            let displayTxt = `URL: ${currentContext.url}\nTitle: ${currentContext.title}\nAdapter: ${currentContext.adapter}`;
            if (currentContext.github) {
                displayTxt += `\nGitHub PR/Issue: ${currentContext.github.prTitle || 'N/A'}`;
            }
            display.textContent = displayTxt;
        } else {
            display.textContent = "No context available.";
        }
    });
}

function appendChatMessage(sender, text, isError = false) {
    const chatLog = document.getElementById('chat-log');
    const div = document.createElement('div');
    if (isError) {
        div.style.color = 'red';
    }
    const b = document.createElement('b');
    b.textContent = `${sender}: `;
    div.appendChild(b);
    const span = document.createElement('span');
    span.textContent = text;
    div.appendChild(span);
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    appendChatMessage('You', msg);
    input.value = '';

    try {
        const config = await getConfig();
        if (!config.authKey) {
            appendChatMessage('Error', 'Authentication key not configured. Please set it in options.', true);
            return;
        }

        const response = await fetch(`${config.backendUrl}/api/browser-companion/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.authKey}`
            },
            body: JSON.stringify({
                message: msg,
                context: currentContext
            })
        });

        const data = await response.json();
        appendChatMessage('Solomon', data.reply);

        if (data.proposed_actions && data.proposed_actions.length > 0) {
            queueActions(data.proposed_actions);
        }

    } catch (err) {
        appendChatMessage('Error', err.message, true);
    }
}

function queueActions(actions) {
    const section = document.getElementById('action-queue-section');
    const list = document.getElementById('action-list');

    section.style.display = 'block';

    actions.forEach((action, index) => {
        const cardId = `action-card-${Date.now()}-${index}`;
        const card = document.createElement('div');
        card.className = 'action-card';
        card.id = cardId;

        const typeStrong = document.createElement('strong');
        typeStrong.textContent = `Proposed Action: ${action.type}`;
        card.appendChild(typeStrong);

        const targetDiv = document.createElement('div');
        targetDiv.textContent = 'Target: ';
        const targetCode = document.createElement('code');
        targetCode.textContent = action.selector;
        targetDiv.appendChild(targetCode);
        card.appendChild(targetDiv);

        if (action.value) {
            const valDiv = document.createElement('div');
            valDiv.textContent = 'Value: ';
            const valCode = document.createElement('code');
            valCode.textContent = action.value;
            valDiv.appendChild(valCode);
            card.appendChild(valDiv);
        }

        const btnGroup = document.createElement('div');
        btnGroup.className = 'button-group';

        const approveBtn = document.createElement('button');
        approveBtn.className = 'btn-approve';
        approveBtn.textContent = 'Approve';
        approveBtn.addEventListener('click', () => {
            approveAction(cardId, action);
        });

        const rejectBtn = document.createElement('button');
        rejectBtn.className = 'btn-reject';
        rejectBtn.textContent = 'Reject';
        rejectBtn.addEventListener('click', () => {
            rejectAction(cardId);
        });

        btnGroup.appendChild(approveBtn);
        btnGroup.appendChild(rejectBtn);
        card.appendChild(btnGroup);

        list.appendChild(card);
    });
}

function approveAction(cardId, actionData) {
    if (!currentTabId) {
        alert("Cannot determine active tab.");
        return;
    }

    chrome.runtime.sendMessage({
        action: "EXECUTE_APPROVED_ACTION",
        payload: {
            tabId: currentTabId,
            actionData: actionData
        }
    }, (response) => {
        const card = document.getElementById(cardId);
        if (!card) return;

        // Clear card
        while(card.firstChild) { card.removeChild(card.firstChild); }

        if (response && response.success) {
            const strong = document.createElement('strong');
            strong.style.color = 'green';
            strong.textContent = 'Action Executed!';
            card.appendChild(strong);

            const msgDiv = document.createElement('div');
            msgDiv.textContent = response.message;
            card.appendChild(msgDiv);

            setTimeout(() => {
                card.remove();
                checkQueueEmpty();
            }, 3000);
        } else {
            const errDiv = document.createElement('div');
            errDiv.style.color = 'red';
            errDiv.style.marginTop = '5px';
            errDiv.textContent = `Execution Failed: ${response ? response.error || response.message : 'Unknown error'}`;
            card.appendChild(errDiv);
        }
    });
}

function rejectAction(cardId) {
    const card = document.getElementById(cardId);
    if (card) {
        card.remove();
        checkQueueEmpty();
    }
}

function checkQueueEmpty() {
    const list = document.getElementById('action-list');
    if (list.children.length === 0) {
        document.getElementById('action-queue-section').style.display = 'none';
    }
}
