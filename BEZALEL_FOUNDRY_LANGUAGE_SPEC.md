# Bezalel Foundry: Canonical Engineering Language Specification

> **Mission Statement**: This document establishes the absolute canonical language for the Bezalel Foundry platform. It is designed to ensure that humans, AI agents, and system architecture operate with zero semantic ambiguity. If two words mean the same thing, one is chosen. If a word is ambiguous, it is replaced.

## Part 1: Philosophical Engineering Principles

### Which engineering words are most commonly confused?
- **Task vs. Job**: 'Task' implies reasoning, intent, and completion by an Actor (human/AI). 'Job' implies blind, automated execution by a machine worker (e.g., a cron job).
- **State vs. Status**: 'State' is the raw, comprehensive data payload of a system's condition. 'Status' is a discrete, human-readable label summarizing that state (e.g., 'Pending').
- **Review vs. Approval**: A 'Review' is the act of looking at something. An 'Approval' is the cryptographic, systemic sign-off that allows a workflow to proceed.
- **Deployment vs. Commit**: A 'Commit' is writing code to storage. A 'Deployment' is running that code in an active environment.
- **Memory vs. Context**: 'Memory' is the vast, persistent storage of all AI interactions. 'Context' is the heavily filtered, strict subset of information passed into a Prompt for a specific Task.

### Which words should be banned?
- **Manager**: The most destructive word in software architecture. It means everything and nothing. Use `Controller`, `Service`, `Coordinator`, or `Adapter`.
- **Master/Slave**: Outdated. Use `Primary/Replica` or `Coordinator/Worker`.
- **Bot**: Implies a rigid, dumb script. Use `Agent` for autonomous AI, or `Worker` for automated scripts.
- **Project Room / Workspace (when used organizationally)**: Blurs the line between the UI environment and the organizational entity. Use `Project` for the organization, `Workspace` strictly for the temporary execution environment.
- **Conductor**: Theatrical and ambiguous. Use `Router` for data flow or `Coordinator` for state consensus.

### Which words create ambiguity?
- **App / Application**: Does this mean the frontend? The backend service? The entire company? Use `Service`, `View`, or `Platform` instead.
- **Script**: Implies a hacky bash file. Use `Job` or `Pipeline` depending on context.
- **Goal**: Too vague. Use `Objective`, which demands a measurable success criteria.

### Which names scale well for ten years?
- Terminology drawn directly from core computer science and distributed systems scales infinitely: `Node`, `Process`, `Thread`, `Queue`, `Event`, `Artifact`, `State`.
- Avoid product-management buzzwords (Epic, Squad, Tribe) as they fade with trends.

### Which names sound professional?
- Nouns with strict boundaries sound professional: `Registry`, `Adapter`, `Gateway`, `Artifact`, `Objective`.
- Gamified or informal terms sound unprofessional: `Quest`, `Banter`, `Widget` (borderline, but accepted for UI), `Scrapbook`.

### Which names should become official standards?
- **Actor**: Universal term for Human or AI.
- **Thread/Message**: Replaces the informal 'Chat'.
- **Objective/Task**: Standardized work breakdown.
- **Store/Index/Cache**: Standardized data layer taxonomy.

---

## Part 2: Canonical Vocabulary Dictionary

### Project
**Definition**: A bounded, long-term organizational structure that groups related Tasks, Artifacts, and Actors to achieve a specific business outcome.

**Why this word is better**: 'Project' is the universal industry standard for grouping work. Alternatives like 'Workspace' or 'Project Room' blur the line between the organizational bucket and the UI/environment used to view it.

**Aliases**: Initiative

**Banned Words**: Project Room, Campaign, Epic, Space

**Examples**: The Platform Migration Project, the Q3 Release Project.

**Common Mistakes**: Using 'Project' to mean a Git Repository. A Project *contains* Repositories.

---

### Task
**Definition**: A discrete, assignable unit of intentional work to be completed by an Actor (human or Agent).

**Why this word is better**: It clearly denotes work requiring reasoning and completion. 'Ticket' implies a support request, and 'Issue' implies a bug.

