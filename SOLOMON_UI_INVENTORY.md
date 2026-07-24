# Solomon UI Inventory & Screen Catalog

This document serves as the master catalog for all user interfaces (screens, dashboards, and panels) developed across the Solomon Intelligence ecosystem.

---

## 1. Solomon Browser Companion (Chrome Extension Side Panel)
**Location:** `extension/sidepanel.html`
**Purpose:** Acts as the AI's "eyes" alongside the user, providing contextual chat, manual action approvals, and offline tools without leaving the browser tab.

### Wireframe "Picture"
```text
+-------------------------------------------------+
| Solomon                               [📋] [🗑️] [🛑] |
+-------------------------------------------------+
| [ TAB: Chat ]  [ TAB: Offline Lab ]             |
+-------------------------------------------------+
| 👀 Context: GITHUB (Pulsing)                    |
|                                                 |
|  [ User: How do I fix this PR? ]                |
|                                                 |
|  [ Solomon: I recommend updating the loop... ]  |
|                                                 |
| +---------------------------------------------+ |
| | ⚠️ Manual Approval Required                 | |
| | Target: #merge-button                       | |
| | [ APPROVE ]  [ CANCEL ]                     | |
| +---------------------------------------------+ |
|                                                 |
| +---------------------------------------------+ |
| | 🤖 Jules API Observer ( [x] Dismiss )       | |
| | Task: SJ-1705-A4B2                          | |
| | Status: awaiting_human_approval             | |
| | [ Approve Merge to SS1 ]                    | |
| +---------------------------------------------+ |
+-------------------------------------------------+
| [ Ask Solomon... (Shift+Enter for newline)  ]   |
| [ SEND ]                                        |
+-------------------------------------------------+
```

### What's on this screen:
*   **Header Bar:** Title alongside Quick Tools (`📋 Copy Context`, `🗑️ Clear Chat`, `🛑 Global HALT` kill-switch).
*   **Navigation Tabs:** Switches between the Context Chat and the Offline Casino Lab.
*   **Context Banner:** A color-coded banner (Green=Generic, Orange=Betting, Red=Blocked) showing what domain the agent is currently extracting.
*   **Chat Container:** Persistent chat history with markdown support (bold/code) and fading timestamps.
*   **Pending Action Modal:** A strict safety gate that intercepts `[ACTION]` or `[FILL]` tags from the AI, demanding a physical click before executing DOM actions in the main window.
*   **Jules API Observer:** A telemetry widget tracking background Jules tasks (SS2 worker), exposing the final SS3 promotion button.
*   **Input Box:** An auto-resizing `<textarea>` supporting Shift+Enter.

---

## 2. Offline Blackjack Strategy Lab (Extension Tab 2)
**Location:** `extension/sidepanel.html` (Tabbed View)
**Purpose:** A safe, manual-input environment providing mathematical Basic Strategy and Hi-Lo counting advice without illegally scraping live casino DOMs.

### Wireframe "Picture"
```text
+-------------------------------------------------+
| [ TAB: Chat ]  [ TAB: Offline Lab ]             |
+-------------------------------------------------+
| Offline Blackjack Advisor                       |
| Manual input only. Real-time extraction blocked.|
|                                                 |
| [ Quick Input Memory ]                          |
| Card: [ 10      ] [ Reset ]                     |
| Count: +2 | True: +0.4 | Cards: 308             |
| History: ["A", "5", "K", "10"]                  |
|                                                 |
| Player Cards:                                   |
| [ 10, 8                                       ] |
|                                                 |
| Dealer Upcard:                                  |
| [ 6                                           ] |
|                                                 |
| [ GET ADVICE ]                                  |
|                                                 |
| +---------------------------------------------+ |
| | Action: STAND (Color coded Red)             | |
| | Reason: Hard 17+ always stands.             | |
| | Hand Total: 18                              | |
| | ------------------------------------------- | |
| | Neutral (True Count: +0.4)                  | |
| +---------------------------------------------+ |
+-------------------------------------------------+
```

### What's on this screen:
*   **Quick Input Memory:** A rapid text input field where hitting 'Enter' instantly logs a card into the backend state memory.
*   **Live Stats:** Auto-updating text showing Running Count, True Count (based on remaining decks), and a sliding history array.
*   **Strategy Inputs:** Fields for the Player's current hand and the Dealer's upcard.
*   **Result Box:** A dynamically colored output box (Green=Double, Blue=Hit, Red=Stand) displaying the mathematical move and reasoning.

