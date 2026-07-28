from typing import List, Dict, Any
from ..parser.canonical_document import CanonicalParagraph

class BaseExtractor:
    def extract(self, paragraph: CanonicalParagraph) -> List[Dict[str, Any]]:
        raise NotImplementedError()

class FactExtractor(BaseExtractor):
    def extract(self, paragraph: CanonicalParagraph) -> List[Dict[str, Any]]:
        # Stub logic: assumes sentences with "is", "are" might contain facts.
        facts = []
        if " is " in paragraph.content or " are " in paragraph.content:
            facts.append({"type": "fact", "content": paragraph.content, "confidence": 0.8})
        return facts

class ConceptExtractor(BaseExtractor):
    def extract(self, paragraph: CanonicalParagraph) -> List[Dict[str, Any]]:
        # Stub logic: simple keyword extraction
        words = paragraph.content.split()
        concepts = []
        for w in words:
            if len(w) > 6 and w[0].isupper():
                concepts.append({"type": "concept", "name": w})
        return concepts

class AlgorithmExtractor(BaseExtractor):
    def extract(self, paragraph: CanonicalParagraph) -> List[Dict[str, Any]]:
        algorithms = []
        if any(kw in paragraph.content.lower() for kw in ["algorithm", "sort", "search", "tree", "graph"]):
            algorithms.append({"type": "algorithm", "description": paragraph.content})
        return algorithms

class PredictionExtractor(BaseExtractor):
    def extract(self, paragraph: CanonicalParagraph) -> List[Dict[str, Any]]:
        predictions = []
        if any(kw in paragraph.content.lower() for kw in ["if", "when", "usually", "probability", "likely"]):
            predictions.append({"type": "prediction", "statement": paragraph.content})
        return predictions
