from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

@dataclass
class FacultyProfile:
    faculty_id: str
    name: str
    title: str
    description: str
    primary_domains: List[str]
    source_document_ids: List[str]
    expertise_score: float = 1.0
    status: str = "VALIDATED"
    allowed_instruction_modes: List[str] = field(default_factory=lambda: ["Direct", "Socratic", "Examples"])
    created_at: float = field(default_factory=time.time)
