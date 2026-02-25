<!--
  Sync Impact Report
  ===================
  Version change: 1.0.0 → 1.1.0 (MINOR — new principles added)
  Modified principles:
    - I. AI-First Development → expanded with skills-driven mandate
  Added sections:
    - Principle VII. Skills-Driven Development
    - Principle VIII. Security-First
    - Skills Mapping (new section under Code Standards & Workflow)
    - Security Checklist (new section under Code Standards & Workflow)
  Removed sections: none
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ compatible
    - .specify/templates/spec-template.md ✅ compatible
    - .specify/templates/tasks-template.md ✅ compatible
  Follow-up TODOs: none
-->

# Blis Travel Agents Constitution

## Core Principles

### I. AI-First Development

Todo o desenvolvimento DEVE ser feito com AI coding agent (Claude Code).
Cada decisão, debug e refactor DEVE ser documentado para compor a seção
obrigatória "Como usei IA no desenvolvimento" no README. A maturidade no
uso de ferramentas de IA é critério de avaliação com peso **alto**.

- Usar Claude Code como ferramenta principal de desenvolvimento
- Documentar MCPs configurados e sua justificativa
- Registrar exemplos reais de uso: geração de código, debug, refactor, análise
- Registrar o que funcionou bem vs. o que precisou correção manual
- Todo prompt DEVE ser enriquecido por skills antes de gerar código (ver Princípio VII)

### II. Commits Incrementais

O histórico de commits DEVE contar a história da construção do projeto.
Commits frequentes e descritivos são critério de avaliação com peso **médio**.
Nunca fazer um dump final de código.

- Formato: `tipo: descrição` (feat, fix, refactor, docs, test, chore)
- Cada fase de desenvolvimento DEVE ter pelo menos um commit
- Mensagens em português ou inglês, consistentes ao longo do projeto
- O histórico DEVE demonstrar evolução incremental e lógica

### III. Type Safety

Pydantic models DEVEM ser usados para TODOS os contratos de dados do
sistema. Nenhum dado transita entre camadas sem validação de tipo.

- Requests e responses da API: Pydantic `BaseModel`
- Estado do grafo LangGraph: `TypedDict` com anotações
- Configurações: `pydantic-settings` com `BaseSettings`
- Todas as funções públicas DEVEM ter type hints completos

### IV. Clean Architecture

Separação clara e estrita entre camadas. Cada camada tem responsabilidade
única e bem definida. Dependências fluem de fora para dentro.

- **API** (FastAPI): validação de requests, roteamento, serialização de responses
- **Orquestração** (LangGraph): grafo de agentes, roteamento por intent, síntese
- **Agentes**: FAQ Agent (RAG), Search Agent (web search) — lógica isolada
- **Ferramentas**: wrappers de RAG retriever e web search
- **Infraestrutura**: vector store (FAISS), checkpointer (Redis), logging

### V. Production-Ready Mindset

Mesmo sendo um teste técnico, o código DEVE ser tratado como código de
produção. Qualidade e clareza do código Python são critério de avaliação
com peso **alto**.

- Logging estruturado com `structlog`
- Error handling com mensagens claras e HTTPException apropriadas
- Configuração exclusivamente via variáveis de ambiente (nunca hardcoded)
- Docker Compose funcional subindo toda a stack
- Health check endpoint verificando dependências (Redis, vector store)

### VI. DRY e KISS

Sem over-engineering, sem abstrações prematuras. O código DEVE ser limpo,
legível e fazer apenas o necessário.

- Sem abstrações para uso único
- Sem feature flags ou backward-compatibility desnecessários
- Três linhas duplicadas são melhores que uma abstração prematura
- Código DEVE ser compreensível sem comentários excessivos

### VII. Skills-Driven Development

Toda tarefa DEVE ser precedida pelo carregamento da(s) skill(s) relevante(s)
de `~/.claude/skills/`. Skills são a base de conhecimento especializado que
enriquece cada prompt antes de gerar código ou tomar decisões.

- **NUNCA codar sem antes carregar a skill relevante**
- Quando a tarefa cruza domínios, DEVEM ser carregadas múltiplas skills
  (ex: criar agente RAG = `langgraph` + `rag-implementation` + `python-patterns`)
