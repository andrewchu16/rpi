import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .schema import (
    ChatMessage,
    ChatResponseInput,
    ChatResponseOutput,
    ChatResponseCacheInfo,
    ChatResponseProcessingInfo,
    MessageCreate,
    CacheInfoCreate,
    ProcessingInfoCreate,
)
from src.models import Message, CacheInfo, ProcessingInfo


class ChatController:
    def __init__(self):
        pass

    def get_info(self):
        return {
            "status": "ok",
            "message": "Message API is running",
            "timestamp": datetime.now(timezone.utc),
        }

    async def create_response(
        self, chat: ChatResponseInput, db: AsyncSession
    ) -> ChatResponseOutput:
        # Get the last user message
        if not chat.messages:
            raise ValueError("No messages provided")

        last_user_message = chat.messages[-1]
        
        # Ensure timestamp is timezone-aware
        timestamp = last_user_message.timestamp
        if timestamp and timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        elif not timestamp:
            timestamp = datetime.now(timezone.utc)

        # Save the user message to database
        user_message_db = Message(
            sender=last_user_message.sender.value,
            content=last_user_message.content,
            timestamp=timestamp,
        )
        db.add(user_message_db)
        await db.flush()  # Get the ID without committing

        # Create AI response message
        ai_response_content = f"Response to: {last_user_message.content}"
        ai_message_db = Message(
            sender="AI", content=ai_response_content, timestamp=datetime.now(timezone.utc)
        )
        db.add(ai_message_db)
        await db.flush()  # Get the ID without committing

        # Create response message with database ID
        response_message = ChatMessage(
            id=ai_message_db.id,
            sender="AI",
            content=ai_response_content,
            timestamp=ai_message_db.timestamp,
        )

        # Handle cache info if requested
        cache_info = None
        cache_info_db = CacheInfo(
            message_id=ai_message_db.id, hit=False, cache_timestamp=None, num_hits=0
        )
        db.add(cache_info_db)
        await db.flush()
        if chat.get_cache_info:
            cache_info = ChatResponseCacheInfo(
                id=cache_info_db.id,
                message_id=cache_info_db.message_id,
                hit=cache_info_db.hit,
                cache_timestamp=cache_info_db.cache_timestamp,
                num_hits=cache_info_db.num_hits,
            )

        # Handle processing info if requested
        processing_info = None
        processing_info_db = ProcessingInfo(
            message_id=ai_message_db.id,
            start_timestamp=datetime.now(timezone.utc),
            end_timestamp=datetime.now(timezone.utc),
        )
        db.add(processing_info_db)
        await db.flush()
        if chat.get_processing_info:
            processing_info = ChatResponseProcessingInfo(
                id=processing_info_db.id,
                message_id=processing_info_db.message_id,
                start_timestamp=processing_info_db.start_timestamp,
                end_timestamp=processing_info_db.end_timestamp,
            )

        # Commit all changes
        await db.commit()

        return ChatResponseOutput(
            message=response_message,
            cache_info=cache_info,
            processing_info=processing_info,
        )

    async def response_stream(self, messages: list[ChatMessage], db: AsyncSession):
        """
        Stream a response to the messages and save to database.
        """
        if not messages:
            return

        # Get the last user message
        last_user_message = messages[-1]
        
        # Ensure timestamp is timezone-aware
        timestamp = last_user_message.timestamp
        if timestamp and timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        elif not timestamp:
            timestamp = datetime.now(timezone.utc)

        # Save the user message to database
        user_message_db = Message(
            sender=last_user_message.sender.value,
            content=last_user_message.content,
            timestamp=timestamp,
        )
        db.add(user_message_db)
        await db.flush()

        # Create AI response message
        ai_message_db = Message(
            sender="AI", content="Streamed response", timestamp=datetime.now(timezone.utc)
        )
        db.add(ai_message_db)
        await db.flush()

        cache_info_db = CacheInfo(
            message_id=ai_message_db.id, hit=False, cache_timestamp=None, num_hits=0
        )
        db.add(cache_info_db)
        await db.flush()

        processing_info_db = ProcessingInfo(
            message_id=ai_message_db.id,
            start_timestamp=datetime.now(timezone.utc),
            end_timestamp=datetime.now(timezone.utc),
        )
        db.add(processing_info_db)
        await db.flush()

        # Stream tokens
        for i in range(5):
            await asyncio.sleep(0.2)
            yield f"data: token-{i}\n\n"

        # Update AI message with final content
        ai_message_db.content = "Streamed response completed"
        await db.commit()


chat_controller = ChatController()