---

## 3. Solomon Core Workspace & Loki Dashboard
**Location:** `templates/solomon_loki_workspace.html` (Accessible via `/` or `/workspace` on the Flask Gateway) *(Note: Documented from systemic memory architecture)*
**Purpose:** The central OS dashboard for the Solomon intelligence, heavily geared toward managing the Project Loki sports betting engine and memory metrics.

### Wireframe "Picture"
```text
+-----------------------------------------------------------------+
|  SOLOMON INTELLIGENCE OS                             [⚙️ Settings] |
+-----------------------------------------------------------------+
|  [ VRAM Budget: 1.2GB / 1.5GB ] [ Active Workers: 3 ]           |
+-----------------------------------------------------------------+
|                                                                 |
|  [ LOKI SPORTS INTELLIGENCE ]                                   |
|  Bankroll: $10,450.00 (+4.5% ROI)                               |
|                                                                 |
|  +--------------------+  +--------------------+                 |
|  | PENDING BETS (CTI) |  | RECENT PERFORMANCE |                 |
|  | NFL: KC vs BUF     |  | Last 10: 7W - 3L   |                 |
|  | Pick: KC -3.5      |  | Edge: +2.4%        |                 |
|  | Kelly Stake: $112  |  | [ View Archive ]   |                 |
|  | [ SIMULATE TICK ]  |  +--------------------+                 |
|  +--------------------+                                         |
|                                                                 |
|  [ MNEMOSYNE MEMORY MATRIX ]                                    |
|  +----------------------------------------------------------+   |
|  | [Search SOK Cards...] [🔍]                                |   |
|  | Node 1242: "Poisson Distribution for NFL..."             |   |
|  | Node 1243: "Kelly Criterion modifiers..."                |   |
|  | [ BLEND SYNAPSE ] [ VIEW GRAPH ]                         |   |
|  +----------------------------------------------------------+   |
+-----------------------------------------------------------------+
```

### What's on this screen:
*   **System Telemetry:** Real-time VRAM/RAM utilization bars showing the Dynamic Context Budgeter's ceiling.
*   **Loki Bankroll:** Live tracking of simulated USD funds and ROI.
*   **Pending Bets & Execution:** Active wagers generated by Loki (Margin Proportional to Odds). Includes buttons to manually resolve/simulate ticks.
*   **Performance Metrics:** ML feature tracking, Kelly edge percentages, and historical drawdown states.
*   **Mnemosyne Graph:** Search interface for retrieving System of Knowledge (SOK) cards. Allows triggering Phase 14 Neural Synapse blending.

---

## 4. Hephaestus App Forge
**Location:** `/hephaestus` (Flask Route) *(Note: Documented from systemic memory architecture)*
**Purpose:** A dedicated workspace for scaffolding cross-platform applications and compiling autonomous agent code into structured repos.

### Wireframe "Picture"
```text
+-----------------------------------------------------------------+
|  HEPHAESTUS FORGE: App Scaffolding Engine                       |
+-----------------------------------------------------------------+
|                                                                 |
| Target Platform: [ Android / iOS / Web / Linux ]                |
| App Name: [ e.g. "Solomon Mobile" ]                             |
|                                                                 |
| Framework: (x) React Native   ( ) Flutter   ( ) Native          |
|                                                                 |
| [ GENERATE SCAFFOLDING ]                                        |
|                                                                 |
| +----------------------------------------------------------+    |
| | TERMINAL OUTPUT                                          |    |
| | > Initializing React Native...                           |    |
| | > Writing App.js...                                      |    |
| | > Assembling routing parameters...                       |    |
| | > Success. Ready for compilation.                        |    |
| +----------------------------------------------------------+    |
+-----------------------------------------------------------------+
```

### What's on this screen:
*   **Configuration Selectors:** Dropdowns and radio buttons to choose target environments and frameworks.
*   **Action Buttons:** Triggers for `/api/hephaestus/scaffold` and `/api/hephaestus/compile`.
*   **Terminal Output Window:** A live-streaming black box showing the build process, AST checks, and code generation steps.