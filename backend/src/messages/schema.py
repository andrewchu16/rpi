from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CacheInfo(BaseModel):
    hit: bool = Field(default=False, description="Whether the message was found in cache")
    cache_timestamp: Optional[datetime] = Field(default=None, description="The timestamp when the message was cached")
    num_hits: int = Field(default=0, description="The number of times the message was hit in cache")


class ProcessingInfo(BaseModel):
    start_timestamp: datetime = Field(default=None, description="The timestamp when the message was started processing")
    end_timestamp: datetime = Field(default=None, description="The timestamp when the message was finished processing")


class MessageInput(BaseModel):
    message: str
    get_cache_info: bool = Field(default=False, description="Whether to get the cache information")
    get_processing_info: bool = Field(default=False, description="Whether to get the processing information")


class MessageResponse(BaseModel):
    message: str = Field(default="", description="The message response")
    cache_info: Optional[CacheInfo] = Field(default=None, description="The cache information")
    processing_info: Optional[ProcessingInfo] = Field(default=None, description="The processing information")