# Bezalel Foundry Architecture Overview

## Mission
Bezalel Foundry is a standalone engineering workspace designed to coordinate AI agents, projects, repositories, servers, documentation, and development workflows.

## Design Philosophy
- **Isolation:** The project remains completely separated from external codebases.
- **Mock-First Integration:** All interactions with AI, Git, Repositories, etc. use adapter patterns backed by mock services initially.
- **Unified Interface:** Provides a coherent operating environment across an Android application and a lightweight backend Gateway.

## Key Components
1. **Gateway:** The standalone backend service routing requests and providing mock data to clients.
2. **Android Application:** The primary interface supporting various device sizes via a clean UI built in Kotlin with Jetpack Compose.
3. **Adapters & Contracts:** Defined interfaces to swap between mock and real implementations of future dependencies cleanly.
4. **Project Rooms:** Central work areas binding repositories, agent conversations, logs, and notes.
5. **Shared Clipboard:** An architectural focus allowing typed sharing of text, markdown, patches, code, and logs across systems.
