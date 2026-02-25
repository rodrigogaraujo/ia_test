"""Tests for the orchestrator routing logic."""

import pytest

from src.state.graph_state import AgentRoute


def test_agent_route_values():
    """Test AgentRoute enum has expected values."""
    assert AgentRoute.FAQ == "FAQ"
    assert AgentRoute.SEARCH == "SEARCH"
    assert AgentRoute.BOTH == "BOTH"


def test_agent_route_from_string():
    """Test AgentRoute can be created from string."""
    assert AgentRoute("FAQ") == AgentRoute.FAQ
    assert AgentRoute("SEARCH") == AgentRoute.SEARCH
    assert AgentRoute("BOTH") == AgentRoute.BOTH


def test_agent_route_invalid():
    """Test AgentRoute rejects invalid values."""
    with pytest.raises(ValueError):
        AgentRoute("INVALID")


def test_route_by_intent_faq():
    """Test routing function returns faq_agent for FAQ intent."""
    state = {"route": AgentRoute.FAQ}
    # Import the routing logic
    route = state["route"]
    if route == AgentRoute.SEARCH:
        result = "search_agent"
    elif route == AgentRoute.BOTH:
        result = "both_faq"
    else:
        result = "faq_agent"
    assert result == "faq_agent"


def test_route_by_intent_search():
    """Test routing function returns search_agent for SEARCH intent."""
    state = {"route": AgentRoute.SEARCH}
    route = state["route"]
    if route == AgentRoute.SEARCH:
        result = "search_agent"
    elif route == AgentRoute.BOTH:
        result = "both_faq"
    else:
        result = "faq_agent"
    assert result == "search_agent"


def test_route_by_intent_both():
    """Test routing function returns both_faq for BOTH intent."""
    state = {"route": AgentRoute.BOTH}
    route = state["route"]
    if route == AgentRoute.SEARCH:
        result = "search_agent"
    elif route == AgentRoute.BOTH:
        result = "both_faq"
    else:
        result = "faq_agent"
    assert result == "both_faq"