**Aliases**: Assignment

**Banned Words**: Ticket, Issue, Chore, To-Do

**Examples**: Implement the auth endpoint; Review the design document.

**Common Mistakes**: Confusing a human 'Task' with an automated 'Job'.

---

### Job
**Definition**: An automated, non-interactive compute execution with a defined start and end, typically run by a Worker.

**Why this word is better**: Strictly separates automated machine execution from human/Agent reasoning (Tasks).

**Aliases**: Batch, Run

**Banned Words**: Task, Process, Script

**Examples**: Nightly database backup Job; CI/CD build Job.

**Common Mistakes**: Calling an automated pipeline step a 'Task'.

---

### Worker
**Definition**: A specialized, unthinking compute process that pulls and executes Jobs from a Queue.

**Why this word is better**: Implies blind, mechanical execution without autonomy. Perfectly contrasts with 'Agent'.

**Aliases**: Daemon, Runner

**Banned Words**: Agent, Node, Slave

**Examples**: Celery worker, GitHub Actions runner.

**Common Mistakes**: Calling an autonomous AI an 'AI Worker'.

---

### Agent
**Definition**: An autonomous AI system capable of reasoning, planning, and executing Tasks via tool use.

**Why this word is better**: Industry standard for autonomous LLM-driven systems. Highlights agency and decision-making.

**Aliases**: AI Assistant, Copilot

**Banned Words**: Bot, AI Worker, Script

**Examples**: The Bezalel Code Agent, the QA Agent.

**Common Mistakes**: Using 'Bot' which implies rigid, rule-based scripting rather than reasoning.

---

### Session
**Definition**: A temporary, stateful period of interaction between an Actor and the Platform.

**Why this word is better**: Standard security and networking term for authenticated time bounds.

**Aliases**: Login Session

**Banned Words**: Connection, Instance

**Examples**: User authentication session; Agent active task session.

**Common Mistakes**: Confusing a logical Session with a physical network Connection.

---

### Thread
**Definition**: A strictly chronological sequence of Messages regarding a specific subject or Context.

**Why this word is better**: Replaces both 'Chat' and 'Conversation'. 'Chat' implies informal human banter. 'Thread' implies structural continuity and is native to engineering.

**Aliases**: Message Chain

**Banned Words**: Chat, Conversation, Discussion

**Examples**: The PR review thread; The debugging thread.

**Common Mistakes**: Using 'Chat' for formal AI tool-use logs.

---

### Message
**Definition**: A single, immutable unit of communication appended to a Thread.

**Why this word is better**: Unambiguous data structure definition.

**Aliases**: Note, Reply

**Banned Words**: Chat, Post, Comment (unless context is specifically code-review)

**Examples**: A user's prompt message; an Agent's tool-response message.

**Common Mistakes**: Confusing a Message with an Event (Events are system-generated, Messages are actor-generated).

---

### Artifact
**Definition**: A persistent, immutable file or binary object produced as the output of a Task or Job.

**Why this word is better**: Universally understood in build systems. Encompasses binaries, compiled reports, and generated assets.

**Aliases**: Output, Asset

**Banned Words**: Result, Deliverable

**Examples**: Compiled Docker image; Generated PDF summary.

**Common Mistakes**: Calling source code an Artifact. Code is source; Artifacts are derived.

---

### Document
**Definition**: A human-readable text file designed for long-term knowledge retention and communication.

**Why this word is better**: Replaces 'Report' (which implies a generated Artifact). Documents are living, authored texts.

**Aliases**: Doc, Wiki

**Banned Words**: Report, Page

**Examples**: Architecture Design Document; API standard Document.

**Common Mistakes**: Confusing an autogenerated metric Report with an authored Document.

---

### Repository
**Definition**: A version-controlled storage location for source code and configuration.

**Why this word is better**: The undisputed Git standard.

**Aliases**: Codebase

**Banned Words**: Project, Repo (in formal text)

**Examples**: The frontend repository.

**Common Mistakes**: Using 'Project' to refer to a Repository.

