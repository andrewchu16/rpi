from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from .models import Chat, Message
from src.database import get_db


async def validate_chat_exists(
    chat_id: UUID, db: AsyncSession = Depends(get_db)
) -> UUID:
    """
    Dependency to validate that a chat with the given UUID exists.

    Args:
        chat_id: The UUID of the chat to validate
        db: Database session

    Returns:
        The validated chat UUID

    Raises:
        HTTPException: 404 if chat not found
    """
    result = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = result.scalar_one_or_none()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat with ID {chat_id} not found",
        )

    return chat_id


async def validate_message_exists(
    message_id: UUID, db: AsyncSession = Depends(get_db)
) -> UUID:
    """
    Dependency to validate that a message with the given UUID exists.

    Args:
        message_id: The UUID of the message to validate
        db: Database session

    Returns:
        The validated message UUID

    Raises:
        HTTPException: 404 if message not found
    """
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with ID {message_id} not found",
        )

    return message_id
