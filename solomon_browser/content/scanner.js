let scanTimeout = null;
let lastScanTime = 0;

export function debouncePageScan(callback, delay = 1000) {
    return function() {
        const now = Date.now();
        // Debounce page scans
        if (scanTimeout) {
            clearTimeout(scanTimeout);
        }

        scanTimeout = setTimeout(() => {
            const context = extractCompactContext();
            callback(context);
            lastScanTime = Date.now();
        }, delay);
    }
}

function extractCompactContext() {
    // Send compact page context, not full DOM
    return {
        url: window.location.href,
        title: document.title,
        mainHeading: document.querySelector('h1')?.innerText || '',
        snippet: document.body.innerText.substring(0, 200) + '...'
    };
}