---

### Branch
**Definition**: A divergent line of development within a Repository.

**Why this word is better**: Standard version control nomenclature.

**Aliases**: Fork (when cross-repository)

**Banned Words**: Stream, Line

**Examples**: The main branch; feature/auth-update.

**Common Mistakes**: Confusing a Branch with a Version (a Branch is active, a Version is a frozen state).

---

### Worktree
**Definition**: A checked-out directory on disk linked to a specific Repository Branch.

**Why this word is better**: Strict Git terminology that prevents confusing the conceptual Branch with the files on disk.

**Aliases**: Checkout, Local Directory

**Banned Words**: Workspace (unless specifically referring to the IDE abstraction), Folder

**Examples**: Creating a secondary worktree to hotfix a bug.

**Common Mistakes**: Referring to the local worktree as 'the repo'.

---

### Commit
**Definition**: An immutable snapshot of changes applied to a Repository.

**Why this word is better**: Universal standard.

**Aliases**: Revision

**Banned Words**: Save, Update, Check-in

**Examples**: Commit 'fix: resolve race condition'.

**Common Mistakes**: Equating a Commit with a Deployment.

---

### Review
**Definition**: The formal process of an Actor analyzing a diff, Artifact, or Document against standards.

**Why this word is better**: Standard engineering practice.

**Aliases**: Audit

**Banned Words**: Check, Look-over

**Examples**: Code review; Architecture review.

**Common Mistakes**: Confusing a Review (the act of looking) with an Approval (the cryptographic/system sign-off).

---

### Approval
**Definition**: An explicit, logged authorization gate required to advance a Workflow.

**Why this word is better**: Implies cryptographic or strict systemic tracking.

**Aliases**: Sign-off, Gate

**Banned Words**: Okay, Blessing

**Examples**: MD6 Governance Approval.

**Common Mistakes**: Assuming a Review inherently includes an Approval.

---

### Permission
**Definition**: A system-enforced right granted to an Actor to perform a specific action.

**Why this word is better**: Standard IAM (Identity and Access Management) terminology.

**Aliases**: Grant, Entitlement

**Banned Words**: Right, Access-level

**Examples**: Write permission; Deploy permission.

**Common Mistakes**: Confusing Authentication (who you are) with Permission (what you can do).

---

### Node
**Definition**: A discrete, addressable physical or virtual compute instance within the platform.

**Why this word is better**: Replaces 'Server' and 'Machine'. 'Server' implies software serving requests; 'Machine' implies physical hardware. 'Node' abstracts both perfectly for distributed systems.

**Aliases**: Instance, Host

**Banned Words**: Server (for infrastructure), Machine, Box

**Examples**: Kubernetes worker node; Database replica node.

**Common Mistakes**: Calling an OS Process a Node.

---

### Service
**Definition**: A continuously running software application that exposes an API over a network.

**Why this word is better**: Standard microservices term.

**Aliases**: Daemon

**Banned Words**: App, Application, Server

**Examples**: The Authentication Service.

**Common Mistakes**: Using 'Server' to refer to the software (Service) rather than the hardware (Node).

---

### Process
**Definition**: An OS-level execution context with its own memory space.

**Why this word is better**: Strict operating system definition.

**Aliases**: PID

**Banned Words**: Task, Thread (unless referring to OS threads), Program

**Examples**: The Node.js process; the Postgres background process.

**Common Mistakes**: Confusing a business Workflow with an OS Process.

---

### Gateway
**Definition**: The singular ingress component that routes external requests into an internal system.

**Why this word is better**: Clearer than 'Proxy' or 'Load Balancer' as it defines the *boundary*.

**Aliases**: Ingress, API Gateway

**Banned Words**: Portal, Door

**Examples**: Nginx API Gateway.

**Common Mistakes**: Using Gateway interchangeably with Router (Router is internal, Gateway bridges boundaries).

---

### Adapter
**Definition**: A software component that translates between the platform's internal data standard and an External System.

**Why this word is better**: Classic GoF design pattern. Better than 'Bridge' or 'Integration'.

