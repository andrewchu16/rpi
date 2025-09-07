import logging
from llama_cpp import Llama, LLAMA_POOLING_TYPE_MEAN
from src.chat.config import chat_config

logger = logging.getLogger(__name__)


class Embedding:
    def __init__(self) -> None:
        logger.info(
            f"Loading embedding model from {chat_config.embedding_model_name}..."
        )
        try:
            self.model = Llama(
                model_path=chat_config.embedding_model_name, embedding=True, dtype=None,
                pooling_type=LLAMA_POOLING_TYPE_MEAN,
            )
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise e
        logger.info("Embedding model loaded successfully!")

    def embed_query(self, query: str) -> list[float]:
        return self.model.embed(query)
