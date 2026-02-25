# Speckit — Blis AI Technical Test: Multi-Agent Travel Assistant

---

## 📜 CONSTITUTION

### Identidade do Projeto
- **Nome**: `blis-travel-agents`
- **Descrição**: Sistema multi-agent de IA para agências de viagem, com FAQ Agent (RAG), Search Agent (Web Search) e Orchestrator, expostos via API REST FastAPI
- **Repositório**: GitHub público
- **Linguagem principal**: Python 3.11+

### Princípios de Desenvolvimento

1. **AI-First Development**: Todo o desenvolvimento DEVE ser feito com AI coding agent (Claude Code/Cursor). Cada decisão, debug e refactor deve ser documentado para a seção "Como usei IA no desenvolvimento"
2. **Commits incrementais**: Commits frequentes e descritivos em português ou inglês. Nunca um dump final. O histórico deve contar a história da construção
3. **Type Safety**: Pydantic models para TODOS os contratos de dados — requests, responses, estados do grafo, configurações
4. **Clean Architecture**: Separação clara entre camadas — API (FastAPI), orquestração (LangGraph), agentes, ferramentas, e infraestrutura (vector store, Redis)
5. **Production-Ready Mindset**: Mesmo sendo um teste, tratar como código de produção — logging estruturado, error handling, configuração via env vars, Docker
6. **DRY e KISS**: Sem over-engineering, sem abstrações prematuras. Código limpo e legível

### Restrições Técnicas Obrigatórias
- Python 3.11+ com tipagem forte
- FastAPI como framework web
- LangGraph para orquestração de agentes
- Redis como checkpointer de sessão (`langgraph-checkpoint-redis`)
- MemorySaver APENAS como fallback local
- Vector store para RAG (FAISS ou Chroma)
- Tool de web search (Tavily preferencial)
- Docker Compose subindo Redis + API
- Endpoint `POST /chat` com `{ "session_id": "...", "message": "..." }`

### Padrões de Código
- **Formatação**: `ruff` para linting e formatting
- **Imports**: organizados com `isort`
- **Docstrings**: Google style em funções públicas
- **Variáveis de ambiente**: gerenciadas via `pydantic-settings`
- **Nomes**: snake_case para funções/variáveis, PascalCase para classes, UPPER_CASE para constantes

### Padrões de Commit
```
feat: adiciona FAQ Agent com RAG sobre políticas de viagem
fix: corrige chunking de tabelas no PDF de bagagem
refactor: extrai lógica de roteamento do orchestrator
docs: adiciona seção de MCPs no README
test: adiciona testes do endpoint /chat
chore: configura docker-compose com Redis
```

### MCPs Configurados e Justificativa
| MCP | Justificativa |
|-----|---------------|
| Filesystem | Navegação, leitura e edição de arquivos do projeto |
| Git | Commits incrementais, diffs, gerenciamento de branches |
| Brave Search / Web Search | Pesquisa de docs atualizadas de LangGraph, langgraph-checkpoint-redis, FastAPI |
| Docker | Gerenciamento de containers Redis e API, debug de logs |
| GitHub (Speckit) | Criação de issues, PRs, e gerenciamento do repositório |
| Sequential Thinking | Planejamento de arquitetura e decisões de design complexas |

---

## 📋 SPECIFY

### Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────┐
│                    Cliente (HTTP)                     │
│              POST /chat + GET /health                │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                  FastAPI Server                       │
│  ┌─────────────────────────────────────────────┐    │
│  │           Router (/api/v1/chat)              │    │
│  │  - Valida request (Pydantic)                 │    │
│  │  - Carrega/cria sessão                       │    │
│  │  - Invoca grafo LangGraph                    │    │
│  │  - Retorna resposta (JSON ou SSE stream)     │    │
│  └──────────────────┬──────────────────────────┘    │
│                     │                                │
│  ┌──────────────────▼──────────────────────────┐    │
│  │         LangGraph Orchestrator Graph         │    │
│  │                                              │    │
│  │  ┌──────────┐   ┌───────────┐               │    │
│  │  │ classify │──▶│  route    │               │    │
│  │  │  intent  │   │ decision  │               │    │
│  │  └──────────┘   └─────┬─────┘               │    │
│  │                  ┌─────┼──────┐              │    │
│  │                  ▼     ▼      ▼              │    │
│  │          ┌──────┐ ┌──────┐ ┌──────┐         │    │
│  │          │ FAQ  │ │Search│ │ Both │         │    │
│  │          │Agent │ │Agent │ │      │         │    │
│  │          └──┬───┘ └──┬───┘ └──┬───┘         │    │
│  │             └────┬───┘        │              │    │
│  │                  ▼            │              │    │
│  │          ┌──────────────┐     │              │    │
│  │          │  synthesize  │◀────┘              │    │
│  │          │   response   │                    │    │
│  │          └──────────────┘                    │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────┐  ┌────────────────────────┐     │
│  │  FAISS / Chroma │  │  Redis (Checkpointer)  │     │
│  │  (Vector Store) │  │  (Session State)       │     │
│  └────────────────┘  └────────────────────────┘     │
└──────────────────────────────────────────────────────┘
```

### Estrutura de Diretórios

```
blis-travel-agents/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── .env.example
├── README.md
├── data/
│   └── manual-politicas-viagem-blis.pdf
├── src/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # pydantic-settings configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── chat.py              # POST /chat, GET /chat/stream (SSE)
│   │   ├── schemas.py               # Request/Response Pydantic models
│   │   └── dependencies.py          # FastAPI dependencies (graph, checkpointer)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py          # LangGraph graph definition + routing
│   │   ├── faq_agent.py             # FAQ Agent (RAG)
│   │   └── search_agent.py          # Search Agent (Tavily)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── web_search.py            # Tavily search tool wrapper
│   │   └── rag_retriever.py         # RAG retrieval tool
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── ingest.py                # PDF loading + chunking + embedding
│   │   ├── vectorstore.py           # FAISS/Chroma setup and persistence
│   │   └── prompts.py               # RAG prompt templates
│   ├── state/
│   │   ├── __init__.py
│   │   └── graph_state.py           # TypedDict/Pydantic state for LangGraph
│   └── core/
│       ├── __init__.py
│       ├── logging.py               # Structured logging (structlog)
│       └── checkpointer.py          # Redis checkpointer setup + MemorySaver fallback
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Fixtures (test client, mock graph)
│   ├── test_chat_endpoint.py        # API endpoint tests
│   ├── test_faq_agent.py            # RAG retrieval tests
│   ├── test_search_agent.py         # Search agent tests
│   └── test_orchestrator.py         # Routing logic tests
└── scripts/
    ├── ingest_documents.py          # Script para popular vector store
    └── healthcheck.py               # Docker healthcheck script
```

### Modelos de Dados (Pydantic)

```python
# === API Schemas ===

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128, examples=["session-abc-123"])
    message: str = Field(..., min_length=1, max_length=4096)

class ChatResponse(BaseModel):
    session_id: str
    response: str
    agent_used: Literal["faq", "search", "both"]
    sources: list[Source] = []
    timestamp: datetime

class Source(BaseModel):
    type: Literal["document", "web"]
    title: str
    content_preview: str = ""
    url: str | None = None

class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded"]
    redis_connected: bool
    vectorstore_loaded: bool
    version: str

# === Graph State ===

class AgentRoute(str, Enum):
    FAQ = "faq"
    SEARCH = "search"
    BOTH = "both"

class GraphState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    route: AgentRoute
    faq_response: str | None
    search_response: str | None
    final_response: str
    sources: list[dict]

# === Config ===

class Settings(BaseSettings):
    # API
    app_name: str = "Blis Travel Agents"
    app_version: str = "1.0.0"
    debug: bool = False

    # LLM
    openai_api_key: SecretStr
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1

    # Search
    tavily_api_key: SecretStr

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Vector Store
    vectorstore_path: str = "./data/vectorstore"
    embedding_model: str = "text-embedding-3-small"

    # RAG
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 5

    model_config = SettingsConfigDict(env_file=".env")
```

### LangGraph — Grafo do Orchestrator

```python
# Nós do grafo:

def classify_intent(state: GraphState) -> GraphState:
    """
    Usa LLM para classificar a intenção do usuário:
    - FAQ: perguntas sobre políticas, bagagem, check-in, documentação, reembolso
    - SEARCH: preços atuais, disponibilidade, notícias de companhias
    - BOTH: perguntas que combinam política + informação atual
    """
    ...

def faq_agent(state: GraphState) -> GraphState:
    """
    1. Retrieval: busca chunks relevantes no vector store
    2. Generation: LLM gera resposta baseada nos chunks + contexto da conversa
    3. Popula faq_response e sources no state
    """
    ...

def search_agent(state: GraphState) -> GraphState:
    """
    1. Reformula query para busca web
    2. Executa Tavily search
    3. LLM sintetiza resultados em resposta útil
    4. Popula search_response e sources no state
    """
    ...

def synthesize_response(state: GraphState) -> GraphState:
    """
    Consolida respostas do(s) agente(s):
    - Se apenas FAQ: usa faq_response diretamente
    - Se apenas Search: usa search_response diretamente
    - Se ambos: LLM combina as duas respostas em uma coerente
    Popula final_response
    """
    ...

# Edges (roteamento condicional):

def route_by_intent(state: GraphState) -> str:
    """Retorna 'faq', 'search', ou 'both' baseado no state.route"""
    ...

# Grafo:
# START -> classify_intent -> route_by_intent -> {faq_agent | search_agent | both}
# both: faq_agent -> search_agent
# {faq_agent, search_agent} -> synthesize_response -> END
```

### RAG Pipeline

```
PDF (manual-politicas-viagem-blis.pdf)
    │
    ▼
PyPDFLoader / pdfplumber (preservar tabelas)
    │
    ▼
RecursiveCharacterTextSplitter
    - chunk_size: 1000 tokens
    - chunk_overlap: 200 tokens
    - separators: ["\n\n", "\n", ". ", " "]
    │
    ▼
Metadata enrichment
    - section: "Políticas de Bagagem", "Documentação", etc.
    - page_number: int
    - source: "manual-politicas-viagem-blis-v2.1"
    │
    ▼
OpenAI Embeddings (text-embedding-3-small)
    │
    ▼
FAISS VectorStore (persistido em disco)
    │
    ▼
Retriever (top_k=5, MMR diversity)
```

### Prompt Templates

```python
# Orchestrator — Classificação de intenção
CLASSIFY_INTENT_PROMPT = """
Você é um roteador inteligente de uma agência de viagens.
Analise a pergunta do usuário e classifique em uma das categorias:

- FAQ: perguntas sobre políticas da agência, bagagem, check-in, documentação,
  remarcação, cancelamento, reembolso, animais de estimação, necessidades especiais,
  fidelidade, conexões. Qualquer coisa coberta pelo manual de políticas.
- SEARCH: perguntas sobre preços atuais de passagens, disponibilidade de voos,
  notícias recentes de companhias aéreas, promoções, destinos.
- BOTH: perguntas que combinam política da agência com informação atual.
  Ex: "Quanto custa despachar bagagem extra na LATAM para Orlando em março?"

Responda APENAS com: FAQ, SEARCH ou BOTH

Pergunta: {query}
Classificação:
"""

# FAQ Agent — RAG
FAQ_AGENT_PROMPT = """
Você é um assistente especialista em políticas de viagem da Blis AI.
Use APENAS as informações do contexto abaixo para responder.
Se a informação não estiver no contexto, diga que não tem essa informação disponível.
Sempre cite a seção relevante do manual quando possível.
Responda em português brasileiro de forma clara e profissional.

Contexto:
{context}

Histórico da conversa:
{chat_history}

Pergunta do cliente: {query}

Resposta:
"""

# Search Agent
SEARCH_AGENT_PROMPT = """
Você é um assistente de viagens com acesso a informações em tempo real.
Use os resultados da busca abaixo para responder a pergunta do cliente.
Sempre mencione a fonte da informação e a data quando disponível.
Se os resultados não forem suficientes, informe o cliente.
Responda em português brasileiro.

Resultados da busca:
{search_results}

Histórico da conversa:
{chat_history}

Pergunta do cliente: {query}

Resposta:
"""

# Synthesizer — Combinação de respostas
SYNTHESIZE_PROMPT = """
Você é o assistente principal da Blis AI, uma agência de viagens.
Combine as informações abaixo em uma resposta única, coerente e completa.
Priorize informações do manual de políticas, complementando com dados atuais da web.
Se houver contradição, mencione ambas as fontes.

Resposta do FAQ Agent (manual de políticas):
{faq_response}

Resposta do Search Agent (busca web):
{search_response}

Pergunta original: {query}

Resposta consolidada:
"""
```

### Endpoints da API

```
POST /api/v1/chat
    Request:  { "session_id": "abc123", "message": "Qual o limite de bagagem na LATAM?" }
    Response: { "session_id": "abc123", "response": "...", "agent_used": "faq", "sources": [...], "timestamp": "..." }

GET /api/v1/chat/stream   (DIFERENCIAL — SSE)
    Query params: session_id, message
    Response: text/event-stream
    Events: { "event": "token", "data": "..." } / { "event": "done", "data": {...} }

