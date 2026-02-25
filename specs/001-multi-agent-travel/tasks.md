# Tasks: Multi-Agent Travel Assistant

**Input**: Design documents from `/specs/001-multi-agent-travel/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api.md

**Tests**: Testes básicos incluídos na fase de Polish (diferencial avaliado no teste técnico).

**Organization**: Tasks agrupadas por user story para implementação e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialização do projeto, estrutura de diretórios, dependências e containerização.

**Skills**: `docker-expert`, `python-patterns`

- [x] T001 Create project directory structure per plan.md (src/, tests/, scripts/, data/ with all __init__.py files)
- [x] T002 Create pyproject.toml with all dependencies (fastapi, langgraph, langchain-openai, faiss-cpu, tavily-python, langgraph-checkpoint-redis, pydantic, pydantic-settings, structlog, sse-starlette, pdfplumber, httpx, pytest) in pyproject.toml
- [x] T003 [P] Create .env.example with all required env vars (OPENAI_API_KEY, TAVILY_API_KEY, REDIS_URL) in .env.example
- [x] T004 [P] Create Dockerfile with Python 3.11-slim, non-root user, pip install from pyproject.toml in Dockerfile
- [x] T005 [P] Create docker-compose.yml with Redis 7-alpine (healthcheck) + API service (depends_on, volumes) in docker-compose.yml
- [x] T006 [P] Create .gitignore (venv, __pycache__, .env, data/vectorstore/, *.faiss, *.pkl) in .gitignore

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestrutura core que DEVE estar completa antes de qualquer user story.

**Skills**: `backend-dev-guidelines`, `cc-skill-security-review`, `api-patterns`

**CRITICAL**: Nenhuma user story pode começar até esta fase estar completa.

- [x] T007 Implement Settings(BaseSettings) with all config fields (SecretStr for API keys, defaults per data-model.md) in src/config.py
- [x] T008 [P] Implement structlog configuration (JSON format, log level from settings, processors) in src/core/logging.py
- [x] T009 [P] Implement Pydantic schemas (ChatRequest, ChatResponse, Source, HealthResponse) per data-model.md in src/api/schemas.py
- [x] T010 [P] Implement GraphState TypedDict with Annotated[list[BaseMessage], add_messages] and AgentRoute enum in src/state/graph_state.py
- [x] T011 [P] Implement all prompt templates (classify_intent, faq_agent, search_agent, synthesizer) in src/rag/prompts.py
- [x] T012 Create FastAPI app skeleton with lifespan context manager, CORS middleware, exception handlers in src/main.py
- [x] T013 Implement GET /health endpoint checking Redis and vectorstore status in src/main.py
- [x] T014 [P] Create Docker healthcheck script using /health endpoint in scripts/healthcheck.py

**Checkpoint**: Foundation ready — user story implementation can now begin.

---

## Phase 3: User Story 1 — FAQ sobre Políticas de Viagem (Priority: P1) MVP

**Goal**: Atendente envia pergunta sobre políticas (bagagem, documentação, check-in) e recebe resposta precisa do manual com citação de seção.

**Independent Test**: `curl -X POST http://localhost:8000/api/v1/chat -H "Content-Type: application/json" -d '{"session_id":"test","message":"Qual o limite de bagagem de mão na LATAM?"}'` retorna resposta com `agent_used: "faq"` e `sources` com referência ao documento.

**Skills**: `rag-implementation`, `rag-engineer`, `langgraph`, `prompt-engineering`

### Implementation for User Story 1

- [x] T015 [US1] Implement PDF ingestion with pdfplumber (table detection, markdown conversion, metadata enrichment with page_number/section) in src/rag/ingest.py
- [x] T016 [US1] Implement FAISS vectorstore setup with OpenAIEmbeddings, save_local/load_local persistence, MMR retriever config (k=5, fetch_k=25, lambda_mult=0.6) in src/rag/vectorstore.py
- [x] T017 [US1] Create ingest CLI script that loads PDF from data/, chunks with RecursiveCharacterTextSplitter (1500/200), builds FAISS index in scripts/ingest_documents.py
- [x] T018 [US1] Implement RAG retriever tool wrapping FAISS vectorstore.as_retriever() with source formatting in src/tools/rag_retriever.py
- [x] T019 [US1] Implement FAQ agent node (retrieve context via RAG, call LLM with faq_prompt, populate faq_response + sources in state) in src/agents/faq_agent.py
- [x] T020 [US1] Implement classify_intent node (LLM call with classify prompt, parse response into AgentRoute, update state.route) in src/agents/orchestrator.py
- [x] T021 [US1] Implement LangGraph StateGraph with nodes (classify_intent, faq_agent, synthesize_response), conditional edges (route_by_intent), FAQ route wired to END in src/agents/orchestrator.py
- [x] T022 [US1] Implement dependency injection (get_graph, get_settings) using FastAPI Depends and app.state in src/api/dependencies.py
- [x] T023 [US1] Implement POST /api/v1/chat endpoint with request validation, graph invocation (MemorySaver temporário), ChatResponse construction in src/api/routes/chat.py
- [x] T024 [US1] Wire chat router into FastAPI app, update lifespan to load vectorstore on startup in src/main.py

