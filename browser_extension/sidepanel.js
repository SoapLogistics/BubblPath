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

    // Tab switching logic
    document.getElementById('tab-companion').addEventListener('click', () => switchTab('companion'));
    document.getElementById('tab-loki').addEventListener('click', () => switchTab('loki'));
    document.getElementById('tab-hephaestus').addEventListener('click', () => switchTab('hephaestus'));
    document.getElementById('tab-casino').addEventListener('click', () => switchTab('casino'));

    // Engine API logic
    document.getElementById('btn-loki-predict').addEventListener('click', requestLokiPrediction);
    document.getElementById('btn-hephaestus-scaffold').addEventListener('click', requestHephaestusScaffold);

    // Casino Lab logic
    document.querySelectorAll('.btn-card').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const val = e.target.getAttribute('data-val');
            logCard(val);
        });
    });
    document.getElementById('btn-reset-shoe').addEventListener('click', resetShoe);
    document.getElementById('kelly-bankroll').addEventListener('input', updateCasinoDisplay);
});

function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

    document.getElementById(`tab-${tabName}`).classList.add('active');
    document.getElementById(`content-${tabName}`).classList.add('active');
}

// Basic Casino Lab Logic (Hi-Lo System)
let runningCount = 0;
let cardsDealt = 0;
const totalDecks = 6;

function logCard(card) {
    cardsDealt++;
    if (['2','3','4','5','6'].includes(card)) {
        runningCount++;
    } else if (['10','A'].includes(card)) {
        runningCount--;
    }
    updateCasinoDisplay();
}

function resetShoe() {
    runningCount = 0;
    cardsDealt = 0;
    updateCasinoDisplay();
}

function updateCasinoDisplay() {
    document.getElementById('rc-display').textContent = runningCount;

    let decksRemaining = totalDecks - (cardsDealt / 52);
    if (decksRemaining < 0.5) decksRemaining = 0.5; // floor

    const trueCount = runningCount / decksRemaining;
    document.getElementById('tc-display').textContent = trueCount.toFixed(1);
    document.getElementById('deck-est').textContent = `Decks Remaining: ~${decksRemaining.toFixed(1)}`;

    // Kelly Criterion calculation
    // Base house edge for a standard 6-deck shoe is roughly -0.5%
    // Each +1 True Count shifts the edge by approximately +0.5% towards the player.
    const playerEdgePercent = -0.5 + (trueCount * 0.5);
    const edgeDisplay = document.getElementById('kelly-edge');
    edgeDisplay.textContent = playerEdgePercent.toFixed(2) + '%';
    edgeDisplay.style.color = playerEdgePercent > 0 ? '#27ae60' : '#e74c3c';

    const bankroll = parseFloat(document.getElementById('kelly-bankroll').value) || 0;

    // Kelly Formula (f* = bp - q / b) simplified for Blackjack paying 1:1 (b=1)
    // f* = edge / variance. Variance in blackjack is roughly 1.33
    const variance = 1.33;
    const decimalEdge = playerEdgePercent / 100;
    let kellyFraction = decimalEdge > 0 ? decimalEdge / variance : 0;

    // Cap at 0 to avoid negative bet sizing suggestions
    if (kellyFraction < 0) kellyFraction = 0;

    const betSize = bankroll * kellyFraction;
    document.getElementById('kelly-bet').textContent = `$${betSize.toFixed(2)}`;
}

let currentContext = null;
let currentTabId = null;

async function requestLokiPrediction() {
    const out = document.getElementById('loki-prediction-output');
    out.textContent = "Analyzing probabilities...";
    out.style.color = "#333";
    try {
        const config = await getConfig();
        const res = await fetch(`${config.backendUrl}/api/loki/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.authKey}`
            },
            body: JSON.stringify({ context: currentContext })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        out.textContent = data.prediction || "No actionable edge detected.";
        out.style.color = data.prediction.includes('BET') ? '#27ae60' : '#e74c3c';
    } catch (e) {
        out.textContent = `Error: ${e.message}`;
        out.style.color = "red";
    }
}

async function requestHephaestusScaffold() {
    const prompt = document.getElementById('hephaestus-prompt').value;
    if (!prompt) return;
    const out = document.getElementById('hephaestus-output');
    out.textContent = "Scaffolding in forge...";
    try {
        const config = await getConfig();
        const res = await fetch(`${config.backendUrl}/api/hephaestus/scaffold`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.authKey}`
            },
            body: JSON.stringify({ prompt, context: currentContext })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        out.textContent = data.status || "Scaffolding complete.";
    } catch (e) {
        out.textContent = `Error: ${e.message}`;
    }
}

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

            // Update Loki Context display if applicable
            const lokiDisplay = document.getElementById('loki-context-display');
            if (currentContext.kalshi || currentContext.polymarket || currentContext.sportsbook) {
                lokiDisplay.textContent = JSON.stringify(currentContext.kalshi || currentContext.polymarket || currentContext.sportsbook, null, 2);
            } else {
                lokiDisplay.textContent = "No supported market context detected on this page.";
            }

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

        // Highlight element on hover
        card.addEventListener('mouseenter', () => {
            if (currentTabId) {
                chrome.runtime.sendMessage({
                    action: "HOVER_ACTION",
                    payload: { tabId: currentTabId, actionData: action, highlight: true }
                });
            }
        });

        card.addEventListener('mouseleave', () => {
            if (currentTabId) {
                chrome.runtime.sendMessage({
                    action: "HOVER_ACTION",
                    payload: { tabId: currentTabId, actionData: action, highlight: false }
                });
            }
        });

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