- Decisões arquiteturais DEVEM sempre carregar `architecture` ou `senior-architect`
- Se não existir skill para o contexto, DEVE ser criada via `skill-developer`
- O mapeamento completo skill-por-fase está em `CLAUDE.md`

Skills primárias deste projeto:

| Domínio | Skills |
|---|---|
| Arquitetura | `architecture`, `senior-architect` |
| Python / FastAPI | `python-patterns`, `backend-dev-guidelines` |
| LangGraph | `langgraph` |
| RAG | `rag-implementation`, `rag-engineer` |
| Agentes IA | `ai-agents-architect`, `autonomous-agent-patterns` |
| LLM patterns | `llm-app-patterns` |
| API | `api-patterns`, `api-security-best-practices` |
| Docker | `docker-expert` |
| Redis | `database-design` |
| Testes | `testing-patterns`, `test-driven-development` |
| Prompts | `prompt-engineering` |
| MCP | `mcp-builder` |
| Clean code | `clean-code`, `cc-skill-coding-standards` |
| Docs | `documentation-templates` |
| Debug | `systematic-debugging` |

### VIII. Security-First

Segurança NÃO é opcional. Toda tarefa que envolva código DEVE passar por
review de segurança usando as skills apropriadas. Vulnerabilidades DEVEM ser
prevenidas proativamente, não corrigidas reativamente.

- Toda interação com endpoints DEVE consultar `api-security-best-practices`
- Todo input de usuário DEVE ser validado (Pydantic) e sanitizado
- Secrets DEVEM usar `SecretStr` e NUNCA ser logados ou hardcoded
- Prompt injection DEVE ser mitigado — user input NUNCA entra raw em prompts de LLM
- Docker containers DEVEM rodar como non-root
- Error messages DEVEM ser genéricas (sem stack traces em produção)
- CORS DEVE ser configurado explicitamente
- Review final DEVE incluir `production-code-audit` + `vulnerability-scanner`

Skills de segurança obrigatórias por contexto:

| Contexto | Skills |
|---|---|
| Endpoints / API | `api-security-best-practices`, `cc-skill-security-review` |
| Input do usuário | `top-web-vulnerabilities` |
| Injeção (SQL, prompt) | `sql-injection-testing`, `xss-html-injection` |
| Sessões | `broken-authentication` |
| Secrets / env vars | `cc-skill-security-review` |
| Docker / infra | `docker-expert`, `server-management` |
| Auditoria de código | `production-code-audit`, `code-review-checklist` |
| Review final | `vulnerability-scanner` |

Checklist de segurança por fase:

- **Fase 0**: `.env.example` sem secrets reais, `.gitignore` protegendo `.env`
- **Fase 1**: `SecretStr` para API keys, nunca logar secrets, Redis com senha em prod
- **Fase 2**: sanitizar conteúdo do PDF antes de embedding
- **Fase 3-4**: prompt injection defense — user input sanitizado antes de entrar em prompts
- **Fase 5**: validar rotas (apenas FAQ/SEARCH/BOTH), sem path traversal
- **Fase 6**: rate limiting, validação Pydantic, CORS, error messages genéricas
- **Fase 7-8**: `production-code-audit` + `vulnerability-scanner` antes de entregar

## Technical Constraints

Restrições técnicas inegociáveis definidas pelo enunciado do teste:

| Requisito | Tecnologia | Observação |
|---|---|---|
| Linguagem | Python 3.11+ | Tipagem forte obrigatória |
| Framework Web | FastAPI | Endpoint `POST /chat` obrigatório |
| Orquestração | LangGraph | Grafo com Orchestrator + 2 agentes |
| Checkpointer | Redis (`langgraph-checkpoint-redis`) | MemorySaver APENAS como fallback local |
| Vector Store | FAISS | Persistido em disco |
| Embeddings | OpenAI `text-embedding-3-small` | Via `langchain-openai` |
| LLM | OpenAI `gpt-4o-mini` | Temperatura baixa (0.1) |
| Web Search | Tavily | Via `tavily-python` |
| Containerização | Docker Compose | Redis + API subindo juntos |
| Base RAG | `manual-politicas-viagem-blis.pdf` | 13 páginas, muitas tabelas — cuidado no chunking |

