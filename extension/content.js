// content.js

function identifyContext(url) {
    // 8. Live Casino DOM Block
    if (url.includes('casino') || url.includes('blackjack') || url.includes('bovada.lv')) {
        return 'blocked_casino';
    }
    if (url.includes('github.com')) return 'github';
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

function extractGitHub() {
    const prTitle = document.querySelector('.gh-header-title')?.innerText || "";
    const issueBody = document.querySelector('.comment-body')?.innerText || "";
    const codeDiffs = document.querySelectorAll('.diff-table');
    let diffSummary = "";
    if (codeDiffs.length > 0) {
        diffSummary = `[Contains ${codeDiffs.length} file diffs]`;
    }
    return `GitHub Context:\nTitle: ${prTitle}\nBody: ${issueBody.substring(0, 1000)}\nDiffs: ${diffSummary}`;
}

function extractGenericNews() {
    // Check for OpenGraph metadata for better context
    const ogTitle = document.querySelector('meta[property="og:title"]')?.content || document.title;
    const ogDesc = document.querySelector('meta[property="og:description"]')?.content || "";
    // 12. Meta Keyword Extraction
    const keywords = document.querySelector('meta[name="keywords"]')?.content || "";

    const article = document.querySelector('article');
    if (article) {
        return `News Title: ${ogTitle}\nDesc: ${ogDesc}\nKeywords: ${keywords}\nContent: ${article.innerText.substring(0, 1000)}`;
    }

    // 13. Main Content Heuristic
    const main = document.querySelector('main') || document.querySelector('[role="main"]');
    if (main) {
         return `Page: ${ogTitle}\nKeywords: ${keywords}\nMain Content: ${main.innerText.substring(0, 1000)}`;
    }
    return `Page: ${ogTitle}\nBody: ${document.body.innerText.substring(0, 800)}`;
}

// 9. Fast-Hash Diffing (DJB2)
function hashString(str) {
    let hash = 5381;
    for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) + hash) + str.charCodeAt(i);
    }
    return hash;
}

function extractTables() {
    // 8. Table Extraction
    const tables = document.querySelectorAll('table');
    let tableData = "";
    tables.forEach((t, i) => {
        if (i > 1) return; // Only top 2 tables
        const rows = Array.from(t.querySelectorAll('tr')).slice(0, 4); // Header + top 3 rows
        if (rows.length > 0) {
            tableData += `\nTable ${i+1}:\n`;
            rows.forEach(r => tableData += r.innerText.replace(/\n/g, ' | ') + "\n");
        }
    });
    return tableData;
}

function extractImages() {
    // 9. Image Alt Text Awareness
    const imgs = document.querySelectorAll('img[alt]');
    let imgData = "\nImages Context:\n";
    let count = 0;
    imgs.forEach(i => {
        if (i.alt.length > 5 && count < 5 && i.getBoundingClientRect().height > 10) {
            imgData += `- [IMG]: ${i.alt}\n`;
            count++;
        }
    });
    return count > 0 ? imgData : "";
}

function extractForms() {
    // Look for visible input fields that might need filling
    const inputs = document.querySelectorAll('input:not([type="hidden"]), textarea');
    let formHints = "\nVisible Inputs:\n";
    let extractedCount = 0;
    for (let input of inputs) {
        if (input.type === 'password') continue; // Skip passwords for security
        // 10. Hidden Element Filtering via Computed Style
        const style = window.getComputedStyle(input);
        if (style.display === 'none' || style.visibility === 'hidden') continue;

        if (input.getBoundingClientRect().height > 0 && extractedCount < 10) {
            formHints += `- ID: #${input.id || 'none'} | Name: ${input.name || 'none'} | Type: ${input.type}\n`;
            extractedCount++;
        }
    }
    return extractedCount > 0 ? formHints : "";
}

function extractPageContent() {
    const url = window.location.href;
    const contextType = identifyContext(url);
    let extractedData = "";

    if (contextType === 'blocked_casino') {
        extractedData = "Safety Boundary: Real-time casino DOM extraction is strictly prohibited. Please use the Offline Lab in the sidepanel for manual input strategy advice.";
    } else {
        switch (contextType) {
            case 'github': extractedData = extractGitHub(); break;
            case 'draftkings': extractedData = extractDraftKings(); break;
            case 'kalshi': extractedData = extractKalshi(); break;
            case 'amazon': extractedData = extractAmazon(); break;
            case 'ebay': extractedData = extractEbay(); break;
            case 'polymarket': extractedData = extractPolymarket(); break;
            case 'fanduel': extractedData = extractFanDuel(); break;
            default: extractedData = extractGenericNews(); break;
        }
        // Append extra modules
        extractedData += extractTables();
        extractedData += extractImages();
        extractedData += extractForms();
    }

    // 11 & 9. Fast-Hash Extraction Diffing
    const currentHash = hashString(extractedData);
    if (window._lastExtractedHash === currentHash) {
        return; // Abort sending if nothing changed
    }
    window._lastExtractedHash = currentHash;

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

// 11. RAF Debouncing
let rafTimer = null;
function requestFrameDebounce(func) {
    return (...args) => {
        if (rafTimer) cancelAnimationFrame(rafTimer);
        rafTimer = requestAnimationFrame(() => {
            setTimeout(() => { func.apply(this, args); }, 300); // Wait for paint to settle
        });
    };
}

const debouncedExtract = requestFrameDebounce(extractPageContent);

// Extract content when the page loads
debouncedExtract();

// Simple SPA listener (for sites like Kalshi/Polymarket)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    debouncedExtract();
  }
}).observe(document.body, {subtree: true, childList: true}); // Limit observe to body

// --- Action Execution Logic ---
let currentHighlight = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'REQUEST_DOM_EXTRACTION') {
        extractPageContent();
        sendResponse({status: "ok"});
    }

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
                // 12. Highlight Z-Index Guarantee
                currentHighlight.style.zIndex = '2147483647';
                currentHighlight.style.pointerEvents = 'none'; // Don't block clicks
                currentHighlight.style.boxShadow = '0 0 10px #ff9800';
                currentHighlight.style.transition = 'all 0.3s ease'; // Smooth visual transitions

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
                if (request.actionType === 'FILL' && request.fillValue) {
                    console.log(`Solomon filling ${request.selector} with ${request.fillValue}`);
                    // 13. Scroll-to-fill
                    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    // 14. Focus & Blur Simulation
                    el.focus();
                    el.value = request.fillValue;
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.blur();
                } else {
                    console.log("Solomon executes manual approved click on:", request.selector);
                    el.click();
                }
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