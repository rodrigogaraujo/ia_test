# Feature Specification: Multi-Agent Travel Assistant

**Feature Branch**: `001-multi-agent-travel`
**Created**: 2025-02-25
**Status**: Draft
**Input**: Sistema multi-agent de IA para agências de viagem com FAQ Agent (RAG), Search Agent (Web Search) e Orchestrator, expostos via API REST

## User Scenarios & Testing *(mandatory)*

### User Story 1 - FAQ sobre Políticas de Viagem (Priority: P1)

Um atendente de agência de viagens envia uma pergunta sobre políticas internas (bagagem, documentação, check-in, remarcação, reembolsos) e recebe uma resposta precisa baseada no manual de políticas da Blis AI, com citação da seção relevante.

**Why this priority**: Este é o caso de uso principal — a maior parte das perguntas diárias de uma agência envolve políticas já documentadas. Sem o FAQ Agent funcionando, o sistema não entrega valor.

**Independent Test**: Pode ser testado enviando perguntas sobre bagagem, documentação ou check-in via POST /chat e verificando que a resposta contém informações do manual com citação de seção.

**Acceptance Scenarios**:

1. **Given** o sistema está rodando com o vector store populado, **When** o atendente pergunta "Qual o limite de bagagem de mão na LATAM?", **Then** o sistema responde com "10 kg, dimensão máxima 115 cm" citando a Seção 1.1 do manual, `agent_used` é "faq" e `sources` contém referência ao documento.

2. **Given** o sistema está rodando, **When** o atendente pergunta "Preciso de visto para ir ao Chile?", **Then** o sistema responde que brasileiros não precisam de visto e podem usar RG ou Passaporte, citando a Seção 2.2.

3. **Given** o sistema está rodando, **When** o atendente pergunta algo que NÃO está no manual (ex: "Qual o PIB do Brasil?"), **Then** o sistema informa que não possui essa informação na base de conhecimento disponível.

---

### User Story 2 - Busca de Informações em Tempo Real (Priority: P2)

Um atendente envia uma pergunta sobre informações atuais (preços de passagens, promoções, notícias de companhias aéreas) e recebe uma resposta baseada em busca web em tempo real, com menção das fontes consultadas.

**Why this priority**: Complementa o FAQ Agent com dados que o manual não cobre — preços e disponibilidade mudam constantemente. Sem isso, o sistema só responde perguntas estáticas.

**Independent Test**: Pode ser testado enviando perguntas sobre preços ou promoções atuais e verificando que a resposta contém dados da web com fontes citadas.

**Acceptance Scenarios**:

1. **Given** o sistema está rodando com acesso à busca web, **When** o atendente pergunta "Quanto está a passagem São Paulo-Lisboa em março?", **Then** o sistema retorna informações de preço com fonte e data, `agent_used` é "search" e `sources` contém URLs.

2. **Given** o sistema está rodando, **When** o atendente pergunta "A GOL está com alguma promoção?", **Then** o sistema busca na web e retorna promoções encontradas com links de referência.

3. **Given** a busca web não retorna resultados relevantes, **When** o atendente faz uma pergunta muito específica, **Then** o sistema informa que os resultados encontrados não foram suficientes para uma resposta completa.

---

### User Story 3 - Perguntas Híbridas (Política + Informação Atual) (Priority: P3)

Um atendente envia uma pergunta que combina política da agência com informação atual, e o sistema consulta ambos os agentes (FAQ + Search), consolidando as respostas em uma resposta única e coerente.

**Why this priority**: Cenário mais complexo que depende dos dois agentes anteriores funcionando. Representa o diferencial de inteligência do orchestrator.

**Independent Test**: Pode ser testado com perguntas que cruzam política e dados atuais, verificando que ambos os agentes são acionados e a resposta é consolidada.

**Acceptance Scenarios**:

1. **Given** o sistema está rodando com FAQ e Search funcionais, **When** o atendente pergunta "Quero levar meu cachorro para Portugal, o que preciso?", **Then** o sistema combina políticas de pet do manual (Seção 6.1) com requisitos sanitários atuais de Portugal, `agent_used` é "both" e `sources` contém documentos internos E URLs.

2. **Given** ambos os agentes retornam informação, **When** há contradição entre manual e dado web, **Then** a resposta menciona ambas as fontes e indica qual é mais atualizada.

---

### User Story 4 - Persistência de Sessão (Priority: P4)

Um atendente mantém uma conversa contínua usando o mesmo `session_id`, e o sistema lembra do contexto anterior para dar respostas mais relevantes.

**Why this priority**: Melhora a experiência conversacional, mas o sistema já funciona sem isso (cada pergunta isolada). Depende do Redis checkpointer.

**Independent Test**: Enviar múltiplas mensagens com o mesmo `session_id` e verificar que o contexto é mantido entre requisições.

**Acceptance Scenarios**:

1. **Given** o atendente já perguntou "Qual o limite de bagagem da LATAM?", **When** ele pergunta "E na GOL?" com o mesmo `session_id`, **Then** o sistema entende que se refere a bagagem e responde sobre a GOL sem precisar repetir o contexto.

2. **Given** o atendente usa um `session_id` novo, **When** envia uma mensagem, **Then** o sistema inicia uma nova conversa sem histórico prévio.

