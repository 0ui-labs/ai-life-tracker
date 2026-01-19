"""Routine service for managing user routines and schedules."""

from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.routine import Routine

# =============================================================================
# Day name mappings for schedule parsing
# =============================================================================

DAY_MAPPINGS = {
    # German
    "montag": "MO",
    "dienstag": "TU",
    "mittwoch": "WE",
    "donnerstag": "TH",
    "freitag": "FR",
    "samstag": "SA",
    "sonntag": "SU",
    # English
    "monday": "MO",
    "tuesday": "TU",
    "wednesday": "WE",
    "thursday": "TH",
    "friday": "FR",
    "saturday": "SA",
    "sunday": "SU",
}

SPECIAL_SCHEDULES = {
    "jeden tag": "FREQ=DAILY",
    "täglich": "FREQ=DAILY",
    "daily": "FREQ=DAILY",
    "werktags": "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
    "weekdays": "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR",
    "am wochenende": "FREQ=WEEKLY;BYDAY=SA,SU",
    "wochenende": "FREQ=WEEKLY;BYDAY=SA,SU",
    "weekend": "FREQ=WEEKLY;BYDAY=SA,SU",
}


def parse_schedule_to_rrule(schedule: str) -> str | None:
    """Convert natural language schedule to RRULE format.
    
    Examples:
        "Montag, Mittwoch, Freitag" -> "FREQ=WEEKLY;BYDAY=MO,WE,FR"
        "jeden Tag" -> "FREQ=DAILY"
        "werktags" -> "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"
    """
    if not schedule:
        return None

    schedule_lower = schedule.lower().strip()

    # Check for special schedules first
    for pattern, rrule in SPECIAL_SCHEDULES.items():
        if pattern in schedule_lower:
            return rrule

    # Try to extract day names
    found_days = []
    for day_name, day_code in DAY_MAPPINGS.items():
        if day_name in schedule_lower:
            if day_code not in found_days:
                found_days.append(day_code)

    if found_days:
        # Sort days in week order
        day_order = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
        found_days.sort(key=lambda d: day_order.index(d))
        return f"FREQ=WEEKLY;BYDAY={','.join(found_days)}"

    return None


# =============================================================================
# CRUD Operations
# =============================================================================

async def create_routine(
    db: AsyncSession,
    user_id: str,
    name: str,
    schedule: str | None = None,
    config: dict[str, Any] | None = None,
) -> Routine:
    """Create a new routine for a user.
    
    Args:
        db: Database session
        user_id: User ID
        name: Routine name
        schedule: Natural language schedule (e.g., "Montag, Mittwoch, Freitag")
        config: Full routine configuration as JSON
    
    Returns:
        Created Routine object
    """
    # Parse schedule to RRULE if provided
    rrule = parse_schedule_to_rrule(schedule) if schedule else None

    # Build config
    routine_config = config or {}
    if rrule and "schedule" not in routine_config:
        routine_config["schedule"] = rrule

    routine = Routine(
        user_id=user_id,
        name=name,
        type="custom",
        config=routine_config,
        is_active=False,
    )

    db.add(routine)
    await db.commit()
    await db.refresh(routine)

    return routine


async def get_routine_by_id(
    db: AsyncSession,
    routine_id: UUID,
) -> Routine | None:
    """Get a routine by ID.
    
    Args:
        db: Database session
        routine_id: Routine UUID
    
    Returns:
        Routine object or None if not found
    """
    result = await db.execute(
        select(Routine).where(Routine.id == routine_id)
    )
    return result.scalar_one_or_none()


async def get_user_routines(
    db: AsyncSession,
    user_id: str,
    active_only: bool = False,
) -> list[Routine]:
    """Get all routines for a user.
    
    Args:
        db: Database session
        user_id: User ID
        active_only: If True, only return active routines
    
    Returns:
        List of Routine objects
    """
    query = select(Routine).where(Routine.user_id == user_id)

    if active_only:
        query = query.where(Routine.is_active == True)

    query = query.order_by(Routine.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_routine(
    db: AsyncSession,
    routine_id: UUID,
    name: str | None = None,
    schedule: str | None = None,
    config: dict[str, Any] | None = None,
) -> Routine | None:
    """Update an existing routine.
    
    Args:
        db: Database session
        routine_id: Routine UUID
        name: New name (optional)
        schedule: New schedule (optional)
        config: New config (optional)
    
    Returns:
        Updated Routine object or None if not found
    """
    routine = await get_routine_by_id(db, routine_id)

    if not routine:
        return None

    if name is not None:
        routine.name = name

    if schedule is not None:
        rrule = parse_schedule_to_rrule(schedule)
        if rrule:
            routine.config = {**routine.config, "schedule": rrule}

    if config is not None:
        routine.config = config

    await db.commit()
    await db.refresh(routine)

    return routine


async def delete_routine(
    db: AsyncSession,
    routine_id: UUID,
) -> bool:
    """Delete a routine.
    
    Args:
        db: Database session
        routine_id: Routine UUID
    
    Returns:
        True if deleted, False if not found
    """
    routine = await get_routine_by_id(db, routine_id)

    if not routine:
        return False

    await db.delete(routine)
    await db.commit()

    return True


async def activate_routine(
    db: AsyncSession,
    routine_id: UUID,
) -> Routine | None:
    """Activate a routine (and deactivate others for the same user).
    
    Args:
        db: Database session
        routine_id: Routine UUID
    
    Returns:
        Activated Routine object or None if not found
    """
    routine = await get_routine_by_id(db, routine_id)

    if not routine:
        return None

    # Deactivate all other routines for this user
    await db.execute(
        update(Routine)
        .where(Routine.user_id == routine.user_id)
        .where(Routine.id != routine_id)
        .values(is_active=False)
    )

    # Activate this routine
    routine.is_active = True

    await db.commit()
    await db.refresh(routine)

    return routine


async def deactivate_routine(
    db: AsyncSession,
    routine_id: UUID,
) -> Routine | None:
    """Deactivate a routine.
    
    Args:
        db: Database session
        routine_id: Routine UUID
    
    Returns:
        Deactivated Routine object or None if not found
    """
    routine = await get_routine_by_id(db, routine_id)

    if not routine:
        return None

    routine.is_active = False

    await db.commit()
    await db.refresh(routine)

    return routine


async def get_active_routine(
    db: AsyncSession,
    user_id: str,
) -> Routine | None:
    """Get the currently active routine for a user.
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Active Routine object or None
    """
    result = await db.execute(
        select(Routine)
        .where(Routine.user_id == user_id)
        .where(Routine.is_active == True)
    )
    return result.scalar_one_or_none()
