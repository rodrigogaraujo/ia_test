# Blis Travel Agents — Instruções do Projeto

## Sobre
- **Projeto**: `blis-travel-agents`
- **Caminho**: `~/Documents/ia_test`
- **Objetivo**: Teste técnico para vaga AI Engineer na Blis AI
- **Idioma de comunicação**: Português (BR)
- **Idioma de código**: Inglês (variáveis, funções, classes) / Português (docstrings, comentários quando necessário)

## Regras Gerais
- Sempre ler este arquivo antes de avançar em qualquer tarefa
- Confirmar com o usuário antes de tomar decisões arquiteturais
- Commits incrementais e descritivos (nunca dump final)
- Commitar apenas quando solicitado
- Todo desenvolvimento deve ser documentado para a seção "Como usei IA no desenvolvimento"

## Skills-Driven Development (OBRIGATÓRIO)

**Antes de executar qualquer tarefa, DEVE carregar a(s) skill(s) relevante(s) de `~/.claude/skills/`.**
Skills são a base de conhecimento especializado deste projeto. Cada prompt deve ser enriquecido
pelo contexto da skill antes de gerar código ou tomar decisões.

### Skill Principal do Projeto (SEMPRE CARREGAR)

**`blis-travel-agents`** — skill customizada que consolida toda a arquitetura, contratos Pydantic,
prompts, stack, endpoints e regras do projeto. DEVE ser carregada em TODA tarefa como base.

```
@blis-travel-agents  ← carregar SEMPRE, em toda tarefa
```

Depois de carregar a skill principal, carregar também a(s) skill(s) específica(s) da tarefa abaixo.

### Mapeamento de Skills por Fase/Tarefa

| Contexto / Tarefa | Skill(s) a carregar | Comando |
|---|---|---|
| **Arquitetura geral** | `architecture`, `senior-architect` | `/skill:arch` |
| **Python / FastAPI / código** | `python-patterns`, `backend-dev-guidelines` | `/skill:python`, `/skill:backend` |
| **LangGraph / Orquestração** | `langgraph` | `@langgraph` |
| **RAG Pipeline** | `rag-implementation`, `rag-engineer` | `@rag-implementation` |
| **Agentes autônomos** | `ai-agents-architect`, `autonomous-agent-patterns` | `@ai-agents-architect` |
| **LLM App patterns** | `llm-app-patterns` | `@llm-app-patterns` |
| **API design** | `api-patterns`, `api-security-best-practices` | `/skill:api` |
| **Docker** | `docker-expert` | `/skill:docker` |
| **Database / Redis** | `database-design` | `/skill:db` |
| **Testes** | `testing-patterns`, `test-driven-development` | `@testing-patterns` |
| **Logging / Observability** | `performance-profiling` | `@performance-profiling` |
| **Clean code / Standards** | `clean-code`, `cc-skill-coding-standards` | `@clean-code` |
| **Git / Commits** | `git-pushing` | `/skill:git` |
| **README / Docs** | `documentation-templates` | `@documentation-templates` |
| **Debug** | `systematic-debugging` | `/skill:debug` |
| **Code review** | `code-review-checklist`, `requesting-code-review` | `@code-review-checklist` |
| **MCP servers** | `mcp-builder` | `@mcp-builder` |
| **Prompt engineering** | `prompt-engineering` | `@prompt-engineering` |
| **Criar nova skill** | `skill-developer`, `skill-creator` | `@skill-developer` |

### Skills de Segurança (OBRIGATÓRIO em todo código)

**Segurança NÃO é opcional.** Toda tarefa que envolva código DEVE passar por review de segurança.
As skills abaixo DEVEM ser consultadas nos contextos indicados:

