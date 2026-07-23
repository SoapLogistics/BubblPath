# Project Loki & Project Hugin: Combined SOSS Analytical & Defensive Super Blueprint

---

## 1. Executive Summary & Unified Mandate

Project Loki and Project Hugin are sister capabilities within **Solomon's Cognitive Architecture**. They operate in tandem to analyze highly complex, structured environments:
*   **Project Loki:** The sports betting and quantitative probability analytics engine. It leverages advanced statistical modeling, ensemble machine learning, and game-theoretic optimization to identify systemic edge.
*   **Project Hugin:** The defensive application security, static program analysis, and software verification engine. It translates raw application binaries, decompiled source trees, and structural flows into clean, structured knowledge representations (ASTs, Call Graphs) for vulnerability mitigation and design audit.

By unifying both under a single **Active Inference Model**, Solomon acquires the ability to deconstruct both statistical systems (markets/sports) and logical systems (code/software structures).

---

## 2. Deconstruction of Competitor & Theoretical DNA

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SOLOMON SOSS SYSTEM                                    │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│               PROJECT LOKI                │               PROJECT HUGIN                │
│       (Quantitative Sports Analytics)     │       (Defensive Software Verification)    │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ • Multi-Model Ensemble Projections        │ • AST parsing and CFG generation           │
│ • Shin's Vig-Removal Algorithms          │ • Call-Graph structural analysis           │
│ • Simultaneous Kelly Optimization         │ • Symbolic Execution for control flow      │
│ • BetScore & PropGPT Letter Grading       │ • Static Analysis & Defensive Verification │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

---

## 3. Project Loki: Quantitative Mathematical Architecture

Loki operates as an automated quant desk, ingesting raw bookmaker markets and applying game-theoretic and probabilistic filters to extract positive expected value (+EV).

### 3.1. Implied Probability & Vig-Removal Models
Bookmaker lines contain an overround ("vig"). Loki extracts the true probability ($p_i$) of sports events using three methods:

#### A. Multiplicative Method (Standard Normalization)
$$p_i = \frac{\pi_i}{\sum_{j} \pi_j}$$
Where $\pi_i = \frac{1}{\text{Decimal Odds}_i}$.

#### B. Power Method (Favorite-Longshot Bias Compensation)
$$\pi_i = p_i^k$$
where $k < 1$ is solved iteratively via Newton-Raphson such that $\sum p_i = 1$.

#### C. Shin's Method (Informed Bettor Model)
Shin models the market where a fraction $z$ of trades are executed by informed bettors (insiders) and $1-z$ by noise traders:
$$\pi_i = (1-z)p_i + z\sqrt{p_i}$$
We solve for $z$ and the true probabilities $p_i$ such that $\sum p_i = 1$. This minimizes prediction error in highly asymmetric niche markets (e.g., WNBA, MLS, esports).

---

### 3.2. Simultaneous Fractional Kelly Criterion
To optimize capital allocation across $N$ concurrent sports bets and protect the bankroll from drawdown, Loki solves the Simultaneous Kelly Optimization:

$$\max_{\mathbf{f}} \mathbb{E}\left[ \ln \left( 1 + \sum_{i=1}^N f_i X_i \right) \right] \quad \text{subject to} \quad \sum_{i=1}^N f_i \le f_{\max}$$
Where:
*   $f_i$ is the fractional bankroll wagered on outcome $i$.
*   $X_i$ is the random payoff of outcome $i$.
*   $f_{\max}$ is the conservative risk ceiling (typically $0.10$ to $0.25$).

---

### 3.3. Ensemble ML, BetScore, and PropGPT Grading
1.  **Ensemble Scoring:** Divergent model architectures (Gradient Boosted Trees, Deep Neural Networks, Bayesian Regressors) generate independent predictions. Standard deviation ($\sigma$) measures model consensus to determine the **Confidence Score (CS)**:
    $$CS = 100 \cdot e^{-\lambda \cdot \sigma}$$
