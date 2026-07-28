from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

@dataclass
class TeachingSession:
    session_id: str
    faculty_id: str
    curriculum_id: str
    instruction_mode: str
    status: str = "PLANNED"
    misconceptions_detected: List[str] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