**Aliases**: Wrapper, Translator

**Banned Words**: Integration, Bridge, Connector

**Examples**: Stripe Adapter; GitHub API Adapter.

**Common Mistakes**: Calling an Adapter an 'Integration'. An integration is the concept; the Adapter is the code.

---

### API
**Definition**: The defined, versioned programmatic interface exposed by a Service.

**Why this word is better**: Universal standard.

**Aliases**: Interface

**Banned Words**: Endpoint (an API *has* endpoints), Protocol

**Examples**: REST API; GraphQL API.

**Common Mistakes**: Using API to mean a specific URL path.

---

### Plugin
**Definition**: Dynamically loaded code that extends a Service at runtime without altering the core codebase.

**Why this word is better**: Implies hot-loading and strict interface adherence.

**Aliases**: Extension, Add-on

**Banned Words**: Module, Package

**Examples**: Authentication Plugin; Logging Plugin.

**Common Mistakes**: Confusing a library dependency (Module) with a runtime Plugin.

---

### Module
**Definition**: A distinct, interchangeable directory or library of source code within a Repository.

**Why this word is better**: Standard software architecture term for code grouping.

**Aliases**: Package, Library

**Banned Words**: Component, Plugin

**Examples**: The database connection module.

**Common Mistakes**: Confusing a codebase Module with a runtime Service.

---

### Component
**Definition**: A self-contained, reusable block of business logic or UI code.

**Why this word is better**: Standard in frontend (React) and general systems architecture.

**Aliases**: Element

**Banned Words**: Part, Piece, Widget

**Examples**: The UserProfile component.

**Common Mistakes**: Using Component when referring to an entire Service.

---

### Feature
**Definition**: A discrete piece of functionality that delivers value to a user.

**Why this word is better**: Standard product management term.

**Aliases**: Capability

**Banned Words**: Tool, Function

**Examples**: The multi-factor authentication feature.

**Common Mistakes**: Calling an API endpoint a Feature. The Feature is the user capability, the API is the implementation.

---

### View
**Definition**: A distinct visual arrangement of UI presented to the user on a display.

**Why this word is better**: Replaces 'Screen'. 'Screen' implies physical hardware. 'View' applies to MVC patterns and frontend routing universally.

**Aliases**: Page

**Banned Words**: Screen, Window, Interface

**Examples**: The Analytics View.

**Common Mistakes**: Using 'Screen' when talking about web development.

---

### Panel
**Definition**: A defined, typically docked sub-section within a View.

**Why this word is better**: Clearer than 'Pane' or 'Sidebar'.

**Aliases**: Sidebar, Drawer

**Banned Words**: Section, Frame

**Examples**: The navigation panel; the details panel.

**Common Mistakes**: Calling a modal dialog a Panel.

---

### Widget
**Definition**: An interactive, single-purpose UI Component embedded within a View.

**Why this word is better**: Replaces 'Card'. 'Card' is a CSS design styling choice. 'Widget' strictly defines functional interactivity.

**Aliases**: Control

**Banned Words**: Card, Block, Gadget

**Examples**: The date-picker widget; the quick-action widget.

**Common Mistakes**: Using 'Card' to describe functional software.

---

### Dashboard
**Definition**: A View specifically designed to aggregate and display system Status, metrics, and high-level KPIs.

**Why this word is better**: Industry standard.

**Aliases**: Control Panel, HUD

**Banned Words**: Console, Monitor

**Examples**: The Operations Dashboard.

**Common Mistakes**: Calling a standard data entry form a Dashboard.

---

### Log
**Definition**: An append-only, immutable record of discrete system Events or textual outputs over time.

**Why this word is better**: Universal standard.

**Aliases**: Trace, Output

**Banned Words**: History, Journal

**Examples**: Application error log; audit log.

**Common Mistakes**: Confusing an Event (the object) with the Log (the file storing the objects).

---

### Event
**Definition**: A system-generated data object representing a state-change that occurred at a specific timestamp.

**Why this word is better**: Core term in event-driven architecture.

**Aliases**: Trigger

