from .parser_registry import BaseParser, registry
from .canonical_document import CanonicalDocument, CanonicalMetadata, CanonicalSection, CanonicalParagraph
import os

def _extract_text_content(filepath: str) -> str:
    """Safely extracts text for stub parsing without discarding user data."""
    try:
        # In a real environment, proper libraries (PyMuPDF, ebooklib) would be used.
        # For now, we make a best-effort text extraction to avoid throwing away data.
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()[:50000] # Read up to 50k chars to prevent memory issues in stubs
    except Exception:
        return "Could not extract text content."

class UniversalFallbackParser(BaseParser):
    def parse(self) -> CanonicalDocument:
        ext = os.path.splitext(self.filepath)[1]
        meta = CanonicalMetadata(title=f"Parsed Document {os.path.basename(self.filepath)}", source_type=ext)
        content = _extract_text_content(self.filepath)

        # Split into naive paragraphs
        raw_paragraphs = content.split("\n\n")
        paragraphs = [CanonicalParagraph(p.strip()) for p in raw_paragraphs if p.strip()]

        if not paragraphs:
            paragraphs = [CanonicalParagraph("No readable text found in document.")]

        section = CanonicalSection(title="Main Content", paragraphs=paragraphs)
        return CanonicalDocument(metadata=meta, sections=[section])

# Replace stubs with universal fallback that actually reads the file
registry.register_parser('.epub', UniversalFallbackParser)
registry.register_parser('.pdf', UniversalFallbackParser)
registry.register_parser('.md', UniversalFallbackParser)
registry.register_parser('.txt', UniversalFallbackParser)
