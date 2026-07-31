# Component Diagrams

## High-Level Architecture

```mermaid
graph TD
    UI[Android UI / Compose]
    Gateway[Gateway Service / FastAPI]
    Adapters[Mock Adapters]
    Contracts[Adapter Contracts]

    UI -->|REST/WebSockets| Gateway
    Gateway --> Contracts
    Contracts <|-- Adapters
```

## Shared Clipboard

```mermaid
graph LR
    App[Android Clipboard Widget] -->|Submit| Gateway
    Gateway --> Memory[Gateway Memory/Shared Model]
    Memory -->|Sync| App2[Other Client View]
```

## Project Room

```mermaid
graph TD
    Room[Project Room View]
    Room --> Git[Git Adapter]
    Room --> AI[AI Agent Adapter]
    Room --> Tasks[Task Adapter]

    Git --> MockGit[Mock Git Data]
    AI --> MockAI[Mock AI Responses]
```
