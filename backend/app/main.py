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


def resolver_arquivo_spa(dist_dir: Path, full_path: str) -> Path:
    """Retorna o arquivo solicitado se estiver dentro de dist_dir; caso contrário, o index.html da SPA."""
    base = dist_dir.resolve()
    try:
        target_file = (base / full_path).resolve()
    except (OSError, ValueError):
        return base / "index.html"
    if target_file.is_relative_to(base) and target_file.is_file():
        return target_file
    return base / "index.html"


def montar_frontend(app: FastAPI, dist_dir: Path) -> None:
    """Registra os arquivos estáticos do build do frontend e a rota catch-all da SPA."""
    assets_dir = dist_dir / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        return FileResponse(resolver_arquivo_spa(dist_dir, full_path))


if frontend_dist_dir.exists():
    montar_frontend(app, frontend_dist_dir)
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
