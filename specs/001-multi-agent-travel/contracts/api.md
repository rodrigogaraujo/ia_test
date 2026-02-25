# API Contract: Multi-Agent Travel Assistant

**Feature**: `001-multi-agent-travel` | **Date**: 2025-02-25

## Base URL

```
http://localhost:8000
```

## Versioning

API versionada via path prefix: `/api/v1/`

---

## Endpoints

### POST /api/v1/chat

Envia uma pergunta e recebe resposta completa.

**Request**:
```json
{
  "session_id": "abc123",
  "message": "Qual o limite de bagagem de mão na LATAM?"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| session_id | string | yes | min_length=1, max_length=128 |
| message | string | yes | min_length=1, max_length=4096 |

**Response (200)**:
```json
{
  "session_id": "abc123",
  "response": "De acordo com a Seção 1.1 do manual...",
  "agent_used": "faq",
  "sources": [
    {
      "type": "document",
      "title": "Manual de Políticas - Seção 1.1",
      "content_preview": "Bagagem de mão: 10 kg, dimensão máxima 115 cm...",
      "url": null
    }
  ],
  "timestamp": "2025-02-25T14:30:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| session_id | string | Echo do session_id da request |
| response | string | Texto completo da resposta em PT-BR |
| agent_used | "faq" \| "search" \| "both" | Agente(s) que processou a pergunta |
| sources | Source[] | Lista de fontes consultadas |
| timestamp | ISO 8601 datetime | Momento da resposta (UTC) |

**Errors**:

| Status | Condition | Body |
|--------|-----------|------|
| 422 | Validação falhou (campo vazio, excede limite) | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| 503 | Dependência crítica indisponível (OpenAI) | `{"detail": "Serviço temporariamente indisponível"}` |
| 500 | Erro interno não tratado | `{"detail": "Erro interno do servidor"}` |

---

### GET /api/v1/chat/stream

Streaming de resposta via Server-Sent Events (SSE). **Diferencial**.

**Query Parameters**:

| Param | Type | Required | Constraints |
|-------|------|----------|-------------|
| session_id | string | yes | min_length=1, max_length=128 |
| message | string | yes | min_length=1, max_length=4096 |

**SSE Events**:

```
event: token
data: {"token": "De"}

event: token
data: {"token": " acordo"}

event: token
data: {"token": " com"}

...

event: done
data: {"session_id": "abc123", "agent_used": "faq", "sources": [...], "timestamp": "2025-02-25T14:30:00Z"}
```

| Event | Data | Description |
|-------|------|-------------|
| token | `{"token": "..."}` | Token individual da resposta |
| done | ChatResponse metadata | Evento final com metadados completos |
| error | `{"detail": "..."}` | Erro durante processamento |

**Headers**:
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

---

### GET /health

Health check do sistema.

**Response (200)**:
```json
{
  "status": "healthy",
  "redis_connected": true,
  "vectorstore_loaded": true,
  "version": "1.0.0"
}
```

| Field | Type | Description |
|-------|------|-------------|
| status | "healthy" \| "degraded" | Estado geral |
| redis_connected | boolean | Conexão Redis ativa |
| vectorstore_loaded | boolean | FAISS index carregado |
| version | string | Versão da aplicação |

**Rules**:
- Sempre retorna 200 (mesmo degraded)
- `healthy` = todas as dependências OK
- `degraded` = alguma dependência indisponível mas sistema operando

---

## Common Headers

**Request**:
```
Content-Type: application/json
```

**Response**:
```
Content-Type: application/json
X-Request-ID: <uuid>  (opcional, para rastreamento)
```

## CORS

- Configurado explicitamente via `CORSMiddleware`
- Origins permitidas definidas via variável de ambiente
- Default: `["*"]` em desenvolvimento, restrito em produção

## Rate Limiting

- Não implementado na v1.0 (escopo do teste)
- Recomendado para produção: 60 req/min por session_id
