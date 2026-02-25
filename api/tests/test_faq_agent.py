"""Tests for the FAQ Agent."""

from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.mark.asyncio
async def test_faq_agent_with_documents(mock_settings):
    """Test FAQ agent returns response with source citations."""
    from langchain_core.documents import Document

    from src.agents.faq_agent import run_faq_agent

    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(
        content="Bagagem de mão: limite de 10 kg conforme Seção 1.1"
    )

    mock_doc = Document(
        page_content="Bagagem de mão: 10 kg, dimensão máxima 115 cm",
        metadata={"page_number": 1, "section": "Seção 1.1", "source": "manual.pdf"},
    )

    mock_vectorstore = MagicMock()
    mock_retriever = AsyncMock()
    mock_retriever.ainvoke.return_value = [mock_doc]
    mock_vectorstore.as_retriever.return_value = mock_retriever

    state = {
        "user_query": "Qual o limite de bagagem de mão?",
        "sources": [],
    }

    result = await run_faq_agent(state, mock_llm, mock_vectorstore, mock_settings)

    assert result["faq_response"] is not None
    assert "Bagagem" in result["faq_response"]
    assert len(result["sources"]) > 0
    assert result["sources"][0]["type"] == "document"


@pytest.mark.asyncio
async def test_faq_agent_no_vectorstore(mock_settings):
    """Test FAQ agent handles missing vectorstore gracefully."""
    from src.agents.faq_agent import run_faq_agent

    mock_llm = AsyncMock()

    state = {
        "user_query": "Pergunta teste",
        "sources": [],
    }

    result = await run_faq_agent(state, mock_llm, None, mock_settings)

    assert "não está disponível" in result["faq_response"]
