from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from .schema import (
    ChatInfoOutput,
    ChatMessage,
    ChatResponseCacheInfo,
    ChatResponseInput,
    ChatResponseOutput,
    ChatMessageSender,
    Chat,
    ChatResponseProcessingInfo,
)
from .controller import chat_controller
from src.database import get_db
from .models import Message
from .dependencies import validate_chat_exists, validate_message_exists

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/create", response_model=Chat)
async def create_chat(db: AsyncSession = Depends(get_db)):
    """
    Create a new chat and return its ID.
    """
    return await chat_controller.create_chat(db)


@router.post("/response", response_model=ChatResponseOutput)
async def get_response(chat: ChatResponseInput, db: AsyncSession = Depends(get_db)):
    """
    Get a response to the chat.
    """
    # Validate chat exists before processing
    await validate_chat_exists(chat.chat_id, db)
    return await chat_controller.create_response(chat, db)


@router.get("/info", response_model=ChatInfoOutput)
async def get_info(db: AsyncSession = Depends(get_db)) -> ChatInfoOutput:
    """
    Get statistics about messages.
    """
    return await chat_controller.get_info(db)


@router.post("/stream")
async def stream_response(
    chat_id: UUID = Depends(validate_chat_exists),
    message_content: str = ...,
    db: AsyncSession = Depends(get_db),
):
    """
    Stream a response to the message. Only streams the response string.
    """

    async def sse_stream():
        yield "event: start\n"
        yield "data: streaming\n\n"
        async for token in chat_controller.response_stream(
            chat_id, message_content, db
        ):
            yield token
        yield "event: done\n"
        yield "data: [END]\n\n"

    headers = {"X-Accel-Buffering": "no"}
    return StreamingResponse(
        sse_stream(), media_type="text/event-stream", headers=headers
    )


@router.get("/messages", response_model=list[ChatMessage])
async def get_messages(
    chat_id: Optional[UUID] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    Get stored messages from the database.
    If chat_id is provided, only return messages from that chat.
    Otherwise, return all messages.
    """
    if limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Limit cannot exceed 1000"
        )

    # Validate chat exists if chat_id is provided
    if chat_id is not None:
        await validate_chat_exists(chat_id, db)

    query = (
        select(Message).order_by(Message.timestamp.desc()).limit(limit).offset(offset)
    )

    if chat_id is not None:
        query = query.where(Message.chat_id == chat_id)

    result = await db.execute(query)
    messages = result.scalars().all()

    return [
        ChatMessage(
            id=msg.id,
            chat_id=msg.chat_id,
            sender=ChatMessageSender(msg.sender),
            content=msg.content,
            timestamp=msg.timestamp,
        )
        for msg in messages
    ]


@router.get("/messages/{message_id}/cache", response_model=ChatResponseCacheInfo)
async def get_message_cache_info(
    message_id: UUID = Depends(validate_message_exists),
    db: AsyncSession = Depends(get_db),
):
    """
    Get cache information for a specific message.
    """
    try:
        return await chat_controller.get_message_cache_info(message_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/messages/{message_id}/processing", response_model=ChatResponseProcessingInfo
)
async def get_message_processing_info(
    message_id: UUID = Depends(validate_message_exists),
    db: AsyncSession = Depends(get_db),
):
    """
    Get processing information for a specific message.
    """
    try:
        return await chat_controller.get_message_processing_info(message_id, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
