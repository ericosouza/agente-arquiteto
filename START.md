# 🚀 Guia de Inicialização Rápida (START.md)
## Agente Arquiteto de Software AI — ArchiMate 3.2

Este guia contém o **passo a passo exato** de como configurar suas credenciais, em qual pasta abrir cada terminal e quais comandos executar para iniciar e testar o sistema completo (Backend FastAPI, Frontend React e Observabilidade FinOps).

---

## 📋 Sumário
1. [Pré-requisitos do Sistema](#1-pré-requisitos-do-sistema)
2. [Passo 1: Configurar a Chave da API do Google (GCA / Gemini)](#passo-1-configurar-a-chave-da-api-do-google-gca--gemini)
3. [Passo 2: Iniciar o Backend (FastAPI + Python)](#passo-2-iniciar-o-backend-fastapi--python)
4. [Passo 3: Iniciar o Frontend (React + Vite)](#passo-3-iniciar-o-frontend-react--vite)
5. [Passo 4 (Opcional): Iniciar a Observabilidade Docker (Arize Phoenix)](#passo-4-opcional-iniciar-a-observabilidade-docker-arize-phoenix)
6. [Alternativa: Iniciar TUDO via Docker Compose (Comando Único)](#alternativa-iniciar-tudo-via-docker-compose-comando-único)
7. [Passo 5: Como Executar os Testes Automatizados (26 Testes)](#passo-5-como-executar-os-testes-automatizados-26-testes)
8. [Roteiro Prático de Teste na Interface Web](#roteiro-prático-de-teste-na-interface-web)
9. [Solução de Problemas Comuns](#solução-de-problemas-comuns)

---

## 1. Pré-requisitos do Sistema

Antes de iniciar, certifique-se de ter instalado:
* **Python 3.12** (ou 3.10+)
* **Node.js 20+** e **npm**
* **Docker Desktop** *(necessário apenas se for rodar via Docker ou usar o container de Observabilidade do Arize Phoenix)*
* **PowerShell** (ou terminal bash de sua preferência)

---

## Passo 1: Configurar a Chave da API do Google (GCA / Gemini)

O backend possui **herança automática de configurações**. Você só precisa configurar o arquivo `.env` uma única vez na **raiz do projeto**. Não é necessário duplicar nada nas subpastas.

### 1.1 Local do arquivo
Abra ou crie o arquivo `.env` na pasta raiz:
```text
C:\DEV\Projetos\Treinamento BV\agente-arquiteto\.env
```
*(Se o arquivo ainda não existir, copie o modelo: execute `Copy-Item .env.example .env` na raiz do projeto).*

### 1.2 Onde colocar as chaves no arquivo `.env`
Abra o arquivo `.env` no seu editor de texto (VS Code, Bloco de Notas, etc.) e configure as seguintes linhas:

```env
# Linha 8: Define o Google Gemini como provedor ativo
LLM_PROVIDER=gemini

# Linha 11: Cole a sua Chave de API do Google / GCA
GEMINI_API_KEY=AQ.Ab8RNT...sua_chave_aqui...

# Linha 12: Modelo oficial homologado
GEMINI_MODEL=gemini-2.0-flash
```

> 💡 **Tipos de chaves suportadas automaticamente:**
> 1. **Chaves Google Cloud / Vertex AI Express (GCA):** Iniciadas por `AQ.` (são roteadas nativamente para o endpoint `aiplatform.googleapis.com`).
> 2. **Chaves Google AI Studio (Gratuitas):** Iniciadas por `AIzaSy...` (roteadas para `generativelanguage.googleapis.com`).
> 3. **Modo 100% Offline (Sem chaves):** Se quiser testar sem internet ou sem chaves, basta alterar a Linha 8 para `LLM_PROVIDER=builtin`. O motor especialista embutido assumirá o raciocínio sem nenhum custo.

---

## Passo 2: Iniciar o Backend (FastAPI + Python)

Abra o **Terminal 1** (PowerShell).

### 2.1 Entrar na pasta do backend
```powershell
cd "C:\DEV\Projetos\Treinamento BV\agente-arquiteto\backend"
```

### 2.2 Ativar o ambiente virtual Python
Execute o comando de ativação do ambiente pré-configurado:
```powershell
.\venv\Scripts\Activate.ps1
```
*(Você verá o prefixo `(venv)` aparecer no seu terminal).*

> *Nota: Se a execução de scripts estiver bloqueada no seu PowerShell, você pode rodar diretamente com o executável sem precisar ativar, usando o comando do item 2.3.*

### 2.3 Iniciar o servidor Uvicorn
Com o ambiente ativado:
```powershell
uvicorn app.main:app --reload --port 8000
```
*Ou, de forma direta sem ativar o terminal:*
```powershell
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

### 2.4 Como validar se o backend subiu
Abra o seu navegador de internet no endereço:
👉 **[http://localhost:8000/api/info](http://localhost:8000/api/info)**

Você verá um JSON confirmando:
* `"activeProvider": "gemini"`
* `"configured": true`
* Documentação interativa Swagger: **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## Passo 3: Iniciar o Frontend (React + Vite)

Abra um **novo terminal** (Terminal 2) no PowerShell.

### 3.1 Entrar na pasta do frontend
```powershell
cd "C:\DEV\Projetos\Treinamento BV\agente-arquiteto\frontend"
```

### 3.2 Instalar dependências (apenas na primeira vez)
```powershell
npm install
```

### 3.3 Iniciar o servidor de desenvolvimento Vite
```powershell
npm run dev
```

### 3.4 Acessar a aplicação
O Vite informará o link local. Abra seu navegador no endereço:
👉 **[http://localhost:5173](http://localhost:5173)**

---

## Passo 4 (Opcional): Iniciar a Observabilidade Docker (Arize Phoenix)

Para acompanhar em tempo real os gráficos de traces, spans do LangGraph e o waterfall de latência sem custo de nuvem externa:

Abra o **Terminal 3** (PowerShell).

### 4.1 Entrar na raiz do projeto
```powershell
cd "C:\DEV\Projetos\Treinamento BV\agente-arquiteto"
```

### 4.2 Subir o container do Arize Phoenix
```powershell
docker compose up -d observability
```

### 4.3 Acessar o Dashboard do Phoenix
Abra seu navegador no endereço:
👉 **[http://localhost:6006](http://localhost:6006)**

---

## Alternativa: Iniciar TUDO via Docker Compose (Comando Único)

Se você prefere subir toda a stack (Backend + Frontend + Arize Phoenix) em containers isolados de produção com apenas um comando:

### 1. Entrar na raiz do projeto
```powershell
cd "C:\DEV\Projetos\Treinamento BV\agente-arquiteto"
```

### 2. Executar o Docker Compose
```powershell
docker compose up -d --build
```

### 3. Acessar as portas:
* **Frontend Web (Aplicação Completa):** [http://localhost:5173](http://localhost:5173)
* **Backend API / Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Dashboard Arize Phoenix (Observabilidade):** [http://localhost:6006](http://localhost:6006)

Para parar os containers:
```powershell
docker compose down
```

---

## Passo 5: Como Executar os Testes Automatizados (26 Testes)

Para validar a integridade dos modelos ArchiMate 3.2, guardrail de escopo, pré-requisitos, validação semântica e FinOps:

Abra o terminal na **raiz do projeto**:
```powershell
cd "C:\DEV\Projetos\Treinamento BV\agente-arquiteto"
```

Execute o comando:
```powershell
.\backend\venv\Scripts\pytest.exe backend\tests -v
```

> **Resultado esperado:**
> ```text
> 26 passed in 1.9s (100% sucesso)
> ```

---

## 🧪 Roteiro Prático de Teste na Interface Web

Siga este passo a passo para testar o agente do início ao fim:

1. Acesse **[http://localhost:5173](http://localhost:5173)** no navegador.
2. Observe o cabeçalho superior:
   * **Provedor:** Verifique o ícone do **Google Gemini** ou clique no botão do provedor para conferir o status *Configurado*.
   * **Badge de FinOps:** Observe o indicador `🪙 FinOps: R$ 0,0000 (0 tkns)`.
3. Na **Área A (Chat)**:
   * Escolha a persona: **Arquiteto de Software** (foco em governança e visão macro) ou **Engenheiro de Software** (foco em esteira técnica, resiliência e protocolos).
   * Mantenha o modo **"💡 Brainstorming & RAG"** selecionado.
4. Digite a solicitação contendo os 3 pré-requisitos obrigatórios do fluxograma:
   ```text
   Sigla: SESG
   Feature: Risco Ambiental
   ARQCOR: ARQ-2026
   Preciso de um portal web corporativo para os analistas avaliarem o risco socioambiental dos clientes, com persistência transacional e relatórios futuros.
   ```
5. Envie a mensagem:
   * O agente consultará o **RAG de Arquitetura do BV** e responderá de forma consultiva com sugestões tecnológicas homologadas (Angular 20 `ng`, Spring Boot `sboot`, MySQL, etc.).
6. Digite **`Ok, pode gerar o modelo!`** e envie:
   * O sistema acionará a geração do modelo oficial ArchiMate 3.2.
   * Na **Área B (Tabela)**: Os componentes padronizados serão listados (`ng-sesg-base-portal-esg`, `sboot-sesg-base-bff-portal-esg`, `sboot-sesg-base-atom-sistema-esg`, `mysql-sesg-base-sistema-esg`).
   * Na **Área C (Centro)**: O **diagrama SVG ArchiMate 3.2** será renderizado em alta definição com faixas de camadas (*Channel Layer*, *Application Layer*, *Technology Layer*), pontas de flecha normatizadas (*Serving*, *Access*) e glifos visuais.
7. Clique no botão de custo **`🪙 FinOps`** no cabeçalho:
   * Um modal abrirá detalhando os tokens consumidos e o valor real da chamada calculado em **R$** e **USD**.
8. Na **Área D (Rodapé)**:
   * Clique em **"Exportar XML (Archi)"** para baixar o arquivo `.archimate` compatível com o software **Archi**.
   * Clique em **"Exportar SVG"** ou **"Exportar JSON"** para baixar a documentação visual e estrutural.

---

## 🛠️ Solução de Problemas Comuns

| Sintoma | Causa Provável | Solução |
|---|---|---|
| **Porta 8000 já em uso** | Outro processo está rodando na porta 8000 | No terminal, encerre o processo anterior com `Ctrl + C` ou mude a porta: `uvicorn app.main:app --port 8001` |
| **Porta 5173 já em uso** | Outro servidor Vite ativo | O Vite sugerirá automaticamente a porta `5174`. Basta acessar a porta indicada |
| **Erro de política de execução do PowerShell** | Scripts PowerShell desabilitados no Windows | Execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` no terminal antes de ativar o venv, ou use o caminho direto `.\venv\Scripts\uvicorn.exe` |
| **Gemini caindo no Fallback Offline** | Chave ausente ou sem cota no Google Cloud | Verifique se a variável `GEMINI_API_KEY` está preenchida sem aspas adicionais no `.env` da raiz e se `LLM_PROVIDER=gemini` |
| **Container Docker Phoenix não sobe** | Docker Desktop desligado | Abra o aplicativo Docker Desktop no Windows e aguarde até o ícone da baleia ficar verde antes de rodar `docker compose up` |
