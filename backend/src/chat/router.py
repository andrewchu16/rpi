from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from .schema import ChatMessage, ChatResponseInput, ChatResponseOutput, ChatSender
from .controller import chat_controller
from src.database import get_db
from src.models import Message, CacheInfo, ProcessingInfo

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/response", response_model=ChatResponseOutput)
async def get_response(chat: ChatResponseInput, db: AsyncSession = Depends(get_db)):
    """
    Get a response to the chat.
    """
    return await chat_controller.create_response(chat, db)


@router.get("/info")
async def get_info():
    """
    Get statistics about messages.
    """
    return chat_controller.get_info()


@router.post("/stream")
async def stream_response(
    messages: list[ChatMessage], db: AsyncSession = Depends(get_db)
):
    """
    Stream a response to the messages. Only streams the response string.
    """

    async def sse_stream():
        yield "event: start\n"
        yield "data: streaming\n\n"
        async for token in chat_controller.response_stream(messages, db):
            yield token
        yield "event: done\n"
        yield "data: [END]\n\n"

    headers = {"X-Accel-Buffering": "no"}
    return StreamingResponse(sse_stream(), media_type="text/event-stream", headers=headers)


@router.get("/messages", response_model=List[ChatMessage])
async def get_messages(
    limit: int = 100, offset: int = 0, db: AsyncSession = Depends(get_db)
):
    """
    Get stored messages from the database.
    """
    if limit > 1000:
        raise HTTPException(status_code=400, detail="Limit cannot exceed 1000")

    result = await db.execute(
        select(Message).order_by(Message.timestamp.desc()).limit(limit).offset(offset)
    )
    messages = result.scalars().all()

    return [
        ChatMessage(
            id=msg.id,
            sender=ChatSender(msg.sender),
            content=msg.content,
            timestamp=msg.timestamp,
        )
        for msg in messages
    ]


@router.get("/messages/{message_id}/cache")
async def get_message_cache_info(message_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get cache information for a specific message.
    """
    result = await db.execute(
        select(CacheInfo).where(CacheInfo.message_id == message_id)
    )
    cache_info = result.scalar_one_or_none()

    if not cache_info:
        raise HTTPException(status_code=404, detail="Cache info not found")

    return {
        "id": cache_info.id,
        "message_id": cache_info.message_id,
        "hit": cache_info.hit,
        "cache_timestamp": cache_info.cache_timestamp,
        "num_hits": cache_info.num_hits,
    }


@router.get("/messages/{message_id}/processing")
async def get_message_processing_info(
    message_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get processing information for a specific message.
    """
    result = await db.execute(
        select(ProcessingInfo).where(ProcessingInfo.message_id == message_id)
    )
    processing_info = result.scalar_one_or_none()

    if not processing_info:
        raise HTTPException(status_code=404, detail="Processing info not found")

    return {
        "id": processing_info.id,
        "message_id": processing_info.message_id,
        "start_timestamp": processing_info.start_timestamp,
        "end_timestamp": processing_info.end_timestamp,
    }
