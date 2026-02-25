"""Search Agent: answers questions using real-time web search via Tavily."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from src.rag.prompts import SEARCH_AGENT_PROMPT

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI

    from src.config import Settings
    from src.state.graph_state import GraphState

logger = structlog.get_logger()


async def run_search_agent(
    state: GraphState,
    llm: ChatOpenAI,
    settings: Settings,
) -> dict:
    """Search the web and generate response from search results."""
    user_query = state["user_query"]
    sources: list[dict] = list(state.get("sources") or [])

    try:
        from src.tools.web_search import search_web

        results = await search_web(user_query, settings)
    except Exception as e:
        await logger.awarning("Web search failed", error=str(e))
        return {
            "search_response": "Não foi possível realizar a busca na web no momento.",
            "sources": sources,
        }

    search_parts = []
    for result in results:
        title = result.get("title", "Sem título")
        url = result.get("url", "")
        content = result.get("content", "")
        search_parts.append(f"**{title}**\n{content}\nFonte: {url}")
        sources.append({
            "type": "web",
            "title": title,
            "content_preview": content[:200],
            "url": url,
        })

    search_text = "\n\n---\n\n".join(search_parts) if search_parts else "Nenhum resultado encontrado."

    from langchain_core.messages import HumanMessage

    prompt = SEARCH_AGENT_PROMPT.format(search_results=search_text, user_query=user_query)
    response = await llm.ainvoke([HumanMessage(content=prompt)])

    await logger.ainfo("Search agent completed", results_found=len(results))
    return {
        "search_response": response.content,
        "sources": sources,
    }
