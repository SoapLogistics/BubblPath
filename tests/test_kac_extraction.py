import pytest
from backend.services.kac.extraction.extraction_engine import ExtractionEngine
from backend.services.kac.parser.canonical_document import CanonicalDocument, CanonicalMetadata, CanonicalSection, CanonicalParagraph

def test_extraction_engine():
    ee = ExtractionEngine()

    doc = CanonicalDocument(
        metadata=CanonicalMetadata(sha256="testhash123"),
        sections=[
            CanonicalSection(
                title="Chapter 1",
                paragraphs=[
                    CanonicalParagraph("This is a fact about the world."),
                    CanonicalParagraph("An algorithm for sorting is quicksort."),
                    CanonicalParagraph("If the sun is shining, probability of rain is low.")
                ]
            )
        ]
    )

    results = ee.extract_intelligence(doc)

    assert len(results["facts"]) > 0
    assert len(results["algorithms"]) > 0
    assert len(results["predictions"]) > 0

    # Check knowledge values and provenance
    assert "knowledge_value" in results["facts"][0]
    assert results["facts"][0]["source"]["document_sha256"] == "testhash123"
