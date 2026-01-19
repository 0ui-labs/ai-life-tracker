"""Entry service for saving tracked data to database."""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entry import Entry
from app.models.tracker import Tracker
from app.services.user import get_or_create_user


# Default categories for common tracker types
TRACKER_CATEGORIES = {
    # Fitness exercises
    "bankdrücken": "fitness",
    "bench press": "fitness",
    "kniebeugen": "fitness",
    "squat": "fitness",
    "kreuzheben": "fitness",
    "deadlift": "fitness",
    "schulterdrücken": "fitness",
    "overhead press": "fitness",
    "rudern": "fitness",
    "row": "fitness",
    "klimmzüge": "fitness",
    "pull-ups": "fitness",
    "dips": "fitness",
    "bizeps": "fitness",
    "trizeps": "fitness",
    "laufen": "fitness",
    "running": "fitness",
    # Health
    "gewicht": "health",
    "weight": "health",
    "schlaf": "health",
    "sleep": "health",
    "wasser": "health",
    "water": "health",
    "blutdruck": "health",
    "blood pressure": "health",
    # Habits
    "meditation": "habit",
    "lesen": "habit",
    "reading": "habit",
    # Default
    "default": "general",
}


def get_category_for_tracker(name: str) -> str:
    """Get category for a tracker name."""
    name_lower = name.lower()
    for key, category in TRACKER_CATEGORIES.items():
        if key in name_lower:
            return category
    return "general"


async def get_or_create_tracker(
    db: AsyncSession,
    user_id: str,
    tracker_name: str,
    category: str | None = None,
) -> Tracker:
    """Get existing tracker or create new one."""
    
    # Normalize tracker name
    normalized_name = tracker_name.strip().title()
    
    # Try to find existing tracker
    result = await db.execute(
        select(Tracker).where(
            Tracker.user_id == user_id,
            Tracker.name == normalized_name,
        )
    )
    tracker = result.scalar_one_or_none()
    
    if tracker:
        return tracker
    
    # Create new tracker
    tracker_category = category or get_category_for_tracker(tracker_name)
    
    new_tracker = Tracker(
        user_id=user_id,
        name=normalized_name,
        category=tracker_category,
        schema={},  # Schema can be populated later based on entries
    )
    db.add(new_tracker)
    await db.commit()
    await db.refresh(new_tracker)
    return new_tracker


async def save_entry(
    db: AsyncSession,
    user_id: str,
    user_email: str | None,
    tracker_name: str,
    data: dict[str, Any],
    notes: str | None = None,
    timestamp: datetime | None = None,
) -> Entry:
    """Save a tracking entry to the database.
    
    This will:
    1. Ensure user exists in DB
    2. Get or create the tracker
    3. Save the entry
    """
    
    # Ensure user exists
    await get_or_create_user(db, user_id, user_email)
    
    # Get or create tracker
    tracker = await get_or_create_tracker(db, user_id, tracker_name)
    
    # Create entry
    entry = Entry(
        user_id=user_id,
        tracker_id=tracker.id,
        data=data,
        notes=notes,
        timestamp=timestamp or datetime.utcnow(),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    
    return entry


async def get_recent_entries(
    db: AsyncSession,
    user_id: str,
    tracker_name: str | None = None,
    limit: int = 10,
) -> list[Entry]:
    """Get recent entries for a user, optionally filtered by tracker."""
    
    query = select(Entry).where(Entry.user_id == user_id)
    
    if tracker_name:
        # Join with tracker to filter by name
        normalized_name = tracker_name.strip().title()
        query = query.join(Tracker).where(Tracker.name == normalized_name)
    
    query = query.order_by(Entry.timestamp.desc()).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_tracker_stats(
    db: AsyncSession,
    user_id: str,
    tracker_name: str,
) -> dict[str, Any]:
    """Get statistics for a tracker (last value, count, etc.)."""
    
    entries = await get_recent_entries(db, user_id, tracker_name, limit=100)
    
    if not entries:
        return {"count": 0, "last_entry": None}
    
    return {
        "count": len(entries),
        "last_entry": {
            "data": entries[0].data,
            "timestamp": entries[0].timestamp.isoformat(),
        },
        "first_entry_date": entries[-1].timestamp.isoformat() if entries else None,
    }
