import pytest
from backend.services.oswald.faculty.faculty_profile import FacultyProfile
from backend.services.oswald.faculty.teaching_session import TeachingSession

def test_faculty_profile():
    prof = FacultyProfile(
        faculty_id="f1",
        name="AI Foundations Instructor",
        title="Instructor",
        description="Teaches basic AI concepts",
        primary_domains=["AI"],
        source_document_ids=["doc1", "doc2"]
    )
    assert prof.status == "VALIDATED"
    assert "Socratic" in prof.allowed_instruction_modes

def test_teaching_session():
    session = TeachingSession(
        session_id="s1",
        faculty_id="f1",
        curriculum_id="c1",
        instruction_mode="Socratic"
    )
    assert session.status == "PLANNED"
    session.misconceptions_detected.append("Confuses weights and biases")
    assert len(session.misconceptions_detected) == 1
