let cachedContext = null;
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "cache_context") {
        cachedContext = request.payload;
        chrome.storage.local.set({ lastContext: cachedContext }, () => {});
        sendResponse({ status: "success" });
    } else if (request.action === "get_cached_context") {
        chrome.storage.local.get("lastContext", (result) => {
            sendResponse({ context: result.lastContext || cachedContext });
        });
        return true;
    }
    return true;
});
