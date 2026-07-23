// content.js

// Safe extractor: We want visible text, but we avoid sensitive fields.
function safeExtractPageContent() {
  const title = document.title;
  const url = window.location.href;

  // Basic heuristic to avoid password fields or credit card inputs
  const sensitiveSelectors = 'input[type="password"], input[name*="cc"], input[name*="card"], input[name*="cvv"]';
  const sensitiveElements = document.querySelectorAll(sensitiveSelectors);
  if (sensitiveElements.length > 0) {
    console.warn("Solomon: Sensitive fields detected. Proceeding with caution.");
  }

  // Extract main visible text (simplified for prototype)
  // In a real implementation, this would use a more robust DOM traversal,
  // respecting the accessibility tree and visual bounding boxes.
  const mainText = document.body.innerText.substring(0, 5000); // Limit size for now

  return {
    title: title,
    url: url,
    contentPreview: mainText,
    hasSensitiveFields: sensitiveElements.length > 0
  };
}

// Phase 3: Preparer - Form Filling (Safe fields only)
function simulateFormFill(payload) {
  console.log("Solomon: Attempting to prepopulate form data...", payload);
  // Example of finding a safe input and filling it.
  // We strictly avoid interacting with financial submission buttons.

  const searchInput = document.querySelector('input[type="search"], input[name="q"]');
  if (searchInput && payload.searchTerm) {
    searchInput.value = payload.searchTerm;
    console.log("Solomon: Populated search term.");
  }

  // We NEVER query for or click buttons like "buy", "submit", "place order"
  return { status: "Form fields prepared. Waiting for Mark to submit." };
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'GET_CONTENT') {
    const data = safeExtractPageContent();
    sendResponse(data);
  } else if (request.type === 'PREPARE_FORM') {
    const result = simulateFormFill(request.payload);
    sendResponse(result);
  }
  return true;
});
