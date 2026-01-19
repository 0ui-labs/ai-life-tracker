from pydantic import BaseModel
from typing import Any


class ChatRequest(BaseModel):
    message: str
    context: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    action: str
    message: str
    data: dict[str, Any] | None = None
    component: str | None = None
    tracker: str | None = None
