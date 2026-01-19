"""User service for syncing Clerk users to database."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_or_create_user(
    db: AsyncSession,
    user_id: str,
    email: str | None = None,
    name: str | None = None,
) -> User:
    """Get existing user or create new one from Clerk data."""
    
    # Try to find existing user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user:
        # Update email/name if changed
        updated = False
        if email and user.email != email:
            user.email = email
            updated = True
        if name and user.name != name:
            user.name = name
            updated = True
        if updated:
            await db.commit()
            await db.refresh(user)
        return user
    
    # Create new user
    # Use email as fallback if no specific email provided
    user_email = email or f"{user_id}@clerk.user"
    
    new_user = User(
        id=user_id,
        email=user_email,
        name=name,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
