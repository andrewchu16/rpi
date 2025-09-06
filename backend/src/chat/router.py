from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from .schema import (
    ChatInfoOutput,
    ChatMessage,
    ChatResponseInput,
    ChatResponseOutput,
    ChatMessageSender,
    Chat,
)
from .controller import chat_controller
from src.database import get_db
from .models import Message

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
    return await chat_controller.create_response(chat, db)


@router.get("/info")
async def get_info(db: AsyncSession = Depends(get_db)) -> ChatInfoOutput:
    """
    Get statistics about messages.
    """
    return await chat_controller.get_info(db)


@router.post("/stream")
async def stream_response(
    chat_id: UUID, message_content: str, db: AsyncSession = Depends(get_db)
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


@router.get("/messages", response_model=List[ChatMessage])
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
        raise HTTPException(status_code=400, detail="Limit cannot exceed 1000")

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


@router.get("/messages/{message_id}/cache")
async def get_message_cache_info(message_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Get cache information for a specific message.
    """
    try:
        return await chat_controller.get_message_cache_info(message_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/messages/{message_id}/processing")
async def get_message_processing_info(
    message_id: UUID, db: AsyncSession = Depends(get_db)
):
    """
    Get processing information for a specific message.
    """
    try:
        return await chat_controller.get_message_processing_info(message_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
