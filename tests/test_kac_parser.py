import pytest
import os
from backend.services.kac.parser.parser_manager import ParserManager
from backend.services.kac.parser.canonical_document import CanonicalDocument

def test_parser_manager_stub(tmp_path):
    output_dir = tmp_path / "kac_canonical_docs"
    pm = ParserManager(output_dir=str(output_dir))

    # Create a dummy file
    dummy_file = tmp_path / "dummy.epub"
    dummy_file.write_text("dummy epub content")

    doc = pm.process_file(str(dummy_file), "fakehash123")

    assert isinstance(doc, CanonicalDocument)
    assert doc.metadata.source_type == "epub"
    assert "fakehash123" in doc.metadata.sha256
    assert len(doc.sections) > 0

    # Check if saved
    saved_path = output_dir / "fakehash123.json"
    assert saved_path.exists()
