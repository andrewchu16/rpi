from pydantic_settings import BaseSettings


class ChatConfig(BaseSettings):
    max_context_messages_count: int = 20
    max_context_message_chars: int = 500

    max_context_token_count: int = 500
    max_response_token_count: int = 300


    vector_store_path: str = "./stores/vector_store"
    
    # LLM settings
    llama_cpp_llm_server_url: str = "http://llama_cpp_llm_server:8000"
    llm_model_name: str = "./models/Llama-3.2-1B-Instruct-Q4_K_S.gguf"
    
    llama_cpp_embedding_server_url: str = "http://llama_cpp_embedding_server:8000"
    embedding_model_name: str = "./models/embeddinggemma-300M-BF16.gguf"


chat_config = ChatConfig()
