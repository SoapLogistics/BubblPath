import os
import openai
import logging
from typing import List

logger = logging.getLogger("MnemosyneEmbeddings")

class EmbeddingGenerator:
    """Generates Vector Embeddings for Project Solomon via OpenAI API."""
    def __init__(self):
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def get_embedding(self, text: str) -> List[float]:
        try:
            # Replaces newlines to improve embedding quality per OpenAI best practices
            text = text.replace("\n", " ")
            response = openai.Embedding.create(
                input=[text],
                model="text-embedding-ada-002"
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []
