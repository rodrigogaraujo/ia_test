# Implementation Plan: Multi-Agent Travel Assistant

**Branch**: `001-multi-agent-travel` | **Date**: 2025-02-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-multi-agent-travel/spec.md`

## Summary

Sistema multi-agent de IA para agências de viagem com 3 componentes principais:
- **Orchestrator** (LangGraph StateGraph) classifica intenção e roteia para agentes
- **FAQ Agent** (RAG: FAISS + OpenAI embeddings) responde sobre políticas de viagem
- **Search Agent** (Tavily web search) busca informações em tempo real

Exposto via **FastAPI** com endpoint REST obrigatório (`POST /chat`) e SSE streaming como diferencial. Persistência de sessão via **Redis** checkpointer com fallback para MemorySaver. Toda a stack sobe via **Docker Compose**.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, LangGraph >=0.2, langchain-openai >=0.2, faiss-cpu >=1.8, tavily-python >=0.5, langgraph-checkpoint-redis >=0.3.5, pydantic >=2.0, pydantic-settings >=2.0, structlog >=24.0, sse-starlette >=2.0, pypdf >=4.0, pdfplumber >=0.11
**Storage**: Redis 7 (session checkpoints), FAISS (vector store persistido em disco)
**Testing**: pytest com httpx (AsyncClient para FastAPI)
**Target Platform**: Docker containers (Linux), API em porta 8000
**Project Type**: web-service (REST API)
**Performance Goals**: <10s FAQ/SEARCH, <15s BOTH, >=85% intent accuracy, >=90% FAQ precision
**Constraints**: Secrets via SecretStr, prompt injection defense, CORS explícito, error messages genéricas
**Scale/Scope**: Teste técnico — 1 PDF (13 págs), 3 endpoints, 2 agentes + orchestrator

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Observação |
|-----------|--------|------------|
| I. AI-First Development | PASS | Todo desenvolvimento via Claude Code, documentado no README |
| II. Commits Incrementais | PASS | Commits por fase, formato `tipo: descrição` |
| III. Type Safety | PASS | Pydantic models para todos os contratos, TypedDict para GraphState |
| IV. Clean Architecture | PASS | Camadas: API → Orquestração → Agentes → Ferramentas → Infra |
| V. Production-Ready Mindset | PASS | structlog, error handling, Docker Compose, /health |
| VI. DRY e KISS | PASS | Sem abstrações prematuras, mínimo necessário |
| VII. Skills-Driven Development | PASS | Skills mapeadas por fase (ver constitution) |
| VIII. Security-First | PASS | SecretStr, sanitização de input, prompt injection defense, CORS |

**Gate Result**: PASS — nenhuma violação identificada.

## Project Structure

### Documentation (this feature)

```text
specs/001-multi-agent-travel/
├── plan.md              # This file
├── research.md          # Phase 0 output — technology decisions
├── data-model.md        # Phase 1 output — entity definitions
├── quickstart.md        # Phase 1 output — getting started guide
├── contracts/
│   └── api.md           # Phase 1 output — API contract
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # FastAPI app + lifespan (Redis, FAISS init)
├── config.py            # Settings(BaseSettings) — todas as configs
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── chat.py      # POST /api/v1/chat, GET /api/v1/chat/stream
│   ├── schemas.py       # ChatRequest, ChatResponse, Source, HealthResponse
│   └── dependencies.py  # Injeção do grafo e checkpointer via Depends
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py  # LangGraph StateGraph + routing condicional
│   ├── faq_agent.py     # RAG agent (FAISS retriever + LLM)
│   └── search_agent.py  # Tavily web search agent
├── tools/
│   ├── __init__.py
│   ├── web_search.py    # Tavily wrapper
│   └── rag_retriever.py # RAG retrieval tool
├── rag/
│   ├── __init__.py
│   ├── ingest.py        # PDF → chunks → embeddings → FAISS
│   ├── vectorstore.py   # FAISS setup + persistence (save/load)
│   └── prompts.py       # Todos os prompt templates
├── state/
│   ├── __init__.py
│   └── graph_state.py   # GraphState TypedDict + AgentRoute enum
└── core/
    ├── __init__.py
    ├── logging.py        # structlog config
    └── checkpointer.py   # AsyncRedisSaver + MemorySaver fallback

tests/
├── __init__.py
├── conftest.py           # Fixtures (client, mock graph, mock vectorstore)
├── test_chat_endpoint.py # Testes do POST /chat e validações
├── test_faq_agent.py     # Testes do FAQ Agent (mock retriever)
├── test_search_agent.py  # Testes do Search Agent (mock Tavily)
└── test_orchestrator.py  # Testes de routing (intent classification)

scripts/
├── ingest_documents.py   # CLI para ingestão do PDF
└── healthcheck.py        # Script para Docker healthcheck

data/
└── manual-politicas-viagem-blis.pdf  # Base de conhecimento RAG

docker-compose.yml        # Redis 7 + API
Dockerfile                # Python 3.11 + deps
pyproject.toml            # Dependencies + pytest config
.env.example              # Template de variáveis de ambiente
README.md                 # Documentação completa + uso de IA
```

**Structure Decision**: Single project (Option 1) — serviço monolítico com FastAPI servindo API REST. Sem frontend separado. Redis roda como container companion via Docker Compose.

## Complexity Tracking

> Nenhuma violação da Constitution identificada. Tabela vazia = conformidade total.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| — | — | — |
