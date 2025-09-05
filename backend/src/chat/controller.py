import asyncio
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from .schema import (
    ChatMessage,
    ChatResponseInput,
    ChatResponseOutput,
    ChatResponseCacheInfo,
    ChatResponseProcessingInfo,
    ChatInfoOutput,
)
from .services.llm import LLM
from src.models import Message, CacheInfo, ProcessingInfo


class ChatController:
    def __init__(self):
        """Initialize the chat controller with transformers-based LLM service."""
        self._llm: LLM | None = None

    @property
    def llm(self) -> LLM:
        """Lazy initialization of LLM service."""
        if self._llm is None:
            self._llm = LLM()
        return self._llm

    async def get_info(self, db: AsyncSession) -> ChatInfoOutput:
        count = (await db.execute(select(func.count(Message.id)))).scalar()
        average_response_time = (await db.execute(select(func.avg(ProcessingInfo.end_timestamp - ProcessingInfo.start_timestamp)))).scalar()
        if average_response_time is None:
            average_response_time = 0
        return ChatInfoOutput(
            messages_received=count,
            average_response_time=average_response_time,
        )

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

        # Generate AI response using MLX LLM
        start_time = datetime.now(timezone.utc)
        ai_response_content = await self.llm.generate_response(chat.messages)
        end_time = datetime.now(timezone.utc)

        # Create AI response message
        ai_message_db = Message(
            sender="AI", content=ai_response_content, timestamp=end_time
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
            start_timestamp=start_time,
            end_timestamp=end_time,
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
            sender="AI", content="", timestamp=datetime.now(timezone.utc)
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
            end_timestamp=None,
        )
        db.add(processing_info_db)
        await db.flush()

        # Stream response using MLX LLM
        accumulated_content = ""
        async for token in self.llm.stream_response(messages):
            accumulated_content = token
            yield f"data: {token}\n\n"

        # Update AI message with final content
        ai_message_db.content = accumulated_content
        processing_info_db.end_timestamp = datetime.now(timezone.utc)
        await db.commit()


chat_controller = ChatController()
