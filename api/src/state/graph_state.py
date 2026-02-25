"""LangGraph graph state definition and agent route enum."""

from enum import Enum
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentRoute(str, Enum):
    """Classification of user intent for routing."""

    FAQ = "FAQ"
    SEARCH = "SEARCH"
    BOTH = "BOTH"


class GraphState(TypedDict):
    """State shared across all nodes in the LangGraph graph."""

    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    route: str
    faq_response: str | None
    search_response: str | None
    final_response: str
    sources: list[dict]