| Contexto | Skill(s) de segurança | Comando |
|---|---|---|
| **Endpoints / API (sempre)** | `api-security-best-practices`, `cc-skill-security-review` | `@api-security-best-practices` |
| **Input do usuário / chat** | `top-web-vulnerabilities` | `@top-web-vulnerabilities` |
| **Injeção (SQL, prompt, etc.)** | `sql-injection-testing`, `xss-html-injection` | `@sql-injection-testing` |
| **Autenticação / sessões** | `broken-authentication` | `@broken-authentication` |
| **Variáveis de ambiente / secrets** | `cc-skill-security-review` | `/skill:security` |
| **Docker / infra** | `docker-expert` + `server-management` | `/skill:docker` |
| **Auditoria geral de código** | `production-code-audit`, `code-review-checklist` | `@production-code-audit` |
| **Review final antes de entregar** | `vulnerability-scanner` | `@vulnerability-scanner` |

### Checklist de Segurança por Fase

- **Fase 0 (Setup)**: `.env.example` sem secrets reais, `.gitignore` protegendo `.env`
- **Fase 1 (Config)**: secrets via `SecretStr`, nunca logar API keys, Redis com senha em prod
- **Fase 2 (RAG)**: sanitizar conteúdo do PDF antes de embedding
- **Fase 3-4 (Agentes)**: prompt injection defense — nunca confiar em user input dentro de prompts sem sanitização
- **Fase 5 (Orchestrator)**: validar que rotas são apenas FAQ/SEARCH/BOTH, sem path traversal
- **Fase 6 (API)**: rate limiting, validação de input (Pydantic), CORS configurado, error messages sem stack traces
- **Fase 7-8 (Final)**: rodar `@production-code-audit` + `@vulnerability-scanner` antes de entregar

### Regras de Uso de Skills

1. **Antes de codar**: identificar qual skill se aplica e carregá-la
2. **Múltiplas skills**: quando a tarefa cruza domínios (ex: criar agente RAG = `langgraph` + `rag-implementation` + `python-patterns`)
3. **Skill não existe?**: usar `@skill-developer` para criar uma nova skill específica
4. **Decisões arquiteturais**: sempre carregar `architecture` ou `senior-architect` antes
5. **Não pular**: mesmo para tarefas simples, verificar se há skill relevante
6. **Segurança sempre**: toda tarefa com código DEVE incluir pelo menos uma skill de segurança relevante

## Stack / Tecnologias
- **Linguagem**: Python 3.11+ com tipagem forte
- **Framework Web**: FastAPI
- **Orquestração de Agentes**: LangGraph
- **Checkpointer de Sessão**: Redis (`langgraph-checkpoint-redis`) — MemorySaver apenas como fallback local
- **Vector Store**: FAISS (persistido em disco)
- **Embeddings**: OpenAI `text-embedding-3-small`
- **LLM**: OpenAI `gpt-4o-mini`
- **Web Search**: Tavily
- **Containerização**: Docker Compose (Redis + API)
- **Validação de Dados**: Pydantic v2 + `pydantic-settings`
- **Logging**: structlog
- **Linting/Formatting**: ruff + isort
- **Testes**: pytest + pytest-asyncio + httpx

## Arquitetura
```
Cliente (HTTP) → FastAPI → Orchestrator (LangGraph)
                             ├── FAQ Agent (RAG sobre PDF de políticas)
                             └── Search Agent (Tavily web search)
```
- **Orchestrator**: classifica intent (FAQ / SEARCH / BOTH), roteia para agentes, consolida resposta
- **FAQ Agent**: RAG sobre `manual-politicas-viagem-blis.pdf` (bagagem, docs, check-in, etc.)
- **Search Agent**: busca web em tempo real (preços, disponibilidade, notícias)

## Endpoints
- `POST /api/v1/chat` — `{ "session_id": "...", "message": "..." }` → resposta JSON
- `GET /api/v1/chat/stream` — SSE streaming (diferencial)
- `GET /health` — health check (Redis + vector store)

