"""Ponto de entrada principal da aplicação FastAPI do Agente Arquiteto de Software AI."""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.api.routes import router as api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Agente inteligente para design e documentação de arquitetura de software no padrão ArchiMate 3.2.",
)

# Configuração do middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monta as rotas da API REST
app.include_router(api_router)

# Monta arquivos estáticos do Frontend se o build (dist) existir
frontend_dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Serve o arquivo estático se existir, caso contrário retorna index.html para roteamento SPA
        target_file = frontend_dist_dir / full_path
        if target_file.is_file():
            return FileResponse(target_file)
        return FileResponse(frontend_dist_dir / "index.html")
else:
    @app.get("/")
    async def index_dev_notice():
        return {
            "status": "running",
            "message": "Backend API está ativa! Para acessar a interface visual durante desenvolvimento, inicie o Vite no frontend (npm run dev) ou gere o build (npm run build).",
            "apiDocumentation": "/docs",
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
