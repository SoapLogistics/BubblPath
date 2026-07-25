// Universal Content Script for observing context and executing DOM actions

let currentAdapter = null;

// Determine adapter based on hostname
const hostname = window.location.hostname;
if (hostname.includes("github.com")) {
    currentAdapter = "GitHubAdapter";
} else if (hostname.includes("kalshi.com")) {
    currentAdapter = "KalshiAdapter";
} else if (hostname.includes("polymarket.com")) {
    currentAdapter = "PolymarketAdapter";
} else if (hostname.includes("draftkings.com")) {
    currentAdapter = "DraftKingsAdapter";
} else if (hostname.includes("fanduel.com")) {
    currentAdapter = "FanDuelAdapter";
} else if (hostname.includes("amazon.com")) {
    currentAdapter = "AmazonAdapter";
} else if (hostname.includes("ebay.com")) {
    currentAdapter = "EbayAdapter";
} else if (hostname.includes("youtube.com")) {
    currentAdapter = "YouTubeAdapter";
} else if (hostname.includes("docs.google.com")) {
    currentAdapter = "GoogleDocsAdapter";
} else if (hostname.includes("chatgpt.com") || hostname.includes("chat.openai.com")) {
    currentAdapter = "ChatGPTAdapter";
} else if (hostname.includes("gemini.google.com")) {
    currentAdapter = "GeminiAdapter";
} else if (hostname.includes("claude.ai")) {
    currentAdapter = "ClaudeAdapter";
} else {
    currentAdapter = "GenericAdapter";
}

// Minimal generic context gathering
function getGenericContext() {
    return {
        url: window.location.href,
        title: document.title,
        text: document.body.innerText.substring(0, 5000), // Cap length
        adapter: currentAdapter
    };
}

// GitHub specific extraction (as per Memory)
function extractGitHub() {
    const context = getGenericContext();
    const titleEl = document.querySelector('.js-issue-title');
    const bodyEl = document.querySelector('.comment-body');
    const diffEl = document.querySelector('.diff-view'); // simplified

    context.github = {
        prTitle: titleEl ? titleEl.innerText : null,
        issueBody: bodyEl ? bodyEl.innerText : null,
        hasDiffs: !!diffEl
    };
    return context;
}

function gatherContext() {
    if (currentAdapter === "GitHubAdapter") {
        return extractGitHub();
    }
    // We can expand other specific adapters here or load them modularly
    return getGenericContext();
}

// Execute explicitly authorized actions
function executeAction(actionData) {
    console.log(`Executing authorized action:`, actionData);

    // Example format: [ACTION: #selector] or [FILL: #selector | value]
    try {
        if (actionData.type === 'ACTION' && actionData.selector) {
            const el = document.querySelector(actionData.selector);
            if (el) {
                el.click();
                return { success: true, message: `Clicked ${actionData.selector}` };
            }
        } else if (actionData.type === 'FILL' && actionData.selector && actionData.value !== undefined) {
            const el = document.querySelector(actionData.selector);
            if (el) {
                el.value = actionData.value;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
                return { success: true, message: `Filled ${actionData.selector}` };
            }
        }
        return { success: false, message: `Selector not found: ${actionData.selector}` };
    } catch (e) {
        return { success: false, error: e.message };
    }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "GATHER_CONTEXT") {
        const ctx = gatherContext();
        sendResponse({ context: ctx });
    } else if (message.action === "EXECUTE_ACTION") {
        const result = executeAction(message.payload);
        sendResponse(result);
    }
    return true;
});
