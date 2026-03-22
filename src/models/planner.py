from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, ConfigDict
from enum import Enum

from src.core.database import Base

class SlotStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SCRIPTED = "scripted"
    READY = "ready"
    PUBLISHED = "published"
    SKIPPED = "skipped"

# --- SQLAlchemy Models ---

class PlannerSlot(Base):
    __tablename__ = "planner_slots"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    channel_id: Mapped[UUID] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    
    strategy_session_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("strategy_sessions.id"), nullable=True)
    trend_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("trends.id"), nullable=True)
    
    status: Mapped[SlotStatus] = mapped_column(SQLEnum(SlotStatus), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trend_window_alert_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

# --- Pydantic Schemas ---

class PlannerSlotBase(BaseModel):
    scheduled_at: datetime
    topic: str
    status: SlotStatus

class PlannerSlotPublic(PlannerSlotBase):
    id: UUID
    channel_id: UUID
    
    model_config = ConfigDict(from_attributes=True)
