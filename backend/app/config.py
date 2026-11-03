"""Configurações e variáveis de ambiente para o backend do Agente Arquiteto de Software AI."""

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple
import dotenv
from pydantic_settings import BaseSettings


def _descobrir_e_carregar_arquivos_env() -> List[Path]:
    """
    Descobre e carrega arquivos .env da árvore de diretórios, priorizando as pastas pai
    (raiz do projeto e ancestrais) para que as credenciais e configurações sejam herdadas
    automaticamente sem a necessidade de duplicar arquivos .env manualmente nos subdiretórios.
    """
    arquivo_config = Path(__file__).resolve()
    diretorio_atual = Path.cwd().resolve()

    diretorios_unicos = set()
    for base in [diretorio_atual, arquivo_config.parent]:
        # Percorre até a raiz do projeto e ancestrais (até 6 níveis)
        for p in [base] + list(base.parents)[:6]:
            if p.is_dir():
                diretorios_unicos.add(p)

    # Ordena do nível mais alto (ancestrais mais rasos) para o mais profundo
    diretorios_ordenados = sorted(list(diretorios_unicos), key=lambda d: len(d.parts))

    arquivos_descobertos: List[Path] = []
    for d in diretorios_ordenados:
        env_path = d / ".env"
        if env_path.is_file() and env_path not in arquivos_descobertos:
            arquivos_descobertos.append(env_path)

    # Mescla valores: valores não vazios das configurações pai são preservados
    # e arquivos filhos só sobrescrevem se tiverem strings não vazias.
    valores_mesclados: Dict[str, str] = {}
    for ef in arquivos_descobertos:
        try:
            dados_arquivo = dotenv.dotenv_values(str(ef))
            for k, v in dados_arquivo.items():
                if v is not None and str(v).strip() != "":
                    valores_mesclados[k] = str(v).strip()
                elif k not in valores_mesclados:
                    valores_mesclados[k] = ""
        except Exception:
            pass

    # Injeta no os.environ se a chave ainda não estiver definida no ambiente do sistema operacional
    for k, v in valores_mesclados.items():
        if v and (k not in os.environ or not os.environ[k].strip()):
            os.environ[k] = v

    return arquivos_descobertos


_arquivos_env_descobertos = _descobrir_e_carregar_arquivos_env()


class Settings(BaseSettings):
    APP_NAME: str = "AI Software Architecture Designer — ArchiMate"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Configurações de LLM
    # Suportados: "gemini", "openai", "anthropic", "ollama", "builtin"
    LLM_PROVIDER: str = "auto"

    # Chaves de API e Modelos
    GEMINI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"

    # Configuração de CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    model_config = {
        "env_file": [str(p) for p in _arquivos_env_descobertos] if _arquivos_env_descobertos else (".env",),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def model_post_init(self, __context: Any) -> None:
        """Sincroniza chaves entre GEMINI_API_KEY, GOOGLE_API_KEY e os.environ."""
        # 1. Recupera do os.environ se ainda estiver vazio na instância
        if not self.GEMINI_API_KEY:
            self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
        if not self.GOOGLE_API_KEY:
            self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

        # 2. Intercambia valores entre GEMINI_API_KEY e GOOGLE_API_KEY
        if not self.GEMINI_API_KEY and self.GOOGLE_API_KEY:
            self.GEMINI_API_KEY = self.GOOGLE_API_KEY
        elif not self.GOOGLE_API_KEY and self.GEMINI_API_KEY:
            self.GOOGLE_API_KEY = self.GEMINI_API_KEY

        # 3. Exporta de volta para os.environ para garantir compatibilidade com SDKs oficiais
        if self.GEMINI_API_KEY:
            os.environ["GEMINI_API_KEY"] = self.GEMINI_API_KEY
            os.environ["GOOGLE_API_KEY"] = self.GEMINI_API_KEY

        if not self.OPENAI_API_KEY:
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
        if not self.ANTHROPIC_API_KEY:
            self.ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()

    def detect_active_provider(self) -> str:
        """Determina o provedor ativo com base na configuração ou nas chaves de API disponíveis."""
        if not self.GEMINI_API_KEY and self.GOOGLE_API_KEY:
            self.GEMINI_API_KEY = self.GOOGLE_API_KEY
        if self.LLM_PROVIDER and self.LLM_PROVIDER != "auto":
            return self.LLM_PROVIDER.lower()
        if self.GEMINI_API_KEY:
            return "gemini"
        if self.OPENAI_API_KEY:
            return "openai"
        if self.ANTHROPIC_API_KEY:
            return "anthropic"
        # Se nenhuma chave em nuvem for detectada, utiliza o motor especialista embutido
        return "builtin"

    def get_gemini_request_config(self) -> Tuple[str, Dict[str, str]]:
        """Retorna (url, headers) compatível com chaves AI Studio (AIza...) e chaves Express Vertex AI (AQ...)."""
        key = (self.GEMINI_API_KEY or self.GOOGLE_API_KEY or "").strip()
        model = self.GEMINI_MODEL.strip()
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": key,
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        return url, headers


settings = Settings()
