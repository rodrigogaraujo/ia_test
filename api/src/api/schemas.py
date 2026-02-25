"""Pydantic models for API request/response validation."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Chat endpoint request body."""

    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=4096)


class Source(BaseModel):
    """Reference to an information source."""

    type: Literal["document", "web"]
    title: str
    content_preview: str = ""
    url: str | None = None


class ChatResponse(BaseModel):
    """Chat endpoint response body."""

    session_id: str
    response: str
    agent_used: Literal["faq", "search", "both"]
    sources: list[Source] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthResponse(BaseModel):
    """Health check endpoint response."""

    status: Literal["healthy", "degraded"]
    redis_connected: bool
    vectorstore_loaded: bool
    version: str
