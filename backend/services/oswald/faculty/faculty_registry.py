from typing import Dict, List, Optional
from .faculty_profile import FacultyProfile

class FacultyRegistry:
    def __init__(self):
        self.profiles: Dict[str, FacultyProfile] = {}

    def register_faculty(self, profile: FacultyProfile):
        self.profiles[profile.faculty_id] = profile

    def get_faculty(self, faculty_id: str) -> Optional[FacultyProfile]:
        return self.profiles.get(faculty_id)

    def find_faculty_for_domain(self, domain: str) -> List[FacultyProfile]:
        return [p for p in self.profiles.values() if domain in p.primary_domains and p.status == "VALIDATED"]
