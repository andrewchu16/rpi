import logging
from typing import List
import asyncio
from functools import partial
from sentence_transformers import SentenceTransformer
from src.chat.config import chat_config

logger = logging.getLogger(__name__)


class Embedding:
    """Embedding service that uses sentence-transformers with mixedbread-ai/mxbai-embed-xsmall-v1."""
    
    def __init__(self) -> None:
        """Initialize the embedding service with sentence-transformers model."""
        self.model_name = "mixedbread-ai/mxbai-embed-xsmall-v1"
        self._model: SentenceTransformer | None = None
        logger.info(f"Embedding service configured to use model: {self.model_name}")

    def preload_model(self) -> None:
        """Preload the embedding model during application startup."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")

    @property
    def model(self) -> SentenceTransformer:
        """Get the embedding model, loading it if necessary."""
        if self._model is None:
            self.preload_model()
        return self._model

    async def embed_query(self, query: str) -> List[float]:
        """Generate embeddings for a query using sentence-transformers.
        
        Args:
            query: Text to embed
            
        Returns:
            List of embedding values truncated to 384 dimensions
            
        Raises:
            Exception: If embedding generation fails
        """
        try:
            # Run the embedding in a thread pool to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            model = self.model
            
            # Generate embedding using the model
            embedding_func = partial(model.encode, query, convert_to_tensor=False)
            embedding = await loop.run_in_executor(None, embedding_func)
            
            # Convert to list and truncate to 384 dimensions as requested
            embedding_list = embedding.tolist()
            if len(embedding_list) > chat_config.embedding_dim:
                embedding_list = embedding_list[:chat_config.embedding_dim]
                logger.debug(f"Truncated embedding from {len(embedding)} to {chat_config.embedding_dim} dimensions")
            
            return embedding_list
                
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise Exception(f"Failed to generate embedding: {e}")
