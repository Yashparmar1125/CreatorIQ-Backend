from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID, uuid4
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict
from enum import Enum

from src.core.database import Base

class SessionStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETE = "complete"
    FAILED = "failed"

class ContentType(str, Enum):
    IDEA = "idea"
    TITLE = "title"
    TAG_SET = "tag_set"
    SCRIPT_OUTLINE = "script_outline"
    THUMBNAIL_BRIEF = "thumbnail_brief"

# --- SQLAlchemy Models ---

class StrategySession(Base):
    __tablename__ = "strategy_sessions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    channel_id: Mapped[UUID] = mapped_column(ForeignKey("channels.id"), index=True, nullable=False)
    trend_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("trends.id"), nullable=True)
    
    input_topic: Mapped[str] = mapped_column(String(500), nullable=False)
    input_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[SessionStatus] = mapped_column(SQLEnum(SessionStatus), nullable=False)
    
    llm_model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    llm_prompt_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    token_usage: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    contents: Mapped[List["GeneratedContent"]] = relationship(back_populates="session", cascade="all, delete-orphan")

class GeneratedContent(Base):
    __tablename__ = "generated_content"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("strategy_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    content_type: Mapped[ContentType] = mapped_column(SQLEnum(ContentType), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    
    predicted_ctr_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    performance_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    selected: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    session: Mapped["StrategySession"] = relationship(back_populates="contents")

# --- Pydantic Schemas ---

class StrategySessionBase(BaseModel):
    input_topic: str
    input_config: dict
    status: SessionStatus

class GeneratedContentPublic(BaseModel):
    id: UUID
    content_type: ContentType
    content: dict
    predicted_ctr_score: Optional[float]
    
    model_config = ConfigDict(from_attributes=True)
