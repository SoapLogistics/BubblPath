# Solomon Threat Model

## Boundaries and Trust
* The `SolomonAgenticClaw` executes untrusted internet queries.
* The local SQLite storage is trusted.

## Data Flows
1. User -> Flask App -> Database
2. Gabriel Engine -> Internet (via DDGS)

## Mitigations
* Strict input validation on Flask API.
