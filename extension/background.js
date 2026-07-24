// background.js

// 15. Tab Context Caching
const contextCache = {};
let currentContext = null;

chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch((error) => console.error(error));

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'EXTRACT_DOM') {
        console.log("Received DOM extraction data:", request.payload);

        const tabId = sender.tab ? sender.tab.id : 'unknown';

        // 14. LRU Tab Cache Limits & 15. Context Stale TTL
        contextCache[tabId] = {
            payload: request.payload,
            timestamp: Date.now()
        };
        const cacheKeys = Object.keys(contextCache);
        if (cacheKeys.length > 20) {
            delete contextCache[cacheKeys[0]]; // Simple LRU (delete oldest key)
        }

        currentContext = request.payload;

        // 19. Badge Text Status & 16. Dynamic Badge Colors
        let badgeColor = '#4caf50'; // Green default
        if (currentContext.type === 'blocked_casino') badgeColor = '#f44336'; // Red blocked
        else if (currentContext.type === 'draftkings' || currentContext.type === 'kalshi') badgeColor = '#ff9800'; // Orange betting

        chrome.action.setBadgeText({text: "AI", tabId: tabId}).catch(()=>{});
        chrome.action.setBadgeBackgroundColor({color: badgeColor, tabId: tabId}).catch(()=>{});

        // Notify side panel that new context is available
        chrome.runtime.sendMessage({
            type: 'CONTEXT_UPDATED',
            payload: currentContext
        }).catch(err => {
            // Ignore error if side panel is closed
        });

        // Optional: Send to local backend for logging/processing
        fetch('http://localhost:10000/api/browser/context', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentContext)
        }).catch(err => console.error("Failed to send context to backend:", err));

        sendResponse({status: "success"});
    }

    if (request.type === 'GET_CURRENT_CONTEXT') {
        sendResponse(currentContext);
    }

    // Route action commands to the active tab's content script
    if (['HIGHLIGHT_ELEMENT', 'EXECUTE_ACTION', 'CLEAR_HIGHLIGHT'].includes(request.type)) {
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            if (tabs[0]) {
                chrome.tabs.sendMessage(tabs[0].id, request).catch(err => console.error("Error sending message to active tab:", err));
            }
        });
        // We don't need to return sendResponse asynchronously here
    }
});

// Update context when the user switches tabs
chrome.tabs.onActivated.addListener((activeInfo) => {
    // 15. Load from cache immediately if available (and not stale)
    const cached = contextCache[activeInfo.tabId];
    if (cached) {
        if (Date.now() - cached.timestamp < 300000) { // 5 minutes TTL
            currentContext = cached.payload;
            chrome.runtime.sendMessage({
                type: 'CONTEXT_UPDATED',
                payload: currentContext
            }).catch(()=>{});
        } else {
            delete contextCache[activeInfo.tabId]; // Expired
        }
    }

    // 17. Timeout Safety for message sending
    Promise.race([
        chrome.tabs.sendMessage(activeInfo.tabId, { type: 'REQUEST_DOM_EXTRACTION' }),
        new Promise((_, reject) => setTimeout(() => reject(new Error("Timeout")), 2000))
    ]).catch(() => {
        console.log("Could not request extraction on new tab (timeout or un-injected).");
    });
});

// 16. Tab Cleanup
chrome.tabs.onRemoved.addListener((tabId) => {
    if (contextCache[tabId]) {
        delete contextCache[tabId];
    }
});

// Update context when the tab finishes loading a new URL
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.active) {
        chrome.tabs.sendMessage(tabId, { type: 'REQUEST_DOM_EXTRACTION' }).catch(() => {});
    }
});

// Passive Learning: Auto-memorize pages user spends > 45 seconds actively viewing
chrome.tabs.onActivated.addListener((activeInfo) => {
    const tabId = activeInfo.tabId;

    // Clear any existing passive learning alarm
    chrome.alarms.clear("passiveLearn");

    // Start new passive learning timer using Chrome Alarms for reliability
    chrome.alarms.create("passiveLearn", { delayInMinutes: 0.75 }); // 45 seconds

    // Store current active tab for the alarm handler
    chrome.storage.session.set({ activeLearningTabId: tabId });
});

// Alarm Handler
chrome.alarms.create("keepAlive", { periodInMinutes: 4 });
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === "keepAlive") {
        console.log("Jules Bridge Keep-Alive Ping.");
    }

    if (alarm.name === "passiveLearn") {
        chrome.storage.session.get(['activeLearningTabId'], (result) => {
            const tabId = result.activeLearningTabId;
            if (tabId && contextCache[tabId]) {
                const cached = contextCache[tabId];
                if (cached.payload && cached.payload.url) {
                    console.log("Passive Learning Triggered for:", cached.payload.url);
                    fetch('http://localhost:10000/api/mnemosyne/remember', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(cached.payload)
                    }).catch(() => {}); // Silent fail
                }
            }
        });
    }
});