from typing import Optional
from typing import Dict, Type
from .canonical_document import CanonicalDocument

class BaseParser:
    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self) -> CanonicalDocument:
        raise NotImplementedError("Parsers must implement parse()")

class ParserRegistry:
    def __init__(self):
        self._parsers: Dict[str, Type[BaseParser]] = {}

    def register_parser(self, extension: str, parser_class: Type[BaseParser]):
        self._parsers[extension.lower()] = parser_class

    def get_parser(self, extension: str) -> Optional[Type[BaseParser]]:
        return self._parsers.get(extension.lower())

registry = ParserRegistry()