2.  **BetScore Engine:** Computes a unified 1-100 rating combining:
    $$BetScore = w_{\text{edge}} \cdot \text{Edge}_{\text{norm}} + w_{\text{conf}} \cdot CS + w_{\text{trend}} \cdot \text{HitRate}_{\text{rolling}} + w_{\text{market}} \cdot \text{LineVelocity}$$
3.  **PropGPT Grades:** Maps the BetScore to clean letter grades (A+ to F) for rapid decision support.

---

## 4. Project Hugin: Defensive Software Verification Architecture

Hugin acts as Solomon's static analyzer and code representation engine. It deconstructs software structures into clean, queryable knowledge graphs.

### 4.1. Structural Mapping & AST Representation
To audit, verify, and understand any application or codebase, Hugin parses the source code into an **Abstract Syntax Tree (AST)**.
*   **Parser Frontends:** Support parsing Python (via `ast` module), JavaScript/TypeScript (via `Babel/Esprima` models), and C/C++ (via `Clang/LLVM` representation).
*   **Control Flow Graphs (CFG):** Hugin structures code blocks into a directed graph $G = (V, E)$, where vertices $V$ are basic blocks (straight-line code sequence) and edges $E$ represent control flow jumps/conditional branches.

```
                  [Function Entry Node]
                           │
                           ▼
                 [Basic Block 1 (Init)]
                           │
                           ▼
                 [Conditional Branch]
                 ├─── True  ───> [Basic Block 2 (Then)]
                 └─── False ───> [Basic Block 3 (Else)]
                           │
                           ▼
                  [Function Exit Node]
```

---

### 4.2. Static Program Analysis & Dependency Audits
Hugin scans the AST and CFG to map system dependencies and spot design errors:
1.  **Call Graph Construction:** Builds a global directed graph representing calling relationships between functions.
2.  **Taint Analysis:** Tracks user inputs (sources) through variables to dangerous sinks (e.g., SQL execution, raw memory writes) to prevent structural vulnerabilities.
3.  **Cyclomatic Complexity Calculation:** Computes the complexity of code blocks to assess maintainability and identify logical bottlenecks:
    $$M = E - V + 2P$$
    Where $E$ is the number of edges, $V$ the number of vertices, and $P$ the number of connected components.

---

### 4.3. Symbolic Execution & Model Verification
To mathematically prove software correctness, Hugin utilizes Symbolic Execution engines:
*   Instead of running the code with concrete inputs, variables are treated as symbolic values $\alpha$.
*   Execution paths are mapped to path formulas (Path Constraints, $PC$).
*   The path formulas are evaluated using an **SMT Solver (e.g., Z3)** to automatically solve for the exact input criteria required to trigger specific logical states.

---

## 5. Hardening Gabriel's Assimilation via Mnemosyne Governance

### 5.1. Resolving the Central Systemic Weakness
A critical structural audit of Solomon's Cognitive Architecture reveals a central vulnerability: **The Gabriel Assimilation Engine's code-synthesis loops operate as an experimental/simulated sandbox without deterministic verification.** Running dynamically generated or "code thief" extracted modules directly in production introduces severe operational risk and model instability.

To resolve this weakness, **Gabriel is formally decoupled from active execution and demoted to a pure "Proposer Substrate."** All capabilities generated or mutated by Gabriel must be audited, compiled, and registered as structured Knowledge Cards within **Mnemosyne—the mature, thread-safe, SQLite-backed, governed learning engine.**

```
 ┌──────────────────────────────────────┐
 │      Gabriel Assimilation Core       │  (Experimental Code Extractor)
 └──────────────────┬───────────────────┘
                    │  [Outputs Raw Dynamic Code & Metadata]
                    ▼
 ┌──────────────────────────────────────┐
 │     Mnemosyne Review Gate (SOSS)     │  (DRAFT State)
 └──────────────────┬───────────────────┘
                    │  [Hugin Static Audit, Taint Checks, & Unit Verifications]
                    ▼
 ┌──────────────────────────────────────┐
 │      Human / SOK Review Panel        │  (REVIEWED ➔ APPROVED State)
 └──────────────────┬───────────────────┘
                    │  [Promoted to Read-Only SQLite Substrate]
                    ▼
 ┌──────────────────────────────────────┐
 │    Active SOK Capability Registry    │  (ACTIVE State: Safe Production Run)
 └──────────────────────────────────────┘
```

