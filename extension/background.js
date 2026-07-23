// background.js

chrome.runtime.onInstalled.addListener(() => {
  console.log("Solomon Browser Companion installed.");
  // Setup side panel behavior
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionIconClick: true }).catch((error) => console.error(error));
});

// Mock memory store for audit logs
let auditLogs = [];

function logAction(actionType, details) {
  const entry = {
    timestamp: new Date().toISOString(),
    action: actionType,
    details: details
  };
  auditLogs.push(entry);
  console.log("Solomon Audit Logger:", entry);
}

// Listen for messages from the side panel or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'PONG') {
    sendResponse({ status: 'ok' });
  }

  if (request.type === 'EXTRACT_PAGE_DATA') {
    logAction('PAGE_READ', 'Requested DOM context extraction from active tab.');
    // Forward request to the active tab's content script
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length > 0 && tabs[0].id) {
        chrome.tabs.sendMessage(tabs[0].id, { type: 'GET_CONTENT' }, (response) => {
          logAction('PAGE_READ_SUCCESS', `Extracted DOM from ${tabs[0].url}`);
          sendResponse(response);
        });
      } else {
        sendResponse({ error: 'No active tab found.' });
      }
    });
    return true; // Keep the message channel open for async response
  }

  if (request.type === 'EXECUTE_ACTION') {
    logAction('CONTROLLED_ACTION', `Requested action: ${request.action}`);
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length > 0 && tabs[0].id) {
        chrome.tabs.sendMessage(tabs[0].id, request, (response) => {
          logAction('CONTROLLED_ACTION_SUCCESS', `Executed ${request.action} successfully.`);
          sendResponse(response);
        });
      } else {
        sendResponse({ error: 'No active tab found.' });
      }
    });
    return true;
  }

  if (request.type === 'EMERGENCY_STOP') {
    logAction('SYSTEM_HALT', 'EMERGENCY STOP requested. Purging transient state.');
    console.warn('SYSTEM-GUARD: EMERGENCY STOP received. Purging transient memory states.');
    // In a real integration, we would clear chrome.storage.session and drop WebSocket connections here.
    sendResponse({ status: 'halted' });
    return false; // synchronous response
  }

  if (request.type === 'GET_AUDIT_LOGS') {
    sendResponse({ logs: auditLogs });
    return false;
  }
});
