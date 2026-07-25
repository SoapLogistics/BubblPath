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

// Context Menu for Teaching SPLE
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "teach-solomon",
        title: "Teach Solomon (SPLE)",
        contexts: ["selection"]
    });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === "teach-solomon") {
        const text = info.selectionText;
        if (text) {
            const context = {
                url: tab.url,
                title: tab.title,
                text: text,
                is_explicit_teaching: true
            };
            await pushToMnemosyne(context, tab.id);
            // Optional: Provide UI feedback via content script injection
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                func: () => alert("Memory pushed to Solomon Perpetual Learning Engine.")
            }).catch(e => console.error(e));
        }
    }
});

// Initialize Side Panel to open on extension icon click (Chrome/Edge only)
if (chrome.sidePanel && chrome.sidePanel.setPanelBehavior) {
    chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch((error) => console.error(error));
} else {
    // Firefox fallback: Open sidebar on action click
    chrome.action.onClicked.addListener(() => {
        // Firefox uses sidebar_action, clicking the action button toggles it automatically
        console.log("Action clicked. Sidebar should open in Firefox.");
    });
}

// Track Active Tab Time for Passive Learning (Memory: pushing context to /api/mnemosyne/remember after 45s)
chrome.tabs.onActivated.addListener(async (activeInfo) => {
    await chrome.storage.session.set({ currentTabId: activeInfo.tabId });
    chrome.alarms.create(`passive_learning_${activeInfo.tabId}`, { delayInMinutes: 0.75 }); // 45 seconds
});

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    const data = await chrome.storage.session.get('currentTabId');
    if (tabId === data.currentTabId && changeInfo.status === 'complete') {
        chrome.alarms.create(`passive_learning_${tabId}`, { delayInMinutes: 0.75 });
    }
});

chrome.alarms.onAlarm.addListener(async (alarm) => {
    if (alarm.name.startsWith('passive_learning_')) {
        const targetTabId = parseInt(alarm.name.split('_').pop());
        const data = await chrome.storage.session.get('currentTabId');

        if (targetTabId === data.currentTabId) {
            // Send a message to content script to gather context
            chrome.tabs.sendMessage(targetTabId, { action: "GATHER_CONTEXT" }, async (response) => {
                if (chrome.runtime.lastError) {
                    console.error("Tab closed or script not ready.");
                    return;
                }
                if (response && response.context) {
                    await pushToMnemosyne(response.context, targetTabId);
                }
            });
        }
    }
});

async function pushToMnemosyne(context, tabId) {
    try {
        const config = await getConfig();
        if (!config.authKey) {
            console.error("Mnemosyne Sync Error: No Auth Key configured.");
            return;
        }

        const res = await fetch(`${config.backendUrl}/api/mnemosyne/remember`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.authKey}`
            },
            body: JSON.stringify({ context, source: "browser_companion", tabId })
        });
        if (!res.ok) throw new Error("Failed to push to memory");
    } catch (error) {
        console.error("Mnemosyne Sync Error:", error);
    }
}

// Listen for explicit execution approvals from sidepanel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "EXECUTE_APPROVED_ACTION") {
        const { tabId, actionData } = message.payload;
        chrome.tabs.sendMessage(tabId, { action: "EXECUTE_ACTION", payload: actionData }, (response) => {
            sendResponse(response);
        });
        return true; // async response
    }

    if (message.action === "HOVER_ACTION") {
        const { tabId, actionData, highlight } = message.payload;
        chrome.tabs.sendMessage(tabId, { action: "HIGHLIGHT_ACTION", payload: { actionData, highlight } });
        return true;
    }

    if (message.action === "GET_CURRENT_TAB_CONTEXT") {
         chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
             if (tabs.length === 0) {
                 sendResponse({ error: "No active tab" });
                 return;
             }
             chrome.tabs.sendMessage(tabs[0].id, { action: "GATHER_CONTEXT" }, (response) => {
                 sendResponse(response || { error: "No response from content script" });
             });
         });
         return true; // async response
    }
});
