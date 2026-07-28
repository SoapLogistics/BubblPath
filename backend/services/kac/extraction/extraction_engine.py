from typing import List, Dict, Any
from .extractors import FactExtractor, ConceptExtractor, AlgorithmExtractor, PredictionExtractor
from .knowledge_value import calculate_knowledge_value
from ..parser.canonical_document import CanonicalDocument

class ExtractionEngine:
    """
    Orchestrates the conversion of CanonicalDocuments into Intelligence Artifacts.
    """
    def __init__(self):
        self.extractors = [
            FactExtractor(),
            ConceptExtractor(),
            AlgorithmExtractor(),
            PredictionExtractor()
        ]

    def extract_intelligence(self, document: CanonicalDocument) -> Dict[str, Any]:
        """
        Extracts intelligence and computes knowledge values.
        Returns a dict of extracted items categorized.
        """
        results = {
            "facts": [],
            "concepts": [],
            "algorithms": [],
            "predictions": []
        }

        for section in document.sections:
            for paragraph in section.paragraphs:
                for extractor in self.extractors:
                    extracted_items = extractor.extract(paragraph)
                    for item in extracted_items:
                        # Score the knowledge
                        item['knowledge_value'] = calculate_knowledge_value({
                            "novelty": 0.6,
                            "reuse_potential": 0.7 if item['type'] in ['algorithm', 'prediction'] else 0.4
                        })

                        # Add provenance
                        item['source'] = {
                            "document_sha256": document.metadata.sha256,
                            "section": section.title,
                            "page": paragraph.page_number
                        }

                        if item['type'] == 'fact':
                            results['facts'].append(item)
                        elif item['type'] == 'concept':
                            results['concepts'].append(item)
                        elif item['type'] == 'algorithm':
                            results['algorithms'].append(item)
                        elif item['type'] == 'prediction':
                            results['predictions'].append(item)

        return results
