"""
store.py — In-memory vector store using numpy for fast cosine similarity.
"""
import logging
from typing import List, Dict
import numpy as np
from openai import AsyncOpenAI
from agent.config import settings

logger = logging.getLogger("knowledge-store")

class KnowledgeStore:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embeddings: np.ndarray = np.array([])
        self.chunks: List[Dict] = []
        self._is_loaded = False
        
    async def get_embedding(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return []

    def set_data(self, chunks: List[Dict], embeddings_matrix: List[List[float]]):
        """Used by the loader to inject data into the store."""
        self.chunks = chunks
        self.embeddings = np.array(embeddings_matrix)
        self._is_loaded = True
        logger.info(f"Loaded {len(self.chunks)} knowledge chunks into memory.")

    async def search(self, query: str, top_k: int = 3) -> str:
        if not self._is_loaded or len(self.chunks) == 0:
            return "I'm sorry, my knowledge base is currently offline or empty."
            
        query_embedding = await self.get_embedding(query)
        if not query_embedding:
            return "Internal error accessing knowledge base."
            
        q_vec = np.array(query_embedding)
        
        # Calculate cosine similarity quickly using numpy
        norms = np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q_vec)
        # Avoid division by zero
        norms[norms == 0] = 1e-10
        similarities = np.dot(self.embeddings, q_vec) / norms
        
        # Get top k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.3: # Minimum similarity threshold
                results.append(self.chunks[idx].get("content", ""))
                
        if not results:
            return "I couldn't find any relevant information in the clinic's knowledge base regarding that."
            
        return "\n\n".join(results)

# Global singleton instance
knowledge_store = KnowledgeStore()
