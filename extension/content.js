// content.js

function identifyContext(url) {
    if (url.includes('draftkings.com')) return 'draftkings';
    if (url.includes('kalshi.com')) return 'kalshi';
    if (url.includes('amazon.com')) return 'amazon';
    if (url.includes('ebay.com')) return 'ebay';
    if (url.includes('polymarket.com')) return 'polymarket';
    if (url.includes('fanduel.com')) return 'fanduel';
    return 'generic';
}

function extractDraftKings() {
    // DraftKings often uses specific classes for odds, e.g. .sportsbook-odds
    const oddsElements = document.querySelectorAll('.sportsbook-odds');
    let data = "DraftKings Lines:\n";
    oddsElements.forEach(el => data += el.innerText + "\n");
    return data || "Could not find specific odds elements.";
}

function extractKalshi() {
    // Kalshi uses complex React DOM, we'll try to find common price elements
    const priceElements = document.querySelectorAll('[class*="price"], [class*="Offer"]');
    let data = "Kalshi Prices:\n";
    priceElements.forEach(el => data += el.innerText + "\n");
    return data || "Could not find specific price elements.";
}

function extractAmazon() {
    const title = document.getElementById('productTitle')?.innerText || "";
    const price = document.querySelector('.a-price .a-offscreen')?.innerText || "";
    // Hint to the AI about what the "Add to Cart" button selector usually is on Amazon
    return `Product: ${title}\nPrice: ${price}\n(Hint: "Add to Cart" selector is usually #add-to-cart-button)`;
}

function extractEbay() {
    const title = document.querySelector('.x-item-title__mainTitle')?.innerText || "";
    const price = document.querySelector('.x-price-primary')?.innerText || "";
    // Hint for eBay "Buy It Now" or "Place Bid"
    return `eBay Item: ${title}\nPrice: ${price}\n(Hint: Buy button selector is usually [id^="binBtn_btn"])`;
}

function extractPolymarket() {
    const questions = document.querySelectorAll('[class*="Market"]');
    let data = "Polymarket Markets:\n";
    questions.forEach(el => data += el.innerText.substring(0, 50) + "...\n");
    return data || "Could not extract specific Polymarket data.";
}

function extractFanDuel() {
    const odds = document.querySelectorAll('[role="button"][aria-label*="odds"]');
    let data = "FanDuel Odds:\n";
    odds.forEach(el => data += el.getAttribute('aria-label') + "\n");
    return data || "Could not find specific FanDuel odds elements.";
}

function extractGenericNews() {
    const article = document.querySelector('article');
    if (article) {
        return `Article Content: ${article.innerText.substring(0, 1500)}`;
    }
    return `Page Body: ${document.body.innerText.substring(0, 1000)}`;
}

function extractPageContent() {
    const url = window.location.href;
    const contextType = identifyContext(url);
    let extractedData = "";

    switch (contextType) {
        case 'draftkings': extractedData = extractDraftKings(); break;
        case 'kalshi': extractedData = extractKalshi(); break;
        case 'amazon': extractedData = extractAmazon(); break;
        case 'ebay': extractedData = extractEbay(); break;
        case 'polymarket': extractedData = extractPolymarket(); break;
        case 'fanduel': extractedData = extractFanDuel(); break;
        default: extractedData = extractGenericNews(); break;
    }

    const payload = {
        type: contextType,
        url: url,
        title: document.title,
        data: extractedData
    };

    // Safely send the data to the background script
    chrome.runtime.sendMessage({
        type: 'EXTRACT_DOM',
        payload: payload
    });
}

// Extract content when the page loads, and perhaps on URL change for SPAs
extractPageContent();

// Simple SPA listener (for sites like Kalshi/Polymarket)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    setTimeout(extractPageContent, 2000); // Wait for render
  }
}).observe(document, {subtree: true, childList: true});

// --- Action Execution Logic ---
let currentHighlight = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'HIGHLIGHT_ELEMENT') {
        clearHighlight();
        try {
            const el = document.querySelector(request.selector);
            if (el) {
                // Apply a prominent visual highlight
                currentHighlight = document.createElement('div');
                currentHighlight.id = 'solomon-action-highlight';
                currentHighlight.style.position = 'absolute';
                currentHighlight.style.border = '4px solid #ff9800';
                currentHighlight.style.backgroundColor = 'rgba(255, 152, 0, 0.2)';
                currentHighlight.style.zIndex = '999999';
                currentHighlight.style.pointerEvents = 'none'; // Don't block clicks
                currentHighlight.style.boxShadow = '0 0 10px #ff9800';

                const rect = el.getBoundingClientRect();
                currentHighlight.style.top = (rect.top + window.scrollY - 5) + 'px';
                currentHighlight.style.left = (rect.left + window.scrollX - 5) + 'px';
                currentHighlight.style.width = (rect.width + 10) + 'px';
                currentHighlight.style.height = (rect.height + 10) + 'px';

                document.body.appendChild(currentHighlight);

                // Scroll element into view smoothly
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } catch (e) {
            console.error("Invalid selector or element not found:", request.selector);
        }
    }

    if (request.type === 'CLEAR_HIGHLIGHT') {
        clearHighlight();
    }

    if (request.type === 'EXECUTE_ACTION') {
        clearHighlight();
        try {
            const el = document.querySelector(request.selector);
            if (el) {
                console.log("Solomon executes manual approved click on:", request.selector);
                el.click();
            }
        } catch (e) {
            console.error("Failed to execute action on:", request.selector);
        }
    }
});

function clearHighlight() {
    if (currentHighlight && currentHighlight.parentNode) {
        currentHighlight.parentNode.removeChild(currentHighlight);
    }
    currentHighlight = null;
}