from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

@dataclass
class Lesson:
    lesson_id: str
    title: str
    source_assignment_id: str
    extraction_goal: str
    status: str = "PENDING"

@dataclass
class Module:
    module_id: str
    title: str
    lessons: List[Lesson] = field(default_factory=list)
    status: str = "PENDING"

@dataclass
class Course:
    course_id: str
    title: str
    modules: List[Module] = field(default_factory=list)
    status: str = "PENDING"

@dataclass
class LearningPath:
    path_id: str
    goal_id: str
    courses: List[Course] = field(default_factory=list)
    status: str = "PLANNED"
    created_at: float = field(default_factory=time.time)
