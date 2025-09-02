from .schema import ChatMessage


def get_message_history(messages: list[ChatMessage]) -> list[ChatMessage]:
    """
    Get the message history.
    """
    return messages