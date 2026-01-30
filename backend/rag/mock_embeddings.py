"""
Mock embeddings for testing without OpenAI API key.
Compatible with LangChain's embedding interface.
"""
import numpy as np
from typing import List, Any


class MockEmbeddings:
    """Mock embeddings that return random vectors for testing."""
    
    def __init__(self, **kwargs: Any):
        """Initialize mock embeddings (accepts kwargs for compatibility)."""
        self.embedding_dimension = 1536  # Same as OpenAI ada-002
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for documents."""
        embeddings = []
        for text in texts:
            # Create deterministic but random-looking embeddings based on text
            np.random.seed(hash(text) % (2**32))
            embedding = np.random.normal(0, 0.1, self.embedding_dimension).tolist()
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """Generate mock embedding for query."""
        np.random.seed(hash(text) % (2**32))
        return np.random.normal(0, 0.1, self.embedding_dimension).tolist()
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Make it callable like OpenAIEmbeddings."""
        return self.embed_documents(input)

