"""Serviço de Guardrail de Escopo para o Agente Arquiteto de Software AI.

Valida se a solicitação do usuário se enquadra estritamente no domínio de
arquitetura de software, design de sistemas, integração de componentes e modelagem Archi / ArchiMate.
Caso esteja fora de escopo, recusa educadamente o pedido conforme exigido no fluxograma oficial.
"""

import logging
import re
from typing import Tuple, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Palavras-chave que indicam que a requisição está dentro do escopo de arquitetura de software
IN_SCOPE_KEYWORDS = [
    "sistema", "arquitetura", "desenho", "modelagem", "archi", "archimate",
    "componente", "backend", "frontend", "api", "microsserviço", "microservico",
    "banco de dados", "database", "mensageria", "pubsub", "fila", "kafka",
    "spring", "sboot", "python", "pyweb", "angular", "ng", "streamlit",
    "dataflow", "batch", "gcs", "nuvem", "cloud", "integracao", "integrar",
    "fluxo", "pipeline", "bff", "rest", "grpc", "autenticacao", "login",
    "servico", "aplicacao", "deploy", "gke", "kubernetes", "sigla", "feature",
    "arqcor", "projeto", "proposta", "diagrama", "requisito", "escalabilidade",
    "resiliencia", "tabela", "cache", "redis", "postgres", "sql", "nosql"
]

# Gatilhos explícitos de fora de escopo (receitas culinárias, piadas, suporte de TI pessoal, horóscopo, etc.)
OUT_OF_SCOPE_PATTERNS = [
    r"\breceita\s+de\s+(?:bolo|pao|comida|torta|pizza|cafe)\b",
    r"\bcomo\s+fazer\s+(?:um\s+bolo|almoco|jantar)\b",
    r"\bprevisao\s+do\s+tempo\b",
    r"\bpiada\b",
    r"\bhoroscopo\b",
    r"\bqual\s+a\s+capital\s+d[aeo]\b",
    r"\bme\s+conte\s+uma\s+historia\b",
]

DEFAULT_REFUSAL_MESSAGE = (
    "Olá! Meu escopo de atuação é estritamente a **modelagem de arquiteturas de software, "
    "desenho de soluções e geração de modelos para o software Archi (ArchiMate 3.2)**.\n\n"
    "Não posso atender a solicitações fora desse domínio. "
    "Por favor, descreva uma necessidade de sistema, aplicação ou arquitetura "
    "(incluindo a Sigla, Feature e ARQCOR do seu projeto)."
)


