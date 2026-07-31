# Repository Map

The `bezalel-foundry` platform consists of the following isolated directories:

- `/android-app`: A modern Android application using Kotlin, Compose, Room, Coroutines, and MVVM.
- `/gateway`: A standalone service handling API requests and providing simulated data.
- `/contracts`: Abstract interface definitions representing integrations with AI, git, terminals, etc.
- `/adapters`: Implementations of contracts (initially solely providing Mock data).
- `/shared`: Reusable data schemas (e.g., Pydantic models for Project Rooms and Clipboard) accessible to the Gateway.
- `/mock-services`: Infrastructure designed specifically to generate realistic non-production data.
- `/sample-data`: Static JSON or text files used to seed the initial platform state.
- `/design`: UI/UX assets or notes.
- `/documentation`: Developer and architectural documentation.
- `/tests`: Automated test suites targeting the platform framework (Gateway, Adapters, Android scaffolding).
- `/scripts`: Execution and automation scripts.
- `/tools`: Auxiliary tools to assist with development and testing.
