"""LangGraph StateGraph orchestrator with intent classification and routing."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from src.rag.prompts import CLASSIFY_INTENT_SYSTEM, SYNTHESIZER_SYSTEM
from src.state.graph_state import AgentRoute, GraphState

if TYPE_CHECKING:
    from langchain_community.vectorstores import FAISS

    from src.config import Settings

logger = structlog.get_logger()


def build_graph(settings: Settings, vectorstore: FAISS | None, checkpointer=None):
    """Build and compile the LangGraph StateGraph."""
    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        openai_api_key=settings.openai_api_key.get_secret_value(),
    )

    async def classify_intent(state: GraphState) -> dict:
        """Classify user query intent into FAQ, SEARCH, or BOTH."""
        user_query = state["user_query"]
        response = await llm.ainvoke([
            SystemMessage(content=CLASSIFY_INTENT_SYSTEM),
            HumanMessage(content=user_query),
        ])
        route_text = response.content.strip().upper()

        if route_text not in ("FAQ", "SEARCH", "BOTH"):
            route_text = "FAQ"

        await logger.ainfo("Intent classified", route=route_text, query=user_query[:80])
        return {"route": route_text}

    async def faq_agent(state: GraphState) -> dict:
        """Answer from policy documents via RAG."""
        from src.agents.faq_agent import run_faq_agent

        return await run_faq_agent(state, llm, vectorstore, settings)

    async def search_agent(state: GraphState) -> dict:
        """Answer using web search results."""
        from src.agents.search_agent import run_search_agent

        return await run_search_agent(state, llm, settings)

    async def synthesize_response(state: GraphState) -> dict:
        """Synthesize final response from agent outputs."""
        route = state["route"]
        faq_resp = state.get("faq_response")
        search_resp = state.get("search_response")

        if route == AgentRoute.BOTH and faq_resp and search_resp:
            system_prompt = SYNTHESIZER_SYSTEM.format(
                faq_response=faq_resp,
                search_response=search_resp,
            )
            response = await llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=state["user_query"]),
            ])
            final = response.content
        elif faq_resp:
            final = faq_resp
        elif search_resp:
            final = search_resp
        else:
            final = "Desculpe, não consegui processar sua pergunta no momento."

        await logger.ainfo("Response synthesized", route=route)
        return {"final_response": final}

    def route_by_intent(state: GraphState) -> Literal["faq_agent", "search_agent", "both_faq"]:
        """Route to appropriate agent based on classified intent."""
        route = state["route"]
        if route == AgentRoute.SEARCH:
            return "search_agent"
        elif route == AgentRoute.BOTH:
            return "both_faq"
        return "faq_agent"

    def after_both_faq(state: GraphState) -> Literal["both_search"]:
        """After FAQ in BOTH route, always go to search."""
        return "both_search"

    # Build graph
    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("faq_agent", faq_agent)
    graph.add_node("search_agent", search_agent)
    graph.add_node("both_faq", faq_agent)
    graph.add_node("both_search", search_agent)
    graph.add_node("synthesize_response", synthesize_response)

    # Set entry point
    graph.set_entry_point("classify_intent")

    # Add conditional routing
    graph.add_conditional_edges("classify_intent", route_by_intent)

    # FAQ route: faq_agent → synthesize → END
    graph.add_edge("faq_agent", "synthesize_response")

    # SEARCH route: search_agent → synthesize → END
    graph.add_edge("search_agent", "synthesize_response")

    # BOTH route: both_faq → both_search → synthesize → END
    graph.add_edge("both_faq", "both_search")
    graph.add_edge("both_search", "synthesize_response")

    # Synthesize → END
    graph.add_edge("synthesize_response", END)

    compiled = graph.compile(checkpointer=checkpointer)
    return compiled
