# Manual Consolidado · Treinamento AI Experts Banco BV II (Ecossistema Moderno de Agentes)

> **Metadados RAG Unificados**
> - **Título:** Manual Arquitetural Consolidado — Engenharia de Agentes Corporativos de IA
> - **Programa:** Treinamento AI Experts Banco BV II · Módulos 3 e 4
> - **Instrutor:** Prof. Ioannis Eleftheriou
> - **Público:** Engenheiros de IA, Arquitetos de Software, Desenvolvedores e Especialistas do Banco BV
> - **Finalidade:** Referência Integral para RAG (*Retrieval-Augmented Generation*) em Projetos de Conclusão de Curso
> - **Stack Principal:** MCP (FastMCP), Google ADK 2.10, LangGraph, CrewAI 1.15, LangSmith, Presidio PT-BR, ChromaDB, Ollama (Qwen 2.5, nomic-embed-text), OpenAI, Google Gemini

---

## 1. Visão Geral do Programa e o Caso Integrador BV Assist

O treinamento **AI Experts Banco BV II** aborda a transição de protótipos de chat com inteligência artificial generativa para **sistemas agênticos corporativos em produção**, operando em ambientes altamente regulados como o setor financeiro.

### 1.1 A Dor do Conhecimento Inacessível
Em grandes instituições financeiras, o conhecimento existe em abundância, mas permanece isolado em portais internos, manuais em PDF e filas desordenadas de Service Desk. Isso gera retrabalho constante de áreas especialistas (RH, Jurídico, TI) e fricção no onboarding de novos colaboradores.

### 1.2 Os 7 Critérios Arquiteturais de Decisão
1. **Aderência ao Problema:** Capacidade de consultar bases documentais com groundedness E executar ações no mundo real (abertura de tickets).
2. **Governança:** Produção contínua de trilha de auditoria para reguladores (BACEN / CVM).
3. **Segurança:** Defesa em camadas com ofuscação de PII (LGPD) e mitigação contra injeção de prompt.
4. **Extensibilidade:** Adoção de protocolo aberto (MCP) que desacopla fontes de dados e ferramentas dos modelos.
5. **Custo Controlado (FinOps):** Equilíbrio de TCO entre modelos locais leves e modelos avançados em nuvem.
6. **Debugabilidade:** Capacidade de inspecionar spans, tempos de resposta e falhas ponta a ponta.
7. **Portabilidade:** Independência de fornecedor (*anti vendor lock-in*).

---

## 2. Model Context Protocol (MCP)

O **Model Context Protocol (MCP)** é o padrão aberto para integração entre modelos de linguagem e ferramentas corporativas.

### 2.1 Primitivas do MCP
- **Tools (Ferramentas):** Ações executáveis com parâmetros validados por JSON Schema (ex: `abrir_chamado_servicedesk`).
- **Resources (Recursos):** Conteúdo somente-leitura identificado por URIs estruturadas (ex: `bv://politicas/ia-generativa`).
- **Prompts:** Modelos parametrizados para padronizar comportamentos recorrentes.

### 2.2 Camada de Transporte
- **`stdio`:** Comunicação via entrada e saída padrão, ideal para CLI e subprocessos locais na mesma máquina.
- **`HTTP + SSE`:** Comunicação em rede via Server-Sent Events, ideal para microserviços e contêineres corporativos.

### 2.3 Implementação com FastMCP (Python)
Utiliza-se o FastMCP para criar servidores leves na porta `8875` (servidor bancário) e `8876` (servidor RAG), integrados à **MCP Store** na porta `8883` e inspecionados com o **MCP Inspector** (`@modelcontextprotocol/inspector@2.7.0`).

---

## 3. RAG Corporativo, Indexação Semântica e Groundedness

Em bancos, o RAG deve eliminar alucinações através de **groundedness estrito, citações de página e preservação de lacunas**.

### 3.1 Corpus e Indexação
- **Documento Didático:** Regulamento do Fundo KNCR (maio/2025, 40 páginas, SHA-256: `e1efcfa1c73f5f65526fba2254f843f31f7e2e398e6a14c4e08b57d962372b8e`).
- **Embeddings:** `nomic-embed-text` (local via Ollama) ou `text-embedding-3-small` (OpenAI).
- **Vector Store:** ChromaDB local com metadados detalhados de página e seção.
- **Chunking:** 1000 caracteres com overlap de 150 caracteres, preservando artigos regulatórios.

### 3.2 O Conceito de Preservação de Lacunas (*Gap Preservation*)
O modelo é instruído a responder com base estrita nos dados recuperados. Se o regulamento remeter a terceiros ou omitir valores, o agente declara explicitamente a ausência, impedindo alucinações financeiras.

---

## 4. Google Agent Development Kit (ADK 2.10)

Framework corporativo do Google para construir agentes com gerenciamento de sessões, runtimes e ferramentas.

### 4.1 Três Modos Arquiteturais
- **`bv_regras`:** Determinístico puro (Python + Regex). 0 tokens, < 10ms de latência.
- **`bv_workflow`:** Híbrido controlado. Orquestração fixa em código com LLM na redação final.
- **`bv_agente`:** Autonomia completa de tool calling pelo modelo.

