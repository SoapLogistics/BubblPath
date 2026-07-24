// background.js

chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch((error) => console.error(error));

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'EXTRACT_DOM') {
        // Forward DOM data from content script to sidepanel or handle it here
        console.log("Received DOM extraction data.");
        // This is where we might send it to the local Solomon backend,
        // or pass it to the sidepanel for it to handle.
        sendResponse({status: "success"});
    }
});