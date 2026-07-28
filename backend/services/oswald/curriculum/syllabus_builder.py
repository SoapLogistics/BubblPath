import uuid
from typing import List, Dict, Any
from .learning_path import LearningPath, Course, Module, Lesson

class SyllabusBuilder:
    def build_syllabus(self, goal_id: str, objectives: List[Any], sources: List[Dict[str, Any]]) -> LearningPath:
        path_id = str(uuid.uuid4())
        courses = []

        # Naive matching of sources to objectives
        for obj in objectives:
            modules = []
            for source in sources:
                if any(kw in source.get("display_title", "").lower() for kw in obj.description.lower().split()):
                    lesson = Lesson(str(uuid.uuid4()), f"Study {source['display_title']}", source["source_id"], "Understand concepts")
                    modules.append(Module(str(uuid.uuid4()), f"Module for {obj.description[:20]}", [lesson]))
            if modules:
                courses.append(Course(str(uuid.uuid4()), f"Course: {obj.description}", modules))

        return LearningPath(path_id, goal_id, courses)
