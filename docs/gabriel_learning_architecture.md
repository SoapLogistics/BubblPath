# Gabriel Learning and Assimilation Core

This document outlines the architecture for integrating perpetual learning inside Gabriel, rather than building a disconnected Learning Engine.

## The Formal Subsystem
Gabriel acts as the central organ responsible for:
* learning, evaluating, adapting, and assimilating improvements.

## Component Responsibilities
* **Daily Inventory**: Senses outcomes (what happened, changed, failed, deployed, claimed, agent performance).
* **Gabriel Learning**: Interprets evidence (extracts lesson candidates, asks if it happened before, determines best agent, revises procedures).
* **Laboratory/Crucible**: Proves hypotheses (tests if the proposed lesson works, if it beats baseline, if it generalizes without regressions).
* **Mnemosyne**: Acts as durable storage (preserves the procedure, scope, evidence, confidence, contradictions, history).
* **Planner/Prometheus**: Uses validated procedures for making future plans.
* **Foundry/Hands**: Performs the execution and returns outcomes.

## Integration Path
```text
gabriel_engine/
    learning/
        ingestion/
        normalization/
        lesson_extraction/
        procedure_evolution/
        agent_evaluation/
        hypothesis_generation/
        validation/
        promotion/
        feedback/
```

We will build the first slice as the `Mission Outcome Learning Loop v1`, ingesting mission records, test outcomes, PR results, deployment outcomes, and human feedback to produce procedure candidates, agent profiles, and failure prevention rules.
