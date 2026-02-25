# Blis Travel Agents

Sistema multi-agent de IA para agências de viagem, desenvolvido como teste técnico para a posição de AI Engineer na Blis AI.

## Arquitetura

```
Browser → Next.js (web:3457) → FastAPI (api:3456) → Orchestrator (LangGraph)
                                                       ├── classify_intent → route_by_intent
                                                       ├── FAQ Agent (RAG: FAISS + OpenAI)
                                                       ├── Search Agent (Tavily web search)
                                                       └── synthesize_response → END
```

### Fluxo do Grafo

1. **classify_intent** — LLM classifica a query em FAQ / SEARCH / BOTH
2. **route_by_intent** — roteamento condicional para o(s) agente(s) correto(s)
3. **faq_agent** e/ou **search_agent** — executam conforme a rota
4. **synthesize_response** — consolida a resposta final

### Componentes

| Componente | Tecnologia | Função |
|---|---|---|
| Frontend | Next.js 15 + React 19 | Chat UI com SSE streaming |
| Framework Web | FastAPI | API REST + SSE streaming |
| Orquestração | LangGraph | Grafo de agentes com routing condicional |
| LLM | OpenAI gpt-4o-mini | Classificação, respostas, síntese |
| Embeddings | text-embedding-3-small | Vetorização de documentos |
| Vector Store | FAISS | Busca semântica persistida em disco |
| Web Search | Tavily | Busca em tempo real |
| Checkpointer | Redis | Persistência de sessão conversacional |
| Validação | Pydantic v2 | Type safety em todos os contratos |
| Logging | structlog | Logs estruturados em JSON |

## Setup Rápido

### Pré-requisitos

- Docker e Docker Compose
- API key OpenAI
- API key Tavily

### 1. Clone e configure

```bash
git clone <repo-url>
cd blis-travel-agents
cp api/.env.example api/.env
# Edite api/.env com suas API keys
```

### 2. Suba com Docker Compose

```bash
docker compose up --build
```

Serviços e portas:

| Serviço | Porta | URL |
|---|---|---|
| Frontend (Next.js) | 3457 | http://localhost:3457 |
| API (FastAPI) | 3456 | http://localhost:3456 |
| Swagger/OpenAPI | 3456 | http://localhost:3456/docs |
| Redis | 6380 | redis://localhost:6380 |

### 3. Ingestão do PDF

A ingestão é **automática** no primeiro startup — se o vectorstore não existir, a API detecta e ingere o PDF automaticamente.

Para forçar re-ingestão manual:

```bash
docker compose exec api python scripts/ingest_documents.py
```

### 4. Verifique o health

```bash
curl http://localhost:3456/health
```

### 5. Acesse o frontend

Abra http://localhost:3457 no navegador.

## Uso da API

### POST /api/v1/chat — Pergunta com resposta completa

```bash
# FAQ (política de viagem)
curl -X POST http://localhost:3456/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "s1", "message": "Qual o limite de bagagem de mão na LATAM?"}'

# Search (informação atual)
curl -X POST http://localhost:3456/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "s2", "message": "Quanto está a passagem SP-Lisboa em março?"}'

# Hybrid (FAQ + Search)
curl -X POST http://localhost:3456/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "s3", "message": "Quero levar meu cachorro para Portugal, o que preciso?"}'
```

### GET /api/v1/chat/stream — Streaming SSE

```bash
curl -N "http://localhost:3456/api/v1/chat/stream?session_id=s4&message=Como+funciona+o+check-in+online?"
```

### GET /health — Health Check

```bash
curl http://localhost:3456/health
```

## Desenvolvimento Local

### Backend (API)

```bash
cd api

# Instalar dependências
pip install -e ".[dev]"

# Subir Redis
docker run -d --name redis -p 6380:6379 redis:7-alpine

# Ingerir documentos
python scripts/ingest_documents.py

# Rodar API
uvicorn src.main:app --reload --port 3456

# Rodar testes
pytest tests/ -v
```

### Frontend (Web)

```bash
cd web

# Instalar dependências
npm install

# Rodar em modo dev
npm run dev
# Acesse http://localhost:3457
```

## Estrutura do Projeto

