from llama_cpp import np
from src.chat.config import chat_config
from sentence_transformers import SentenceTransformer


class Embedding:
    def __init__(self) -> None:
        self.model = SentenceTransformer(chat_config.embedding_model_name)

    def embed_query(self, query: str) -> np.ndarray:
        return self.model.encode(query)