GET /health
    Response: { "status": "healthy", "redis_connected": true, "vectorstore_loaded": true, "version": "1.0.0" }
```

### Docker Compose

```yaml
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - vectorstore_data:/app/data/vectorstore

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
    volumes:
      - redis_data:/data

volumes:
  redis_data:
  vectorstore_data:
```

### Dependências Principais

```toml
[project]
name = "blis-travel-agents"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "langchain>=0.3",
    "langgraph>=0.2",
    "langchain-openai>=0.2",
    "langchain-community>=0.3",
    "langgraph-checkpoint-redis>=0.1",
    "faiss-cpu>=1.8",
    "tavily-python>=0.5",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "python-dotenv>=1.0",
    "structlog>=24.0",
    "sse-starlette>=2.0",
    "pypdf>=4.0",
    "redis>=5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "httpx>=0.27",
    "ruff>=0.6",
]
```

---

## 🗺️ PLAN

### Fase 0 — Setup Inicial (30 min)
**Objetivo**: Repo funcional com estrutura base

- [ ] Criar repositório no GitHub `blis-travel-agents`
- [ ] `git init` + `.gitignore` (Python)
- [ ] Criar `pyproject.toml` com todas as dependências
- [ ] Criar estrutura de diretórios conforme SPECIFY
- [ ] Criar `.env.example` com todas as variáveis necessárias
- [ ] Criar `docker-compose.yml` com Redis + API
- [ ] Criar `Dockerfile` multi-stage (builder + runtime)
- [ ] **Commit**: `chore: setup inicial do projeto com estrutura de diretórios e dependências`

### Fase 1 — Configuração e Infraestrutura (30 min)
**Objetivo**: Config carregando, logging funcionando, Redis conectando

- [ ] Implementar `src/config.py` com `Settings(BaseSettings)`
- [ ] Implementar `src/core/logging.py` com structlog
- [ ] Implementar `src/core/checkpointer.py` — Redis checkpointer com fallback MemorySaver
- [ ] Implementar `src/main.py` — FastAPI app com lifespan (startup: conectar Redis, carregar vectorstore)
- [ ] Implementar `GET /health` endpoint
- [ ] Testar: `docker-compose up` e verificar que Redis sobe e health retorna OK
- [ ] **Commit**: `feat: adiciona configuração, logging estruturado e checkpointer Redis`

### Fase 2 — RAG Pipeline (45 min)
**Objetivo**: PDF ingerido, vector store populado, retrieval funcionando

- [ ] Colocar `manual-politicas-viagem-blis.pdf` em `data/`
- [ ] Implementar `src/rag/ingest.py`:
  - Carregar PDF com PyPDFLoader
  - Chunking com RecursiveCharacterTextSplitter
  - Enriquecer metadata (seção, página)
- [ ] Implementar `src/rag/vectorstore.py`:
  - Criar FAISS index a partir dos chunks
  - Persistir em disco
  - Carregar index existente no startup
- [ ] Implementar `scripts/ingest_documents.py` (CLI para popular o vector store)
- [ ] Implementar `src/tools/rag_retriever.py` como LangChain tool
- [ ] Testar: rodar ingestão e fazer query de teste no vector store
- [ ] **Commit**: `feat: implementa pipeline RAG com ingestão de PDF e vector store FAISS`

### Fase 3 — FAQ Agent (30 min)
**Objetivo**: Agent que responde perguntas usando RAG

- [ ] Implementar `src/rag/prompts.py` com templates
- [ ] Implementar `src/agents/faq_agent.py`:
  - Recebe state do grafo
  - Faz retrieval no vector store
  - Gera resposta com LLM + contexto
  - Retorna state atualizado com `faq_response` e `sources`
- [ ] Testar isoladamente com queries sobre bagagem, documentação, check-in
- [ ] **Commit**: `feat: implementa FAQ Agent com RAG sobre manual de políticas`

### Fase 4 — Search Agent (30 min)
**Objetivo**: Agent que busca informações em tempo real

- [ ] Implementar `src/tools/web_search.py` — wrapper do Tavily
- [ ] Implementar `src/agents/search_agent.py`:
  - Recebe state do grafo
  - Reformula query para busca
  - Executa Tavily search
  - Sintetiza resultados com LLM
  - Retorna state com `search_response` e `sources`
- [ ] Testar com queries sobre preços de passagem, novidades de companhias
- [ ] **Commit**: `feat: implementa Search Agent com Tavily para busca em tempo real`

### Fase 5 — Orchestrator + LangGraph (45 min)
**Objetivo**: Grafo completo orquestrando ambos os agentes

- [ ] Implementar `src/state/graph_state.py` com TypedDict
- [ ] Implementar `src/agents/orchestrator.py`:
  - Nó `classify_intent` — LLM classifica FAQ/SEARCH/BOTH
  - Nó `faq_agent` — chama FAQ Agent
  - Nó `search_agent` — chama Search Agent
  - Nó `synthesize_response` — consolida resposta final
  - Função `route_by_intent` — roteamento condicional
  - Montar grafo com `StateGraph`
  - Compilar com Redis checkpointer
- [ ] Testar grafo end-to-end com os 3 tipos de rota
- [ ] **Commit**: `feat: implementa Orchestrator com LangGraph e roteamento condicional`

### Fase 6 — API Endpoint /chat (30 min)
**Objetivo**: Endpoint REST funcional

- [ ] Implementar `src/api/schemas.py` com Pydantic models
- [ ] Implementar `src/api/dependencies.py` — injeção do grafo e checkpointer
- [ ] Implementar `src/api/routes/chat.py`:
  - `POST /chat` — recebe request, invoca grafo, retorna response
  - Gerenciar `session_id` como `thread_id` do LangGraph checkpointer
  - Error handling com HTTPException
- [ ] Testar via curl/httpx
- [ ] **Commit**: `feat: implementa endpoint POST /chat com persistência de sessão`

### Fase 7 — Diferenciais (45 min)
**Objetivo**: Streaming SSE, testes, polish

- [ ] **SSE Streaming** (`GET /chat/stream`):
  - Usar `sse-starlette` + `astream_events` do LangGraph
  - Stream tokens conforme são gerados
  - Evento final com metadata (agent_used, sources)
- [ ] **Commit**: `feat: adiciona streaming de resposta via SSE`
- [ ] **Testes básicos**:
  - `test_chat_endpoint.py` — testa POST /chat retorna 200, valida schema
  - `test_faq_agent.py` — testa que RAG retorna contexto relevante
  - `test_orchestrator.py` — testa que roteamento funciona para cada tipo
- [ ] **Commit**: `test: adiciona testes básicos para endpoint, FAQ agent e orchestrator`

### Fase 8 — Documentação e Finalização (30 min)
**Objetivo**: README completo, tudo rodando no Docker

- [ ] Escrever `README.md`:
  - Visão geral do projeto e arquitetura (com diagrama)
  - Pré-requisitos (Docker, API keys)
  - Setup: `docker-compose up --build`
  - Variáveis de ambiente (.env.example)
  - Exemplos de uso (curl commands)
  - **Seção "Como usei IA no desenvolvimento"**:
    - Ferramentas: Claude Code + Speckit
    - MCPs configurados e justificativa
    - Exemplos reais de uso (geração, debug, refactor)
    - O que funcionou vs. o que precisou de correção manual
  - Decisões técnicas e trade-offs
- [ ] Testar: clone limpo → `cp .env.example .env` → preencher keys → `docker-compose up` → funciona
- [ ] **Commit**: `docs: README completo com instruções de setup e seção de uso de IA`
- [ ] Review final do código + cleanup
- [ ] **Commit**: `chore: cleanup final e review de código`

### Tempo Estimado Total: ~5 horas

### Ordem de Prioridade (se faltar tempo)
1. ✅ Obrigatório: Fases 0–6 (API funcional com RAG + Search + Orchestrator + Redis)
2. ⭐ Alto impacto: Fase 8 (README — é critério de avaliação)
3. 🌟 Diferenciais: Fase 7 (SSE streaming + testes)

### Exemplos de Queries para Testar

| Query | Rota esperada | Agente(s) |
|-------|---------------|-----------|
| "Qual o limite de bagagem de mão na LATAM?" | FAQ | FAQ Agent |
| "Preciso de visto para ir ao Chile?" | FAQ | FAQ Agent |
| "Como funciona o check-in online?" | FAQ | FAQ Agent |
| "Quanto está a passagem São Paulo-Lisboa em março?" | SEARCH | Search Agent |
| "A GOL está com alguma promoção?" | SEARCH | Search Agent |
| "Quero levar meu cachorro para Portugal, o que preciso?" | BOTH | FAQ + Search |
| "Qual a franquia de bagagem da Azul e quanto custa um upgrade?" | BOTH | FAQ + Search |
| "Posso remarcar minha passagem Light da LATAM? Tem alguma promoção pra mesma data?" | BOTH | FAQ + Search |
