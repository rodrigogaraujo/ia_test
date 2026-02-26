"""FAQ Agent: answers questions using RAG over travel policy documents."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

from src.rag.prompts import FAQ_AGENT_SYSTEM

if TYPE_CHECKING:
    from langchain_community.vectorstores import FAISS
    from langchain_openai import ChatOpenAI

    from src.config import Settings
    from src.state.graph_state import GraphState

logger = structlog.get_logger()


async def run_faq_agent(
    state: GraphState,
    llm: ChatOpenAI,
    vectorstore: FAISS | None,
    settings: Settings,
) -> dict:
    """Retrieve relevant documents and generate FAQ response."""
    user_query = state["user_query"]
    sources: list[dict] = list(state.get("sources") or [])

    if vectorstore is None:
        await logger.awarning("Vectorstore not available for FAQ agent")
        return {
            "faq_response": "A base de conhecimento não está disponível no momento.",
            "sources": sources,
        }

    from langchain_core.messages import HumanMessage, SystemMessage

    from src.rag.vectorstore import get_retriever

    retriever = get_retriever(vectorstore, top_k=settings.retrieval_top_k)
    docs = await retriever.ainvoke(user_query)

    context_parts = []
    for doc in docs:
        page = doc.metadata.get("page_number", "?")
        section = doc.metadata.get("section", "")
        source_label = f"[Página {page}]"
        if section:
            source_label = f"[{section} - Página {page}]"
        context_parts.append(f"{source_label}\n{doc.page_content}")
        sources.append({
            "type": "document",
            "title": f"Manual de Políticas - Página {page}" + (f" ({section})" if section else ""),
            "content_preview": doc.page_content[:200],
            "url": None,
        })

    context = "\n\n---\n\n".join(context_parts) if context_parts else "Nenhum documento relevante encontrado."

    system_prompt = FAQ_AGENT_SYSTEM.format(context=context)
    response = await llm.ainvoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query),
    ])

    await logger.ainfo("FAQ agent completed", docs_found=len(docs))
    return {
        "faq_response": response.content,
        "sources": sources,
    }
