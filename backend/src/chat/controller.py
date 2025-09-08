from datetime import datetime, timezone, timedelta
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select


from .config import chat_config
from .schema import (
    ChatMessage,
    ChatResponseCacheInfo,
    ChatInfoOutput,
    ChatMessageSender,
    Chat,
    ChatResponseStreamEventType,
)
from .services import LLM, Embedding, VectorStore
from .models import Message, CacheInfo, ProcessingInfo, Chat as ChatModel
from .utils import shorten_chat_messages

logger = logging.getLogger(__name__)
class ChatController:
    def __init__(self):
        """Initialize the chat controller with transformers-based LLM service."""
        self._llm: LLM | None = None
        self._embedding: Embedding | None = None
        self._vector_store: VectorStore | None = None

    @property
    def llm(self) -> LLM:
        """Lazy initialization of LLM service."""
        if self._llm is None:
            self._llm = LLM()
        return self._llm

    @property
    def embedding(self) -> Embedding:
        """Lazy initialization of Embedding service."""
        if self._embedding is None:
            self._embedding = Embedding()
        return self._embedding

    @property
    def vector_store(self) -> VectorStore:
        """Lazy initialization of VectorStore service."""
        if self._vector_store is None:
            # Initialize with reasonable defaults - you may want to adjust these
            self._vector_store = VectorStore(
                dim=chat_config.embedding_dim,  # Adjust based on your embedding model dimensions
                capacity=1000,  # Adjust based on your needs
                space="cosine"
            )
        return self._vector_store

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
                        ProcessingInfo.first_token_timestamp
                        - ProcessingInfo.start_timestamp
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
        self,
        chat_id: UUID,
        message_content: str,
        db: AsyncSession,
        include_processing_info: bool = False,
        include_cache_info: bool = False,
    ):
        """
        Stream a response with caching based on conversation summarization and vector search.
        Yields either tokens (str) or processing info events (dict).
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

        # Convert to ChatMessage objects
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

        start_time = datetime.now(timezone.utc)
        
        # Step 1: Summarize the conversation history
        summarized_query = await self.llm.summarize_conversation(messages_for_llm)
        logger.info(f"Summarized query: {summarized_query}")
        
        # Step 2: Embed the summarized query
        query_embedding = await self.embedding.embed_query(summarized_query)
        
        # Step 3: Search for similar cached responses
        search_results = self.vector_store.search(query_embedding, k=1)
        
        # Step 4: Check if we found a good match (you may want to adjust the threshold)
        if search_results and len(search_results) > 0:
            best_match_id, similarity_score = search_results[0]
            # Cosine similarity threshold - adjust as needed (0.9 means very similar)
            if 1 - similarity_score > 0.9:
                try:
                    # Try to retrieve the cached message
                    cached_result = await db.execute(
                        select(Message).where(Message.id == UUID(best_match_id))
                    )
                    cached_message = cached_result.scalar_one_or_none()
                    
                    if cached_message:
                        # Increment cache hit count
                        cache_result = await db.execute(
                            select(CacheInfo).where(CacheInfo.message_id == cached_message.id)
                        )
                        cache_info = cache_result.scalar_one_or_none()
                        if cache_info:
                            cache_info.num_hits += 1
                            await db.commit()
                        
                        # Stream the cached response and cache info if requested
                        async for item in self._stream_cached_response(
                            cached_message, start_time, include_processing_info, cache_info
                        ):
                            yield item
                        return
                        
                except (ValueError, Exception) as e:
                    # If there's any error with the cached message, fall back to generation
                    logger.error(f"Error with cached message: {e}")

        # Step 5: Generate new response if no cache hit
        ai_message_db = Message(
            chat_id=chat_id,
            sender=ChatMessageSender.AI.value,
            content="",
            timestamp=datetime.now(timezone.utc),
        )
        db.add(ai_message_db)
        await db.flush()

        if include_processing_info:
            yield {
                "event": ChatResponseStreamEventType.MESSAGE_CREATED,
                "data": {
                    "message_id": str(ai_message_db.id),
                    "timestamp": ai_message_db.timestamp.isoformat(),
                },
            }

        # Create cache info for the new message
        cache_info_db = CacheInfo(message_id=ai_message_db.id, num_hits=0)
        db.add(cache_info_db)
        await db.flush()

        processing_info_db = ProcessingInfo(
            message_id=ai_message_db.id,
            start_timestamp=start_time,
            first_token_timestamp=None,
            end_timestamp=None,
        )
        db.add(processing_info_db)
        await db.flush()

        if include_processing_info:
            yield {
                "event": ChatResponseStreamEventType.PROCESSING_STARTED,
                "data": {
                    "message_id": str(ai_message_db.id),
                    "start_timestamp": start_time.isoformat(),
                },
            }

        # Generate new response
        accumulated_content = ""
        first_token_sent = False
        async for token in self.llm.stream_response(messages_for_llm):
            # Record timestamp when first token is sent to client
            if not first_token_sent:
                first_token_time = datetime.now(timezone.utc)
                processing_info_db.first_token_timestamp = first_token_time
                first_token_sent = True

                if include_processing_info:
                    yield {
                        "event": ChatResponseStreamEventType.FIRST_TOKEN,
                        "data": {
                            "message_id": str(ai_message_db.id),
                            "first_token_timestamp": first_token_time.isoformat(),
                            "time_to_first_token": (
                                first_token_time - start_time
                            ).total_seconds(),
                        },
                    }

            accumulated_content += token
            yield {"data": {"type": "token", "content": token}}

        # Update AI message with final content
        end_time = datetime.now(timezone.utc)
        ai_message_db.content = accumulated_content
        processing_info_db.end_timestamp = end_time
        
        # Step 6: Add the new response to the vector store cache
        # response_embedding = await self.embedding.embed_query(accumulated_content)
        self.vector_store.add(str(ai_message_db.id), query_embedding)
        
        await db.commit()

        if include_processing_info:
            yield {
                "event": ChatResponseStreamEventType.PROCESSING_COMPLETED,
                "data": {
                    "message_id": str(ai_message_db.id),
                    "end_timestamp": end_time.isoformat(),
                    "total_time": (end_time - start_time).total_seconds(),
                    "time_to_first_token": (
                        processing_info_db.first_token_timestamp - start_time
                    ).total_seconds()
                    if processing_info_db.first_token_timestamp
                    else None,
                },
            }

        if include_cache_info:
            # Create cache info for the new message (cache miss)
            cache_info_response = ChatResponseCacheInfo(
                hit=False,  # This is a cache miss since we generated a new response
            )
            yield {
                "event": ChatResponseStreamEventType.CACHE_INFO,
                "data": cache_info_response.model_dump(mode='json'),
            }

    async def _stream_cached_response(
        self, cached_message: Message, start_time: datetime, include_processing_info: bool, cache_info: CacheInfo = None
    ):
        """Stream a cached response with simulated timing."""
        if include_processing_info:
            yield {
                "event": ChatResponseStreamEventType.MESSAGE_CREATED, 
                "data": {
                    "message_id": str(cached_message.id),
                    "timestamp": cached_message.timestamp.isoformat(),
                    "cache_hit": True,
                }
            }
            
            yield {
                "event": ChatResponseStreamEventType.PROCESSING_STARTED,
                "data": {
                    "message_id": str(cached_message.id),
                    "start_timestamp": start_time.isoformat(),
                    "cache_hit": True,
                }
            }
            
            # Simulate first token time for cached responses
            first_token_time = datetime.now(timezone.utc)
            yield {
                "event": ChatResponseStreamEventType.FIRST_TOKEN,
                "data": {
                    "message_id": str(cached_message.id),
                    "first_token_timestamp": first_token_time.isoformat(),
                    "time_to_first_token": (first_token_time - start_time).total_seconds(),
                }
            }

        # Stream the cached content token by token with small delays
        import asyncio
        for i, char in enumerate(cached_message.content):
            yield {"data": {"type": "token", "content": char}}
            # Small delay to simulate streaming
            if i % 5 == 0:  # Delay every 5 characters
                await asyncio.sleep(0.01)
        
        end_time = datetime.now(timezone.utc)
        
        if include_processing_info:
            yield {
                "event": ChatResponseStreamEventType.PROCESSING_COMPLETED,
                "data": {
                    "message_id": str(cached_message.id),
                    "end_timestamp": end_time.isoformat(),
                    "total_time": (end_time - start_time).total_seconds(),
                    "time_to_first_token": (first_token_time - start_time).total_seconds(),
                }
            }

        if cache_info:
            # Create cache info response for the cached message hit
            cache_info_response = ChatResponseCacheInfo(
                id=cache_info.id,
                message_id=cached_message.id,
                hit=True,  # This is a cache hit
                message_timestamp=cached_message.timestamp,
                num_hits=cache_info.num_hits,
            )
            yield {
                "event": ChatResponseStreamEventType.CACHE_INFO, 
                "data": cache_info_response.model_dump(mode='json'),
            }


chat_controller = ChatController()
