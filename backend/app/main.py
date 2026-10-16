"""Main entry point for AI Software Architecture Designer FastAPI Application."""

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

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API
app.include_router(api_router)

# Mount Frontend static files if built
frontend_dist_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Serve static file if exists, otherwise index.html for SPA routing
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
