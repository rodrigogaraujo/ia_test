"""Tests for the Search Agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_search_agent_with_results(mock_settings):
    """Test search agent returns response with web sources."""
    from src.agents.search_agent import run_search_agent

    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(
        content="Passagens SP-Lisboa a partir de R$3.500 em março."
    )

    mock_results = [
        {
            "title": "Voos para Lisboa",
            "url": "https://example.com/voos",
            "content": "Passagens a partir de R$3.500",
        },
    ]

    state = {
        "user_query": "Quanto está a passagem SP-Lisboa em março?",
        "sources": [],
    }

    with patch("src.tools.web_search.search_web", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_results
        result = await run_search_agent(state, mock_llm, mock_settings)

    assert result["search_response"] is not None
    assert "3.500" in result["search_response"]
    assert len(result["sources"]) > 0
    assert result["sources"][0]["type"] == "web"
    assert result["sources"][0]["url"] == "https://example.com/voos"


@pytest.mark.asyncio
async def test_search_agent_api_failure(mock_settings):
    """Test search agent handles Tavily API failure gracefully."""
    from src.agents.search_agent import run_search_agent

    mock_llm = AsyncMock()

    state = {
        "user_query": "Teste busca",
        "sources": [],
    }

    with patch("src.tools.web_search.search_web", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = Exception("API unavailable")
        result = await run_search_agent(state, mock_llm, mock_settings)

    assert "não foi possível" in result["search_response"].lower()
