from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import CurrentUser
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai import ai_service
from app.services.context import context_engine
from app.services.entry import save_entry
from app.services.routine import (
    create_routine,
    delete_routine,
    get_active_routine,
    get_user_routines,
    update_routine,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Process a chat message through the AI."""
    user_id = user.id

    # Get current context
    context = await context_engine.get_context(user_id)

    # Add active routine to context
    active_routine = await get_active_routine(db, user_id)
    if active_routine:
        context["active_routine"] = {
            "id": str(active_routine.id),
            "name": active_routine.name,
            "config": active_routine.config,
        }

    # Merge with request context if provided
    if request.context:
        context.update(request.context)

    # Process through AI
    result = await ai_service.process_message(request.message, context)

    action = result.get("action")
    data = result.get("data", {})
    routine_id = None

    # Handle tracking actions - save to database
    if action == "track":
        tracker_name = result.get("tracker")

        if tracker_name and data:
            # Save entry to database
            try:
                entry = await save_entry(
                    db=db,
                    user_id=user_id,
                    user_email=user.email,
                    tracker_name=tracker_name,
                    data=data,
                )
                # Add entry ID to response data
                result["entry_id"] = str(entry.id)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Error saving entry: {e}")

        # Update workout context if active
        if context.get("workout_active"):
            weight = data.get("weight", context.get("last_weight"))
            reps = data.get("reps", 0)
            if weight and reps:
                await context_engine.record_set(user_id, weight, reps)

    # Handle routine creation
    elif action == "create_routine":
        try:
            routine = await create_routine(
                db=db,
                user_id=user_id,
                name=data.get("name", "Neue Routine"),
                schedule=data.get("schedule"),
                config=data,
            )
            routine_id = str(routine.id)
        except Exception as e:
            print(f"Error creating routine: {e}")
            result["message"] = f"Fehler beim Erstellen der Routine: {e}"

    # Handle show routines
    elif action == "show_routines":
        try:
            routines = await get_user_routines(db, user_id)
            result["data"] = {
                "routines": [
                    {
                        "id": str(r.id),
                        "name": r.name,
                        "is_active": r.is_active,
                        "config": r.config,
                    }
                    for r in routines
                ]
            }
        except Exception as e:
            print(f"Error fetching routines: {e}")

    # Handle routine update
    elif action == "update_routine":
        routine_name = data.get("name")
        if routine_name:
            try:
                # Find routine by name
                routines = await get_user_routines(db, user_id)
                matching = [r for r in routines if r.name.lower() == routine_name.lower()]
                if matching:
                    updated = await update_routine(
                        db=db,
                        routine_id=matching[0].id,
                        config={**matching[0].config, **data.get("update", {})},
                    )
                    if updated:
                        routine_id = str(updated.id)
            except Exception as e:
                print(f"Error updating routine: {e}")

    # Handle routine deletion
    elif action == "delete_routine":
        routine_name = data.get("name")
        if routine_name:
            try:
                routines = await get_user_routines(db, user_id)
                matching = [r for r in routines if r.name.lower() == routine_name.lower()]
                if matching:
                    await delete_routine(db, matching[0].id)
            except Exception as e:
                print(f"Error deleting routine: {e}")

    return ChatResponse(
        action=result.get("action", "chat"),
        message=result.get("message", ""),
        data=result.get("data"),
        component=result.get("component"),
        tracker=result.get("tracker"),
        routine_id=routine_id,
    )


@router.post("/workout/start")
async def start_workout(user: CurrentUser, routine_name: str | None = None):
    """Start a workout session."""
    user_id = user.id
    await context_engine.start_workout(user_id, routine_name)
    return {"status": "started", "routine": routine_name}


@router.post("/workout/end")
async def end_workout(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """End the current workout session and save summary."""
    user_id = user.id
    summary = await context_engine.end_workout(user_id)

    # TODO: Could save workout session summary here

    return {"status": "ended", "summary": summary}


@router.get("/context")
async def get_context(user: CurrentUser):
    """Get current context for debugging."""
    user_id = user.id
    return await context_engine.get_context(user_id)


@router.get("/history")
async def get_history(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    tracker: str | None = None,
    limit: int = 20,
):
    """Get recent tracking history."""
    from app.services.entry import get_recent_entries

    entries = await get_recent_entries(
        db=db,
        user_id=user.id,
        tracker_name=tracker,
        limit=limit,
    )

    return [
        {
            "id": str(entry.id),
            "tracker_id": str(entry.tracker_id),
            "data": entry.data,
            "notes": entry.notes,
            "timestamp": entry.timestamp.isoformat(),
        }
        for entry in entries
    ]
