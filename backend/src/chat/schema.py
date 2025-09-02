from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from enum import StrEnum

from .config import chat_config


class ChatSender(StrEnum):
    USER = "user"
    AI = "AI"


class ChatMessage(BaseModel):
    id: Optional[int] = Field(default=None, description="Database ID of the message")
    sender: ChatSender = Field(
        default=ChatSender.USER, description="The sender of the message"
    )
    content: str = Field(default="", description="The content of the message")
    timestamp: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of the message")

    @field_validator("content")
    def validate_content_length(cls, v):
        if len(v) > chat_config.max_message_length:
            raise ValueError(
                f"Message content cannot exceed {chat_config.max_message_length} characters"
            )
        return v


class ChatResponseCacheInfo(BaseModel):
    id: Optional[int] = Field(default=None, description="Database ID of the cache info")
    message_id: Optional[int] = Field(default=None, description="ID of the related message")
    hit: bool = Field(
        default=False, description="Whether the message was found in cache"
    )
    cache_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp when the message was cached",
    )
    num_hits: int = Field(
        default=0, description="The number of times the message was hit in cache"
    )


class ChatResponseProcessingInfo(BaseModel):
    id: Optional[int] = Field(default=None, description="Database ID of the processing info")
    message_id: Optional[int] = Field(default=None, description="ID of the related message")
    start_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp when the message was started processing",
    )
    end_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp when the message was finished processing",
    )


class ChatResponseInput(BaseModel):
    messages: list[ChatMessage] = Field(..., description="List of chat messages")
    get_cache_info: bool = Field(
        default=False, description="Whether to get the cache information"
    )
    get_processing_info: bool = Field(
        default=False, description="Whether to get the processing information"
    )

    @field_validator("messages")
    def validate_messages_count(cls, v):
        if len(v) > chat_config.max_messages:
            raise ValueError(
                f"Cannot send more than {chat_config.max_messages} messages at once"
            )
        return v


class ChatResponseOutput(BaseModel):
    message: ChatMessage = Field(..., description="The message response")
    cache_info: Optional[ChatResponseCacheInfo] = Field(
        default=None, description="The cache information"
    )
    processing_info: Optional[ChatResponseProcessingInfo] = Field(
        default=None, description="The processing information"
    )


class ChatInfoOutput(BaseModel):
    messages_received: int = Field(
        default=0, description="The number of messages received"
    )
    average_response_time: float = Field(
        default=0, description="The average response time in seconds"
    )


# Database response models
class MessageCreate(BaseModel):
    sender: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CacheInfoCreate(BaseModel):
    message_id: int
    hit: bool
    cache_timestamp: Optional[datetime] = None
    num_hits: int = 0


class ProcessingInfoCreate(BaseModel):
    message_id: int
    start_timestamp: Optional[datetime] = None
    end_timestamp: Optional[datetime] = None
