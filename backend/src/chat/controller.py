from datetime import datetime, timezone, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from .config import chat_config
from .schema import (
    ChatMessage,
    ChatResponseCacheInfo,
    ChatResponseProcessingInfo,
    ChatInfoOutput,
    ChatMessageSender,
    Chat,
)
from .services.llm import LLM
from .models import Message, CacheInfo, ProcessingInfo, Chat as ChatModel
from .utils import shorten_chat_messages


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

    async def create_chat(self, db: AsyncSession) -> Chat:
        """Create a new chat and return its information."""
        chat_db = ChatModel()
        db.add(chat_db)
        await db.flush()  # Get the ID without committing
        await db.commit()

        return Chat(
            id=chat_db.id,
            created_at=chat_db.created_at,
        )

    async def get_info(self, db: AsyncSession) -> ChatInfoOutput:
        chats_count = (await db.execute(select(func.count(ChatModel.id)))).scalar()
        messages_count = (
            await db.execute(
                select(func.count(Message.id)).where(
                    Message.sender == ChatMessageSender.USER.value
                )
            )
        ).scalar()
        average_response_time: timedelta | None = (
            await db.execute(
                select(
                    func.avg(
                        ProcessingInfo.end_timestamp - ProcessingInfo.start_timestamp
                    )
                )
            )
        ).scalar()
        if average_response_time is None:
            average_response_time = timedelta(0)
            
        average_first_token_time: timedelta | None = (
            await db.execute(
                select(
                    func.avg(
                        ProcessingInfo.first_token_timestamp - ProcessingInfo.start_timestamp
                    )
                ).where(ProcessingInfo.first_token_timestamp.is_not(None))
            )
        ).scalar()
        if average_first_token_time is None:
            average_first_token_time = timedelta(0)
            
        return ChatInfoOutput(
            chats_created=chats_count,
            messages_received=messages_count,
            average_response_time=average_response_time.total_seconds(),
            average_first_token_time=average_first_token_time.total_seconds(),
        )


    async def response_stream(
        self, chat_id: UUID, message_content: str, db: AsyncSession
    ):
        """
        Stream a response to the message and save to database.
        """
        # Create timestamp for the message
        timestamp = datetime.now(timezone.utc)

        # Save the user message to database
        user_message_db = Message(
            chat_id=chat_id,
            sender=ChatMessageSender.USER.value,
            content=message_content,
            timestamp=timestamp,
        )
        db.add(user_message_db)
        await db.flush()

        # Get the most recent messages in the chat for context
        result = await db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp.desc())
            .limit(chat_config.max_context_messages_count)
        )
        chat_messages = list(reversed(result.scalars().all()))

        # Convert to ChatMessage objects for LLM
        messages_for_llm = [
            ChatMessage(
                id=msg.id,
                sender=ChatMessageSender(msg.sender),
                content=msg.content,
                timestamp=msg.timestamp,
            )
            for msg in chat_messages
        ]

        # Shorten messages to comply with chat config restrictions
        messages_for_llm = shorten_chat_messages(messages_for_llm)

        # Create AI response message
        ai_message_db = Message(
            chat_id=chat_id,
            sender=ChatMessageSender.AI.value,
            content="",
            timestamp=datetime.now(timezone.utc),
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
            first_token_timestamp=None,
            end_timestamp=None,
        )
        db.add(processing_info_db)
        await db.flush()

        # Stream response
        accumulated_content = ""
        first_token_sent = False
        async for token in self.llm.stream_response(messages_for_llm):
            # Record timestamp when first token is sent to client
            if not first_token_sent:
                processing_info_db.first_token_timestamp = datetime.now(timezone.utc)
                first_token_sent = True
                
            accumulated_content += token
            # Escape newlines for proper SSE transmission - replace \n with \\n
            # This preserves newlines in the content while maintaining SSE format
            escaped_token = token.replace("\n", "\\n")
            yield f"data: {escaped_token}\n\n"

        # Update AI message with final content
        ai_message_db.content = accumulated_content
        processing_info_db.end_timestamp = datetime.now(timezone.utc)
        await db.commit()

    async def get_message_cache_info(
        self, message_id: UUID, db: AsyncSession
    ) -> ChatResponseCacheInfo:
        """Get cache information for a specific message."""
        result = await db.execute(
            select(CacheInfo).where(CacheInfo.message_id == message_id)
        )
        cache_info = result.scalar_one_or_none()

        if not cache_info:
            raise ValueError("Cache info not found")

        return ChatResponseCacheInfo(
            id=cache_info.id,
            message_id=cache_info.message_id,
            hit=cache_info.hit,
            cache_timestamp=cache_info.cache_timestamp,
            num_hits=cache_info.num_hits,
        )

    async def get_message_processing_info(
        self, message_id: UUID, db: AsyncSession
    ) -> ChatResponseProcessingInfo:
        """Get processing information for a specific message."""
        result = await db.execute(
            select(ProcessingInfo).where(ProcessingInfo.message_id == message_id)
        )
        processing_info = result.scalar_one_or_none()

        if not processing_info:
            raise ValueError("Processing info not found")

        return ChatResponseProcessingInfo(
            id=processing_info.id,
            message_id=processing_info.message_id,
            start_timestamp=processing_info.start_timestamp,
            first_token_timestamp=processing_info.first_token_timestamp,
            end_timestamp=processing_info.end_timestamp,
        )


chat_controller = ChatController()
