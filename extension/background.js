// background.js

let currentContext = null;

chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch((error) => console.error(error));

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'EXTRACT_DOM') {
        console.log("Received DOM extraction data:", request.payload);

        // Context Diffing: Only broadcast if url or type changed
        if (!currentContext || currentContext.url !== request.payload.url || currentContext.type !== request.payload.type) {
            currentContext = request.payload;
            // Notify side panel that new context is available
            chrome.runtime.sendMessage({
                type: 'CONTEXT_UPDATED',
                payload: currentContext
            }).catch(err => {
                // Ignore error if side panel is closed
            });
        } else {
             currentContext = request.payload; // Update data silently
        }

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
    chrome.tabs.sendMessage(activeInfo.tabId, { type: 'REQUEST_DOM_EXTRACTION' }).catch(() => {
        // Ignore errors for internal chrome:// pages or un-injected tabs
        console.log("Could not request extraction on new tab.");
    });
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