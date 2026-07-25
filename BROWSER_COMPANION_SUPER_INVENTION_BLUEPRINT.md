# Browser Companion: Super Invention Blueprint

This blueprint outlines the strategy to evolve the Solomon Browser Companion from a passive observer into an active, multi-modal interface seamlessly bridging live web applications (GitHub, Amazon, Sportsbooks) with the core OS v2.0 engines (Loki, Hephaestus, Mnemosyne, Gabriel).

## Phase 1: Deep Semantic Adapters & High-Volume Data Streaming (The "Living DOM" Strategy)
Standard DOM scraping breaks easily. Super Invention adapters will use a combination of semantic heuristics, CSS Grid inference, and `MutationObserver` telemetry to quietly extract high-volume data streams (90+ bets simultaneously).

1. **GitHub Deep-Context (Project Nexus)**
   - **Goal:** Extract not just titles, but PR diffs, build status (`.branch-action-item`), commit chains, and merge conflict markers.
   - **Mechanism:** Intercept GitHub's PJAX/Turbo page loads to maintain state. Map code diffs directly into the Hephaestus context window for auto-suggested PR reviews.

2. **Amazon E-Commerce Brain (Arbitrage & Supply)**
   - **Goal:** Track historical price points, hidden BuyBox data, shipping latency, and review sentiment.
   - **Mechanism:** Identify structured JSON-LD or schema.org microdata embedded in the DOM. Cross-reference this with Loki's macroeconomic tracking to detect supply chain inflation in real-time.

3. **DraftKings, FanDuel, Kalshi, Polymarket (Mass Volume Real-Time Grids)**
   - **Goal:** Stream live, fluctuating odds grids (up to 100+ bets per page) directly into the Loki Predictive Engine.
   - **Mechanism:** Because odds are heavily obfuscated and load via WebSockets/React, the adapters use regex heuristics (matching `+150`, `-110`, `45¢`) and grab preceding text nodes to deduce market context (e.g. "Kansas City Chiefs"). A passive, stealth `MutationObserver` detects micro-changes and streams these arrays to Loki without user interaction.

## Phase 2: Engine Integration (The "God-Mode" Side Panel)
The Side Panel will evolve into a multi-tabbed command center, breaking out of just "Chat".

1. **Loki Predictive Tab**
   - **UI:** Render real-time Probability Density Functions (PDF) and Kelly Criterion gauges.
   - **Action:** When on a Kalshi or DraftKings tab, the UI automatically polls `/api/loki/predict` with the extracted order book imbalance, rendering an immediate "Bet / Hold" recommendation.

2. **Hephaestus App Forge Tab**
   - **UI:** A mini-IDE view.
   - **Action:** When on GitHub or StackOverflow, Hephaestus pulls the semantic code context and offers 1-click AST injections or architectural scaffolds (`/api/hephaestus/scaffold`) directly through the browser.

## Phase 3: Stealth Tech & Headless Chromium Simulation
Browser extensions are notoriously hard to test, and scraping hostile domains requires extreme care.

1. **Stealth Tech (Shadow DOMs & Debouncing):** Visual UI elements injected into hostile domains (like sportsbooks) are wrapped inside `attachShadow({ mode: 'closed' })` to blind standard `querySelectorAll` anti-cheat sweeps. Observers are aggressively debounced.
2. **Persistent Context Loading:** Playwright will launch Chromium with the `--disable-extensions-except` and `--load-extension` flags pointing to our `build/` directory for automated CI testing.

## What You Are In For (The Reality Check)
By pushing this to "Super Invention Land", we are embracing immense technical complexity:

* **The DOM is Hostile:** Amazon, DraftKings, and FanDuel actively obfuscate their DOM to prevent scraping. Selectors will change weekly. Our adapters must rely on heuristics (e.g., "find the nearest number formatting to odds like +150") rather than hardcoded classes.
* **Extension Testing Hell:** Playwright testing of MV3 Service Workers is brittle. You will face race conditions where the Service Worker sleeps mid-test.
* **Bandwidth & Latency:** Streaming 100+ live sportsbook odds via `MutationObserver` to a Flask API every 500ms will stress rate-limiters. We must implement delta-compression on the extension side in the future.

Embracing this means shifting from a static codebase to an actively managed, continuously healing ecosystem.
