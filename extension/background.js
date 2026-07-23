// background.js

chrome.runtime.onInstalled.addListener(() => {
  console.log("Solomon Browser Companion installed.");
  // Setup side panel behavior
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionIconClick: true }).catch((error) => console.error(error));
});

// Listen for messages from the side panel or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'PONG') {
    sendResponse({ status: 'ok' });
  }

  if (request.type === 'EXTRACT_PAGE_DATA') {
    // Forward request to the active tab's content script
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length > 0 && tabs[0].id) {
        chrome.tabs.sendMessage(tabs[0].id, { type: 'GET_CONTENT' }, (response) => {
          sendResponse(response);
        });
      } else {
        sendResponse({ error: 'No active tab found.' });
      }
    });
    return true; // Keep the message channel open for async response
  }
});
