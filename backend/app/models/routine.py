import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Routine(Base):
    """Training routines/programs (e.g., Push/Pull/Legs, 5x5, Dorian Yates HIT)"""

    __tablename__ = "routines"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # template = predefined, custom = user created
    type: Mapped[str] = mapped_column(String(20), default="custom")
    
    # Full routine configuration as JSON
    # Example: {"days": [{"name": "Push", "exercises": [...]}], "schedule": "MWF"}
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="routines")


class ScheduledEvent(Base):
    """Planned/recurring events (workouts, habits, etc.)"""

    __tablename__ = "scheduled_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    
    # Can be linked to a tracker or routine
    tracker_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("trackers.id"), nullable=True
    )
    routine_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("routines.id"), nullable=True
    )
    
    name: Mapped[str] = mapped_column(String(100))
    
    # RRULE format for recurring events
    # Example: "FREQ=WEEKLY;BYDAY=MO,WE,FR"
    recurrence: Mapped[str | None] = mapped_column(String(200), nullable=True)
    
    # Time of day (optional)
    time: Mapped[str | None] = mapped_column(String(10), nullable=True)
    
    # Reminder settings as JSON
    reminder_settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
