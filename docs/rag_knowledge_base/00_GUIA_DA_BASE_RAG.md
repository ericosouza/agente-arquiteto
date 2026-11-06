# Guia da Base de Conhecimento RAG · Treinamento AI Experts Banco BV II

## Metadados da Base
- **Programa:** Treinamento AI Experts Banco BV II · Ecossistema Moderno de Agentes
- **Instrutor:** Prof. Ioannis Eleftheriou
- **Público-Alvo:** Engenheiros de IA, Arquitetos de Software, Desenvolvedores e Especialistas em Tecnologia
- **Finalidade:** Base de Conhecimento Estruturada para Ingestão e Consulta via RAG (*Retrieval-Augmented Generation*) em Projetos de Conclusão de Curso
- **Formato:** Markdown Semântico com Cabeçalhos Padronizados, Metadados Explícitos, Snippets de Código, Diagramas e FAQs

---

## 1. Organização dos Documentos na Base

Esta base de conhecimento foi projetada especificamente para alimentar pipelines de RAG (busca vetorial, busca lexical BM25 e busca híbrida). Cada documento é autocontido, preserva seu contexto em nível de chunking e contém blocos de perguntas e respostas (FAQs) que maximizam a similaridade de cosseno com as dúvidas reais dos usuários.

| Arquivo | Tópico Principal | Tecnologias Chave |
| :--- | :--- | :--- |
| `01_VISAO_GERAL_E_ARQUITETURA_BV_ASSIST.md` | Caso Integrador BV Assist, 7 critérios de decisão, FinOps e Governança | BV Assist, FinOps, TCO, LGPD, Service Desk |
| `02_MODEL_CONTEXT_PROTOCOL_MCP.md` | Protocolo MCP, Servidores, Clientes, Ferramentas e Recursos | FastMCP, JSON-RPC, stdio, SSE/HTTP, MCP Store |
| `03_RAG_ARQUITETURA_INDEXACAO_E_BUSCA.md` | RAG Corporativo, Embeddings, ChromaDB e Estratégias de Busca | ChromaDB, Ollama, nomic-embed-text, Qwen 2.5, OpenAI |
| `04_GOOGLE_ADK_AGENT_DEVELOPMENT_KIT.md` | Google Agent Development Kit, Agentes, Runtimes e Workflows | Google ADK 2.10, Gemini, ADK Web UI, Sessions |
| `05_SEGURANCA_THREAT_MODELLING_E_GUARDRAILS.md` | Threat Modelling, OWASP Top 10 LLM, Presidio e Guardrails | Presidio PT-BR, Llama Guard 3, Model Armor, OWASP |
| `06_LANGGRAPH_ORQUESTRACAO_E_HUMAN_IN_THE_LOOP.md` | LangGraph, Grafos de Estado, Checkpoints e Human-in-the-Loop | LangGraph, StateGraph, Memory, Interrupts, SQLite |
| `07_PADROES_MULTIAGENTE_E_SUPERVISAO.md` | Padrões Arquiteturais: Sequencial, Paralelo, Roteamento e Supervisor | Multiagentes, Supervisor Pattern, Fan-out/Fan-in |
| `08_CREWAI_EQUIPES_AGENTICAS_E_JUIZ.md` | Equipes Agênticas com CrewAI, Tarefas e Juiz Avaliador | CrewAI 1.15, Roles, Tasks, LLM-as-a-Judge |
| `09_OBSERVABILIDADE_E_EVALS_LANGSMITH.md` | Observabilidade Corporativa, Traces, Spans e Avaliações | LangSmith, Tracing, aevaluate, Groundedness |
| `10_MANUAL_CONSOLIDADO_RAG_BV_EXPERTS.md` | Documento Consolidado Único (para indexadores mono-arquivo) | Todos os módulos compilados em documento único |

---

## 2. Recomendações para Ingestão e Chunking no Pipeline RAG

Para obter a máxima taxa de recuperação (*hit rate*) e precisão de resposta (*relevance score*):

1. **Chunking Strategy:**
   - **Recomendado:** `MarkdownHeaderTextSplitter` combinando divisões nos níveis `#`, `##` e `###`, seguido por `RecursiveCharacterTextSplitter` (chunk_size: 1000 - 1500 tokens, chunk_overlap: 150 - 200 tokens).
   - **Preservação de Metadados:** Certifique-se de que cada chunk herde os metadados do documento (`modulo`, `tema`, `tecnologias`).

2. **Modelos de Embedding Sugeridos:**
   - **Local:** `nomic-embed-text` ou `bge-m3` (excelente suporte a código e português).
   - **Nuvem:** `text-embedding-3-small` / `text-embedding-3-large` (OpenAI) ou `text-embedding-004` (Google Gemini).

3. **Estratégia de Busca:**
   - **Híbrida:** 70% Densidade Semântica (Embeddings) + 30% Busca Lexical (BM25) para capturar termos técnicos exatos como nomes de métodos (`FastMCP`, `StateGraph`, `aevaluate`).
   - **Reranker:** Cross-Encoder ou FlashRank para reclassificar o top 10 antes de injetar no prompt do LLM.