---

### User Story 5 - Streaming de Resposta (Priority: P5)

O atendente recebe a resposta do sistema em tempo real, token por token via SSE, proporcionando feedback imediato em vez de esperar a resposta completa.

**Why this priority**: Diferencial avaliado. Melhora UX significativamente em respostas longas, mas o sistema funciona sem isso.

**Independent Test**: Conectar via SSE ao endpoint de stream e verificar que tokens chegam incrementalmente com evento final contendo metadata.

**Acceptance Scenarios**:

1. **Given** o sistema está rodando, **When** o atendente faz uma requisição ao endpoint de streaming, **Then** tokens são entregues incrementalmente com eventos `token` e um evento `done` final com metadata (agent_used, sources).

---

### Edge Cases

- O que acontece quando o Redis está indisponível? O sistema DEVE usar fallback para MemorySaver e continuar operando em modo degradado, reportado via /health.
- O que acontece quando a pergunta do usuário está vazia ou contém apenas espaços? O sistema DEVE rejeitar com erro de validação (422).
- O que acontece quando o `session_id` excede 128 caracteres? O sistema DEVE rejeitar com erro de validação.
- O que acontece quando a mensagem excede 4096 caracteres? O sistema DEVE rejeitar com erro de validação.
- O que acontece quando a API key da OpenAI é inválida? O sistema DEVE retornar erro 503 com mensagem genérica (sem expor detalhes do erro interno).
- O que acontece quando a Tavily API está indisponível? O Search Agent DEVE retornar que não conseguiu buscar informações no momento, sem derrubar o sistema.
- O que acontece quando o vector store não está populado? O FAQ Agent DEVE informar que a base de conhecimento não está disponível, e /health DEVE reportar status "degraded".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE expor um endpoint REST que recebe pergunta em texto e retorna resposta em texto com metadados (agente usado, fontes, timestamp)
- **FR-002**: Sistema DEVE classificar automaticamente a intenção da pergunta em FAQ, SEARCH ou BOTH
- **FR-003**: FAQ Agent DEVE responder perguntas usando exclusivamente informações da base documental (manual de políticas de viagem), citando seções relevantes
- **FR-004**: Search Agent DEVE buscar informações em tempo real na web e sintetizar resultados com citação de fontes
- **FR-005**: Orchestrator DEVE rotear a pergunta para o(s) agente(s) correto(s) baseado na classificação de intenção
- **FR-006**: Sistema DEVE consolidar respostas de múltiplos agentes em uma resposta única e coerente quando ambos são acionados (rota BOTH)
- **FR-007**: Sistema DEVE manter contexto conversacional entre mensagens do mesmo `session_id`
- **FR-008**: Sistema DEVE persistir estado de sessão em serviço externo de armazenamento, com fallback local quando o serviço está indisponível
- **FR-009**: Sistema DEVE validar todos os dados de entrada (tamanho, formato, campos obrigatórios) e rejeitar entradas inválidas com mensagens de erro claras
- **FR-010**: Sistema DEVE expor endpoint de health check que verifica o status de todas as dependências
- **FR-011**: Sistema DEVE gerar logs estruturados para todas as operações (classificação, roteamento, retrieval, busca, síntese)
- **FR-012**: Sistema DEVE funcionar dentro de containers, com todas as dependências subindo via um único comando
- **FR-013**: Sistema DEVE proteger secrets (API keys) usando variáveis de ambiente tipadas, nunca expostas em logs ou respostas de erro
- **FR-014**: Todas as respostas DEVEM ser em português brasileiro

### Key Entities

- **ChatMessage**: Uma mensagem enviada pelo atendente contendo identificador de sessão e texto da pergunta
- **ChatResponse**: Resposta do sistema contendo texto, identificação do agente utilizado, lista de fontes consultadas e timestamp
- **Source**: Referência a uma fonte de informação (documento interno ou URL web), com tipo, título e prévia do conteúdo
- **Session**: Contexto conversacional persistido, vinculado a um identificador único, contendo histórico de mensagens
- **AgentRoute**: Classificação da intenção (FAQ, SEARCH ou BOTH) que determina qual(is) agente(s) processam a pergunta
- **HealthStatus**: Estado do sistema com indicadores de saúde de cada dependência

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Atendentes recebem respostas para perguntas sobre políticas de viagem com precisão de pelo menos 90% em relação ao conteúdo do manual
- **SC-002**: O sistema classifica corretamente a intenção (FAQ/SEARCH/BOTH) em pelo menos 85% das perguntas testadas
- **SC-003**: Respostas são entregues em menos de 10 segundos para perguntas simples (FAQ ou SEARCH) e menos de 15 segundos para perguntas híbridas (BOTH)
- **SC-004**: O contexto conversacional é mantido corretamente entre mensagens — perguntas de follow-up recebem respostas contextualizadas
- **SC-005**: O sistema continua operando em modo degradado quando uma dependência está indisponível, sem crashes ou erros não tratados
- **SC-006**: Toda a stack sobe com um único comando a partir de um clone limpo do repositório (após configurar variáveis de ambiente)
- **SC-007**: O README permite que um desenvolvedor configure e rode o projeto em menos de 10 minutos
