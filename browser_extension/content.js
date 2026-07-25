// Universal Content Script for observing context and executing DOM actions

let currentAdapter = null;

class AdapterManager {
    constructor() {
        this.hostname = window.location.hostname;
        this.adapterName = this._determineAdapter();
    }

    _determineAdapter() {
        const h = this.hostname;
        if (h.includes("github.com")) return "GitHubAdapter";
        if (h.includes("kalshi.com")) return "KalshiAdapter";
        if (h.includes("polymarket.com")) return "PolymarketAdapter";
        if (h.includes("draftkings.com")) return "DraftKingsAdapter";
        if (h.includes("fanduel.com")) return "FanDuelAdapter";
        if (h.includes("amazon.com")) return "AmazonAdapter";
        if (h.includes("ebay.com")) return "EbayAdapter";
        if (h.includes("youtube.com")) return "YouTubeAdapter";
        if (h.includes("docs.google.com")) return "GoogleDocsAdapter";
        if (h.includes("chatgpt.com") || h.includes("chat.openai.com")) return "ChatGPTAdapter";
        if (h.includes("gemini.google.com")) return "GeminiAdapter";
        if (h.includes("claude.ai")) return "ClaudeAdapter";
        return "GenericAdapter";
    }

    getBaseContext() {
        return {
            url: window.location.href,
            title: document.title,
            text: document.body.innerText.substring(0, 5000), // Cap length
            adapter: this.adapterName
        };
    }

    gatherContext() {
        const ctx = this.getBaseContext();

        if (this.adapterName === "GitHubAdapter") {
            const titleEl = document.querySelector('.js-issue-title');
            const bodyEl = document.querySelector('.comment-body');
            const diffEl = document.querySelector('.diff-view'); // simplified
            ctx.github = {
                prTitle: titleEl ? titleEl.innerText : null,
                issueBody: bodyEl ? bodyEl.innerText : null,
                hasDiffs: !!diffEl
            };
        } else if (this.adapterName === "KalshiAdapter") {
            // Advanced Kalshi Logic with Mock Order Book Imbalance calculation
            const titleEl = document.querySelector('h1');
            const bidEls = document.querySelectorAll('.bid-size'); // Mock selectors
            const askEls = document.querySelectorAll('.ask-size');

            let totalBidSize = 0;
            let totalAskSize = 0;
            bidEls.forEach(el => totalBidSize += (parseInt(el.innerText) || 0));
            askEls.forEach(el => totalAskSize += (parseInt(el.innerText) || 0));

            const imbalance = (totalBidSize + totalAskSize) === 0 ? 0
                : (totalBidSize - totalAskSize) / (totalBidSize + totalAskSize);

            ctx.kalshi = {
                marketTitle: titleEl ? titleEl.innerText : null,
                totalBidSize,
                totalAskSize,
                orderBookImbalanceRatio: imbalance.toFixed(4)
            };
        } else if (this.adapterName === "PolymarketAdapter") {
            const titleEl = document.querySelector('h1');
            const probEls = document.querySelectorAll('.probability-display'); // Generic stub selector
            ctx.polymarket = {
                marketTitle: titleEl ? titleEl.innerText : null,
                detectedProbabilities: Array.from(probEls).map(el => el.innerText).slice(0, 5)
            };
        }
        return ctx;
    }
}

const adapterManager = new AdapterManager();

// Execute explicitly authorized actions
let activeHighlightEl = null;

function toggleHighlight(actionData, highlight) {
    try {
        if (!actionData.selector) return;
        const el = document.querySelector(actionData.selector);
        if (!el) return;

        if (highlight) {
            // Remove existing
            if (activeHighlightEl) activeHighlightEl.remove();

            const rect = el.getBoundingClientRect();

            // Inject Keyframes if not present
            if (!document.getElementById('solomon-highlight-style')) {
                const style = document.createElement('style');
                style.id = 'solomon-highlight-style';
                style.textContent = `
                    @keyframes solomonPulse {
                        0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }
                        70% { box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }
                        100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
                    }
                `;
                document.head.appendChild(style);
            }

            activeHighlightEl = document.createElement('div');
            activeHighlightEl.style.position = 'fixed';
            activeHighlightEl.style.top = `${rect.top}px`;
            activeHighlightEl.style.left = `${rect.left}px`;
            activeHighlightEl.style.width = `${rect.width}px`;
            activeHighlightEl.style.height = `${rect.height}px`;
            activeHighlightEl.style.backgroundColor = 'rgba(231, 76, 60, 0.3)';
            activeHighlightEl.style.border = '2px dashed #e74c3c';
            activeHighlightEl.style.pointerEvents = 'none';
            activeHighlightEl.style.zIndex = '999999';
            activeHighlightEl.style.animation = 'solomonPulse 1.5s infinite';

            // Add a crosshair / tooltip label
            const tooltip = document.createElement('div');
            tooltip.style.position = 'absolute';
            tooltip.style.bottom = '100%';
            tooltip.style.left = '0';
            tooltip.style.backgroundColor = '#e74c3c';
            tooltip.style.color = 'white';
            tooltip.style.padding = '2px 6px';
            tooltip.style.fontSize = '10px';
            tooltip.style.fontWeight = 'bold';
            tooltip.style.borderRadius = '3px 3px 0 0';
            tooltip.style.whiteSpace = 'nowrap';
            tooltip.textContent = `⚡ Solomon Intent: ${actionData.type}`;
            activeHighlightEl.appendChild(tooltip);

            document.body.appendChild(activeHighlightEl);
        } else {
            if (activeHighlightEl) {
                activeHighlightEl.remove();
                activeHighlightEl = null;
            }
        }
    } catch (e) {
        // ignore highlight errors
    }
}

function executeAction(actionData) {
    console.log(`Executing authorized action:`, actionData);
    if (activeHighlightEl) activeHighlightEl.remove();

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
    if (message.action === "GATHER_SEMANTIC_SELECTION") {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const container = range.commonAncestorContainer;
            let parentEl = container.nodeType === 3 ? container.parentNode : container;

            // Try to find nearest header for context
            let nearestHeader = null;
            let current = parentEl;
            while(current && current !== document.body) {
                const header = current.previousElementSibling;
                if (header && ['H1','H2','H3','H4'].includes(header.tagName)) {
                    nearestHeader = header.innerText;
                    break;
                }
                current = current.parentElement;
            }

            const rawText = selection.toString();
            let semanticContext = rawText;
            if (nearestHeader) {
                semanticContext = `[Section: ${nearestHeader}]\n${rawText}`;
            }

            // If it's inside a code block, denote it
            if (parentEl.closest('pre') || parentEl.closest('code')) {
                semanticContext = `[Code Block]\n${semanticContext}`;
            }

            sendResponse({ semanticContext });
        } else {
            sendResponse({ semanticContext: null });
        }
    } else if (message.action === "GATHER_CONTEXT") {
        const ctx = adapterManager.gatherContext();
        sendResponse({ context: ctx });
    } else if (message.action === "HIGHLIGHT_ACTION") {
        toggleHighlight(message.payload.actionData, message.payload.highlight);
        sendResponse({ success: true });
    } else if (message.action === "EXECUTE_ACTION") {
        const result = executeAction(message.payload);
        sendResponse(result);
    }
    return true;
});
