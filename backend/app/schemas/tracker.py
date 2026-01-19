from pydantic import BaseModel
from typing import Any
from uuid import UUID
from datetime import datetime


class TrackerCreate(BaseModel):
    name: str
    category: str
    schema: dict[str, Any] = {}
    icon: str | None = None
    color: str | None = None


class TrackerResponse(BaseModel):
    id: UUID
    name: str
    category: str
    schema: dict[str, Any]
    icon: str | None
    color: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class EntryCreate(BaseModel):
    tracker_id: UUID
    data: dict[str, Any]
    notes: str | None = None
    timestamp: datetime | None = None


class EntryResponse(BaseModel):
    id: UUID
    tracker_id: UUID
    data: dict[str, Any]
    notes: str | None
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True
