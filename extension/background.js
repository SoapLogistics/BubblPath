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

  if (request.type === 'EXTRACT_VISUAL_DATA') {
    logAction('VISUAL_DATA', 'Requested visual DOM context from active tab.');
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length > 0 && tabs[0].id) {
        chrome.tabs.sendMessage(tabs[0].id, { type: 'EXTRACT_VISUAL_DATA' }, (response) => {
          logAction('VISUAL_DATA_SUCCESS', `Extracted visual elements from ${tabs[0].url}`);
          sendResponse(response);
        });
      } else {
        sendResponse({ error: 'No active tab found.' });
      }
    });
    return true;
  }

  if (request.type === 'PREPARE_FORM') {
    logAction('PREPARE_FORM', 'Requested safe form preparation.');
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (tabs.length > 0 && tabs[0].id) {
        chrome.tabs.sendMessage(tabs[0].id, request, (response) => {
          logAction('PREPARE_FORM_SUCCESS', `Safely prepared form on ${tabs[0].url}`);
          sendResponse(response);
        });
      } else {
        sendResponse({ error: 'No active tab found.' });
      }
    });
    return true;
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

  if (request.type === 'GET_ALL_TABS_DATA') {
    logAction('CROSS_TAB_SYNC', 'Requested metadata for all open tabs in current window.');
    chrome.tabs.query({ currentWindow: true }, (tabs) => {
      // In a real implementation, we would send a message to each tab's content script to grab the DOM payload.
      // For this mock phase, we just count the tabs and return success.
      sendResponse({ tabCount: tabs.length, status: 'success' });
    });
    return true;
  }
});
