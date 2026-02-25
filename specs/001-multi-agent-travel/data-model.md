# Data Model: Multi-Agent Travel Assistant

**Feature**: `001-multi-agent-travel` | **Date**: 2025-02-25

## Entities

### 1. ChatRequest (API Input)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| session_id | string | min=1, max=128, required | Identificador único da sessão conversacional |
| message | string | min=1, max=4096, required | Texto da pergunta do atendente |

**Validation Rules**:
- `session_id` não pode ser vazio nem conter apenas espaços
- `message` não pode ser vazio nem conter apenas espaços
- Campos extras são rejeitados (Pydantic `model_config = ConfigDict(extra="forbid")`)

---

### 2. ChatResponse (API Output)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| session_id | string | required | Echo do session_id da request |
| response | string | required | Texto completo da resposta |
| agent_used | enum | "faq" \| "search" \| "both", required | Qual agente processou |
| sources | list[Source] | default=[] | Fontes consultadas |
| timestamp | datetime | auto-generated (UTC) | Momento da resposta |

---

### 3. Source (Reference)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| type | enum | "document" \| "web", required | Tipo da fonte |
| title | string | required | Título/nome da fonte |
| content_preview | string | default="" | Trecho relevante do conteúdo |
| url | string \| null | default=None | URL (apenas para fontes web) |

**State Transitions**: N/A (imutável)

---

### 4. GraphState (Orchestrator State)

| Field | Type | Reducer | Description |
|-------|------|---------|-------------|
| messages | list[BaseMessage] | add_messages | Histórico de mensagens (merge automático) |
| user_query | string | overwrite | Pergunta original do usuário |
| route | AgentRoute | overwrite | Classificação de intenção |
| faq_response | string \| None | overwrite | Resposta do FAQ Agent |
| search_response | string \| None | overwrite | Resposta do Search Agent |
| final_response | string | overwrite | Resposta consolidada final |
| sources | list[dict] | overwrite | Fontes coletadas de todos os agentes |

**State Transitions**:
```
INIT → classify_intent → route_by_intent
  → FAQ: faq_agent → synthesize_response → END
  → SEARCH: search_agent → synthesize_response → END
  → BOTH: faq_agent → search_agent → synthesize_response → END
```

---

### 5. AgentRoute (Enum)

| Value | Description | Agents Acionados |
|-------|-------------|------------------|
| FAQ | Pergunta sobre políticas documentadas | FAQ Agent apenas |
| SEARCH | Pergunta sobre informações atuais | Search Agent apenas |
| BOTH | Combina política + informação atual | FAQ Agent → Search Agent |

---

### 6. HealthStatus (System Status)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| status | enum | "healthy" \| "degraded", required | Estado geral do sistema |
| redis_connected | boolean | required | Conexão com Redis ativa |
| vectorstore_loaded | boolean | required | Vector store carregado em memória |
| version | string | required | Versão da aplicação |

**Rules**:
- `status = "healthy"` quando `redis_connected=true` AND `vectorstore_loaded=true`
- `status = "degraded"` quando qualquer dependência está indisponível
- Nunca `"unhealthy"` — o sistema sempre tenta operar

---

### 7. Settings (Configuration)

| Field | Type | Source | Default | Description |
|-------|------|--------|---------|-------------|
| app_name | string | env/default | "Blis Travel Agents" | Nome da aplicação |
| app_version | string | env/default | "1.0.0" | Versão |
| debug | boolean | env | false | Modo debug |
| openai_api_key | SecretStr | env | required | API key OpenAI |
| llm_model | string | env/default | "gpt-4o-mini" | Modelo LLM |
| llm_temperature | float | env/default | 0.1 | Temperatura do LLM |
| tavily_api_key | SecretStr | env | required | API key Tavily |
| redis_url | string | env/default | "redis://localhost:6379" | URL do Redis |
| vectorstore_path | string | env/default | "./data/vectorstore" | Caminho do FAISS index |
| embedding_model | string | env/default | "text-embedding-3-small" | Modelo de embeddings |
| chunk_size | int | env/default | 1500 | Tamanho do chunk |
| chunk_overlap | int | env/default | 200 | Overlap entre chunks |
| retrieval_top_k | int | env/default | 5 | Quantidade de documentos retornados |

**Security**:
- `openai_api_key` e `tavily_api_key` DEVEM ser `SecretStr`
- Nunca logados, nunca em respostas de erro
- Carregados exclusivamente via `.env` / variáveis de ambiente

## Relationships

```
ChatRequest ──(1:1)──→ GraphState (cria estado inicial)
GraphState  ──(1:1)──→ AgentRoute (classificação)
GraphState  ──(0..n)──→ Source (fontes coletadas)
GraphState  ──(1:1)──→ ChatResponse (resposta final)
Session     ──(1:n)──→ ChatRequest (múltiplas mensagens)
Session     ──(via)──→ Redis Checkpointer (thread_id = session_id)
```