**Banned Words**: Message, Signal, Action

**Examples**: UserCreatedEvent; NodeFailedEvent.

**Common Mistakes**: Confusing a Thread Message (actor generated) with an Event (system generated).

---

### Notification
**Definition**: An Event explicitly routed to an Actor's attention, often interrupting their current workflow.

**Why this word is better**: Standard terminology.

**Aliases**: Alert

**Banned Words**: Ping, Alarm

**Examples**: Email notification; UI toast notification.

**Common Mistakes**: Treating all Events as Notifications. Notifications require routing to an Actor.

---

### Bookmark
**Definition**: A saved reference to a specific state, View, or Document for rapid retrieval by an Actor.

**Why this word is better**: Familiar UI paradigm.

**Aliases**: Favorite, Shortcut

**Banned Words**: Pin, Save

**Examples**: Bookmarking a repository; Bookmarking a specific search query.

**Common Mistakes**: Confusing a UI Bookmark with a system Checkpoint.

---

### Memory
**Definition**: The persistent, structured storage of past interactions, facts, and state available to an Agent for context retrieval.

**Why this word is better**: Specifically delineates Agent data from traditional system databases. Standard AI paradigm.

**Aliases**: Vector Store, Context Window

**Banned Words**: Brain, Storage

**Examples**: Retrieving the user's preference from Memory.

**Common Mistakes**: Using 'Memory' to describe RAM in the context of system architecture (use 'RAM' for hardware, 'Memory' for AI context).

---

### Knowledge
**Definition**: Abstracted, verified, and generalized information synthesized from Documents, Memory, and Code, usable across Tasks.

**Why this word is better**: Elevates raw data to verified truths.

**Aliases**: Wisdom, Lore

**Banned Words**: Data, Information

**Examples**: The Platform Knowledge Base.

**Common Mistakes**: Calling raw log strings 'Knowledge'.

---

### Context
**Definition**: The strict, verified subset of state, Memory, and Knowledge provided to an Agent to execute a specific Task.

**Why this word is better**: Standard LLM term.

**Aliases**: Prompt Context

**Banned Words**: Background, Situation

**Examples**: Injecting the API schema into the Agent's context.

**Common Mistakes**: Confusing Context (the data passed) with the Prompt (the template it is passed into).

---

### Prompt
**Definition**: The programmatic text template and instruction set passed to an LLM to elicit a response.

**Why this word is better**: Universal AI standard.

**Aliases**: System Prompt

**Banned Words**: Query, Question

**Examples**: The code review prompt.

**Common Mistakes**: Using Prompt when you mean the user's Message.

---

### Instruction
**Definition**: A direct, non-negotiable directive given to an Agent or human.

**Why this word is better**: Stronger and more absolute than 'Guidance' or 'Rule'.

**Aliases**: Directive, Command

**Banned Words**: Suggestion, Rule

**Examples**: System instructions inside an AGENTS.md file.

**Common Mistakes**: Mixing up a functional Instruction with a high-level Objective.

---

### Objective
**Definition**: A measurable outcome that a Project or Agent aims to achieve.

**Why this word is better**: Replaces 'Mission' (too emotional) and 'Goal' (too vague). Objective implies a strict success criteria.

**Aliases**: Target

**Banned Words**: Mission, Goal, Dream

**Examples**: Objective: Reduce latency by 50ms.

**Common Mistakes**: Setting an Objective without a measurable Validation metric.

---

### Clipboard
**Definition**: The short-term, ephemeral storage mechanism for moving data between Workspaces, Views, or Nodes.

**Why this word is better**: Universal user-interface paradigm.

**Aliases**: Buffer

**Banned Words**: Scrapbook, Temp

**Examples**: Copying a Snippet to the Clipboard.

**Common Mistakes**: Relying on the Clipboard for persistent data storage.

---

### Snippet
**Definition**: A small, reusable fragment of code or text.

**Why this word is better**: Industry standard.

**Aliases**: Fragment

**Banned Words**: Chunk, Piece

**Examples**: A bash configuration snippet.

