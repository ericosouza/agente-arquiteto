# 🏛️ Agente Arquiteto de Software · AI Architecture Designer (ArchiMate 3.2)

> **Agente Inteligente de Arquitetura de Software aderente às diretrizes corporativas do Banco BV e compatível com o aplicativo desktop [Archi](https://www.archimatetool.com/).**

O sistema recebe demandas de negócio em linguagem natural, valida o escopo, interage via chat consultivo com **Personas Especialistas** (Arquiteto de Software ou Engenheiro de Software), consulta a base de conhecimento **RAG de Arquitetura BV**, projeta a esteira de dados ponta a ponta e gera o modelo oficial **ArchiMate 3.2** exportável em **XML Open Group** e **JSON**.

---

## 🧭 Fluxograma Oficial de Funcionamento

O projeto foi construído para seguir 100% o fluxo definido em [`docs/DesenhoFluxograma_V2.png`](docs/DesenhoFluxograma_V2.png):

```mermaid
flowchart TD
    Inicio(["Usuário solicita desenho/modelagem"]) --> Escopo{"1. Dentro do Escopo?<br/>(LLM Online Guardrail)"}
    
    Escopo -- Não --> Recusa["Recusa Educada & Orientativa"]
    Escopo -- Sim --> ChecaPrereq{"2. Contém Sigla, Feature e ARQCOR?<br/>(Extração com LLM Online)"}
    
    ChecaPrereq -- Não --> PedeInfo["Pergunta campos faltantes (Loop)"]
    PedeInfo -->|Usuário responde| ChecaPrereq
    
    ChecaPrereq -- Sim --> DefinePersona["3. Seleção / Definição da Persona<br/>(Arquiteto de Software OU Engenheiro de Software)"]
    
    DefinePersona --> Refinamento["4. Interação para Refinamento & Brainstorming"]
    Refinamento <--> PersonaPesquisa["Persona atua pesquisando no RAG de Arquitetura BV<br/>+ Conhecimento / Pesquisa da LLM Online<br/>(Evita o padrãozinho, propõe soluções sob medida)"]
    
    Refinamento --> OkRefinamento{"5. Ok?<br/>(Alinhamento do Usuário)"}
    OkRefinamento -- Não --> Refinamento
    
    OkRefinamento -- Sim --> MapeiaPipeline["6. Persona Mapeia Pipeline de Dados<br/>(Canal → BFF → Core → Mensageria/Storage)"]
    
    MapeiaPipeline --> Ferramentas["7. Ativação de Ferramentas Técnicas<br/>(MCP Schema Validator + Skill Modelagem ArchiMate)"]
    
    Ferramentas --> SaidaModelo["8. Saída: Proposta Estruturada + Diagrama Preview"]
    SaidaModelo --> ValidaUsuario["9. Validação do Usuário (Preview)"]
    
    ValidaUsuario --> PreviewOk{"10. Preview ok?"}
    PreviewOk -- Não --> Ajuste["Ajuste com a Persona"]
    Ajuste --> Refinamento
    
    PreviewOk -- Sim --> Fim(["11. Fim: Desenho entregue em XML ArchiMate"])
```

---

## ⚙️ Principais Funcionalidades

- **🛡️ Guardrail de Escopo com LLM Online:** Classifica se o pedido está no domínio de arquitetura de software, recusando educadamente assuntos fora de escopo.
- **📋 Tríade Mandatória de Pré-requisitos:** Exige estritamente **Sigla do Projeto (4 letras)**, **Feature** e **ARQCOR**. Caso algum falte, questiona amigavelmente o usuário em loop conversacional.
- **🎭 Personas Especialistas Selecionáveis:**
  - **Arquiteto de Software:** Visão holística macro, governança, camadas corporativas ArchiMate e conformidade.
  - **Engenheiro de Software:** Detalhamento prático de protocolos, resiliência (Circuit Breakers, retries, DLQ) e contratos.
- **💡 Brainstorming Dinâmico com RAG (Sem "padrãozinho"):** A persona e o LLM Online (Gemini, OpenAI ou Ollama) pesquisam no catálogo técnico oficial e propõem soluções inovadoras sob medida.
- **📊 Esteira de Dados e Nomenclatura Corporativa BV:**
  - Fórmula oficial: `[sigla-tech]-[sigla-sistema]-[modulo]-[tipo]-[dominio]`.
  - Esteira completa: $\text{Canal} \rightarrow \text{BFF} \rightarrow \text{Core Atômico} \rightarrow \text{Mensageria / Storage}$.
- **🔄 Preview Interativo & Loop de Ajustes:** Visualização do diagrama SVG, validação de regras metamodelo e botão para solicitar ajustes que retornam ao refinamento com a persona.
- **💾 Exportação Oficial The Open Group XML:** Arquivo `.archimate` compatível para importação imediata no aplicativo **Archi**.

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologias |
|---|---|
| **Backend** | Python 3.12 / 3.10+, FastAPI, Pydantic v2, Uvicorn, Pytest |
| **Frontend** | Node.js 20+, React 19, TypeScript, Vite 6, Lucide React |
| **IA / LLM Online** | **Google Gemini** (`gemini-2.0-flash` via Google AI Studio / GCP / GCA), OpenAI (`gpt-4o-mini`), Ollama (`llama3.2`) ou Built-in Expert Engine (fallback offline) |
| **Modelagem** | ArchiMate 3.2, The Open Group Model Exchange XML, SVG Dinâmico |

---

## 🔑 Configuração do Google Cloud (GCA) e LLM do Google (Gemini Online)

Para utilizar o Agente Arquiteto com a **LLM Online do Google (Gemini)** — permitindo que o agente elabore propostas inovadoras, consulte o RAG de forma dinâmica e aplique guardrails de escopo com IA de última geração —, siga o passo a passo abaixo:

### 1. Obter a Chave da API (API Key)

Você pode obter a chave de duas maneiras:

#### Opção A: Via Google AI Studio (Recomendado — Gratuito e Imediato)
1. Acesse o portal: [Google AI Studio (API Keys)](https://aistudio.google.com/app/apikey).
2. Faça login com sua Conta Google (ou conta corporativa vinculada ao **Google Cloud / GCA**).
3. Clique no botão azul **"Create API Key"** (Criar chave de API).
4. Selecione ou crie um projeto Google Cloud (GCP) associado.
5. Copie a chave gerada (iniciada por `AIzaSy...`).

#### Opção B: Via Google Cloud Console (GCP / Vertex AI / GCA)
1. Acesse o [Console do Google Cloud](https://console.cloud.google.com/).
2. Certifique-se de que o projeto Google Cloud (GCA) correto está ativo no seletor de projetos.
3. No menu lateral, vá em **APIs e Serviços** > **Biblioteca** e pesquise por **Generative Language API** (ou Vertex AI API). Clique em **Ativar**.
4. Em **APIs e Serviços** > **Credenciais**, clique em **Criar Credenciais** > **Chave de API**.
5. Copie a chave gerada.

---

### 2. Configurar a Chave no Projeto

Na pasta `backend/`, crie ou edite o arquivo `.env` (a partir do modelo `.env.example`):

```powershell
cd backend
cp .env.example .env
```

Abra o arquivo `backend/.env` e insira sua chave:

```env
# Define o Google Gemini como provedor ativo
LLM_PROVIDER=gemini

# Chave de API do Google (aceita GEMINI_API_KEY ou GOOGLE_API_KEY)
GEMINI_API_KEY=AIzaSySuaChaveAqui123456789
GEMINI_MODEL=gemini-2.0-flash
```

> 💡 **Dica de Compatibilidade:** O backend aceita tanto `GEMINI_API_KEY` quanto `GOOGLE_API_KEY`. Se você já tiver a variável `GOOGLE_API_KEY` definida no seu ambiente, o sistema a reconhece automaticamente sem conflitos.

---

### 3. Configurar via Terminal (Sem arquivo `.env`)

Caso prefira exportar a chave diretamente na sessão do terminal antes de iniciar o backend:

**No Windows PowerShell:**
```powershell
$env:LLM_PROVIDER="gemini"
$env:GEMINI_API_KEY="AIzaSySuaChaveAqui123456789"
```

**No Windows CMD:**
```cmd
set LLM_PROVIDER=gemini
set GEMINI_API_KEY=AIzaSySuaChaveAqui123456789
```

**No Linux / macOS (Bash / Zsh):**
```bash
export LLM_PROVIDER="gemini"
export GEMINI_API_KEY="AIzaSySuaChaveAqui123456789"
```

---

### 4. Como Validar se a LLM do Google está Ativa

1. Inicie o backend:
   ```powershell
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
2. Abra no navegador ou via curl: [http://127.0.0.1:8000/api/info](http://127.0.0.1:8000/api/info).
3. A resposta JSON confirmará a conexão ativa:
   ```json
   {
     "appName": "AI Software Architecture Designer — ArchiMate",
     "appVersion": "1.0.0",
     "activeProvider": "gemini",
     "providers": {
       "gemini": {
         "name": "Google Gemini",
         "available": true,
         "configured": true,
         "model": "gemini-2.0-flash"
       }
     }
   }
   ```
4. Na interface web ([http://localhost:5173](http://localhost:5173)), o cabeçalho exibirá o badge verde indicando **"Google Gemini (Online)"**.
5. *(Fallback Seguro)*: Caso a chave expire, atinja cota ou a máquina fique sem internet, o backend ativa automaticamente o **Built-in Expert Engine**, garantindo que as modelagens continuem funcionando normalmente.

---

## 🚀 Passo a Passo para Rodar o Sistema

### Pré-requisitos
- **Python 3.10+** (recomendado Python 3.12)
- **Node.js 18+ ou 20+** (com npm)
- **Git**

---

### 1. Clonar o Repositório
```bash
git clone <URL_DO_REPOSITORIO>
cd agente-arquiteto
```

---

### 2. Configurar e Rodar o Backend (FastAPI)

Abra um terminal PowerShell (ou Bash):

```powershell
# 1. Entrar na pasta do backend
cd backend

# 2. Criar o ambiente virtual Python (se ainda não existir)
python -m venv venv

# 3. Ativar o ambiente virtual
# No Windows PowerShell:
.\venv\Scripts\Activate.ps1
# (Se der erro de permissão no PowerShell, execute antes: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned)
# No Windows CMD:
.\venv\Scripts\activate.bat
# No Linux/macOS:
source venv/bin/activate

# 4. Instalar as dependências do backend
pip install -r requirements.txt

# 5. Configurar variáveis de ambiente (conforme seção do Gemini acima)
cp .env.example .env
# Edite o .env se desejar ativar a chave do Gemini ou OpenAI.

# 6. Iniciar o servidor backend FastAPI
uvicorn app.main:app --reload --port 8000
```

> 🌐 **Backend ativo em:** [http://127.0.0.1:8000](http://127.0.0.1:8000)  
> 📑 **Documentação Swagger (OpenAPI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### 3. Configurar e Rodar o Frontend (React + Vite)

Abra **outro terminal** na raiz do projeto:

```powershell
# 1. Entrar na pasta do frontend
cd frontend

# 2. Instalar as dependências Node.js
npm install

# 3. Iniciar o servidor de desenvolvimento Vite
npm run dev
```

> 💻 **Frontend ativo em:** [http://localhost:5173](http://localhost:5173)

---

### 4. (Opcional) Gerar Build de Produção do Frontend

Se você preferir que o próprio backend sirva a aplicação web completa em uma única porta (`8000`), basta compilar o frontend:

```powershell
cd frontend
npm run build
```
Uma pasta `frontend/dist` será gerada. Ao acessar [http://127.0.0.1:8000](http://127.0.0.1:8000), o backend servirá a UI completa automaticamente.

---

### 5. Executar a Suíte de Testes Automatizados

O projeto conta com **23 testes automatizados** que cobrem todos os componentes do fluxograma oficial:

```powershell
# Na raiz do projeto com o venv ativado:
$env:PYTHONPATH='backend'
.\backend\venv\Scripts\python.exe -m pytest backend/tests/ -v
```

Output esperado:
```text
backend/tests/test_api.py::test_api_info_endpoint PASSED
backend/tests/test_api.py::test_api_scope_guardrail_blocks_out_of_scope PASSED
backend/tests/test_api.py::test_api_scope_guardrail_allows_in_scope PASSED
backend/tests/test_api.py::test_api_brainstorm_endpoint PASSED
backend/tests/test_api.py::test_api_analyze_blocks_without_prerequisites PASSED
backend/tests/test_api.py::test_api_analyze_refine_approve_and_export_flow PASSED
backend/tests/test_archimate_models.py (3 testes) PASSED
backend/tests/test_archimate_validator.py (4 testes) PASSED
backend/tests/test_architect_agent.py (4 testes) PASSED
backend/tests/test_exporter.py (1 teste) PASSED
backend/tests/test_flowchart_adherence.py (5 testes) PASSED

============================= 23 passed in ~0.50s =============================
```

---

## 📁 Estrutura do Repositório

```text
agente-arquiteto/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py              # Endpoints da API (brainstorm, analyze, refine, export)
│   │   ├── knowledge/                 # Base de Conhecimento RAG de Domínio BV
│   │   │   ├── catalogo_tecnologias_bv.md
│   │   │   ├── padroes_nomenclatura_bv.md
│   │   │   ├── diretrizes_modelagem_archimate.md
│   │   │   └── padroes_integracao_e_pipeline.md
│   │   ├── models/
│   │   │   ├── archimate.py           # Metamodelo formal ArchiMate 3.2
│   │   │   ├── chat.py                # Modelos de requisição/resposta do chat e brainstorm
│   │   │   ├── persona.py             # Definição e prompts das Personas
│   │   │   └── proposal.py            # Modelos de proposta e pré-requisitos corporativos
│   │   ├── services/
│   │   │   ├── architect_agent.py     # Orquestrador do fluxo arquitetural
│   │   │   ├── architecture_rag.py    # Motor de busca RAG do Banco BV
│   │   │   ├── brainstorm_agent.py    # Agente consultivo com suporte a 'Ok?'
│   │   │   ├── diagram_generator.py   # Renderizador de diagramas em SVG oficial
│   │   │   ├── exporter.py            # Exportador Open Group XML e JSON
│   │   │   ├── llm_provider.py        # Integração com Gemini, OpenAI, Ollama e Builtin
│   │   │   └── scope_guardrail.py     # Guardrail classificador de escopo
│   │   ├── config.py                  # Configurações e detecção de provedores
│   │   └── main.py                    # Inicialização do FastAPI e montagem dos estáticos
│   ├── tests/                         # Suíte de testes automatizados (pytest)
│   ├── .env.example                   # Exemplo de configuração de chaves de API
│   └── requirements.txt               # Dependências Python
│
├── frontend/
│   ├── src/
│   │   ├── components/                # Áreas A (Chat/Persona), B (Proposta), C (SVG), D (Export)
│   │   ├── services/                  # Chamadas de API para o backend
│   │   ├── types/                     # Tipos TypeScript do ArchiMate e Personas
│   │   └── App.tsx                    # Componente principal integrando o fluxo
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   ├── DesenhoFluxograma_V2.png       # Fluxograma oficial do sistema
│   ├── PLANO_IMPLEMENTACAO_AGENTE_ARQUITETO.md # Registro técnico e plano executivo
│   ├── RECOMENDACOES_INGESTAO_RAG.md  # Diretrizes de engenharia RAG
│   └── rag_knowledge_base/            # Meta-documentação do treinamento (LangGraph, MCP, etc.)
│
└── README.md                          # Este guia completo de execução
```

---

## 💡 Exemplo Rápido de Uso

1. Abra a aplicação em `http://localhost:5173`.
2. Escolha a **Persona**: *Arquiteto de Software* ou *Engenheiro de Software*.
3. Na caixa de texto da Área A, clique em **"Usar Exemplo BV"** ou digite:
   ```text
   Sigla: SESG
   Feature: Cálculo e monitoramento de risco ambiental com Spring Boot, Angular, PubSub e GCS
   ARQCOR: ARQ-2026
   ```
4. No modo **Brainstorming**, dialogue com o agente sobre arquitetura, pergunte por alternativas e confira os padrões do Banco BV sugeridos.
5. Quando estiver satisfeito com o alinhamento, confirme com *"Ok, pode prosseguir para a modelagem"* ou clique no botão **"Prosseguir para Modelagem (Ok)"**.
6. Veja o modelo e o diagrama SVG gerados nas Áreas B e C.
7. Clique em **"Exportar XML (Archi)"** na Área D e abra o arquivo diretamente no aplicativo **Archi** (`Arquivo -> Importar -> Modelo Open Exchange...`).

---

## 📜 Licença

Este projeto é desenvolvido para fins educacionais e profissionais no âmbito do treinamento **AI Experts Banco BV**. Distribuído sob a licença **MIT**.