class ScopeGuardrail:
    """Avalia se a solicitação do usuário está dentro do escopo permitido."""

    @classmethod
    def check_scope_sync(cls, message: str) -> Tuple[bool, Optional[str]]:
        """Verificação heurística síncrona de escopo."""
        clean_text = message.strip().lower()

        # 1. Heurísticas rápidas: verifica padrões explícitos fora de escopo
        for pattern in OUT_OF_SCOPE_PATTERNS:
            if re.search(pattern, clean_text):
                return False, DEFAULT_REFUSAL_MESSAGE

        # 2. Saudações curtas ou mensagens iniciais (ex: "olá", "iniciar", "quero criar um sistema")
        if any(kw in clean_text for kw in IN_SCOPE_KEYWORDS):
            return True, None

        tokens = re.findall(r"\b\w{3,}\b", clean_text)
        if len(tokens) <= 2 and clean_text in ["ola", "olá", "oi", "bom dia", "boa tarde", "boa noite", "ajuda", "começar", "iniciar"]:
            return True, None

        matches = [kw for kw in IN_SCOPE_KEYWORDS if kw in clean_text]
        if len(matches) >= 1 or len(tokens) >= 5:
            return True, None

        return False, DEFAULT_REFUSAL_MESSAGE

    @classmethod
    async def evaluate_scope(cls, message: str) -> Tuple[bool, Optional[str]]:
        """Avalia o escopo usando heurísticas rápidas e recorre à LLM online quando necessário."""
        # 1. Executa primeiro as heurísticas rápidas
        is_in, refusal = cls.check_scope_sync(message)
        if not is_in:
            from app.services.cost_tracker import CostTracker
            CostTracker.record_span(
                name="scope_guardrail_refusal",
                model="heuristic",
                prompt_tokens=max(len(message) // 4, 10),
                completion_tokens=30,
                latency_ms=1.5,
            )
            return False, refusal

        # 2. Consulta a LLM Online se estiver configurada com credenciais
        provider = settings.detect_active_provider()
        if provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                return await cls._evaluate_with_gemini(message)
            except Exception as e:
                logger.warning(f"Avaliação de escopo com Gemini falhou: {e}. Mantendo decisão heurística.")
        elif provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return await cls._evaluate_with_openai(message)
            except Exception as e:
                logger.warning(f"Avaliação de escopo com OpenAI falhou: {e}. Mantendo decisão heurística.")

        from app.services.cost_tracker import CostTracker
        CostTracker.record_span(
            name="scope_guardrail",
            model="heuristic",
            prompt_tokens=max(len(message) // 4, 10),
            completion_tokens=10,
            latency_ms=2.0,
        )
        return True, None

    @classmethod
    async def _evaluate_with_gemini(cls, message: str) -> Tuple[bool, Optional[str]]:
        import time
        import httpx
        from app.services.cost_tracker import CostTracker

        url, headers = settings.get_gemini_request_config()
        prompt = (
            "Você é um classificador rigoroso de escopo para um Agente Arquiteto de Software corporativo.\n"
            "O escopo permitido é EXCLUSIVAMENTE: arquitetura de software, desenho de sistemas, "
            "modelagem Archi/ArchiMate, APIs, bancos de dados, integrações, requisitos funcionais e não funcionais de TI.\n"
            "Responda em formato JSON: {\"in_scope\": true/false, \"reason\": \"breve justificativa\"}.\n\n"
            f"Mensagem do usuário: \"{message}\""
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        t0 = time.perf_counter()
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            latency_ms = (time.perf_counter() - t0) * 1000
            usage = data.get("usageMetadata", {})
            CostTracker.record_span(
                name="scope_guardrail",
                model=settings.GEMINI_MODEL,
                prompt_tokens=usage.get("promptTokenCount", max(len(prompt) // 4, 40)),
                completion_tokens=usage.get("candidatesTokenCount", 25),
                latency_ms=latency_ms,
            )
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            import json
            parsed = json.loads(raw_text)
            in_scope = bool(parsed.get("in_scope", True))
            return in_scope, None if in_scope else DEFAULT_REFUSAL_MESSAGE

    @classmethod
    async def _evaluate_with_openai(cls, message: str) -> Tuple[bool, Optional[str]]:
        import time
        import httpx
        from app.services.cost_tracker import CostTracker

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        prompt = (
            "Classifique se a mensagem do usuário pertence ao escopo de arquitetura de software, "
            "engenharia de sistemas ou modelagem ArchiMate.\n"
            "Responda exclusivamente em JSON: {\"in_scope\": true/false}"
        )
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": message}
            ],
            "response_format": {"type": "json_object"}
        }
        t0 = time.perf_counter()
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            latency_ms = (time.perf_counter() - t0) * 1000
            usage = data.get("usage", {})
            CostTracker.record_span(
                name="scope_guardrail",
                model=settings.OPENAI_MODEL,
                prompt_tokens=usage.get("prompt_tokens", max((len(prompt) + len(message)) // 4, 40)),
                completion_tokens=usage.get("completion_tokens", 20),
                latency_ms=latency_ms,
            )
            import json
            parsed = json.loads(data["choices"][0]["message"]["content"])
            in_scope = bool(parsed.get("in_scope", True))
            return in_scope, None if in_scope else DEFAULT_REFUSAL_MESSAGE
