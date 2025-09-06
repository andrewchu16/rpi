from typing import List
from .schema import ChatMessage
from .config import chat_config


def get_message_history(messages: list[ChatMessage]) -> list[ChatMessage]:
    """
    Get the message history.
    """
    return messages


def shorten_chat_messages(messages: List[ChatMessage]) -> List[ChatMessage]:
    """
    Shorten a list of chat messages to comply with the max restrictions in chat config.

    This function applies the following restrictions:
    1. Limits the number of messages to max_messages (keeping most recent)
    2. Truncates individual messages to max_message_chars
    3. Considers max_context_length for token estimation

    Args:
        messages: List of chat messages to shorten

    Returns:
        Shortened list of chat messages that complies with restrictions
    """
    if not messages:
        return messages

    # Step 1: Limit number of messages (keep most recent)
    if len(messages) > chat_config.max_context_messages_count:
        messages = messages[-chat_config.max_context_messages_count :]

    # Step 2: Truncate individual messages to max_message_chars
    shortened_messages = []
    for message in messages:
        if len(message.content) > chat_config.max_context_message_chars:
            truncated_content = (
                message.content[: chat_config.max_context_message_chars - 3] + "..."
            )
            # Create a new ChatMessage with truncated content
            shortened_message = ChatMessage(
                id=message.id,
                sender=message.sender,
                content=truncated_content,
                timestamp=message.timestamp,
            )
            shortened_messages.append(shortened_message)
        else:
            shortened_messages.append(message)

    # Step 3: Estimate token count and further reduce if needed
    # Simple token estimation: ~4 characters per token (rough approximation)
    estimated_tokens = sum(len(msg.content) for msg in shortened_messages) // 4

    # If we exceed max_context_length, remove older messages
    while (
        estimated_tokens > chat_config.max_context_token_count
        and len(shortened_messages) > 1
    ):
        # Remove the oldest message (but keep at least the last message)
        removed_message = shortened_messages.pop(0)
        estimated_tokens -= len(removed_message.content) // 4

    return shortened_messages