## Estrutura de Diretórios
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
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── routes/chat.py
│   │   ├── schemas.py
│   │   └── dependencies.py
│   ├── agents/
│   │   ├── orchestrator.py
│   │   ├── faq_agent.py
│   │   └── search_agent.py
│   ├── tools/
│   │   ├── web_search.py
│   │   └── rag_retriever.py
│   ├── rag/
│   │   ├── ingest.py
│   │   ├── vectorstore.py
│   │   └── prompts.py
│   ├── state/
│   │   └── graph_state.py
│   └── core/
│       ├── logging.py
│       └── checkpointer.py
├── tests/
│   ├── conftest.py
│   ├── test_chat_endpoint.py
│   ├── test_faq_agent.py
│   ├── test_search_agent.py
│   └── test_orchestrator.py
└── scripts/
    ├── ingest_documents.py
    └── healthcheck.py
```

## Padrões de Código
- **Nomes**: snake_case (funções/variáveis), PascalCase (classes), UPPER_CASE (constantes)
- **Docstrings**: Google style em funções públicas
- **Type hints**: obrigatório em todas as funções
- **Pydantic models**: para TODOS os contratos de dados (requests, responses, estados, configs)
- **Variáveis de ambiente**: via `pydantic-settings`, nunca hardcoded

## Padrões de Commit
```
feat: adiciona FAQ Agent com RAG sobre políticas de viagem
fix: corrige chunking de tabelas no PDF de bagagem
refactor: extrai lógica de roteamento do orchestrator
docs: adiciona seção de MCPs no README
test: adiciona testes do endpoint /chat
chore: configura docker-compose com Redis
```

## Fases de Execução
0. Setup inicial (repo, estrutura, deps, Docker)
1. Config + infra (Settings, logging, checkpointer, FastAPI app, /health)
2. RAG Pipeline (ingestão PDF, chunking, FAISS, retriever)
3. FAQ Agent (RAG + prompts)
4. Search Agent (Tavily + prompts)
5. Orchestrator + LangGraph (grafo completo com roteamento)
6. Endpoint POST /chat
7. Diferenciais (SSE streaming, testes, polish)
8. Documentação + finalização (README completo)

## Prioridade (se faltar tempo)
1. **Obrigatório**: Fases 0–6 (API funcional com RAG + Search + Orchestrator + Redis)
2. **Alto impacto**: Fase 8 (README — é critério de avaliação)
3. **Diferenciais**: Fase 7 (SSE streaming + testes)

## Cuidados Especiais
- O PDF de políticas tem muitas tabelas — usar `pdfplumber` ou cuidar no chunking para preservar dados tabulares
- Redis checkpointer é obrigatório como solução principal (MemorySaver só fallback)
- Histórico de commits será avaliado — manter frequência e clareza
- Seção "Como usei IA" no README é obrigatória e tem peso alto na avaliação

## Decisões Importantes
<!-- Registrar decisões arquiteturais conforme forem tomadas -->

## Notas
- Referência completa do teste: `teste-tecnico-blis-ai.pdf`
- Base RAG: `manual-politicas-viagem-blis.pdf`
- Plano Speckit: `speckit-blis-ai.md`

## Active Technologies
- Python 3.11+ + FastAPI, LangGraph >=0.2, langchain-openai >=0.2, faiss-cpu >=1.8, tavily-python >=0.5, langgraph-checkpoint-redis >=0.3.5, pydantic >=2.0, pydantic-settings >=2.0, structlog >=24.0, sse-starlette >=2.0, pypdf >=4.0, pdfplumber >=0.11 (001-multi-agent-travel)
- Redis 7 (session checkpoints), FAISS (vector store persistido em disco) (001-multi-agent-travel)

## Recent Changes
- 001-multi-agent-travel: Added Python 3.11+ + FastAPI, LangGraph >=0.2, langchain-openai >=0.2, faiss-cpu >=1.8, tavily-python >=0.5, langgraph-checkpoint-redis >=0.3.5, pydantic >=2.0, pydantic-settings >=2.0, structlog >=24.0, sse-starlette >=2.0, pypdf >=4.0, pdfplumber >=0.11
