from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from enum import StrEnum


class ChatMessageSender(StrEnum):
    USER = "user"
    AI = "assistant"


class BaseModelWithUUID(BaseModel):
    """Base model with UUID serialization configuration."""
    model_config = ConfigDict(
        # Serialize UUID and datetime objects properly
        json_encoders={
            UUID: str,
            # datetime: lambda v: v.isoformat(),
        },
    )


class Chat(BaseModelWithUUID):
    id: Optional[UUID] = Field(default=None, description="Database ID of the chat")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the chat was created",
    )
    

class ChatMessage(BaseModelWithUUID):
    id: Optional[UUID] = Field(default=None, description="Database ID of the message")
    chat_id: Optional[UUID] = Field(
        default=None, description="ID of the chat this message belongs to"
    )
    sender: ChatMessageSender = Field(
        default=ChatMessageSender.USER, description="The sender of the message"
    )
    content: str = Field(default="", description="The content of the message")
    timestamp: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the message",
    )


class ChatResponseCacheInfo(BaseModelWithUUID):
    id: Optional[UUID] = Field(
        default=None, description="Database ID of the cache info"
    )
    message_id: Optional[UUID] = Field(
        default=None, description="ID of the retrieved message"
    )
    hit: bool = Field(
        default=False, description="Whether the message was found in cache"
    )
    message_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp when the retrieved message was generated",
    )
    num_hits: int = Field(
        default=0, description="The number of times this message has been retrieved"
    )


class ChatResponseProcessingInfo(BaseModelWithUUID):
    id: Optional[UUID] = Field(
        default=None, description="Database ID of the processing info"
    )
    message_id: Optional[UUID] = Field(
        default=None, description="ID of the related message"
    )
    start_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp when the message was started processing",
    )
    first_token_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp when the first token was sent to the client",
    )
    end_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp when the message was finished processing",
    )




class ChatInfoOutput(BaseModel):
    chats_created: int = Field(default=0, description="The number of chats created")
    messages_received: int = Field(
        default=0, description="The number of messages received"
    )
    average_response_time: float = Field(
        default=0, description="The average response time in seconds"
    )
    average_first_token_time: float = Field(
        default=0, description="The average time to first token in seconds"
    )


class ChatResponseStreamEventType(StrEnum):
    MESSAGE_CREATED = "message_created"
    PROCESSING_STARTED = "processing_started"
    FIRST_TOKEN = "first_token"
    PROCESSING_COMPLETED = "processing_completed"
    CACHE_INFO = "cache_info"
    STATUS = "status"
    DONE = "done"