---

### 5.2. The Governed Capability Promotion Pipeline (GCPP)
Any dynamic model compiled by Gabriel (e.g., a custom WNBA sports model, or a custom parser hook) must traverse a strict 4-stage GCPP pipeline before execution:

1.  **Stage 1: Card Structuring (DRAFT)**
    Gabriel's raw python code payloads are formatted as a JSONL SOSS Capability Card. The card *must* record its core engineering rationale:
    *   `why_created`: Objective context behind the generation.
    *   `problem_solved`: The specific math, bug, or endpoint targeting.
    *   `future_work_dependent`: Upstream capabilities relying on this card.
2.  **Stage 2: Automatic Defensive Verification (REVIEWED)**
    The draft card payload is queried by **Project Hugin**. Hugin runs:
    *   **AST Safety Scanner**: Rejects cards containing unauthorized OS operations or unsanitized eval structures.
    *   **Automated Unit Test Prober**: Runs isolated test scripts on the generated capability to verify it compiles and runs without memory leaks.
3.  **Stage 3: Policy-Guided Review Gate (APPROVED)**
    The card's metadata must satisfy SOK constraints. It transitions through `ReviewGate.review_card()` to enforce compliance checks.
4.  **Stage 4: Capability Promotion (ACTIVE)**
    Upon approval, the card is promoted to the immutable SQLite master ledger. The capability is registered inside the `DynamicCapabilityRegistry` and loaded into the namespace via safe `importlib` bindings. It is now cleared for secure production execution.

---

## 6. Solomon Blueprint 2.0: The Perpetual Learning Machine

To shift Solomon from "accumulating features" to "becoming an engine that builds himself," we formally restructure SOSS into a series of **evolutionary, governed phases** powered by the **Perpetual Learning Core (PLC)**.

```
                    ┌──────────────────────────────┐
                    │             USER             │
                    └──────────────┬───────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │         Solomon Core         │
                    └──────────────┬───────────────┘
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      │                            │                            │
┌─────▼──────────────┐   ┌─────────▼──────────┐   ┌─────────────▼──────┐
│  Mnemosyne Memory  │   │ Prometheus Curiosity│   │ Gabriel Skill Fact.│
│ (Governed Storage) │   │  (Opportunity Map) │   │ (Capability Synt.) │
└─────┬──────────────┘   └─────────┬──────────┘   └─────────────┬──────┘
      │                            │                            │
      └────────────────────────────┼────────────────────────────┘
                                   │
                    ┌──────────────▼───────────────┐
                    │   Perpetual Learning Core   │
                    └──────────────┬───────────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │                           │                           │
┌──────▼─────────────┐   ┌─────────▼──────────┐   ┌────────────▼───────┐
│ Experiment Engine  │   │    Review Gate     │   │ Deployment Engine  │
└────────────────────┘   └────────────────────┘   └────────────────────┘
```

Every design choice within Solomon 2.0 answers a single directive: **"Does this make Solomon learn better?"** If the answer is negative, execution is suspended.

---

### 6.1. Phase-by-Phase Evolutionary Roadmap

#### Phase 0: Freeze the Foundation (SS1)
Establish a locked, immutable production brain. Features must be frozen to preserve complete baseline stability.
*   **Active Controls:** 1 production API, 1 unified memory database, 1 execution planner, and 1 deployment pipeline.

#### Phase 1: Perpetual Learning Core (Mnemosyne OS)
Establish Mnemosyne as the perpetual operating system. Learning is the sole system responsibility.
*   **Card Families:** Knowledge Cards, Procedural Cards, Repair Cards, Skill Cards, Failure Cards.
*   **Lifecycle Rules:** Version control on all files. Memories must earn their retention score; obsolete knowledge is garbage collected.

