from pydantic_settings import BaseSettings


class ChatConfig(BaseSettings):
    max_messages: int = 50  # in messages
    max_message_chars: int = 500  # in characters

    max_context_length: int = 500  # in tokens
    max_response_tokens: int = 300  # in tokens
    
    model_name: str = "./models/Llama-3.2-1B-Instruct-IQ4_XS.gguf"


chat_config = ChatConfig()
