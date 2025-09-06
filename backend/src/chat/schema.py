from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from enum import StrEnum


class ChatMessageSender(StrEnum):
    USER = "user"
    AI = "AI"


class Chat(BaseModel):
    id: Optional[UUID] = Field(default=None, description="Database ID of the chat")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when the chat was created",
    )


class ChatMessage(BaseModel):
    id: Optional[UUID] = Field(default=None, description="Database ID of the message")
    chat_id: Optional[UUID] = Field(default=None, description="ID of the chat this message belongs to")
    sender: ChatMessageSender = Field(
        default=ChatMessageSender.USER, description="The sender of the message"
    )
    content: str = Field(default="", description="The content of the message")
    timestamp: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of the message",
    )


class ChatResponseCacheInfo(BaseModel):
    id: Optional[UUID] = Field(default=None, description="Database ID of the cache info")
    message_id: Optional[UUID] = Field(
        default=None, description="ID of the related message"
    )
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
    end_timestamp: Optional[datetime] = Field(
        default=None,
        description="The timestamp when the message was finished processing",
    )


class ChatResponseInput(BaseModel):
    chat_id: UUID = Field(..., description="ID of the chat")
    message_content: str = Field(
        ..., description="The content of the new message to add to the chat"
    )
    get_cache_info: bool = Field(
        default=False, description="Whether to get the cache information"
    )
    get_processing_info: bool = Field(
        default=False, description="Whether to get the processing information"
    )


class ChatResponseOutput(BaseModel):
    message: ChatMessage = Field(..., description="The message response")
    cache_info: Optional[ChatResponseCacheInfo] = Field(
        default=None, description="The cache information"
    )
    processing_info: Optional[ChatResponseProcessingInfo] = Field(
        default=None, description="The processing information"
    )


class ChatInfoOutput(BaseModel):
    chats_created: int = Field(default=0, description="The number of chats created")
    messages_received: int = Field(
        default=0, description="The number of messages received"
    )
    average_response_time: float = Field(
        default=0, description="The average response time in seconds"
    )
