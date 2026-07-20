# Project Loki: Solomon's Advanced Sports Betting & Analytical Intel Engine
## Architectural Blueprint & System Specifications

---

## 1. Executive Summary & System Mandate

Project Loki is designed to be the ultimate sports betting and player-prop research tool, built directly as an evolutionary capability of the **Solomon SOK (Solomon Operating Knowledge) ecosystem**. By assimilating and synthesizing the core methodologies of the five market-leading products reviewed in 2026 (PropsBot, Rithmm, PlayerProps.ai, RotoBot AI, and PropGPT), Loki merges deep data analytics, customizable modeling, conversational intelligence, and robust mathematics into a single unified workspace.

Loki does not simply act as a chatbot; it operates as an **Active Inference Agent**. Following Solomon's continuous learning loop, Loki observes real-time markets, understands systemic edge, builds and tests custom prediction models, remembers historical outcomes, and continuously improves its strategies.

---

## 2. Deconstruction of Competitor DNA

To construct the ultimate betting workspace, we deconstruct the core mechanics and "scavenge" the capabilities of the five best-in-class tools:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PROJECT LOKI                                         │
│                      (The Ultimate Synthesized Workspace)                              │
├───────────────────┬───────────────────┬───────────────────┬───────────────────┬────────┴──────────┐
│     PROPSBOT      │      RITHMM       │  PLAYERPROPS.AI   │    ROTOBOT AI     │     PROPGPT       │
│   (Ensemble EV    │  (Custom Factor   │ (BetScore & Trend │  (Conversational  │  (App-First Quick │
│    & Shopping)    │    Weighting)     │  Visualizations)  │    RAG & Sync)    │     Grading)      │
└───────────────────┴───────────────────┴───────────────────┴───────────────────┴───────────────────┘
```

### 2.1. PropsBot (Best Overall EV & Multi-Sport Ingestion)
*   **Abilities Ingested:** High-confidence player-prop boards, multi-sportsbook odds shopping, DFS optimizer workflows, and multi-model ensemble consensus.
*   **Core Math:**
    *   **Confidence Score:** Measures the convergence of divergent model architectures.
    *   **Edge Score:** Discrepancy between implied probability (price) and calculated probability.

### 2.2. Rithmm (Custom Modeling & Sandbox Backtesting)
*   **Abilities Ingested:** Customizable, user-adjusted factor weights (e.g., pace, defense-adjusted splits, rest/fatigue indices), personal model tracking, and backtesting simulations.
*   **Core Math:** Multivariable linear/logistic regressions and random forest models where input features are dynamically scaled by user weights.

### 2.3. PlayerProps.ai (Beginner Trends & Visual Context)
*   **Abilities Ingested:** 1-100 BetScore indexing, visual rolling hit rates (last 5, 10, 20 games), line movement velocity trackers, and sentiment gauges of public vs. sharp money.
*   **Core Math:** Rolling statistical means, standard deviations, and Z-scores of historical hit frequencies.

### 2.4. RotoBot AI (Conversational Intelligence & League Sync)
*   **Abilities Ingested:** Interactive natural language queries, structured reasoning cards, parlay building, and native fantasy league synchronization (Yahoo, Sleeper, ESPN) to contextualize advice.
*   **Core Math:** Conversational RAG pipelines extracting specific player embeddings and matching them against active database projections.

### 2.5. PropGPT (Fast App-First Grading & Feed Freshness)
*   **Abilities Ingested:** Fast, intuitive letter grades (A+ down to F) with concise, bulletproof reasoning justifications.
*   **Core Math:** Grade thresholding derived from continuous probability-distribution density functions.

---

## 3. Project Loki Unified System Architecture

Project Loki integrates with Solomon as a modular suite under the Capability Growth Layer (Project Prometheus) and the active Knowledge Card Engine.

```
                  ┌─────────────────────────────────────────┐
                  │          Real-Time Data Ingestion       │
                  │   (Sportsbook Odds, Box Scores, News)   │
                  └────────────────────┬────────────────────┘
                                       │
                                       ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            LOKI DATA PIPELINE                                │
├──────────────────────────────┬──────────────────────────────┬────────────────┤
│       Mathematical           │       Ensemble Machine       │     Fantasy    │
│    Calculators Engine        │       Learning Core          │    League Sync │
│  (Shin/Power/Kelly/EV)       │    (Custom Weights)          │  (Yahoo/Sleeper)│
└──────────────┬───────────────┴──────────────┬───────────────┴────────┬───────┘
               │                              │                        │
               ▼                              ▼                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            LOKI REASONING PANEL                              │
├──────────────────────────────┬──────────────────────────────┬────────────────┤
│      BetScore Generator      │      PropGPT Grade Mapper    │ RotoBot RAG &  │
│         (1 - 100)            │          (A+ - F)            │  Answer Cards  │
└──────────────┬───────────────┴──────────────┬───────────────┴────────┬───────┘
               │                              │                        │
               ▼                              ▼                        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            SOLOMON INTEGRATION GATEWAY                       │
