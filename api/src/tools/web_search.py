"""Tavily web search tool wrapper."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from src.config import Settings

logger = structlog.get_logger()


async def search_web(query: str, settings: Settings) -> list[dict]:
    """Search the web using Tavily and return results."""
    from langchain_community.tools.tavily_search import TavilySearchResults

    tool = TavilySearchResults(
        max_results=5,
        tavily_api_key=settings.tavily_api_key.get_secret_value(),
    )
    results = await tool.ainvoke({"query": query})

    await logger.ainfo("Web search completed", query=query[:80], results=len(results))
    return results
