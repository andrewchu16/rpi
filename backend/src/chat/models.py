from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from ..database import Base


class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender = Column(String(10), nullable=False)  # "user" or "AI"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    cache_info = relationship("CacheInfo", back_populates="message", uselist=False)
    processing_info = relationship("ProcessingInfo", back_populates="message", uselist=False)


class CacheInfo(Base):
    __tablename__ = "cache_info"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    hit = Column(Boolean, default=False, nullable=False)
    cache_timestamp = Column(DateTime(timezone=True), nullable=True)
    num_hits = Column(Integer, default=0, nullable=False)
    
    # Relationship
    message = relationship("Message", back_populates="cache_info")


class ProcessingInfo(Base):
    __tablename__ = "processing_info"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    start_timestamp = Column(DateTime(timezone=True), nullable=True)
    end_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    message = relationship("Message", back_populates="processing_info")