├──────────────────────────────────────────────────────────────────────────────┤
│  • Automated AST Injector: Programmatically deploys dynamic ML features      │
│  • Recursive Optimizer: Continuously optimizes model parameters              │
│  • SOSS Card Promotion Engine: Saves profitable insights as SOK Knowledge   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Mathematical & Algorithmic Blueprint

The mathematical foundation ensures Loki's predictions are calibrated and profitable. No black-box projections; every prediction includes exact derivation and proof.

### 4.1. Implied Probability & Vig-Removal Models
Bookmaker lines contain an overround ("vig" or "juice"). To discover the true probability of an outcome, we must remove the vig. Loki incorporates three distinct methods:

#### A. Multiplicative Method (Standard Normalization)
$$p_i = \frac{\pi_i}{\sum_{j} \pi_j}$$
Where $\pi_i$ is the implied probability of outcome $i$ directly from the bookmaker's decimal odds ($1 / \text{odds}$).

#### B. Power Method (Favorite-Longshot Bias Compensation)
Acknowledges that bookmakers load disproportionate overround onto longshots:
$$\pi_i = p_i^k$$
where $k < 1$ is solved iteratively via Newton-Raphson such that:
$$\sum_{i} \pi_i^{1/k} = 1$$

#### C. Shin's Method (Informed Bettor Model)
Shin assumes the market consists of a fraction $z$ of informed bettors (insiders) and $1-z$ of uninformed noise traders.
$$\pi_i = (1-z)p_i + z\sqrt{p_i}$$
We solve for $z$ and the true probabilities $p_i$ such that $\sum p_i = 1$. This yields extremely accurate true probabilities, especially in highly asymmetric markets.

---

### 4.2. Fractional Kelly Criterion Optimization
Once true probability $p$ is calculated, we determine stake sizing. Standard Kelly is highly volatile; Loki utilizes Fractional Kelly to minimize drawdown:

$$f^* = \text{Fraction} \times \frac{p \cdot b - (1 - p)}{b}$$
Where:
*   $b$ is the decimal odds net payout ($\text{odds} - 1$).
*   $p$ is our model's true probability estimate.
*   $\text{Fraction}$ is the conservative scaling multiplier (typically $0.10$ for micro-Kelly, $0.25$ for quarter-Kelly).

For $N$ concurrent bets, Loki solves the **Simultaneous Kelly Optimization** problem, maximizing the expected growth rate of the portfolio:
$$\max_{\mathbf{f}} \mathbb{E}\left[ \ln \left( 1 + \sum_{i=1}^N f_i X_i \right) \right]$$
subject to $\sum f_i \le f_{max}$ to protect against bankroll ruin.

---

### 4.3. Ensemble ML & Confidence Scoring (PropsBot-Style)
Loki deploys a multi-model ensemble consensus:
1.  **Model 1 (Gradient-Boosted Trees - XGBoost):** Focuses on team splits, defensive efficiency, and recent pace.
2.  **Model 2 (Deep Feedforward Neural Network):** Extracts non-linear interaction features (e.g., player vs. defensive scheme, rest day compounding).
3.  **Model 3 (Bayesian Ridge Regressor):** Highly robust baseline prediction to prevent overfitting on small sample sizes.

#### Confidence Score (CS)
Let $\{p_1, p_2, \dots, p_N\}$ be the probability projections from $N$ different models. We compute the ensemble mean $\mu$ and standard deviation $\sigma$:
$$\mu = \frac{1}{N} \sum_{k=1}^N p_k$$
$$\sigma = \sqrt{\frac{1}{N} \sum_{k=1}^N (p_k - \mu)^2}$$
The **Confidence Score** is mapped from $[0, 100]$ using a calibrated decay function:
$$CS = 100 \cdot e^{-\lambda \cdot \sigma}$$
where $\lambda$ is a penalty parameter tuned against empirical validation datasets. High CS means the ensemble is in tight consensus.

#### Edge Score (ES)
$$ES = p_{\text{true}} - p_{\text{implied\_no\_vig}}$$
Only bets with $ES > T_{edge}$ and $CS > T_{confidence}$ are promoted to the active recommendations panel.

---

### 4.4. Custom Model Builder & Dynamic Weighting (Rithmm-Style)
Loki allows the user to act as the head data scientist. The system exposes a vector of raw factors $\mathbf{X}$ and weights $\mathbf{W}$ that adjust the final prediction:

$$P_{\text{custom}} = \sigma \left( \sum_{i=1}^M w_i \cdot f_i(x_i) \right)$$
Where:
*   $f_i(x_i)$ is the normalized factor value (e.g., offense rating, defensive matchup score, rest factor).
*   $w_i$ is the weight customized by the user.
*   $\sigma$ is the sigmoid activation function mapping the raw value to a valid probability.

Loki's **sandbox backtester** simulates the custom weights against historical databases (e.g., WNBA 2025 season, MLB 2025 season) and outputs a detailed backtest report featuring:
*   Win rate over historical lines.
*   Simulated ROI using Kelly sizing.
*   Overfitting warning score (using K-fold cross-validation metrics).

