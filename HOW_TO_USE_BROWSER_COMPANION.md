# How To Use The Solomon Browser Companion

The Solomon Browser Companion acts as the unified frontend bridging your web browser with the powerful Solomon OS v2.0 ecosystem. It features advanced context extraction, passive memory syncing, and explicitly-authorized DOM manipulation.

## Installation

Because this is an advanced developer tool, it is not yet on the Chrome Web Store. You must load it "Unpacked".

1. **Build the Extension:**
   Open your terminal in the root of the repository and run:
   ```bash
   ./build_extension.sh
   ```
   *This packages the extension into `solomon_browser_companion.zip` and creates a clean `build/` directory.*

2. **Load into Chrome or Edge:**
   - Open your browser and navigate to `chrome://extensions/` (or `edge://extensions/`).
   - In the top right, turn on **Developer Mode**.
   - Click the **"Load unpacked"** button in the top left.
   - Select the `browser_extension` directory located inside your repository.

3. **Configuration (Important!):**
   - Once installed, right-click the Solomon Companion icon in your browser toolbar and click **Options**.
   - You must enter the **Backend URL** (usually `http://localhost:10000`) and your **Authorization Key** (matching the `SOLOMON_INTERNAL_AUTH_KEY` environment variable running on your server).
   - Click **Test Connection** to ensure the extension can talk to the backend.

## Opening the Companion

- **Chrome / Edge:** Click the Solomon icon in your toolbar. The companion will slide out gracefully into the browser's native **Side Panel**.
- **Firefox:** Click the icon to open the native **Sidebar**.

## Using The Tabs

### 1. The Companion Tab
This is your general AI chat. Solomon will observe the context of the page you are on. If you ask it to perform an action (like "Click the submit button"), it will queue an action card.
*Hover over the card to see the target element pulse in red on the webpage.* Click **Approve** to execute it.

### 2. The Loki Predictive Engine Tab
When navigating to Kalshi, Polymarket, DraftKings, or FanDuel, the extension utilizes "Stealth Tech" (Closed Shadow DOMs and debounced Mutation Observers) to silently scrape odds and order book imbalances.
*Click **Request Market Prediction** to ask the backend Loki engine if there is an actionable mathematical edge.*

### 3. The App Forge Tab
When browsing GitHub PRs or StackOverflow code blocks, you can seamlessly open the Hephaestus App Forge tab and command it to scaffold new project architectures or inject AST code fixes based on the page context.

### 4. The Casino Lab Tab
A local, offline Blackjack tracker. Use the buttons to log cards as they are dealt. The system calculates the Running Count, True Count (based on 6 decks), and uses the **Kelly Criterion** to calculate exact bet sizing based on your configured bankroll and shifting mathematical edge.

## Teaching Solomon (Context Menu)
At any time, on any webpage, you can highlight a block of text, right-click, and select **"Teach Solomon (SPLE)"**. The extension will automatically traverse the DOM to find contextual headers or code blocks surrounding your highlight, and instantly push that memory to the Solomon Perpetual Learning Engine.
