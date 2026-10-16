# AI Software Architecture Designer – ArchiMate

## 📖 O que o projeto faz?

Este repositório implementa **um agente inteligente de arquitetura de software** que recebe uma descrição textual de um sistema e gera:
- Uma **proposta de arquitetura** (componentes, integrações, decisões, requisitos não‑funcionais);
- Um **modelo ArchiMate** completo (JSON, XML) e um **diagrama SVG** visualizando a arquitetura;
- Ferramentas para **editar, refinar e validar** a proposta diretamente numa aplicação web simples.

A aplicação é composta por duas partes independentes:
1. **Backend** – API **FastAPI** que executa o fluxo de 8 etapas do agente, valida o modelo e expõe endpoints de exportação.
2. **Frontend** – UI **React + TypeScript** (Vite) que permite ao usuário conversar com o agente, visualizar o diagrama, editar componentes e exportar arquivos ArchiMate.

O objetivo é ser **leve, fácil de instalar** e usar **provedores gratuitos de LLM** (modo offline padrão) ou configurar um provedor como Gemini ou OpenAI.

---

## 🛠️ Tecnologias
| Camada | Tecnologias |
|--------|-------------|
| **Backend** | Python 3.10+, FastAPI, Pydantic, Uvicorn |
| **Frontend** | Node.js 20, Vite 6, React 19, TypeScript, lucide‑react |
| **ArchiMate** | Modelos JSON/XML, geração de SVG (via `DiagramGenerator`) |

---

## 🚀 Como executar localmente

> **Requisitos**
> - Python 3.10 ou mais recente
> - Node.js 20.x (inclui npm)
> - Git (opcional)
> - PowerShell ou CMD
> - Todos os comandos devem ser executados a partir da raiz do projeto (`C:\Users\erico\OneDrive\Documentos\DEV\agente-arquiteto`).

### 1. Backend
```powershell
# Entrar na pasta backend
cd backend

# Criar e ativar virtual‑env
python -m venv venv
.\venv\Scripts\Activate.ps1   # PowerShell (ou `venv\Scripts\activate` no CMD)

# Instalar dependências Python
pip install -r requirements.txt

# (Opcional) Copiar arquivo de variáveis de ambiente e ajustar se quiser usar um LLM externo
cp .env.example .env
# edit .env if needed

# Iniciar a API FastAPI
uvicorn app.main:app --reload --port 8000
```
A API ficará disponível em **http://127.0.0.1:8000**.

### 2. Frontend
```powershell
# Em outra janela do terminal, entrar na pasta frontend
cd frontend

# Instalar dependências Node
npm install

# Desenvolvimento (hot‑reload) – abre http://localhost:5173
npm run dev

# OU, para gerar a versão de produção que será servida pelo backend:
npm run build   # cria a pasta frontend/dist
# Depois, basta manter o backend rodando (ele serve os arquivos estáticos).
```
Quando a pasta `frontend/dist` existir, acessar **http://127.0.0.1:8000** exibirá a UI completa.

---

## 📂 Estrutura de diretórios (visão geral)
```
agente-arquiteto/
│   README.md                ← este documento
│   .gitignore
│
├─ backend/
│   ├─ app/
│   │   ├─ main.py           # ponto de entrada FastAPI
│   │   └─ …                 # rotas, serviços, modelos
│   ├─ requirements.txt
│   └─ .env.example
│
├─ frontend/
│   ├─ src/                 # código React/TS
│   ├─ public/              # assets estáticos
│   ├─ package.json
│   └─ ...
│
└─ examples/                # arquivos ArchiMate de exemplo (json, xml, svg)
```

---

## 💡 Próximos passos / exploração
- **Teste a UI**: descreva um sistema na Área A (ex.: “catálogo de produtos com busca e carrinho”) e siga o fluxo.
- **Edite a proposta** nas Áreas B e C, adicione integrações ou altere decisões.
- **Exporte** o modelo ArchiMate (JSON, XML ou SVG) usando a barra de ferramentas da Área D.
- **Mude o provedor LLM** editando `.env` (ex.: `LLM_PROVIDER=gemini` + sua chave API) para gerar propostas mais detalhadas.

---

## 📜 Licença
Este projeto está licenciado sob a **MIT License** – sinta‑se livre para usar, modificar e distribuir.

---

**Happy architecting!** 🎉
