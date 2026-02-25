# Research: Multi-Agent Travel Assistant

**Feature**: `001-multi-agent-travel` | **Date**: 2025-02-25

## 1. LangGraph Redis Checkpointer

### Decision
Usar `langgraph-checkpoint-redis` v0.3.5+ com `AsyncRedisSaver` para persistência de sessão.

### Rationale
- `AsyncRedisSaver` é a variante recomendada para aplicações FastAPI assíncronas
- Suporta `from_conn_string(redis_url)` para configuração via URL
- Requer chamada explícita a `.setup()` ou `.asetup()` antes do primeiro uso (inicializa índices Redis Search)
- `thread_id` no `RunnableConfig` mapeia diretamente para `session_id` da API
- TTL configurável para expiração automática de checkpoints
- Requer Redis 8+ ou Redis Stack (RedisJSON + RediSearch)

### Padrão de Fallback
```python
try:
    checkpointer = AsyncRedisSaver.from_conn_string(redis_url)
    await checkpointer.asetup()
except Exception:
    checkpointer = MemorySaver()
    logger.warning("Redis indisponível, usando MemorySaver como fallback")
```

### Lifecycle com FastAPI
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncRedisSaver.from_conn_string(redis_url) as checkpointer:
        await checkpointer.asetup()
        app.state.checkpointer = checkpointer
        yield
```

### Invocação com session_id
```python
config = {"configurable": {"thread_id": session_id}}
result = await graph.ainvoke(state, config=config)
```

### Alternatives Considered
- **MemorySaver**: Apenas para desenvolvimento local, não persiste entre restarts
- **SQLite checkpointer**: Funcionaria mas Redis é requisito do teste
- **Redis puro (sem checkpointer)**: Reinventaria o que `langgraph-checkpoint-redis` já faz

---

## 2. FAISS RAG Pipeline

### Decision
Usar `langchain_community.vectorstores.FAISS` com `pdfplumber` para extração de tabelas e `RecursiveCharacterTextSplitter` para chunking.

### Rationale
- Import path correto: `from langchain_community.vectorstores import FAISS` (deprecated: `langchain.vectorstores`)
- Embeddings: `from langchain_openai import OpenAIEmbeddings` (pacote separado `langchain-openai`)
- Persistência: `save_local(folder_path)` gera `index.faiss` + `index.pkl`
- Reload: `load_local(folder_path, embeddings, allow_dangerous_deserialization=True)` — flag obrigatória para fontes confiáveis
- MMR (Maximum Marginal Relevance) para diversidade de resultados

### Estratégia de Chunking para Tabelas
- **pdfplumber** é preferível ao PyPDFLoader para PDFs com tabelas densas
- Converter tabelas para formato markdown antes de criar chunks
- `RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)` com separadores hierárquicos (`\n\n`, `\n`, `. `, ` `)
- Chunks maiores (1500) preservam integridade de tabelas
- Overlap (200) garante continuidade de contexto entre chunks

### Configuração MMR
```python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 25,
        "lambda_mult": 0.6  # 0=max diversidade, 1=max relevância
    }
)
```

### Metadata Enrichment
- Adicionar `page_number`, `section`, `source` como metadata em cada chunk
- Permite citação precisa de seção do manual na resposta

### Alternatives Considered
- **PyPDFLoader**: Mais simples mas perde estrutura de tabelas
- **Unstructured**: Mais robusto para documentos complexos, mas overhead desnecessário
- **ChromaDB**: Alternativa ao FAISS, mas FAISS é requisito do teste

---

## 3. LangGraph StateGraph Multi-Agent

### Decision
Usar `StateGraph` com `TypedDict` e routing condicional via `add_conditional_edges`. Rota BOTH executa agentes sequencialmente (FAQ → Search → Synthesize).

### Rationale

#### Graph State
```python
class GraphState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    route: str  # "FAQ", "SEARCH", "BOTH"
    faq_response: str | None
    search_response: str | None
    final_response: str
    sources: list[dict]
```
- Campos sem reducer são sobrescritos
- `messages` com `add_messages` faz merge automático

#### Routing Pattern
```python
def route_by_intent(state: GraphState) -> Literal["faq_agent", "search_agent", "both_faq"]:
    route = state["route"]
    if route == "FAQ":
        return "faq_agent"
    elif route == "SEARCH":
        return "search_agent"
    else:
        return "both_faq"  # Inicia pelo FAQ

graph.add_conditional_edges("classify_intent", route_by_intent)
```

#### Rota BOTH (Sequencial)
- `both_faq` → `both_search` → `synthesize_response`
- Sequencial é preferível a paralelo quando a ordem é determinística e os agentes não têm dependências cruzadas
- A síntese precisa de ambos os resultados antes de executar

#### SSE Streaming
```python
async for event in graph.astream_events(state, config=config, version="v2"):
    if event["event"] == "on_chat_model_stream":
        token = event["data"]["chunk"].content
        yield f"data: {json.dumps({'event': 'token', 'data': token})}\n\n"
```
- `astream_events(version="v2")` é a API recomendada
- Filtrar por `event == "on_chat_model_stream"` para tokens do LLM
- Metadata `langgraph_node` identifica qual nó está emitindo

#### Tavily Integration
```python
from langchain_community.tools.tavily_search import TavilySearchResults

tool = TavilySearchResults(max_results=5)
results = await tool.ainvoke({"query": query})
```
- Integração direta como tool call no nó do Search Agent
- Retorna lista de dicts com `url`, `content`, `title`

### Alternatives Considered
- **Send() API (paralelo)**: Mais complexo, desnecessário para 2 agentes sem dependência
- **ReAct Agent**: Over-engineering para um caso simples de tool call
- **CrewAI**: Framework alternativo, mas LangGraph é requisito do teste
