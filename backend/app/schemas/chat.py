from typing import Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    context: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    action: str
    message: str
    data: dict[str, Any] | None = None
    component: str | None = None
    tracker: str | None = None
    routine_id: str | None = None
