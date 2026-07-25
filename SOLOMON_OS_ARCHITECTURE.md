# Solomon Operating System Architecture

Solomon Operating System (SOSS) treats all its cognitive and functional capabilities as modular subsystems, much like a Linux OS treats kernel modules. The architecture is built around a central `SolomonKernel` that manages the lifecycle, Inter-Module Communication (IPC), and resource allocation for these subsystems.

## The Kernel

The **SolomonKernel** is the heart of the system. It is responsible for:
- **Module Registration & Lifecycle**: Bootstrapping, pausing, restarting, or shutting down subsystems.
- **Inter-Module Communication (IPC)**: Providing an Event Bus and RPC mechanism so that subsystems can seamlessly communicate without tight coupling.
- **Resource Management**: Tracking system resource usage (compute, tokens, memory) and routing workloads appropriately.

## Subsystems (Modules)

Each subsystem extends a base `SolomonModule` class and registers with the Kernel upon startup.

### 1. Memory Subsystem (`solomon_os/modules/memory.py`)
- **Role**: Manages the System of Knowledge (SOK). Handles short-term context windows and long-term disk storage, including semantic embeddings and Knowledge Graphs.
- **IPC**: Broadcasts memory-indexed events, listens for `STORE_MEMORY` or `RETRIEVE_MEMORY` requests.

### 2. Planning Subsystem (`solomon_os/modules/planning.py`)
- **Role**: The cognitive scheduler. Takes complex goals and decomposes them into executable task trees, using Multi-Agent Heuristics.
- **IPC**: Sends `EXECUTE_TASK` events to Workers and listens for `TASK_COMPLETED` or `TASK_FAILED`.

### 3. Workers Subsystem (`solomon_os/modules/workers.py`)
- **Role**: Spawns and manages specialized AI agents (e.g., Gabriel Workers) to execute specific tasks. Handles consensus and swarm logic.
- **IPC**: Registers available worker pools, processes `EXECUTE_TASK` events.

### 4. Browser Subsystem (`solomon_os/modules/browser.py`)
- **Role**: Acts as the system's eyes and hands on the web. Interacts with the Browser Companion Extension via web sockets or REST endpoints for DOM manipulation and web scraping.
- **IPC**: Emits `DOM_MUTATED` or `BROWSER_ACTION_RESULT` events.

### 5. Vision Subsystem (`solomon_os/modules/vision.py`)
- **Role**: Multi-modal image analysis. Processes screenshots, UI elements, and real-world images.
- **IPC**: Receives `ANALYZE_IMAGE` RPC calls and returns structured JSON context.

### 6. Voice Subsystem (`solomon_os/modules/voice.py`)
- **Role**: Audio processing. Handles Speech-to-Text (ASR) for input and Text-to-Speech (TTS) for conversational output.
- **IPC**: Emits `AUDIO_RECEIVED` events, listens for `SPEAK_TEXT` events.

### 7. Scheduling Subsystem (`solomon_os/modules/scheduling.py`)
- **Role**: The cron daemon. Manages time-based tasks, background loops (like the Perpetual Learning Loop), and priority queueing.
- **IPC**: Emits time-based tick events (`TICK_1S`, `TICK_1M`).

### 8. Learning Subsystem (`solomon_os/modules/learning.py`)
- **Role**: The Perpetual Learning Engine (SPLE). Analyzes system performance, fine-tunes models, synthesizes new capabilities via SOSS clean-room code generation, and manages AST hot-reloading.
- **IPC**: Listens to system-wide metrics, triggers `AST_INJECT` or `RELOAD_MODULE` events.

### 9. Security Subsystem (`solomon_os/modules/security.py`)
- **Role**: The firewall and permission manager. Enforces the `SOLOMON_INTERNAL_AUTH_KEY`, validates prompt injections, and manages manual user approval gates (e.g., for browser actions or AST injection).
- **IPC**: Intercepts high-privilege events and ensures validation before passing them along.

### 10. Networking Subsystem (`solomon_os/modules/networking.py`)
- **Role**: Handles external API integrations, proxy management, rate limiting, and network fault tolerance (retries, circuit breakers).
- **IPC**: Used by all modules for outbound HTTP/RPC traffic.

### 11. Storage Subsystem (`solomon_os/modules/storage.py`)
- **Role**: File system manager. Handles SQLite connection pooling, WAL enforcement, vacuuming, and file I/O operations safely.
- **IPC**: Provides a unified storage API for other modules, abstracting raw DB queries.

### 12. AI Models Subsystem (`solomon_os/modules/ai_models.py`)
- **Role**: The Quantization and LLM Engine. Manages local vs. remote model execution, ExL2 Sparse Quantization, and model hot-swapping based on latency/accuracy.
- **IPC**: Handles `INFERENCE_REQUEST` calls, abstracting the underlying LLM provider.

### 13. Tool Routing Subsystem (`solomon_os/modules/tool_routing.py`)
- **Role**: Exposes dynamic tools to the AI models. Acts as the `Action` parser and executor. When an AI outputs an action, this module routes it to the correct subsystem (e.g., Vision, Browser, or System bash).
- **IPC**: Parses text for `[ACTION: xxx]` and translates it into specific IPC events.

## Linux Module Analogy

- **`insmod` / `modprobe`**: The Kernel dynamically imports python modules from `solomon_os/modules/` and registers them via `Kernel.load_module(MemoryModule())`.
- **`rmmod`**: The Kernel can hot-unload a module via `Kernel.unload_module('memory')`.
- **`dmesg` / `/var/log`**: The Kernel maintains a central telemetry buffer accessible by the Security and Learning subsystems.
- **`/dev` and `/sys`**: Subsystems can expose virtual state to other modules (e.g., `Kernel.get_state('browser', 'current_url')`).

This architecture allows Solomon to scale infinitely. If a new capability is needed, a new module is written, injected into the `modules` directory, and the Kernel picks it up seamlessly.