**Checkpoint**: FAQ Agent funcional. POST /chat responde perguntas sobre políticas com citação de seção. agent_used="faq".

---

## Phase 4: User Story 2 — Busca de Informações em Tempo Real (Priority: P2)

**Goal**: Atendente envia pergunta sobre informações atuais (preços, promoções) e recebe resposta baseada em busca web com fontes citadas.

**Independent Test**: `curl -X POST http://localhost:8000/api/v1/chat -H "Content-Type: application/json" -d '{"session_id":"test","message":"Quanto está a passagem SP-Lisboa em março?"}'` retorna resposta com `agent_used: "search"` e `sources` com URLs.

**Skills**: `langgraph`, `llm-app-patterns`

### Implementation for User Story 2

- [x] T025 [P] [US2] Implement Tavily web search wrapper (TavilySearchResults, max_results=5, error handling for API unavailability) in src/tools/web_search.py
- [x] T026 [US2] Implement Search agent node (call Tavily tool, call LLM with search_prompt + results, populate search_response + sources in state) in src/agents/search_agent.py
- [x] T027 [US2] Add SEARCH route to orchestrator graph (search_agent node, conditional edge from classify_intent to search_agent, edge to synthesize_response) in src/agents/orchestrator.py

**Checkpoint**: Search Agent funcional. POST /chat roteia perguntas de preço/promoção para busca web. agent_used="search".

---

## Phase 5: User Story 3 — Perguntas Híbridas (Priority: P3)

**Goal**: Atendente envia pergunta que combina política + informação atual, sistema consulta ambos agentes e consolida em resposta única.

**Independent Test**: `curl -X POST http://localhost:8000/api/v1/chat -H "Content-Type: application/json" -d '{"session_id":"test","message":"Quero levar meu cachorro para Portugal, o que preciso?"}'` retorna resposta com `agent_used: "both"` e `sources` contendo documentos E URLs.

**Skills**: `langgraph`, `ai-agents-architect`, `architecture`

### Implementation for User Story 3

- [x] T028 [US3] Add BOTH route to orchestrator (sequential: faq_agent → search_agent → synthesize_response) with conditional edge from classify_intent in src/agents/orchestrator.py
- [x] T029 [US3] Implement synthesize_response node for BOTH route (combine faq_response + search_response via LLM with synthesizer prompt, merge sources) in src/agents/orchestrator.py

**Checkpoint**: Rota BOTH funcional. Perguntas híbridas acionam ambos agentes com resposta consolidada. agent_used="both".

---

## Phase 6: User Story 4 — Persistência de Sessão (Priority: P4)

**Goal**: Atendente mantém conversa contínua com mesmo session_id, sistema lembra contexto anterior.

**Independent Test**: Enviar "Qual o limite de bagagem da LATAM?" seguido de "E na GOL?" com mesmo session_id — segunda resposta deve ser contextualizada sobre bagagem.

**Skills**: `langgraph`, `database-design`, `backend-dev-guidelines`

### Implementation for User Story 4

- [x] T030 [US4] Implement AsyncRedisSaver initialization with from_conn_string(), asetup(), MemorySaver fallback via try/except in src/core/checkpointer.py
- [x] T031 [US4] Integrate checkpointer into FastAPI lifespan (async context manager, store in app.state) in src/main.py
- [x] T032 [US4] Update graph invocation to pass config={"configurable": {"thread_id": session_id}} and use checkpointer in src/api/dependencies.py and src/api/routes/chat.py
- [x] T033 [US4] Update /health endpoint to verify Redis connection status (ping) in src/main.py

**Checkpoint**: Sessões persistidas no Redis. Conversas multi-turn funcionam. /health reporta redis_connected.

---

## Phase 7: User Story 5 — Streaming de Resposta (Priority: P5)

**Goal**: Atendente recebe resposta token por token via SSE, com evento final contendo metadata.

**Independent Test**: `curl -N "http://localhost:8000/api/v1/chat/stream?session_id=test&message=Como+funciona+o+check-in+online?"` retorna eventos SSE incrementais com evento `done` final.

**Skills**: `backend-dev-guidelines`, `api-patterns`

### Implementation for User Story 5

- [x] T034 [US5] Implement GET /api/v1/chat/stream SSE endpoint with query parameter validation, EventSourceResponse from sse-starlette in src/api/routes/chat.py
- [x] T035 [US5] Implement async generator using graph.astream_events(version="v2"), filter on_chat_model_stream events, yield token/done/error SSE events in src/api/routes/chat.py

**Checkpoint**: Streaming SSE funcional. Tokens chegam incrementalmente com evento done final.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Testes, documentação, segurança e validação final.

**Skills**: `testing-patterns`, `documentation-templates`, `production-code-audit`, `vulnerability-scanner`

