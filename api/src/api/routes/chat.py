"""Chat API routes: POST /chat and GET /chat/stream."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sse_starlette.sse import EventSourceResponse

from src.api.dependencies import get_graph, get_settings
from src.api.schemas import ChatRequest, ChatResponse, Source
from src.config import Settings

limiter = Limiter(key_func=get_remote_address)
"""Rate limiter: 20 requests/minute per IP on chat endpoints."""

logger = structlog.get_logger()

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(
    request: Request,
    body: ChatRequest,
    graph=Depends(get_graph),
    settings: Settings = Depends(get_settings),
):
    """Process a chat message and return the response."""
    await logger.ainfo(
        "Chat request received",
        session_id=body.session_id,
        message_length=len(body.message),
    )

    try:
        from langchain_core.messages import HumanMessage

        config = {"configurable": {"thread_id": body.session_id}}
        initial_state = {
            "messages": [HumanMessage(content=body.message)],
            "user_query": body.message,
            "route": "",
            "faq_response": None,
            "search_response": None,
            "final_response": "",
            "sources": [],
        }

        result = await graph.ainvoke(initial_state, config=config)

        route = result.get("route", "faq").lower()
        agent_used = route if route in ("faq", "search", "both") else "faq"

        raw_sources = result.get("sources", [])
        sources = [Source(**s) for s in raw_sources if isinstance(s, dict)]

        return ChatResponse(
            session_id=body.session_id,
            response=result.get("final_response", ""),
            agent_used=agent_used,
            sources=sources,
            timestamp=datetime.now(timezone.utc),
        )

    except Exception as e:
        await logger.aerror("Chat processing failed", error=str(e))
        raise HTTPException(status_code=503, detail="Serviço temporariamente indisponível")


@router.get("/chat/stream")
@limiter.limit("20/minute")
async def chat_stream(
    request: Request,
    session_id: str = Query(..., min_length=1, max_length=128),
    message: str = Query(..., min_length=1, max_length=4096),
    graph=Depends(get_graph),
    settings: Settings = Depends(get_settings),
):
    """Stream chat response via Server-Sent Events."""

    async def event_generator():
        try:
            from langchain_core.messages import HumanMessage

            config = {"configurable": {"thread_id": session_id}}
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "user_query": message,
                "route": "",
                "faq_response": None,
                "search_response": None,
                "final_response": "",
                "sources": [],
            }

            final_state = {}
            async for event in graph.astream_events(
                initial_state, config=config, version="v2"
            ):
                if event["event"] == "on_chat_model_stream":
                    # Filter out classify_intent tokens (route labels leak)
                    node = event.get("metadata", {}).get("langgraph_node", "")
                    if node == "classify_intent":
                        continue
                    token = event["data"]["chunk"].content
                    if token:
                        yield {
                            "event": "token",
                            "data": json.dumps({"token": token}),
                        }

                if event["event"] == "on_chain_end" and event.get("name") == "LangGraph":
                    final_state = event.get("data", {}).get("output", {})

            route = final_state.get("route", "faq")
            agent_used = route.lower() if route.lower() in ("faq", "search", "both") else "faq"

            yield {
                "event": "done",
                "data": json.dumps({
                    "session_id": session_id,
                    "agent_used": agent_used,
                    "sources": final_state.get("sources", []),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }),
            }

        except Exception as e:
            await logger.aerror("Stream processing failed", error=str(e))
            yield {
                "event": "error",
                "data": json.dumps({"detail": "Erro durante processamento"}),
            }

    return EventSourceResponse(event_generator())
