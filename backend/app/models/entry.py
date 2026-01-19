import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Entry(Base):
    """Individual tracking entry - the actual data points"""

    __tablename__ = "entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    tracker_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("trackers.id"), index=True
    )
    
    # The actual tracked values as JSON
    # Example: {"weight": 80, "sets": 3, "reps": 10}
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Optional notes
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Link to scheduled event if this was planned
    scheduled_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="entries")
    tracker: Mapped["Tracker"] = relationship(back_populates="entries")
