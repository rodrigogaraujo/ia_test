# Quickstart: Multi-Agent Travel Assistant

**Feature**: `001-multi-agent-travel` | **Date**: 2025-02-25

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- API key OpenAI (modelo gpt-4o-mini + embeddings)
- API key Tavily (busca web)

## Setup (< 10 minutos)

### 1. Clone e configure

```bash
git clone <repo-url>
cd blis-travel-agents
cp .env.example .env
```

Edite `.env` com suas API keys:
```env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

### 2. Suba com Docker Compose

```bash
docker compose up --build
```

Isso sobe:
- **API** em `http://localhost:8000`
- **Redis 7** em `localhost:6379`

### 3. Ingira o PDF (primeira vez)

```bash
docker compose exec api python scripts/ingest_documents.py
```

O vector store FAISS será gerado em `/app/data/vectorstore/`.

### 4. Verifique o health

```bash
curl http://localhost:8000/health
```

Resposta esperada:
```json
{"status": "healthy", "redis_connected": true, "vectorstore_loaded": true, "version": "1.0.0"}
```

## Uso

### Pergunta FAQ (política de viagem)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "teste-1", "message": "Qual o limite de bagagem de mão na LATAM?"}'
```

### Pergunta Search (informação atual)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "teste-2", "message": "Quanto está a passagem SP-Lisboa em março?"}'
```

### Pergunta Híbrida (FAQ + Search)

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "teste-3", "message": "Quero levar meu cachorro para Portugal, o que preciso?"}'
```

### Streaming SSE

```bash
curl -N "http://localhost:8000/api/v1/chat/stream?session_id=teste-4&message=Como+funciona+o+check-in+online?"
```

## Desenvolvimento Local (sem Docker)

```bash
# Instale dependências
pip install -e ".[dev]"

# Suba Redis manualmente
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Ingira documentos
python scripts/ingest_documents.py

# Rode a API
uvicorn src.main:app --reload --port 8000
```

## Testes

```bash
pytest tests/ -v
```