**Common Mistakes**: Calling an entire file a Snippet.

---

### Diff
**Definition**: The computed, line-by-line textual difference between two states of a file.

**Why this word is better**: Replaces 'Patch'. Diff is the read-only output; Patch is the action of applying it.

**Aliases**: Delta

**Banned Words**: Patch, Changeset

**Examples**: The Git diff between main and feature branch.

**Common Mistakes**: Using Diff and Patch interchangeably.

---

### Timeline
**Definition**: A unified, chronological visualization of Events, Commits, and Messages.

**Why this word is better**: Replaces 'History', which implies a static archive. Timeline implies an active, ongoing sequence.

**Aliases**: Activity Feed

**Banned Words**: History, Log-view

**Examples**: The Project Timeline.

**Common Mistakes**: Confusing the Timeline (the UI representation) with the Log (the underlying data).

---

### Workspace
**Definition**: The transient, isolated environment containing the files, tools, and Context for a specific Task.

**Why this word is better**: Standard IDE and cloud-execution term.

**Aliases**: Environment

**Banned Words**: Project Room, Sandbox (unless explicitly testing security)

**Examples**: The Agent's execution workspace.

**Common Mistakes**: Using Workspace to mean the overall Project organization.

---

### Deployment
**Definition**: The orchestrated process of moving a verified Artifact into an active Service or Node.

**Why this word is better**: Universal standard.

**Aliases**: Release

**Banned Words**: Push, Rollout, Shipping

**Examples**: Production deployment.

**Common Mistakes**: Confusing a Commit (writing code) with a Deployment (running code).

---

### Validation
**Definition**: The systemic process of verifying that an Artifact, State, or input meets its required specifications.

**Why this word is better**: Replaces 'Testing' for non-code artifacts. Validation applies to data, AI outputs, and user inputs.

**Aliases**: Verification

**Banned Words**: Checking, Testing (unless referring specifically to unit/integration code tests)

**Examples**: Schema validation; Approval packet validation.

**Common Mistakes**: Saying 'Testing the data' instead of 'Validating the data'.

---

### Testing
**Definition**: The programmatic execution of assertions against source code to verify behavior.

**Why this word is better**: Strict software engineering term.

**Aliases**: QA

**Banned Words**: Experimenting, Proving

**Examples**: Unit testing; Integration testing.

**Common Mistakes**: Using Testing for data integrity checks (use Validation).

---

### Queue
**Definition**: A data structure acting as a buffer for pending Tasks, Jobs, or Messages, typically processed first-in-first-out.

**Why this word is better**: Universal computer science standard.

**Aliases**: Buffer, Backlog

**Banned Words**: Line, Waitlist

**Examples**: The async job queue; the message queue.

**Common Mistakes**: Confusing a Queue (execution buffer) with a Stream (continuous data flow).

---

### Pipeline
**Definition**: A strict, automated sequence of data processing or CI/CD steps where the output of one becomes the input of the next.

**Why this word is better**: Standard CI/CD and data engineering term.

**Aliases**: Build chain

**Banned Words**: Workflow, Conveyor

**Examples**: The ETL pipeline; the GitLab CI pipeline.

**Common Mistakes**: Using Pipeline for human-driven business processes (use Workflow).

---

### Workflow
**Definition**: A defined sequence of stages, rules, and Approvals that Tasks or Projects move through.

**Why this word is better**: Best models human and Agent organizational logic.

**Aliases**: Process Flow

**Banned Words**: Pipeline (unless fully automated code/data), Lifecycle

**Examples**: The document approval workflow.

**Common Mistakes**: Confusing a business Workflow with a CI/CD Pipeline.

---

### State
**Definition**: The complete, instantaneous set of variables and data defining a system or entity at a specific point in time.

**Why this word is better**: Core computer science definition.

**Aliases**: Condition

**Banned Words**: Status

**Examples**: The database state; application state.

**Common Mistakes**: Confusing State (the actual raw data) with Status (the human-readable label).

---

### Status
**Definition**: A discrete, human-readable label summarizing the current condition of an entity (e.g., Pending, Active, Failed).

