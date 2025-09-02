from pydantic_settings import BaseSettings


class ChatConfig(BaseSettings):
    max_messages: int = 50  # in messages
    max_message_length: int = 500  # in characters

    max_context_length: int = 500  # in tokens
    max_response_length: int = 300  # in otkens


chat_config = ChatConfig()
