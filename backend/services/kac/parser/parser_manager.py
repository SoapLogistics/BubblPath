import os
import json
from .parser_registry import registry
from .stub_parsers import *  # ensure parsers are registered
from .canonical_document import CanonicalDocument

class ParserManager:
    def __init__(self, output_dir: str = "kac_canonical_docs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def process_file(self, filepath: str, file_hash: str) -> CanonicalDocument:
        """
        Takes a raw file, finds the right parser, parses it into a CanonicalDocument,
        and saves it.
        """
        _, ext = os.path.splitext(filepath)
        parser_class = registry.get_parser(ext)

        if not parser_class:
            # Fallback to markdown/text parser if unknown
            parser_class = registry.get_parser('.txt')

        parser_inst = parser_class(filepath)
        canonical_doc = parser_inst.parse()

        # Update metadata with known fields
        canonical_doc.metadata.sha256 = file_hash
        canonical_doc.metadata.file_size = os.path.getsize(filepath)

        # Save to disk
        save_path = os.path.join(self.output_dir, f"{file_hash}.json")
        with open(save_path, "w") as f:
            json.dump(canonical_doc.to_dict(), f, indent=4)

        return canonical_doc
