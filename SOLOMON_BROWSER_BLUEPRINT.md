# SOLOMON_BROWSER_BLUEPRINT

## Overview
The Solomon Browser Companion is a Chrome extension designed to act as Solomon's "eyes" on the web. It provides DOM access, allows Solomon to read webpages, and acts as a sophisticated assistant across various domains like prediction markets, sports betting, e-commerce, and news.

## Core Capabilities
- **Chrome Extension (Manifest V3):** The foundation of the companion, utilizing the latest web extension standards for performance and security.
- **DOM Access & Webpage Reading:** Safely extracts content from the active tab's DOM to provide context to Solomon.
- **Market Awareness:** Specifically tuned to read and understand data from:
  - DraftKings
  - Kalshi
  - FanDuel
  - Polymarket
- **E-Commerce Assistant:** Provides contextual assistance on:
  - Amazon
  - eBay
- **News Awareness:** Extracts and summarizes news articles.
- **Chat Side Panel:** A persistent side panel for users to interact with Solomon directly alongside their browsing experience.
- **Strict Manual Approval:** A hard safety constraint. Solomon cannot autonomously make purchases, place bets, or execute sensitive transactions. It can prepare the action, but manual user approval (a physical click) is strictly required.

## Architecture

### 1. `manifest.json`
- Manifest V3 standard.
- Permissions: `activeTab`, `scripting`, `sidePanel`, `storage`, `declarativeNetRequest` (if needed for API blocking/routing).
- Host permissions: `<all_urls>` (for broad webpage reading) or specific domains.

### 2. Service Worker (`background.js`)
- Handles background tasks.
- Manages communication between the content script and the side panel.
- Coordinates API calls to the Solomon backend (Flask server).

### 3. Content Script (`content.js`)
- Injected into specific pages or all pages based on permissions.
- Responsibilities:
  - Extracting text, tables, and relevant DOM elements.
  - Parsing specific market data (e.g., odds on Kalshi or DraftKings).
  - Highlighting or interacting with elements (only up to the point of a final transaction).

### 4. Side Panel (`sidepanel.html` & `sidepanel.js`)
- The primary UI for the user.
- Displays Solomon's analysis, context-aware suggestions, and chat interface.
- Implements strict safety boundaries using `textContent` and `escapeHtml` to prevent XSS.

## Security & Ethics Boundaries
- **No Automated Wagering/Purchasing:** The extension is strictly read-only or draft-only for financial actions. It cannot click "Buy" or "Place Bet".
- **Data Privacy:** DOM extraction is sent to the local Solomon backend.
- **Safe Rendering:** The side panel ensures that any HTML or text returned from the backend is properly sanitized before rendering.

## Next Steps
1. Initialize the extension skeleton (`manifest.json`, `background.js`, `content.js`, `sidepanel.html`, `sidepanel.js`).
2. Integrate the side panel chat with the local Flask server (`http://localhost:10000/chat`).
3. Implement site-specific content parsers (e.g., extracting odds from Kalshi).
