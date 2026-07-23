# SOLOMON BROWSER: GRAND EXTENSION BLUEPRINT

## 1. Vision & Architecture

Solomon Browser is an omnipresent, human-guided, Chrome-based intelligent companion. It bridges the gap between passive web browsing and active, AI-assisted research and preparation, particularly focusing on prediction markets (Kalshi), safe betting analysis, and deep integration with Jules-assisted developer tools.

### The Immutable Boundary
**Solomon may investigate, calculate, compare, prepare, and advise. The User (Mark) performs the final irreversible action.**
Solomon *never* autonomously clicks "Submit Wager", "Place Order", or "Buy".

---

## 2. Kalshi: The Core Prediction Engine

Kalshi is the pivotal API for Solomon’s forecasting capabilities. Because Kalshi offers official, structured APIs, Solomon will use it as the primary sensor for world events and probability calibration.

### 2.1 Kalshi API Integration Layers
* **Public Market Data (No Auth):** Continuous monitoring of event probabilities, order book depth, and historical pricing.
* **Authenticated Trading Data:** (If authorized by the user) Monitoring of active positions and account balance.
* **Order Preparation (No Execution):** Solomon can build complete JSON payloads for limit or market orders, but the final `POST /trade` request is triggered *strictly* by a user action in the browser extension UI.

### 2.2 Kalshi Intelligence Loop
1. **Event Detection:** Solomon scans news articles in the active tab.
2. **Market Mapping:** Solomon automatically queries the Kalshi API for markets related to the news.
3. **Probability Divergence Analysis:** Compares the news sentiment against Kalshi's implied probability.
4. **Action Proposal:** "Mark, Kalshi prices this event at 45%. Based on this breaking news, I estimate 60%. I have prepared a limit order for 50 contracts at 48¢. Please review and click 'Submit' if you agree."

---

## 3. Sports & Casino Analytics (Safe Interaction)

Solomon interacts with sportsbooks and casinos purely as an external analytical engine, strictly avoiding bot-detection triggers or automated gameplay.

### 3.1 Sportsbook Companion (DraftKings, FanDuel, etc.)
* **No DOM Scraping:** Solomon does not scrape hidden sportsbook data.
* **Manual Input / Permitted APIs:** The user inputs the line (e.g., "Eagles -3.5 at -110") or Solomon fetches consensus lines from permitted third-party odds APIs.
* **Deep Research:** Solomon cross-references weather, injury reports, and the Loki Engine's Shin Probability calculations.
* **Output:** Expected Value (EV), Kelly Criterion stake recommendations, and confidence intervals.

### 3.2 Blackjack Laboratory & Training
* **No Live Casino Assistance:** Solomon will not analyze live, real-money blackjack hands in real-time (to comply with casino ToS and avoid software-assistance bans).
* **Training Mode:** A dedicated UI tab where Solomon simulates a shoe, drills the user on Hi-Lo running/true counts, and flags deviations from basic strategy.

---

## 4. Jules Integration (The Engineering Loop)

The Solomon Browser extension serves as the UI for interacting with Jules (the AI engineering agent) and the local Solomon server.

### 4.1 Jules Workspace Interaction
* **Context Awareness:** When Mark is viewing a GitHub PR, a Render deployment log, or the local Jules web workspace, the extension is aware of the context.
* **One-Click Sandbox Execution:** The extension allows Mark to highlight code on a web page and send it directly to the local Jules Docker sandbox for isolated execution.
* **System Telemetry Panel:** A tab in the extension that continuously polls the local `app.py` `/health` and `/metrics` endpoints, displaying RAM usage and worker modes (Gabriel, Mnemosyne, Loki).

---

## 5. Implementation Roadmap

### Phase 1: The Observer (Read-Only)
* Build the Manifest V3 side panel.
* Implement safe DOM extraction (excluding passwords/CVVs).
* Build the Kalshi public API viewer.

### Phase 2: The Researcher
* Integrate the Kalshi API for probability divergence analysis against news articles.
* Add manual sports odds input for Loki Engine analysis.
* Build the Blackjack basic strategy quizzer.

### Phase 3: The Preparer (Human-in-the-Loop)
* Implement form-filling capabilities.
* Allow Solomon to construct (but not submit) Kalshi trade payloads.
* Integrate with the local Jules workspace for seamless code pushing/testing.

### Phase 4: Full Deployment
* Extensive testing of the "Financial Hard Stop" mechanism (ensuring DENIED_ACTIONS like `purchase.confirm` are blocked at the lowest script level).
* Rollout to SS1 (Production) with all authorized APIs fully mapped.