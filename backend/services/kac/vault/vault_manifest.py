from dataclasses import dataclass, field
from typing import List, Dict, Any
import time

@dataclass
class VaultManifest:
    vault_id: str
    vault_name: str
    topics: List[str]
    creation_date: float = field(default_factory=time.time)
    parser_version: str = "1.0"
    extraction_version: str = "1.0"
    book_count: int = 0
    document_count: int = 0
    original_size_bytes: int = 0
    compressed_size_bytes: int = 0
    knowledge_cards_count: int = 0
    memory_atoms_count: int = 0
    algorithms_count: int = 0
    prediction_models_count: int = 0
    formulas_count: int = 0
    images_count: int = 0
    average_quality: float = 1.0
    integrity_hash: str = ""
    last_verification: float = 0.0
    last_reprocessing: float = 0.0
    status: str = "ACTIVE"
    documents: Dict[str, str] = field(default_factory=dict) # hash -> original_filename

    @property
    def compression_ratio(self) -> float:
        if self.original_size_bytes == 0:
            return 1.0
        return self.compressed_size_bytes / self.original_size_bytes

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d['compression_ratio'] = self.compression_ratio
        return d