```
├── api/                       # Backend Python
│   ├── src/
│   │   ├── main.py            # FastAPI app + lifespan
│   │   ├── config.py          # Settings(BaseSettings)
│   │   ├── api/
│   │   │   ├── routes/chat.py # POST /chat, GET /chat/stream
│   │   │   ├── schemas.py     # Pydantic models
│   │   │   └── dependencies.py
│   │   ├── agents/
│   │   │   ├── orchestrator.py # LangGraph StateGraph
│   │   │   ├── faq_agent.py    # RAG agent
│   │   │   └── search_agent.py # Tavily agent
│   │   ├── tools/
│   │   │   ├── web_search.py   # Tavily wrapper
│   │   │   └── rag_retriever.py
│   │   ├── rag/
│   │   │   ├── ingest.py       # PDF → chunks → FAISS
│   │   │   ├── vectorstore.py  # FAISS persistence
│   │   │   └── prompts.py      # Prompt templates
│   │   ├── state/
│   │   │   └── graph_state.py  # GraphState + AgentRoute
│   │   └── core/
│   │       ├── logging.py      # structlog config
│   │       └── checkpointer.py # Redis + fallback
│   ├── tests/                  # pytest (17 tests)
│   ├── scripts/                # ingest, healthcheck
│   ├── Dockerfile
│   └── pyproject.toml
├── web/                        # Frontend Next.js
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx      # Root layout (dark theme)
│   │   │   └── page.tsx        # Chat UI + SSE streaming
│   │   └── components/
│   │       ├── ChatMessage.tsx  # Message bubble + sources
│   │       └── ChatInput.tsx    # Input com Enter/Shift+Enter
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml          # api + web + redis
└── README.md
```

## Como usei IA no desenvolvimento

Todo o desenvolvimento foi feito com **Claude Code** (Anthropic Claude Opus 4), utilizando uma abordagem skills-driven com MCPs e workflow estruturado.

### Ferramenta principal

**Claude Code** — CLI agent da Anthropic rodando localmente via terminal, com acesso direto ao filesystem, git, terminal e execução de comandos. Modelo: Claude Opus 4.

### MCPs configurados e justificativa

| MCP | Para quê | Como usei |
|---|---|---|
| **Claude Memory MCP** (`claude-mem`) | Persistência de contexto e decisões entre sessões | Indexou 50+ observações (143k tokens de trabalho investido). Permitiu retomar o projeto entre sessões sem perder contexto de decisões arquiteturais, bugs resolvidos e patterns escolhidos. Usado via `mcp-search`, `timeline` e `get_observations` |
| **Speckit** (skill-based workflow) | Gestão estruturada do ciclo de desenvolvimento | Pipeline completo: constitution → specify → clarify → plan → tasks → implement. Cada etapa gera artefatos que alimentam a próxima |
| **Web Search** | Pesquisa de documentação atualizada | Pesquisa de best practices para LangGraph, langgraph-checkpoint-redis, FAISS patterns e FastAPI async patterns |

### Ferramentas nativas do Claude Code utilizadas

| Tool | Uso no projeto |
|---|---|
| **Filesystem** (Read/Write/Edit/Glob) | Navegação, leitura e edição de todos os arquivos do projeto |
| **Grep** | Busca de patterns no codebase (imports, referências, TODO markers) |
| **Bash/Terminal** | Execução de comandos: pip install, pytest, docker compose, uvicorn, npm |
| **Git** (via Bash) | Commits incrementais, diffs, gerenciamento de branches |
| **GitHub CLI** (`gh`) | Push de branches, criação de PR detalhado com descrição completa, configuração do repositório remoto |
| **Task** (subagents) | 3 agentes de pesquisa paralelos na fase de planning (Redis, FAISS, LangGraph) |

### Processo de desenvolvimento

1. **Constitution** (`/speckit.constitution`): Definição dos princípios do projeto — AI-First, Clean Architecture, Type Safety, Production-Ready
2. **Especificação** (`/speckit.specify`): Geração da spec com 5 user stories, 14 requisitos funcionais e 7 critérios de sucesso
3. **Clarificação** (`/speckit.clarify`): Scan de ambiguidade automatizado — nenhuma ambiguidade crítica encontrada
4. **Planejamento** (`/speckit.plan`): 3 agentes de pesquisa em paralelo investigaram Redis checkpointer, FAISS RAG e LangGraph patterns. Gerou research.md, data-model.md, contracts/api.md e quickstart.md
5. **Tarefas** (`/speckit.tasks`): 44 tarefas organizadas por user story em 8 fases com dependências mapeadas
6. **Implementação** (`/speckit.implement`): Execução fase a fase com skills especializadas carregadas por contexto

### Skills carregadas por fase

