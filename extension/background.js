// background.js

// 15. Tab Context Caching
const contextCache = {};
let currentContext = null;

chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch((error) => console.error(error));

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'EXTRACT_DOM') {
        console.log("Received DOM extraction data:", request.payload);

        const tabId = sender.tab ? sender.tab.id : 'unknown';
        contextCache[tabId] = request.payload;
        currentContext = request.payload;

        // 19. Badge Text Status
        chrome.action.setBadgeText({text: "AI", tabId: tabId}).catch(()=>{});
        chrome.action.setBadgeBackgroundColor({color: '#4caf50', tabId: tabId}).catch(()=>{});

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
    // 15. Load from cache immediately if available
    if (contextCache[activeInfo.tabId]) {
        currentContext = contextCache[activeInfo.tabId];
        chrome.runtime.sendMessage({
            type: 'CONTEXT_UPDATED',
            payload: currentContext
        }).catch(()=>{});
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

// Keep-Alive for Service Worker
chrome.alarms.create("keepAlive", { periodInMinutes: 4 });
chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === "keepAlive") {
        console.log("Jules Bridge Keep-Alive Ping.");
    }
});