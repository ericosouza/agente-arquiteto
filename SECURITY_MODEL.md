# Modelo de ameaças — agente-arquiteto

> Construído a partir do código de `denisgibikoski/agente-arquiteto` e das respostas do Denis. Não há repositório de infraestrutura: a implantação é descrita apenas por `docker-compose.yml` e pelos Dockerfiles.

## 1. Visão geral do sistema

MVP de um "agente arquiteto": o usuário descreve um sistema em linguagem natural, o backend coleta pré-requisitos corporativos (Sigla, Feature, ARQCOR), chama um LLM (Gemini, OpenAI, Anthropic, Ollama) ou o motor de regras offline (`builtin`), gera uma proposta de arquitetura, um modelo ArchiMate 3.2, um diagrama SVG e exportações JSON/XML (Open Group Exchange Format) para o Archi.

**Implantação (fato do usuário):** rede interna corporativa, usada por arquitetos da empresa. Não exposto na internet. O backend roda com `uvicorn app.main:app` servindo o `frontend/dist` (rota catch-all em `backend/app/main.py`), acessível por outras máquinas da rede interna, e não pelo docker-compose. Portanto a porta 8000 é alcançável por qualquer pessoa da rede interna.

## 2. Componentes

| Componente | Código | Notas |
|---|---|---|
| **Frontend** | `frontend/src/**`, `frontend/nginx.conf`, `frontend/Dockerfile` | React 19 + Vite; Nginx faz proxy de `/api/` para o backend. Renderiza o SVG do diagrama com `dangerouslySetInnerHTML` (`AreaC_DiagramViewer.tsx`). |
| **API** | `backend/app/main.py`, `backend/app/api/routes.py`, `backend/app/models/**` | FastAPI, rotas `/api/*` sem autenticação; CORS com `*` e `allow_credentials=True`; serve `frontend/dist` via rota catch-all `/{full_path:path}`. |
| **Agente LLM** | `backend/app/services/llm_provider.py`, `architect_agent.py`, `brainstorm_agent.py`, `scope_guardrail.py`, `architecture_rag.py`, `backend/app/knowledge/**` | Monta prompts com texto do usuário + base de conhecimento (RAG em markdown local); faz parsing do JSON devolvido pelo LLM. Guardrail de escopo heurístico/LLM. |
| **Geração e exportação de modelos** | `backend/app/services/diagram_generator.py`, `exporter.py`, `archimate_validator.py` | Gera SVG por f-strings com nomes vindos da proposta; gera XML ArchiMate e JSON para download. |
| **Configuração e segredos** | `backend/app/config.py`, `.env*`, `backend/Dockerfile`, `docker-compose.yml` | Carrega `.env` de até 6 diretórios ancestrais para `os.environ`; chaves de API de LLM; chave Gemini também enviada na query string (`?key=`). |
| **Observabilidade/FinOps** | `backend/app/services/cost_tracker.py`, `backend/app/models/observability.py`, serviço `observability` (Arize Phoenix, porta 6006) | Métricas e spans em memória, globais (compartilhados entre todos os usuários); endpoints `/api/observability/finops/*` incluindo `reset` sem autenticação. |

## 3. Fronteiras de confiança

1. Navegador do arquiteto → Nginx/Frontend → API (`/api/*`), dentro da rede corporativa.
2. API → provedores de LLM externos (Gemini/OpenAI/Anthropic) pela internet, levando o conteúdo das propostas e as chaves de API.
3. Resposta do LLM → API → navegador (texto, JSON da proposta, nomes que viram SVG/XML).
4. Base de conhecimento (`backend/app/knowledge/*.md`) → prompts.
5. Containers no host: backend (8000), frontend (5173→80), Phoenix (6006), portas publicadas no host.

## 4. Pontos de entrada

- `POST /api/architecture/{scope-check,brainstorm,analyze,refine,approve,validate,export/json,export/xml}` — qualquer pessoa que alcance a porta.
- `GET /api/info`, `GET /api/observability/finops/{summary,traces}`, `POST /api/observability/finops/reset`.
- `GET /{full_path:path}` (arquivos estáticos do build, quando existe `frontend/dist`).
- Dashboard/coletor Phoenix na porta 6006.

## 5. Ativos e sensibilidade (fato do usuário: os três abaixo são críticos)

- **Chaves de API dos LLMs** (`.env`, `os.environ`, URL do Gemini) — crítico.
- **Conteúdo das propostas de arquitetura** (descrições, histórico, siglas/ARQCOR, spans de FinOps) — informação corporativa confidencial — crítico.
- **Integridade dos modelos ArchiMate exportados** (JSON/XML/SVG consumidos pelo Archi e por outros arquitetos) — crítico.
- Custo/cota de uso dos LLMs — não indicado como crítico pelo usuário.

## 6. Atacantes (fato do usuário: todos importam)

- Qualquer pessoa na rede interna que alcance as portas, sem login.
- Usuário legítimo mal-intencionado (ex.: prompt injection direto para extrair segredos ou corromper modelos).
- Conteúdo malicioso na base de conhecimento/RAG ou na resposta do LLM (prompt injection indireto, saída do LLM tratada como confiável → XSS no SVG, XML malformado).

Não há atacante externo direto na internet (o sistema não é exposto), mas atacantes via conteúdo (LLM/RAG) e via navegador de um usuário interno (ex.: página maliciosa que chama a API) continuam relevantes.

## 7. Controles existentes

- Guardrail de escopo (`scope_guardrail.py`) — heurístico; não é controle de segurança.
- Validação de schema Pydantic nos requests.
- Validador ArchiMate (`archimate_validator.py`) — regras de metamodelo, não de segurança.
- `.env` fora do controle de versão (`.gitignore`); `backend/Dockerfile` copia apenas `.env.example`.

## 8. Fora de escopo / risco aceito (fato do usuário)

- **Falta de autenticação/autorização na API** — aceito para o MVP. Achados cujo único problema é "endpoint sem auth" (incluindo `finops/reset` e leitura de traces) são risco aceito, a menos que encadeiem com outro defeito que exponha um ativo crítico.
- **CORS aberto (`*`)** — aceito.
- **Dashboard Phoenix (porta 6006) sem autenticação** — aceito.

## 9. Perguntas em aberto

- Haverá HTTPS/proxy corporativo na frente do uvicorn?
- Os logs/spans do Phoenix podem conter o texto das propostas? Para onde vão?
- A base de conhecimento (`backend/app/knowledge/`) pode ser editada por quem?
