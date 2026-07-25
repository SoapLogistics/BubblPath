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
            const prStatusEl = document.querySelector('.State'); // PR state (Merged, Closed, Open)

            ctx.github = {
                prTitle: titleEl ? titleEl.innerText : null,
                issueBody: bodyEl ? bodyEl.innerText : null,
                prState: prStatusEl ? prStatusEl.innerText.trim() : 'Unknown',
                hasDiffs: !!diffEl
            };
        } else if (this.adapterName === "AmazonAdapter") {
            const titleEl = document.querySelector('#productTitle');
            const priceEl = document.querySelector('.a-price .a-offscreen');
            const reviewEl = document.querySelector('#acrPopover');

            ctx.amazon = {
                productTitle: titleEl ? titleEl.innerText.trim() : null,
                detectedPrice: priceEl ? priceEl.innerText.trim() : null,
                reviewRating: reviewEl ? reviewEl.getAttribute('title') : null
            };
        } else if (this.adapterName === "DraftKingsAdapter" || this.adapterName === "FanDuelAdapter") {
            // Advanced Heuristic Scraping: Capture up to 100 bets with contextual labels
            const textNodes = document.body.innerText.split('\n').map(t => t.trim()).filter(t => t.length > 0);
            const bets = [];

            for (let i = 0; i < textNodes.length; i++) {
                if (/^[+-]\d{3,}$/.test(textNodes[i])) {
                    // Try to grab the previous 1-2 lines for context (e.g., Team Name, Prop)
                    let contextStr = "";
                    if (i >= 1 && !/^[+-]\d{3,}$/.test(textNodes[i-1])) contextStr += textNodes[i-1];
                    if (i >= 2 && !/^[+-]\d{3,}$/.test(textNodes[i-2])) contextStr = textNodes[i-2] + " " + contextStr;

                    bets.push({
                        odds: textNodes[i],
                        context: contextStr.trim() || "Unknown Market"
                    });

                    if (bets.length >= 100) break; // Capture top 100
                }
            }

            ctx.sportsbook = {
                platform: this.adapterName,
                detectedBets: bets,
                totalCaptured: bets.length,
                liveMutationActive: true
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
            // Advanced Heuristic Scraping for Polymarket probabilities (e.g., 45¢, 62%)
            const textNodes = document.body.innerText.split('\n').map(t => t.trim()).filter(t => t.length > 0);
            const markets = [];

            for (let i = 0; i < textNodes.length; i++) {
                if (/^\d{1,2}(¢|%)$/.test(textNodes[i])) {
                    let contextStr = "";
                    if (i >= 1 && !/^\d{1,2}(¢|%)$/.test(textNodes[i-1])) contextStr += textNodes[i-1];

                    markets.push({
                        price: textNodes[i],
                        context: contextStr.trim() || "Unknown Outcome"
                    });

                    if (markets.length >= 100) break;
                }
            }

            const titleEl = document.querySelector('h1');
            ctx.polymarket = {
                marketTitle: titleEl ? titleEl.innerText : null,
                detectedMarkets: markets,
                totalCaptured: markets.length
            };
        }
        return ctx;
    }
}

const adapterManager = new AdapterManager();

// Stealth Mutation Observer: Re-gather context quietly when DOM changes, rather than polling aggressively
let stealthObserver = null;
let mutationTimeout = null;

function initStealthObserver() {
    // Only attach if we are on a known volatile platform (Sportsbooks, Prediction Markets)
    const volatileAdapters = ["DraftKingsAdapter", "FanDuelAdapter", "KalshiAdapter", "PolymarketAdapter"];
    if (volatileAdapters.includes(adapterManager.adapterName)) {
        stealthObserver = new MutationObserver(() => {
            // Debounce the mutation events (wait 500ms after mutations stop before reacting)
            clearTimeout(mutationTimeout);
            mutationTimeout = setTimeout(() => {
                // Silently update the backend with the new odds/imbalances without user interaction
                const ctx = adapterManager.gatherContext();
                chrome.runtime.sendMessage({
                    action: "STEALTH_CONTEXT_UPDATE",
                    payload: ctx
                });
            }, 500);
        });

        // Only observe the body for text/child list changes to remain lightweight
        stealthObserver.observe(document.body, { childList: true, subtree: true, characterData: true });
    }
}
initStealthObserver();

// Execute explicitly authorized actions
let activeHighlightHost = null;

function toggleHighlight(actionData, highlight) {
    try {
        if (!actionData.selector) return;
        const el = document.querySelector(actionData.selector);
        if (!el) return;

        if (highlight) {
            // Remove existing host
            if (activeHighlightHost) activeHighlightHost.remove();

            const rect = el.getBoundingClientRect();

            // STEALTH TECH: Use a closed Shadow Root.
            // Anti-cheat scripts running in the main page context cannot query into a 'closed' shadow root.
            // This hides our injected "Solomon Intent" text and pulsing UI from simple document.querySelectorAll() sweeps.
            activeHighlightHost = document.createElement('div');
            // Give the host an obscure, random-looking ID rather than "solomon-highlight"
            activeHighlightHost.id = `s-${Math.random().toString(36).substr(2, 9)}`;
            activeHighlightHost.style.position = 'fixed';
            activeHighlightHost.style.top = '0';
            activeHighlightHost.style.left = '0';
            activeHighlightHost.style.width = '100%';
            activeHighlightHost.style.height = '100%';
            activeHighlightHost.style.pointerEvents = 'none';
            activeHighlightHost.style.zIndex = '2147483647'; // Max z-index

            const shadow = activeHighlightHost.attachShadow({ mode: 'closed' });

            const style = document.createElement('style');
            style.textContent = `
                @keyframes solomonPulse {
                    0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7); }
                    70% { box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }
                    100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
                }
                .highlight-box {
                    position: absolute;
                    top: ${rect.top}px;
                    left: ${rect.left}px;
                    width: ${rect.width}px;
                    height: ${rect.height}px;
                    background-color: rgba(231, 76, 60, 0.3);
                    border: 2px dashed #e74c3c;
                    animation: solomonPulse 1.5s infinite;
                    pointer-events: none;
                }
                .highlight-tooltip {
                    position: absolute;
                    bottom: 100%;
                    left: 0;
                    background-color: #e74c3c;
                    color: white;
                    padding: 2px 6px;
                    font-size: 10px;
                    font-weight: bold;
                    border-radius: 3px 3px 0 0;
                    white-space: nowrap;
                }
            `;

            const box = document.createElement('div');
            box.className = 'highlight-box';

            const tooltip = document.createElement('div');
            tooltip.className = 'highlight-tooltip';
            tooltip.textContent = `⚡ Solomon Intent: ${actionData.type}`;

            box.appendChild(tooltip);
            shadow.appendChild(style);
            shadow.appendChild(box);

            document.body.appendChild(activeHighlightHost);
        } else {
            if (activeHighlightHost) {
                activeHighlightHost.remove();
                activeHighlightHost = null;
            }
        }
    } catch (e) {
        // ignore highlight errors
    }
}

function executeAction(actionData) {
    console.log(`Executing authorized action:`, actionData);
    if (activeHighlightHost) activeHighlightHost.remove();

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