| Fase | Skills |
|---|---|
| Setup | `docker-expert`, `python-patterns` |
| Foundational | `backend-dev-guidelines`, `api-patterns` |
| FAQ Agent | `rag-implementation`, `rag-engineer`, `langgraph` |
| Search Agent | `langgraph`, `llm-app-patterns` |
| Orchestrator | `ai-agents-architect`, `architecture` |
| Frontend | `nextjs-best-practices`, `frontend-design` |
| Polish | `testing-patterns`, `documentation-templates` |

### Exemplos reais de como a IA ajudou

**Geração de código:**
- Pipeline RAG completo (ingest.py) com detecção de tabelas via pdfplumber e conversão para markdown — gerado de primeira, funcionou sem edição manual
- LangGraph StateGraph com routing condicional (3 rotas: FAQ, SEARCH, BOTH) — arquitetura do grafo definida na fase de planning e implementada diretamente
- Frontend Next.js com SSE streaming usando EventSource API — incluindo handling de 3 tipos de evento (token, done, error)

**Debug assistido:**
- `pyproject.toml`: hatchling não encontrava os pacotes para build → IA diagnosticou e adicionou `[tool.hatch.build.targets.wheel] packages = ["src"]`
- `conftest.py`: Settings validava env vars no import antes dos mocks serem aplicados → IA reestruturou para `os.environ.setdefault()` antes dos imports + lazy app creation
- `test_search_agent.py`: mock no path errado (`src.agents.search_agent.search_web` vs `src.tools.web_search.search_web`) → IA identificou que a função era importada localmente dentro do agente

**Refactoring:**
- Reestruturação monorepo (flat → api/ + web/) com atualização de todos os Dockerfiles, docker-compose, paths e scripts
- Auto-ingestão do PDF no lifespan — adicionado automaticamente quando detectou que o vectorstore não existia no startup

**Pesquisa (via subagents paralelos):**
- 3 agentes pesquisaram simultaneamente: AsyncRedisSaver patterns, FAISS com LangChain patterns, e LangGraph StateGraph best practices
- Resultados consolidados em research.md com Decision/Rationale/Alternatives para cada tópico

**Git & GitHub (via `gh` CLI):**
- 14 commits incrementais criados automaticamente pela IA, organizados na ordem lógica do desenvolvimento (setup → specs → config → RAG → tools → agents → API → tests → Docker → frontend → docs)
- Push da branch `001-multi-agent-travel` e criação do PR #1 com descrição detalhada (arquitetura, endpoints, stack, test plan) — tudo via `gh pr create`
- Configuração da default branch via `gh repo edit`

### O que funcionou bem

- **Pesquisa paralela**: 3 agentes rodando em paralelo aceleraram significativamente a fase de planning
- **Skills especializadas**: Cada fase carregou skills relevantes (ex: `rag-engineer` para o FAQ Agent, `langgraph` para o orchestrator)
- **Memory MCP**: Permitiu continuidade entre sessões — decisões e bugs resolvidos ficaram indexados e acessíveis
- **Geração incremental**: Código emergiu naturalmente das decisões de pesquisa, respeitando o plano
- **Constitution**: Manteve consistência arquitetural ao longo de todo o desenvolvimento

### O que precisou ajuste manual

- **Import paths do LangChain**: Mudanças frequentes entre versões (langchain-community vs langchain-core) exigiram correção manual
- **Redis checkpointer**: `AsyncRedisSaver` requer Redis 8+ ou Redis Stack para funcionalidade completa — precisou pesquisa específica
- **Tabelas no PDF**: pdfplumber precisou de ajuste fino no chunking (1500 chars) para preservar integridade das tabelas do manual de políticas
- **Mock paths nos testes**: O pattern de import local dentro das funções dos agentes quebrou os mocks padrão — necessitou investigação do path correto

## Decisões Técnicas

| Decisão | Escolha | Motivo |
|---|---|---|
| Checkpointer | `AsyncRedisSaver` | Recomendado para FastAPI async, `thread_id` = `session_id` |
| PDF extraction | `pdfplumber` | Preserva tabelas do manual (vs PyPDFLoader que perde estrutura) |
| Chunking | 1500 chars, 200 overlap | Chunks maiores preservam integridade de tabelas |
| Retriever | MMR (k=5, fetch_k=25) | Diversidade nos resultados evitando redundância |
| BOTH route | Sequencial (FAQ→Search→Synthesize) | Determinístico e mais simples que paralelo para 2 agentes |
| Streaming | `astream_events(v2)` | API recomendada do LangGraph para SSE |
| Portas | API:3456, Web:3457, Redis:6380 | Portas não-convencionais para evitar conflitos |
| Frontend | Next.js 15 standalone | Output standalone otimizado para Docker |

## Licença

Projeto desenvolvido como teste técnico. Uso interno.
