"""FastAPI application entry point with lifespan management."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.api.schemas import HealthResponse
from src.config import Settings, get_settings
from src.core.logging import setup_logging

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: initialize and cleanup resources."""
    settings = get_settings()
    setup_logging(debug=settings.debug)
    app.state.settings = settings
    app.state.vectorstore = None
    app.state.checkpointer = None
    app.state.graph = None

    log = structlog.get_logger()
    await log.ainfo("Starting application", app_name=settings.app_name, version=settings.app_version)

    # Load vectorstore — auto-ingest PDF if index doesn't exist
    try:
        from src.rag.vectorstore import load_vectorstore

        vectorstore = load_vectorstore(settings)
        app.state.vectorstore = vectorstore
        await log.ainfo("Vectorstore loaded successfully")
    except FileNotFoundError:
        await log.ainfo("Vectorstore not found, attempting auto-ingestion...")
        try:
            from src.rag.ingest import build_vectorstore, chunk_documents, extract_pages_with_tables

            pdf_path = os.path.join("data", "manual-politicas-viagem-blis.pdf")
            if os.path.exists(pdf_path):
                documents = extract_pages_with_tables(pdf_path)
                chunks = chunk_documents(documents, settings.chunk_size, settings.chunk_overlap)
                build_vectorstore(chunks, settings)
                app.state.vectorstore = load_vectorstore(settings)
                await log.ainfo("Auto-ingestion complete", chunks=len(chunks))
            else:
                await log.awarning("PDF not found for auto-ingestion", path=pdf_path)
        except Exception as ingest_err:
            await log.awarning("Auto-ingestion failed", error=str(ingest_err))
    except Exception as e:
        await log.awarning("Vectorstore not available", error=str(e))

    # Initialize checkpointer
    try:
        from src.core.checkpointer import create_checkpointer

        checkpointer = await create_checkpointer(settings.redis_url)
        app.state.checkpointer = checkpointer
        await log.ainfo("Redis checkpointer initialized")
    except Exception as e:
        await log.awarning("Redis checkpointer not available, using MemorySaver", error=str(e))
        from langgraph.checkpoint.memory import MemorySaver

        app.state.checkpointer = MemorySaver()

    # Build graph
    try:
        from src.agents.orchestrator import build_graph

        graph = build_graph(settings, app.state.vectorstore, app.state.checkpointer)
        app.state.graph = graph
        await log.ainfo("LangGraph graph built successfully")
    except Exception as e:
        await log.aerror("Failed to build graph", error=str(e))

    yield

    await log.ainfo("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    limiter = Limiter(key_func=get_remote_address)

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Parse allowed origins from comma-separated env var
    origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(Exception)
    async def generic_exception_handler(request, exc):
        await logger.aerror("Unhandled exception", error=str(exc))
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor"},
        )

    @application.get("/health", response_model=HealthResponse)
    async def health_check():
        redis_connected = False
        vectorstore_loaded = application.state.vectorstore is not None

        # Real ping to Redis instead of just isinstance check
        checkpointer = application.state.checkpointer
        if checkpointer is not None:
            try:
                from langgraph.checkpoint.memory import MemorySaver

                if not isinstance(checkpointer, MemorySaver):
                    # Try actual Redis ping via the checkpointer's connection
                    if hasattr(checkpointer, "conn") and checkpointer.conn is not None:
                        await checkpointer.conn.ping()
                    redis_connected = True
            except Exception:
                redis_connected = False

        status = "healthy" if redis_connected and vectorstore_loaded else "degraded"

        return HealthResponse(
            status=status,
            redis_connected=redis_connected,
            vectorstore_loaded=vectorstore_loaded,
            version=settings.app_version,
        )

    # Register routers
    from src.api.routes.chat import router as chat_router

    application.include_router(chat_router, prefix="/api/v1")

    return application


def get_app() -> FastAPI:
    """Get or create the FastAPI application (lazy singleton)."""
    if not hasattr(get_app, "_app"):
        get_app._app = create_app()
    return get_app._app


app = get_app()