---

### 4.5. BetScore Engine (PlayerProps.ai-Style)
The BetScore is a single, intuitive rating from 1 to 100 representing total bet quality:

$$BetScore = w_{\text{edge}} \cdot \text{Edge}_{\text{normalized}} + w_{\text{conf}} \cdot CS + w_{\text{trend}} \cdot T_{\text{hit\_rate}} + w_{\text{market}} \cdot M_{\text{velocity}}$$
Where:
*   $T_{\text{hit\_rate}}$ is the rolling historical frequency of crossing the line (last 5, 10, and 20 games combined).
*   $M_{\text{velocity}}$ is the line movement rate (how fast the line is moving, indicating sharp inflow).

---

### 4.6. PropGPT-Style Grade Mapper
To democratize complex mathematics, Loki maps the analytical outputs directly into readable, quick grades:

| Grade | BetScore Range | Interpretation | Action Guidance |
| :---: | :---: | :--- | :--- |
| **A+** | $\ge 95$ | Maximum Edge & Tight Ensemble Consensus | Prime value play. Target with high confidence. |
| **A** | $90 - 94$ | High Edge, Strong Consensus | Excellent wager. Standard play. |
| **B** | $80 - 89$ | Moderate Edge, Normal Consensus | Value exists but proceed with cautious sizing. |
| **C** | $70 - 79$ | Neutral Edge | Low value, high vig. Avoid unless narrative dictates otherwise. |
| **D** | $60 - 69$ | Negative Edge | Overpriced line. Potential under-play opportunity. |
| **F** | $< 60$ | High Dispersion / Heavy Juice | Negative EV. Total avoid. |

---

## 5. RAG & Conversational Analysis Pipeline (RotoBot-Style)

Loki features a highly sophisticated conversational interface integrated with Solomon's core reasoning engine.

```
[User Query] ──> [Query Categorizer] ──> [Entity Extractor (Player, Prop, League)]
                                                       │
                                                       ▼
[Formatted Answer Card] <── [Context Fusion] <── [Loki Core DB Query] (Stats, Odds, Model Reads)
```

1.  **Conversational Intent Parsing:** Natural language queries (e.g., *"How does Sabrina Ionescu match up against the Las Vegas Aces tonight for points?"*) are parsed into structured entity vectors:
    *   `Entity`: Sabrina Ionescu
    *   `League`: WNBA
    *   `Market`: Player Points Prop
    *   `Opponent`: Las Vegas Aces
2.  **Context Assembly:** Loki performs a hybrid lexical/semantic vector query against the sports stats DB, pulling current injury news, rolling 5-game average, historical H2H matchups against Las Vegas, and the current sportsbook line.
3.  **Synthesized Answer Cards:** Loki yields structured, markdown-rich cards containing:
    *   The **True Probability Line** versus the **Bookmaker Line**.
    *   The **Loki Grade** and **BetScore**.
    *   Concise, bulleted justifications based on quantitative data.

---

## 6. Integration & Sync Layer

### 6.1. Fantasy League Roster Ingestion
Loki connects with major fantasy platforms (Yahoo, Sleeper, ESPN) to contextualize advisory wagers and optimize lineups:
*   **Sleeper API:** Direct websocket client listening to league state, transaction logs, and roster tables.
*   **Yahoo Sports API (OAuth 2.0):** Pulls weekly rosters and matches player names using high-recall Jaro-Winkler string-matching algorithms.
*   **ESPN Fantasy API:** Ingests private league JSON cookies to parse active league configurations.

### 6.2. Real-Time Bookmaker Odds Shopping
To guarantee finding the best line, Loki maintains an active ingestion worker:
*   **Direct API Connections:** Ingests live sportsbook feeds (DraftKings, FanDuel, BetMGM, Caesars, Pinnacle) and DFS hubs (PrizePicks, Underdog Fantasy, Sleeper).
*   **Best Price Router:** For any selected prop (e.g., "Over 7.5 Strikeouts"), Loki identifies the optimal bookmaker to execute the play, securing crucial line/price differences.

---

## 7. Technology Stack & Operational Blueprint

*   **Core Backend Language:** Python 3.11+
*   **Data Science Stack:** NumPy, SciPy (for Newton-Raphson Shin calculations), Pandas, Scikit-learn, and XGBoost.
*   **RAG Engine:** LlamaIndex / LangChain integrated with Solomon's OpenAI/Codex pipelines.
*   **Database:** PostgreSQL (production data, line movement records) + SQLite (highly optimized local caches and thread-safe testing states).
*   **Downstream Self-Learning:** Integrated with Solomon's **Gabriel Assimilation Engine**'s AST Injector and Recursive Optimizer to dynamically test, improve, and deploy self-generated sports betting algorithms in production.

---
## RECOMMENDED NEXT STEP
Implement the modular backend prototype for Loki inside a new python package `loki/` containing the core mathematical algorithms, the custom model builder, the grading engine, and a Flask endpoint test layer.
