# Diretrizes do Projeto: Agente Arquiteto de Software AI (Banco BV)

## Comando de Inicialização Rápida no Chat (Start)
Quando o usuário enviar uma mensagem solicitando iniciar, startar ou subir o sistema (como `start`, `iniciar`, `/start`, `subir sistema`):
1. Verifique se os serviços já estão em execução (Backend na porta 8000 e Frontend na porta 5173).
2. Caso algum esteja parado, inicialize o Backend (`powershell -Command "Set-Location 'backend'; .\venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000"`) e o Frontend (`powershell -Command "Set-Location 'frontend'; npm run dev"`) em modo daemon fora do sandbox (`BypassSandbox: true`, `IsDaemon: true`).
3. Responda imediatamente com os links prontos para teste manual:
   - **Frontend (Interface Web):** http://localhost:5173
   - **Backend API (Swagger Docs):** http://localhost:8000/docs
   - **Backend Status (Info):** http://localhost:8000/api/info

## Regras de Engenharia
- Fonte única de configuração: o arquivo `.env` fica na raiz do projeto (`agente-arquiteto/.env`) e é herdado automaticamente.
- Todas as mensagens, comentários de código e interações com o usuário devem ser estritamente em Português do Brasil (pt-BR).
- Respeitar 100% o fluxo oficial de arquitetura com a tríade de pré-requisitos (`Sigla`, `Feature`, `ARQCOR`), RAG corporativo e validação ArchiMate 3.2.
