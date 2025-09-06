from pydantic_settings import BaseSettings


class ChatConfig(BaseSettings):
    max_messages: int = 50  # in messages
    max_message_chars: int = 500  # in characters

    max_context_length: int = 500  # in tokens
    max_response_tokens: int = 300  # in tokens
    
    llm_model_name: str = "./models/Llama-3.2-1B-Instruct-Q4_K_S.gguf"
    embedding_model_name: str = "./models/embeddinggemma-300M-BF16.gguf"
    
    vector_store_path: str = "./stores/vector_store"


chat_config = ChatConfig()