#### Phase 2: Curiosity Engine (Prometheus Opportunity Mapper)
Instead of waiting for human prompts, Prometheus actively scans execution logs, CLI metrics, and user feedback to detect **Learning Opportunities (LOs)**.
*   **Opportunity Weighting Matrix:**
    $$\text{LO Score} = w_v \cdot \text{Value} + w_d \cdot \text{Difficulty} + w_u \cdot \text{FutureUse} - w_r \cdot \text{Risk} - w_c \cdot \text{ComputeCost}$$
*   The highest-scoring LOs populate the automated learning queue.

#### Phase 3: Experiment Engine (Scientific Method Pipeline)
Every LO is converted into a structured, reproducible experiment:
$$\text{Hypothesis} \longrightarrow \text{Plan} \longrightarrow \text{Sandbox Execution} \longrightarrow \text{Evidence Capture} \longrightarrow \text{Review} \longrightarrow \text{Mnemosyne Promotion}$$

#### Phase 4: Skill Factory (Gabriel Re-engineered)
Gabriel transitions from copy-pasting code into synthesizing structured, modular, and benchmarked **Skill Packages** (e.g., Git workflow, conflict resolution, mathematical models).
*   Each package is isolated and contains defined: purpose, inputs, outputs, automated unit tests, and safety constraints.

#### Phase 5: Skill Graph & Dependency Maps
Skills teach each other by building a directed dependency graph.
*   Loki and Hugin analyze the graph to discover prerequisites, missing knowledge vectors, and structural redundancies, automatically recommending what to learn next.

#### Phase 6: Learning Process Optimization (Self-Study)
Solomon monitors his own performance metrics (e.g., embedding search success, recall relevance, and execution accuracy).
*   The system iteratively modifies its own hyperparameters (e.g., RAG vector search weights, decay parameters, and confidence thresholds) to optimize the learning rate.

#### Phase 7: Autonomous Research & Proactive Evaluation
Solomon initiates research projects independently (e.g., benchmark comparison of different mathematical calculators, sports databases, or parsing schemas), storing winners in the active ledger and archiving losers.

#### Phase 8: Autonomous Tool Creation
Solomon identifies missing operational capabilities, prototypes the utility in sandboxes, subjects it to AST safety audits, and registers it as a reusable skill.

#### Phase 9: Self-Repair & Telemetry Probes
Continuous self-audit probes monitor: memory corruption, broken APIs, hallucination rates, and model drift. Repair templates are automatically compiled and deployed.

#### Phase 10: Distributed Node Ledger
Nodes (macOS, Ubuntu local server, mobile nodes) sync knowledge updates, new failures, and repairs back to the primary SOSS ledger.

#### Phase 11: SOSS Wisdom Layer
A final ethical and limitation gate. Every promoted skill is marked with explicit constraints:
$$\text{Wisdom Vector} = \{\text{Confidence}, \text{Risks}, \text{Limits}, \text{Human Overrides}, \text{Ethics Limits}\}$$

#### Phase 12: Learning How to Learn (Meta-Learning)
Solomon optimizes his own learning algorithms. Rather than just acquiring Python scripts or sports statistics, he modifies the structural algorithms of the Experiment Engine and the Review Gate. This is the point where growth transitions from additive to exponential.

---

### 6.2. The Solomon North Star Governing Rule
To align every capability with self-improvement, Solomon commits to a single sovereign rule:

> **Every hour Solomon must become measurably better than the hour before—not by changing randomly, but by acquiring verified, reusable knowledge that increases his ability to solve future problems safely and efficiently.**

---

## 8. Technology Stack & Implementation Blueprint

*   **Languages:** Python 3.11+, TypeScript, Rust (for high-speed binary parsing).
*   **Analysis Tools:** Python `ast` parser, `Z3 Theorem Prover` (SMT Solver), `NetworkX` (for Call Graphs and CFG graph math).
*   **Data Science Stack:** NumPy, SciPy (Newton-Raphson solvers), Scikit-learn, and Pandas.
*   **API Gateway:** Integrated under `app.py` on the proxy-secured port `18789`.

---
## RECOMMENDED NEXT STEP
**Deploy the GCPP pipeline validation routes inside `app.py` under the `/api/gabriel/promote-to-mnemosyne` endpoint to programmatically bind Gabriel's output to Mnemosyne's SQLite storage.**
