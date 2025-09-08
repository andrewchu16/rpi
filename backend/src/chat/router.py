from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID
from .schema import (
    ChatInfoOutput,
    ChatMessage,
    ChatMessageSender,
    Chat,
)
from .controller import chat_controller
from src.database import get_db
from .models import Message
from .dependencies import validate_chat_exists

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/create", response_model=Chat)
async def create_chat(db: AsyncSession = Depends(get_db)):
    """
    Create a new chat and return its ID.
    """
    return await chat_controller.create_chat(db)


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
    include_processing_info: bool = False,
    include_cache_info: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """
    Stream a response to the message. Can optionally include processing info and cache info events.
    """

    async def sse_stream():
        import json

        yield "event: start\n"
        yield f"data: {json.dumps({'type': 'status', 'content': 'streaming'})}\n\n"

        message_id = None
        async for item in chat_controller.response_stream(
            chat_id, message_content, db, include_processing_info, include_cache_info
        ):
            if isinstance(item, dict):
                if "event" in item:
                    
                    yield f"event: {item['event']}\n"
                    if item["event"] == "message_created":
                        message_id = item["data"]["message_id"]
                yield f"data: {json.dumps(item['data'])}\n\n"

        yield "event: done\n"
        yield f"data: {json.dumps({'type': 'status', 'content': '[END]', 'message_id': str(message_id) if message_id else None})}\n\n"

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
