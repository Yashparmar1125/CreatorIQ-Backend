from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pydantic import BaseModel, ConfigDict
from enum import Enum

from src.core.database import Base

class TrendStatus(str, Enum):
    EMERGING = "emerging"
    PEAKING = "peaking"
    PEAKED = "peaked"
    DECLINING = "declining"

class SignalSource(str, Enum):
    GOOGLE_TRENDS = "google_trends"
    YOUTUBE_DATA = "youtube_data"
    CROSS_PLATFORM = "cross_platform"

# --- SQLAlchemy Models ---

class Trend(Base):
    __tablename__ = "trends"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    topic_slug: Mapped[str] = mapped_column(String(500), unique=True, index=True, nullable=False)
    # niches: Mapped[list[str]] = mapped_column... (Using a simple String for now)
    
    tvs_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    prediction_confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    peak_window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    peak_window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[TrendStatus] = mapped_column(SQLEnum(TrendStatus), nullable=False)
    
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    signals: Mapped[List["TrendSignal"]] = relationship(back_populates="trend", cascade="all, delete-orphan")

class TrendSignal(Base):
    __tablename__ = "trend_signals"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    trend_id: Mapped[UUID] = mapped_column(ForeignKey("trends.id", ondelete="CASCADE"), index=True, nullable=False)
    signal_source: Mapped[SignalSource] = mapped_column(SQLEnum(SignalSource), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True, index=True, nullable=False) # TimescaleDB partition key
    relative_interest: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    search_volume_est: Mapped[Optional[int]] = mapped_column(nullable=True)
    region: Mapped[str] = mapped_column(String(10), default="GLOBAL")

    trend: Mapped["Trend"] = relationship(back_populates="signals")

# --- Pydantic Schemas ---

class TrendBase(BaseModel):
    topic: str
    topic_slug: str
    tvs_score: float
    status: TrendStatus

class TrendPublic(TrendBase):
    id: UUID
    prediction_confidence: float
    peak_window_start: datetime
    peak_window_end: datetime
    
    model_config = ConfigDict(from_attributes=True)