**Why this word is better**: Perfectly contrasts with 'State'.

**Aliases**: Label

**Banned Words**: State, Phase

**Examples**: Job status: Failed.

**Common Mistakes**: Logging a massive JSON block and calling it a Status (it is State).

---

### Checkpoint
**Definition**: A deliberate, recoverable saved state of a long-running Job or Agent Session.

**Why this word is better**: Standard distributed systems term.

**Aliases**: Savepoint

**Banned Words**: Snapshot, Backup

**Examples**: Resuming the ML training from the last Checkpoint.

**Common Mistakes**: Confusing Checkpoint (in-flight recovery) with Snapshot (permanent archival).

---

### Snapshot
**Definition**: An immutable, point-in-time copy of a Store, File system, or State for backup or archival.

**Why this word is better**: Standard infrastructure term.

**Aliases**: Image

**Banned Words**: Checkpoint, Copy

**Examples**: The nightly EBS volume Snapshot.

**Common Mistakes**: Using Snapshot for active memory caching.

---

### Version
**Definition**: A specific, immutable numbered release of a Module, Service, or Artifact (e.g., SemVer).

**Why this word is better**: Standard engineering practice.

**Aliases**: Release

**Banned Words**: Iteration, Draft

**Examples**: Version 1.4.2.

**Common Mistakes**: Calling a Git branch a Version.

---

### Archive
**Definition**: Long-term, cold storage for immutable data that is no longer actively queried.

**Why this word is better**: Clearly denotes read-only, slow-access intent.

**Aliases**: Cold Storage

**Banned Words**: Backup (backup implies recovery of active systems, archive implies historical retention), Trash

**Examples**: Archiving the 2022 access logs.

**Common Mistakes**: Deleting data when it should be Archived.

---

### Package
**Definition**: A bundled, distributable archive containing compiled code, Modules, and metadata.

**Why this word is better**: Standard for distribution (NPM, PyPI, Debian).

**Aliases**: Bundle, Tarball

**Banned Words**: Library, Installer

**Examples**: The node_modules package.

**Common Mistakes**: Calling source code a Package before it is built.

---

### Connection
**Definition**: An active, physical or logical network link established between two Nodes.

**Why this word is better**: Strict networking terminology.

**Aliases**: Socket, Link

**Banned Words**: Session, Integration

**Examples**: TCP Connection; Database Connection.

**Common Mistakes**: Confusing an active TCP Connection with a high-level API Integration.

---

### External System
**Definition**: Any Service, API, or Actor that exists outside the security boundary of the Bezalel Foundry platform.

**Why this word is better**: Unambiguously defines the security and trust boundary.

**Aliases**: Third-Party

**Banned Words**: Outside world, Vendor

**Examples**: AWS S3; GitHub API.

**Common Mistakes**: Trusting External System inputs without Validation.

---

### Internal System
**Definition**: Any Service, Store, or Node residing within the trusted network boundary of the platform.

**Why this word is better**: Clear perimeter definition.

**Aliases**: Platform Service

**Banned Words**: Core, Backend (too vague)

**Examples**: The Governance Database.

**Common Mistakes**: Applying zero-trust Gateway patterns between tightly coupled Internal Systems unnecessarily.

---

### Integration
**Definition**: The architectural concept of linking the platform with an External System via an Adapter.

**Why this word is better**: High-level concept standard.

**Aliases**: Partnership (business)

**Banned Words**: Plugin, Connection

**Examples**: The Slack integration.

**Common Mistakes**: Using Integration to refer to the actual code (which is the Adapter).

---

### Controller
**Definition**: A localized Component responsible for receiving inputs and orchestrating state changes within a specific Service or View.

**Why this word is better**: Standard MVC pattern.

**Aliases**: Handler

**Banned Words**: Manager, Coordinator

**Examples**: The Authentication Controller.

**Common Mistakes**: Putting raw business logic inside a Controller (it should orchestrate, not calculate).

---

### Manager
**Definition**: BANNED TERM. Do not use. Use 'Controller', 'Coordinator', or 'Service'.

