from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import CurrentUser
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai import ai_service
from app.services.context import context_engine
from app.services.entry import save_entry

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
    context = context_engine.get_context(user_id)
    
    # Merge with request context if provided
    if request.context:
        context.update(request.context)
    
    # Process through AI
    result = await ai_service.process_message(request.message, context)
    
    # Handle tracking actions - save to database
    if result.get("action") == "track":
        tracker_name = result.get("tracker")
        data = result.get("data", {})
        
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
                context_engine.record_set(user_id, weight, reps)
    
    return ChatResponse(
        action=result.get("action", "chat"),
        message=result.get("message", ""),
        data=result.get("data"),
        component=result.get("component"),
        tracker=result.get("tracker"),
    )


@router.post("/workout/start")
async def start_workout(user: CurrentUser, routine_name: str | None = None):
    """Start a workout session."""
    user_id = user.id
    context_engine.start_workout(user_id, routine_name)
    return {"status": "started", "routine": routine_name}


@router.post("/workout/end")
async def end_workout(
    user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """End the current workout session and save summary."""
    user_id = user.id
    summary = context_engine.end_workout(user_id)
    
    # TODO: Could save workout session summary here
    
    return {"status": "ended", "summary": summary}


@router.get("/context")
async def get_context(user: CurrentUser):
    """Get current context for debugging."""
    user_id = user.id
    return context_engine.get_context(user_id)


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
