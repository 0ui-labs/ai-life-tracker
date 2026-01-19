import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Tracker(Base):
    """Flexible tracker definition - can track anything (workouts, habits, health, etc.)"""

    __tablename__ = "trackers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50))  # fitness, habit, health, etc.
    
    # JSON schema defining what fields this tracker has
    # Example: {"fields": [{"name": "weight", "type": "number", "unit": "kg"}, ...]}
    schema: Mapped[dict] = mapped_column(JSON, default=dict)
    
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="trackers")
    entries: Mapped[list["Entry"]] = relationship(back_populates="tracker")
