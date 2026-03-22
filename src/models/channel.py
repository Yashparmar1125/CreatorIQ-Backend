from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Boolean, DateTime, ForeignKey, BigINT, Integer, Numeric, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict
from enum import Enum

from src.core.database import Base

class ContentFormat(str, Enum):
    LONG_FORM = "long_form"
    SHORTS = "shorts"
    BOTH = "both"

class ChannelTone(str, Enum):
    EDUCATIONAL = "educational"
    ENTERTAINING = "entertaining"
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    MIXED = "mixed"

class MetricPeriod(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

# --- SQLAlchemy Models ---

class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    youtube_channel_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    handle: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    subscriber_count: Mapped[int] = mapped_column(BigINT, default=0)
    video_count: Mapped[int] = mapped_column(Integer, default=0)
    # niches: Mapped[List[str]] = mapped_column... (Using a simple String for now or a specialized Array type if needed)
    # For MVP, we can use JSONB or separate mapping, but PRD says VARCHAR(64)[]
    # niches: Mapped[list[str]] = mapped_column(ARRAY(String(64)), nullable=False) # Requires postgres imports
    
    metrics_last_refreshed: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    metrics: Mapped[List["ChannelMetrics"]] = relationship(back_populates="channel", cascade="all, delete-orphan")

class ChannelMetrics(Base):
    __tablename__ = "channel_metrics"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    channel_id: Mapped[UUID] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, nullable=False) # Primary key for TimescaleDB composite
    period: Mapped[MetricPeriod] = mapped_column(SQLEnum(MetricPeriod), nullable=False)
    views: Mapped[int] = mapped_column(BigINT, nullable=False)
    watch_time_minutes: Mapped[int] = mapped_column(BigINT, nullable=False)
    subscribers_gained: Mapped[int] = mapped_column(Integer, nullable=False)
    subscribers_lost: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_revenue_usd: Mapped[Optional[float]] = mapped_column(Numeric(12, 4), nullable=True)
    avg_view_duration_secs: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_ctr: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)
    impressions: Mapped[Optional[int]] = mapped_column(BigINT, nullable=True)

    channel: Mapped["Channel"] = relationship(back_populates="metrics")

# --- Pydantic Schemas ---

class ChannelBase(BaseModel):
    youtube_channel_id: str
    name: str
    handle: Optional[str] = None
    thumbnail_url: Optional[str] = None

class ChannelPublic(ChannelBase):
    id: UUID
    subscriber_count: int
    video_count: int
    is_primary: bool
    metrics_last_refreshed: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)
