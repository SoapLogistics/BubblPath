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
    return `Product: ${title}\nPrice: ${price}`;
}

function extractEbay() {
    const title = document.querySelector('.x-item-title__mainTitle')?.innerText || "";
    const price = document.querySelector('.x-price-primary')?.innerText || "";
    return `eBay Item: ${title}\nPrice: ${price}`;
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