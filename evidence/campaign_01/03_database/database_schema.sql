-- Solomon Canonical Database Schema (Version 3)

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cards (
    card_id TEXT PRIMARY KEY,
    card_type TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence REAL NOT NULL,
    validation_state TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    source_type TEXT NOT NULL,
    security_classification TEXT NOT NULL,
    evidence TEXT NOT NULL,
    supersedes TEXT,
    superseded_by TEXT,
    why_created TEXT NOT NULL,
    problem_solved TEXT NOT NULL,
    future_work_dependent TEXT NOT NULL,
    extra_metadata TEXT,
    deleted INTEGER DEFAULT 0,
    embedding TEXT
);

CREATE TABLE IF NOT EXISTS card_tags (
    card_id TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (card_id, tag),
    FOREIGN KEY (card_id) REFERENCES cards(card_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS card_links (
    link_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    link_type TEXT NOT NULL,
    UNIQUE (source_id, target_id, link_type)
);

CREATE TABLE IF NOT EXISTS card_sources (
    card_id TEXT NOT NULL,
    source_id TEXT NOT NULL,
    PRIMARY KEY (card_id, source_id),
    FOREIGN KEY (card_id) REFERENCES cards(card_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS card_revisions (
    revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id TEXT NOT NULL,
    revision_number INTEGER NOT NULL,
    serialized_card TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    updated_by TEXT NOT NULL,
    reason TEXT,
    FOREIGN KEY (card_id) REFERENCES cards(card_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS system_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_locator TEXT,
    actor_id TEXT NOT NULL,
    task_id TEXT,
    payload_json TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_system_events_content
ON system_events(event_type, source_type, content_hash);

CREATE TABLE IF NOT EXISTS learning_candidates (
    id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    candidate_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    source_type TEXT NOT NULL,
    source_locator TEXT,
    actor_id TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence REAL NOT NULL,
    utility REAL NOT NULL,
    risk TEXT NOT NULL,
    scope_json TEXT NOT NULL,
    validation_method TEXT,
    validation_result_json TEXT,
    duplicate_of TEXT,
    supersedes TEXT,
    contradicts TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(event_id) REFERENCES system_events(id),
    FOREIGN KEY(duplicate_of) REFERENCES learning_candidates(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_learning_candidate_hash
ON learning_candidates(content_hash, candidate_type, source_type);

CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL UNIQUE,
    memory_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    summary TEXT,
    provenance_json TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence REAL NOT NULL,
    utility REAL NOT NULL,
    risk TEXT NOT NULL,
    scope_json TEXT NOT NULL,
    tags_json TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    embedding_version TEXT,
    times_retrieved INTEGER NOT NULL DEFAULT 0,
    times_used INTEGER NOT NULL DEFAULT 0,
    successful_uses INTEGER NOT NULL DEFAULT 0,
    failed_uses INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_retrieved_at TEXT,
    last_used_at TEXT,
    review_due_at TEXT,
    FOREIGN KEY(candidate_id) REFERENCES learning_candidates(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_memories_content_hash
ON memories(content_hash, memory_type);

CREATE TABLE IF NOT EXISTS memory_links (
    id TEXT PRIMARY KEY,
    source_memory_id TEXT NOT NULL,
    target_memory_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    weight REAL NOT NULL,
    evidence_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(source_memory_id) REFERENCES memories(id),
    FOREIGN KEY(target_memory_id) REFERENCES memories(id),
    UNIQUE(source_memory_id, target_memory_id, relation_type)
);

CREATE TABLE IF NOT EXISTS retrieval_traces (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    query_text TEXT NOT NULL,
    filters_json TEXT NOT NULL,
    strategy TEXT NOT NULL,
    embedding_version TEXT,
    candidates_json TEXT NOT NULL,
    selected_json TEXT NOT NULL,
    rejected_json TEXT NOT NULL,
    latency_ms REAL NOT NULL,
    plan_created_after_retrieval INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_uses (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    memory_id TEXT NOT NULL,
    retrieval_trace_id TEXT NOT NULL,
    use_status TEXT NOT NULL,
    influence_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(memory_id) REFERENCES memories(id),
    FOREIGN KEY(retrieval_trace_id) REFERENCES retrieval_traces(id)
);

CREATE TABLE IF NOT EXISTS task_outcomes (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL UNIQUE,
    result_status TEXT NOT NULL,
    quality_score REAL,
    duration_ms REAL,
    resource_json TEXT NOT NULL,
    human_correction_json TEXT,
    evidence_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_outcomes (
    id TEXT PRIMARY KEY,
    memory_use_id TEXT NOT NULL,
    outcome_id TEXT NOT NULL,
    success INTEGER NOT NULL,
    utility_delta REAL NOT NULL,
    confidence_delta REAL NOT NULL,
    failure_type TEXT,
    correction_candidate_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(memory_use_id) REFERENCES memory_uses(id),
    FOREIGN KEY(outcome_id) REFERENCES task_outcomes(id),
    FOREIGN KEY(correction_candidate_id) REFERENCES learning_candidates(id)
);

CREATE TABLE IF NOT EXISTS governance_events (
    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    packet_id TEXT NOT NULL,
    previous_record_hash TEXT,
    record_type TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    target_environment TEXT NOT NULL,
    change_type TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    summary TEXT NOT NULL,
    artifact_json TEXT NOT NULL,
    tests_json TEXT NOT NULL,
    security_json TEXT NOT NULL,
    backup_json TEXT NOT NULL,
    rollback_json TEXT NOT NULL,
    reviewer_id TEXT,
    decision TEXT,
    decision_reason TEXT,
    occurred_at TEXT NOT NULL,
    record_hash TEXT NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS ix_governance_packet
ON governance_events(packet_id, sequence);

CREATE TABLE IF NOT EXISTS resident_leases (
    resident_id TEXT PRIMARY KEY,
    lease_owner TEXT NOT NULL,
    acquired_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    heartbeat_at TEXT NOT NULL,
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS resident_checkpoints (
    resident_id TEXT PRIMARY KEY,
    cycle_id TEXT NOT NULL,
    state TEXT NOT NULL,
    current_task_id TEXT,
    checkpoint_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS learning_targets (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    source_json TEXT NOT NULL,
    expected_value REAL NOT NULL,
    frequency_score REAL NOT NULL,
    severity_score REAL NOT NULL,
    reusability_score REAL NOT NULL,
    dependency_score REAL NOT NULL,
    learning_cost REAL NOT NULL,
    risk_score REAL NOT NULL,
    confidence REAL NOT NULL,
    status TEXT NOT NULL,
    selected_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence_artifacts (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    artifact_type TEXT NOT NULL,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    metadata_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
