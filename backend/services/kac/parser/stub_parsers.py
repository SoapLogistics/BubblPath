from .parser_registry import BaseParser, registry
from .canonical_document import CanonicalDocument, CanonicalMetadata, CanonicalSection, CanonicalParagraph
import os

class StubEpubParser(BaseParser):
    def parse(self) -> CanonicalDocument:
        meta = CanonicalMetadata(title=f"Parsed EPUB {os.path.basename(self.filepath)}", source_type="epub")
        section = CanonicalSection(title="Chapter 1", paragraphs=[
            CanonicalParagraph("This is stub content from an EPUB.")
        ])
        return CanonicalDocument(metadata=meta, sections=[section])

class StubPdfParser(BaseParser):
    def parse(self) -> CanonicalDocument:
        meta = CanonicalMetadata(title=f"Parsed PDF {os.path.basename(self.filepath)}", source_type="pdf")
        section = CanonicalSection(title="Introduction", paragraphs=[
            CanonicalParagraph("This is stub content from a PDF.", page_number=1)
        ])
        return CanonicalDocument(metadata=meta, sections=[section])

class StubMarkdownParser(BaseParser):
    def parse(self) -> CanonicalDocument:
        meta = CanonicalMetadata(title=f"Parsed Markdown {os.path.basename(self.filepath)}", source_type="markdown")
        section = CanonicalSection(title="Header 1", paragraphs=[
            CanonicalParagraph("This is stub content from a Markdown file.")
        ])
        return CanonicalDocument(metadata=meta, sections=[section])

# Register the stubs
registry.register_parser('.epub', StubEpubParser)
registry.register_parser('.pdf', StubPdfParser)
registry.register_parser('.md', StubMarkdownParser)
registry.register_parser('.txt', StubMarkdownParser)  # Fallback for now