### Endpoint Obrigatório

```
POST /chat
Request:  { "session_id": "abc123", "message": "Qual o limite de bagagem?" }
Response: { "session_id": "...", "response": "...", "agent_used": "faq|search|both", "sources": [...], "timestamp": "..." }
```

### Diferenciais Avaliados (peso médio)

- Streaming da resposta via SSE (`GET /chat/stream`)
- Testes (mesmo que básicos)
- Logging estruturado
- Tipagem forte (Pydantic models)

## Code Standards & Workflow

### Padrões de Código

- **Formatação**: `ruff` para linting e formatting
- **Imports**: organizados com `isort`
- **Docstrings**: Google style em funções públicas
- **Variáveis de ambiente**: gerenciadas via `pydantic-settings`
- **Nomes**: `snake_case` (funções/variáveis), `PascalCase` (classes), `UPPER_CASE` (constantes)

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

### Fases de Execução

| Fase | Objetivo | Prioridade | Skills requeridas |
|---|---|---|---|
| 0 | Setup inicial (repo, estrutura, deps, Docker) | Obrigatório | `docker-expert`, `python-patterns` |
| 1 | Config + infra (Settings, logging, checkpointer, /health) | Obrigatório | `backend-dev-guidelines`, `cc-skill-security-review` |
| 2 | RAG Pipeline (ingestão PDF, FAISS, retriever) | Obrigatório | `rag-implementation`, `rag-engineer` |
| 3 | FAQ Agent (RAG + prompts) | Obrigatório | `langgraph`, `prompt-engineering`, `rag-implementation` |
| 4 | Search Agent (Tavily + prompts) | Obrigatório | `langgraph`, `llm-app-patterns` |
| 5 | Orchestrator + LangGraph (grafo completo) | Obrigatório | `langgraph`, `ai-agents-architect`, `architecture` |
| 6 | Endpoint POST /chat | Obrigatório | `api-patterns`, `api-security-best-practices` |
| 7 | Diferenciais (SSE, testes, polish) | Diferencial | `testing-patterns`, `backend-dev-guidelines` |
| 8 | README + documentação final | Alto impacto | `documentation-templates` |

### Ordem de Prioridade (se faltar tempo)

1. Fases 0–6: API funcional (obrigatório)
2. Fase 8: README completo (critério de avaliação)
3. Fase 7: SSE streaming + testes (diferenciais)

## Governance

Esta constitution define as regras inegociáveis do projeto `blis-travel-agents`.
Todas as decisões de código, arquitetura e workflow DEVEM estar em
conformidade com os 8 princípios aqui definidos.

### Regras de Conformidade

- Qualquer desvio dos princípios DEVE ser justificado e documentado
- Alterações na constitution DEVEM ser versionadas (semver) e registradas
- Todo código produzido DEVE ter passado por skills relevantes (Princípio VII)
- Todo código produzido DEVE ter passado por review de segurança (Princípio VIII)
- O arquivo `CLAUDE.md` na raiz do projeto complementa esta constitution
  com instruções operacionais e mapeamento detalhado de skills

### Procedimento de Emenda

1. Propor alteração com justificativa
2. Verificar impacto nos templates (plan, spec, tasks)
3. Incrementar versão (MAJOR: remoção/redefinição de princípio, MINOR: adição, PATCH: clarificação)
4. Atualizar Sync Impact Report no topo do arquivo
5. Atualizar `CLAUDE.md` se houver impacto operacional

### Documentos de Referência

| Documento | Propósito |
|---|---|
| `CLAUDE.md` | Instruções operacionais + mapeamento completo de skills |
| `speckit-blis-ai.md` | Especificação técnica detalhada (arquitetura, modelos, prompts) |
| `teste-tecnico-blis-ai.pdf` | Enunciado oficial do teste |
| `manual-politicas-viagem-blis.pdf` | Base de conhecimento para RAG |

**Version**: 1.1.0 | **Ratified**: 2025-02-25 | **Last Amended**: 2025-02-25
