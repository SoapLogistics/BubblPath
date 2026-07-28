from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

@dataclass
class SourceRecord:
    source_id: str
    original_filename: str
    display_title: str
    authors: List[str] = field(default_factory=list)
    publisher: Optional[str] = None
    publication_date: Optional[str] = None
    edition: Optional[str] = None
    isbn: Optional[str] = None
    language: str = "en"
    source_type: str = "unknown"
    file_size: int = 0
    sha256: str = ""
    content_fingerprint: str = ""
    upload_session_id: str = ""
    uploaded_at: float = field(default_factory=time.time)
    uploaded_by: str = "system"
    collection_ids: List[str] = field(default_factory=list)
    topic_tags: List[str] = field(default_factory=list)
    priority: int = 50
    processing_status: str = "UPLOADING"
    parser_status: str = "PENDING"
    extraction_status: str = "PENDING"
    governance_status: str = "PENDING"
    vault_id: Optional[str] = None
    vault_document_id: Optional[str] = None
    duplicate_group_id: Optional[str] = None
    parent_source_id: Optional[str] = None
    related_source_ids: List[str] = field(default_factory=list)
    notes: str = ""
    last_error: Optional[str] = None
    last_updated: float = field(default_factory=time.time)

@dataclass
class OswaldCollection:
    collection_id: str
    name: str
    description: str
    owner: str = "system"
    topic_tags: List[str] = field(default_factory=list)
    priority: int = 50
    preferred_vault_destination: str = "General Vault"
    default_governance_level: str = "Review-Gated"

@dataclass
class ImportSession:
    session_id: str
    created_at: float = field(default_factory=time.time)
    created_by: str = "system"
    source_count: int = 0
    total_size: int = 0
    accepted_count: int = 0
    rejected_count: int = 0
    duplicate_count: int = 0
    queued_count: int = 0
    failed_count: int = 0
    collection_assignment: Optional[str] = None
    default_priority: int = 50
    notes: str = ""
    status: str = "IN_PROGRESS"
