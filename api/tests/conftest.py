"""Test fixtures for the Blis Travel Agents test suite."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Set test env vars before any import of src.config
os.environ.setdefault("OPENAI_API_KEY", "test-key-for-testing")
os.environ.setdefault("TAVILY_API_KEY", "test-tavily-key-for-testing")


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    settings = MagicMock()
    settings.app_name = "Blis Travel Agents"
    settings.app_version = "1.0.0"
    settings.debug = False
    settings.openai_api_key.get_secret_value.return_value = "test-key"
    settings.tavily_api_key.get_secret_value.return_value = "test-tavily-key"
    settings.redis_url = "redis://localhost:6379"
    settings.vectorstore_path = "./data/vectorstore"
    settings.embedding_model = "text-embedding-3-small"
    settings.llm_model = "gpt-4o-mini"
    settings.llm_temperature = 0.1
    settings.chunk_size = 1500
    settings.chunk_overlap = 200
    settings.retrieval_top_k = 5
    return settings


@pytest.fixture
def mock_graph():
    """Create a mock LangGraph compiled graph."""
    graph = AsyncMock()
    graph.ainvoke.return_value = {
        "route": "FAQ",
        "faq_response": "Resposta de teste do FAQ.",
        "search_response": None,
        "final_response": "Resposta de teste do FAQ.",
        "sources": [
            {
                "type": "document",
                "title": "Manual de Políticas - Página 1",
                "content_preview": "Teste...",
                "url": None,
            }
        ],
    }
    return graph


@pytest.fixture
async def client(mock_graph):
    """Create an async test client with mocked dependencies."""
    from src.main import create_app

    app = create_app()

    # Override app state with mocks
    app.state.graph = mock_graph
    app.state.vectorstore = MagicMock()
    app.state.checkpointer = MagicMock()
    app.state.settings = MagicMock()
    app.state.settings.app_version = "1.0.0"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