**Why this word is better**: Manager is the most ambiguous word in engineering. It means nothing.

**Aliases**: N/A

**Banned Words**: Manager

**Examples**: N/A

**Common Mistakes**: Naming a file `DataTaskManager.java`.

---

### Registry
**Definition**: A central, authoritative database where Services, Plugins, or entities advertise their existence and metadata.

**Why this word is better**: Replaces 'Catalog' and 'Index' for service discovery and metadata.

**Aliases**: Directory

**Banned Words**: Catalog, List

**Examples**: The Engine Registry; Docker Registry.

**Common Mistakes**: Confusing a Registry (metadata about where things are) with a Store (the actual things).

---

### Index
**Definition**: A highly optimized read-only data structure projected from a Store, designed strictly for rapid querying.

**Why this word is better**: Database engineering standard.

**Aliases**: Search Index

**Banned Words**: Catalog, Directory

**Examples**: Elasticsearch Index; B-Tree Index.

**Common Mistakes**: Treating an Index as the source of truth.

---

### Library
**Definition**: A curated, read-only collection of reusable Documents or Code Modules.

**Why this word is better**: Implies reference and reuse without active execution.

**Aliases**: Collection

**Banned Words**: Store, Archive

**Examples**: The Standard Library; The Document Library.

**Common Mistakes**: Using Library to mean a database Store.

---

### Store
**Definition**: The generic, canonical term for any persistent data storage infrastructure.

**Why this word is better**: Abstracts over SQL, NoSQL, Object, and Vector paradigms. Better than just 'Database'.

**Aliases**: Database, Persistence Layer

**Banned Words**: Memory, Drive

**Examples**: The Vector Store; The Object Store.

**Common Mistakes**: Using Store to describe in-memory caching.

---

### Cache
**Definition**: Ephemeral, fast-access storage used to duplicate slow-to-compute or retrieve data to improve performance.

**Why this word is better**: Universal standard.

**Aliases**: Buffer

**Banned Words**: Store, Memory

**Examples**: Redis Cache; CPU L2 Cache.

**Common Mistakes**: Treating a Cache as persistent storage and failing to handle cache eviction.

---

### Provider
**Definition**: A Service or Adapter that supplies data, compute, or capabilities to the platform.

**Why this word is better**: Standard decoupling pattern.

**Aliases**: Supplier

**Banned Words**: Source, Vendor

**Examples**: LLM Provider; Identity Provider.

**Common Mistakes**: Hardcoding Provider names into core logic.

---

### Consumer
**Definition**: An Actor, Service, or Worker that pulls data or Jobs from a Queue or Provider.

**Why this word is better**: Standard publish/subscribe terminology.

**Aliases**: Subscriber, Client

**Banned Words**: Reader, User

**Examples**: Event queue consumer.

**Common Mistakes**: Confusing a backend Consumer with a human end-user.

---

### Coordinator
**Definition**: A distributed systems component that manages state consensus, locking, and synchronization across multiple Nodes or Workers.

**Why this word is better**: Strict distributed systems term (e.g., ZooKeeper, Paxos).

**Aliases**: Consensus Node

**Banned Words**: Manager, Conductor, Master

**Examples**: The Transaction Coordinator.

**Common Mistakes**: Using Coordinator for simple single-node routing.

---

### Router
**Definition**: A network or logical component that inspects incoming Messages/Events and directs them to the correct destination Service or Queue.

**Why this word is better**: Universal standard for traffic direction.

**Aliases**: Dispatcher

**Banned Words**: Conductor, Director

**Examples**: The HTTP Router; The Message Router.

**Common Mistakes**: Putting business logic inside a Router.

---

### Conductor
**Definition**: BANNED TERM. Do not use. Use 'Coordinator' for distributed state or 'Router' for traffic.

**Why this word is better**: Overly theatrical and vague.

**Aliases**: N/A

**Banned Words**: Conductor

**Examples**: N/A

**Common Mistakes**: Building an 'Orchestration Conductor'.

---
