// content.js

function extractPageContent() {
    // Basic extraction
    const title = document.title;
    const bodyText = document.body.innerText;

    // Safely send the data to the background script or sidepanel
    chrome.runtime.sendMessage({
        type: 'EXTRACT_DOM',
        data: {
            title: title,
            // Truncate if necessary to avoid massive payloads
            content: bodyText.substring(0, 5000),
            url: window.location.href
        }
    });
}

// Extract content when the page loads
extractPageContent();