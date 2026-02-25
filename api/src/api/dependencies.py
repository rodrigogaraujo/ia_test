"""FastAPI dependency injection for graph and settings."""

from __future__ import annotations

from fastapi import Depends, Request

from src.config import Settings


def get_settings(request: Request) -> Settings:
    """Get application settings from app state."""
    return request.app.state.settings


def get_graph(request: Request):
    """Get the compiled LangGraph graph from app state."""
    graph = request.app.state.graph
    if graph is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="Serviço temporariamente indisponível")
    return graph
