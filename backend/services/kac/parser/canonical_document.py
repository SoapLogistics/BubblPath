from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class CanonicalMetadata:
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    language: Optional[str] = None
    pages: int = 0
    file_size: int = 0
    sha256: str = ""
    source_type: str = "unknown"
    parser_version: str = "1.0"

@dataclass
class CanonicalParagraph:
    content: str
    page_number: Optional[int] = None
    classification: Optional[str] = None  # Future KEE usage

@dataclass
class CanonicalSection:
    title: str
    paragraphs: List[CanonicalParagraph] = field(default_factory=list)
    subsections: List['CanonicalSection'] = field(default_factory=list)

@dataclass
class CanonicalDocument:
    metadata: CanonicalMetadata
    sections: List[CanonicalSection] = field(default_factory=list)
    quality_score: float = 1.0
    extraction_confidence: float = 1.0

    def to_dict(self) -> dict:
        def section_to_dict(s: CanonicalSection):
            return {
                "title": s.title,
                "paragraphs": [{"content": p.content, "page_number": p.page_number} for p in s.paragraphs],
                "subsections": [section_to_dict(sub) for sub in s.subsections]
            }

        return {
            "metadata": self.metadata.__dict__,
            "sections": [section_to_dict(s) for s in self.sections],
            "quality_score": self.quality_score,
            "extraction_confidence": self.extraction_confidence
        }