- [x] T036 [P] Create test fixtures (AsyncClient, mock settings, mock vectorstore, mock graph) in tests/conftest.py
- [x] T037 [P] Write chat endpoint tests (POST /chat validation: empty message, long session_id, successful FAQ/SEARCH/BOTH responses) in tests/test_chat_endpoint.py
- [x] T038 [P] Write FAQ agent tests (mock retriever returns docs, verify faq_response populated, sources formatted) in tests/test_faq_agent.py
- [x] T039 [P] Write orchestrator routing tests (mock LLM classify returns FAQ/SEARCH/BOTH, verify correct nodes executed) in tests/test_orchestrator.py
- [x] T040 [P] Write Search agent tests (mock Tavily results, verify search_response populated, URLs in sources) in tests/test_search_agent.py
- [x] T041 Write README.md with: project overview, architecture diagram, setup instructions, API usage examples, "Como usei IA no desenvolvimento" section in README.md
- [x] T042 Security hardening review (CORS config, generic error messages, prompt injection defense in all prompts, SecretStr validation) across src/
- [x] T043 Docker optimization (verify non-root user, volume mounts for vectorstore, multi-stage build if needed) in Dockerfile and docker-compose.yml
- [ ] T044 Run quickstart.md validation end-to-end (docker compose up, ingest, health check, test all 3 routes)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **US1 FAQ (Phase 3)**: Depends on Foundational — this IS the MVP
- **US2 Search (Phase 4)**: Depends on US1 (shares orchestrator graph structure)
- **US3 Hybrid (Phase 5)**: Depends on US1 + US2 (needs both agents functional)
- **US4 Session (Phase 6)**: Depends on US1 (needs working graph to add checkpointer)
- **US5 Streaming (Phase 7)**: Depends on US1 (needs working endpoint to add SSE)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational)
                      ↓
                Phase 3 (US1 - FAQ) ← MVP
                   ↓         ↓
            Phase 4 (US2)  Phase 6 (US4) [can run in parallel]
                   ↓              ↓
            Phase 5 (US3)     Phase 7 (US5) [can run in parallel]
                   ↓              ↓
                Phase 8 (Polish)
```

### Within Each User Story

- Models/state before tools
- Tools before agents
- Agents before orchestrator integration
- Orchestrator before endpoint wiring
- Commit after each logical group

### Parallel Opportunities

- **Phase 1**: T003, T004, T005, T006 can run in parallel (after T001, T002)
- **Phase 2**: T008, T009, T010, T011, T014 can run in parallel (after T007)
- **Phase 4**: T025 (Tavily wrapper) can start while US1 is finishing
- **Phase 6 + Phase 4**: US4 (session) can run in parallel with US2 (search) after US1 completes
- **Phase 7 + Phase 5**: US5 (streaming) can run in parallel with US3 (hybrid) after respective deps
- **Phase 8**: T036-T040 (all test files) can run in parallel

---

## Parallel Example: Phase 2 (Foundational)

```bash
# After T007 (config.py), launch these in parallel:
Task: "Implement structlog config in src/core/logging.py"          # T008
Task: "Implement Pydantic schemas in src/api/schemas.py"           # T009
Task: "Implement GraphState + AgentRoute in src/state/graph_state.py" # T010
Task: "Implement prompt templates in src/rag/prompts.py"           # T011
Task: "Create healthcheck script in scripts/healthcheck.py"        # T014
```

## Parallel Example: Phase 8 (Tests)

```bash
# All test files can be written in parallel:
Task: "Create test fixtures in tests/conftest.py"                  # T036
Task: "Write chat endpoint tests in tests/test_chat_endpoint.py"   # T037
Task: "Write FAQ agent tests in tests/test_faq_agent.py"           # T038
Task: "Write orchestrator tests in tests/test_orchestrator.py"     # T039
Task: "Write Search agent tests in tests/test_search_agent.py"     # T040
```

---

## Implementation Strategy

### MVP First (US1 Only — Phases 1-3)

1. Complete Phase 1: Setup (project structure, deps, Docker)
2. Complete Phase 2: Foundational (config, schemas, logging, health)
3. Complete Phase 3: User Story 1 — FAQ Agent
4. **STOP and VALIDATE**: Test FAQ Agent via POST /chat
5. Deploy/demo: `docker compose up` → POST /chat com pergunta de bagagem

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (FAQ) → Test → **MVP entregue** (sistema responde perguntas de política)
3. Add US2 (Search) → Test → Sistema busca informações na web
4. Add US3 (Hybrid) → Test → Rota BOTH funcional
5. Add US4 (Session) → Test → Conversas multi-turn persistidas
6. Add US5 (Streaming) → Test → SSE diferencial
7. Polish → Testes + README + Security → **Entrega final**

### Commit Strategy

Commits incrementais por fase (Constitution II):
- `chore: setup project structure and dependencies`
- `feat: add config, schemas, logging and health endpoint`
- `feat: implement FAQ agent with RAG pipeline`
- `feat: implement search agent with Tavily`
- `feat: implement hybrid route (BOTH) with synthesizer`
- `feat: add Redis session persistence with fallback`
- `feat: add SSE streaming endpoint`
- `test: add basic test suite`
- `docs: add README with architecture and AI usage`

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable after its deps
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Skills DEVEM ser carregadas antes de cada fase (Constitution VII)
- Security review obrigatória em cada fase que envolve código (Constitution VIII)
