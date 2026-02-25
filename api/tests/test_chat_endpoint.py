"""Tests for the POST /api/v1/chat endpoint."""

import pytest


@pytest.mark.asyncio
async def test_chat_success(client):
    """Test successful chat request with FAQ response."""
    response = await client.post(
        "/api/v1/chat",
        json={"session_id": "test-session", "message": "Qual o limite de bagagem?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session"
    assert data["response"] == "Resposta de teste do FAQ."
    assert data["agent_used"] == "faq"
    assert "timestamp" in data
    assert len(data["sources"]) > 0


@pytest.mark.asyncio
async def test_chat_empty_message(client):
    """Test validation rejects empty message."""
    response = await client.post(
        "/api/v1/chat",
        json={"session_id": "test", "message": ""},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_missing_session_id(client):
    """Test validation rejects missing session_id."""
    response = await client.post(
        "/api/v1/chat",
        json={"message": "Pergunta teste"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_long_session_id(client):
    """Test validation rejects session_id exceeding 128 chars."""
    response = await client.post(
        "/api/v1/chat",
        json={"session_id": "a" * 129, "message": "Teste"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_long_message(client):
    """Test validation rejects message exceeding 4096 chars."""
    response = await client.post(
        "/api/v1/chat",
        json={"session_id": "test", "message": "a" * 4097},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_extra_fields_rejected(client):
    """Test validation rejects extra fields (Pydantic extra=forbid)."""
    response = await client.post(
        "/api/v1/chat",
        json={"session_id": "test", "message": "Teste", "extra": "field"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint returns expected structure."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "redis_connected" in data
    assert "vectorstore_loaded" in data
    assert "version" in data
    assert data["status"] in ("healthy", "degraded")