### 4.2 ADK Web UI
Servidor local na porta `8895` para testar fluxos, alternar provedores (Gemini vs Ollama) e inspecionar variáveis de sessão.

---

## 5. Segurança, Threat Modelling e Guardrails

Agentes exigem proteção contra **OWASP Top 10 para LLM** (Prompt Injection direto/indireto, Exposição de PII e Agência Excessiva).

### 5.1 Defesa em Profundidade
1. **Sanitização de PII com Presidio:** Modelo spaCy PT-BR (`pt_core_news_sm`) ofusca CPF, e-mail e telefone antes de qualquer nó ou trace.
2. **Classificação com Llama Guard 3:** Bloqueia prompts maliciosos com política *Fail-Closed*.
3. **Auditoria com Safeguards:** Validação pós-geração da resposta.
4. **Princípio do Menor Privilégio:** O LLM nunca tem permissão para aprovar ações destrutivas ou de alta severidade; gera propostas autenticadas com hash SHA-256.

---

## 6. LangGraph, Grafos de Estado e Human-in-the-Loop

Orquestração baseada em máquinas de estados cíclicas dirigidas (`StateGraph`).

### 6.1 Primitivas
- **Estado (`TypedDict`):** Memória compartilhada tipada.
- **Nós e Arestas:** Funções Python e transições condicionais.
- **Checkpointers (`SqliteSaver`):** Persistência de threads e estados em banco relacional.

### 6.2 O Padrão Human-in-the-Loop
Para chamadas críticas de service desk, o grafo pausa na barreira `interrupt_before`. O operador revisa a proposta na interface web, e a aplicação retoma a execução via `update_state` conferindo o hash criptográfico para garantir idempotência.

---

## 7. Padrões de Sistemas Multiagente e Supervisão

Evolução de prompts monolíticos para especialistas com papéis isolados e contratos Pydantic:
1. **Pipeline Sequencial:** Tarefas dependentes em série.
2. **Paralelo (Fan-Out / Fan-In):** Execução simultânea de múltiplos especialistas com consolidação final.
3. **Roteamento Explícito (Router):** Separação determinística de domínios.
4. **Padrão Supervisor:** Agente LLM central que avalia o estado, escolhe o próximo especialista e decide o momento da síntese final com limites de recursão.

---

## 8. CrewAI e o Padrão Juiz Avaliador (LLM-as-a-Judge)

Framework orientado a equipes de agentes com personas e colaboração em linguagem natural.

### 8.1 Caso `bv_boletim`
- **Leitor:** Extração estritamente factual de comunicados de IA.
- **Analista de Riscos:** Identificação de impactos operacionais e lacunas normativas.
- **Redator Executivo:** Consolidação em boletim Markdown padronizado.

### 8.2 O Juiz Avaliador (*LLM-as-a-Judge*)
Um agente independente confronta o artefato gerado contra os documentos originais, atribuindo notas de 0 a 10 para groundedness, precisão de fontes e verificando alucinações com relatório estruturado gravado no LangSmith.

---

## 9. Observabilidade, Métricas e Evals com LangSmith

Monitoramento semântico profundo de IA.

### 9.1 Hierarquia de Tracing
- **Traces:** A jornada completa da requisição do colaborador.
- **Spans:** Cada nó do grafo, chamada de tool ou inferência de LLM.
- **Runs:** Registros detalhados de inputs/outputs brutos, tokens consumidos e latência.

### 9.2 Avaliações Automatizadas (`aevaluate`)
Testes contínuos em datasets fixos (ex: 8 casos de teste do BV Assist) comparando arquiteturas (ex: `top_k=2` vs `top_k=4`), medindo custo de tokens, acurácia factual e latência P95.

---

## 10. Matriz Síntese de Decisões Técnicas do Treinamento

| Componente | Opção Local / Econômica | Opção Nuvem / Avançada | Critério de Escolha no BV |
| :--- | :--- | :--- | :--- |
| **Modelos de Linguagem** | Ollama Qwen 2.5 7B | Gemini 3.8 / GPT-5.4-mini | Dados ultrassensíveis rodam em Ollama; raciocínio complexo roda em Gemini/GPT. |
| **Embeddings** | `nomic-embed-text` (768d) | `text-embedding-3-small` | Nomic para privacidade local total; OpenAI para maior separabilidade vetorial. |
| **Protocolo de Ferramentas** | FastMCP stdio (Processos) | FastMCP HTTP/SSE (Rede) | stdio para CLIs locais; HTTP para microserviços corporativos. |
| **Orquestrador de Fluxos** | LangGraph (StateGraph) | Google ADK 2.10 | LangGraph para controle de estado e human-in-the-loop; ADK para copiloto institucional. |
| **Guardrails & PII** | Presidio PT-BR + Llama Guard 3 | Model Armor (Google Cloud) | Presidio local garante conformidade estrita LGPD antes de sair da rede. |
| **Observabilidade** | Relatórios locais JSON | LangSmith Cloud Tracing | LangSmith para auditoria centralizada de custos, tokens e qualidade. |
