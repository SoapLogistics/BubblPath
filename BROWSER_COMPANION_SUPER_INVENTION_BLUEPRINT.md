# Browser Companion: Super Invention Blueprint

This blueprint outlines the strategy to evolve the Solomon Browser Companion from a passive observer into an active, multi-modal interface seamlessly bridging live web applications (GitHub, Amazon, Sportsbooks) with the core OS v2.0 engines (Loki, Hephaestus, Mnemosyne, Gabriel).

## Phase 1: Deep Semantic Adapters (The "Living DOM" Strategy)
Standard DOM scraping breaks easily. Super Invention adapters will use a combination of semantic heuristics, CSS Grid inference, and `MutationObserver` telemetry.

1. **GitHub Deep-Context (Project Nexus)**
   - **Goal:** Extract not just titles, but PR diffs, build status (`.branch-action-item`), commit chains, and merge conflict markers.
   - **Mechanism:** Intercept GitHub's PJAX/Turbo page loads to maintain state. Map code diffs directly into the Hephaestus context window for auto-suggested PR reviews.

2. **Amazon E-Commerce Brain (Arbitrage & Supply)**
   - **Goal:** Track historical price points, hidden BuyBox data, shipping latency, and review sentiment.
   - **Mechanism:** Identify structured JSON-LD or schema.org microdata embedded in the DOM. Cross-reference this with Loki's macroeconomic tracking to detect supply chain inflation in real-time.

3. **DraftKings & FanDuel (Real-Time Sportsbook Grids)**
   - **Goal:** Stream live, fluctuating odds grids directly into the Loki Predictive Engine.
   - **Mechanism:** Because odds are heavily obfuscated and load via WebSockets/React, the adapters will inject a `MutationObserver` on the `.sportsbook-event-accordion` (or equivalent) nodes. It will detect micro-changes (green/red flashes) and stream these deltas to Loki to detect sharp money movement.

## Phase 2: Engine Integration (The "God-Mode" Side Panel)
The Side Panel will evolve into a multi-tabbed command center, breaking out of just "Chat".

1. **Loki Predictive Tab**
   - **UI:** Render real-time Probability Density Functions (PDF) and Kelly Criterion gauges.
   - **Action:** When on a Kalshi or DraftKings tab, the UI automatically polls `/api/loki/predict` with the extracted order book imbalance, rendering an immediate "Bet / Hold" recommendation.

2. **Hephaestus App Forge Tab**
   - **UI:** A mini-IDE view.
   - **Action:** When on GitHub or StackOverflow, Hephaestus pulls the semantic code context and offers 1-click AST injections or architectural scaffolds (`/api/hephaestus/scaffold`) directly through the browser.

## Phase 3: Headless Chromium Simulation (Playwright Automation)
Browser extensions are notoriously hard to test because they exist outside normal web context. We will build a fortified CI/CD pipeline using Playwright.

1. **Persistent Context Loading:** Playwright will launch Chromium with the `--disable-extensions-except` and `--load-extension` flags pointing to our `build/` directory.
2. **Service Worker Introspection:** The test suite will hook into the background Service Worker to mock Mnemosyne API calls, ensuring passive learning alarms fire correctly.
3. **Side Panel UI Manipulation:** We will navigate to the `chrome-extension://[ID]/sidepanel.html` URI directly within the test to assert that the Casino Lab calculates Kelly Criterion correctly and that the Action Queue renders `[ACTION]` tags properly.

## What You Are In For (The Reality Check)
By pushing this to "Super Invention Land", we are embracing immense technical complexity:

* **The DOM is Hostile:** Amazon, DraftKings, and FanDuel actively obfuscate their DOM to prevent scraping. Selectors will change weekly. Our adapters must rely on heuristics (e.g., "find the nearest number formatting to odds like +150") rather than hardcoded classes.
* **Extension Testing Hell:** Playwright testing of MV3 Service Workers is brittle. You will face race conditions where the Service Worker sleeps mid-test.
* **Bandwidth & Latency:** Streaming live sportsbook odds via `MutationObserver` to a Flask API every 500ms will stress the rate-limiters. We must implement debouncing and delta-compression on the extension side.

Embracing this means shifting from a static codebase to an actively managed, continuously healing ecosystem.
