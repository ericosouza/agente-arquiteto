"""Scope Guardrail Service for AI Software Architecture Designer.

Validates whether the user's request falls strictly within the domain of
software architecture, system design, component integration, and Archi / ArchiMate modeling.
If out of scope, politely refuses the request as mandated by the system flowchart.
"""

import logging
import re
from typing import Tuple, Optional
from app.config import settings

logger = logging.getLogger(__name__)

# Keywords that indicate the request is within software architecture scope
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

# Explicit out-of-scope triggers (e.g. food recipes, general jokes, IT support tickets, personal advice)
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
    """Evaluates whether the incoming user request is within scope."""

    @classmethod
    def check_scope_sync(cls, message: str) -> Tuple[bool, Optional[str]]:
        """Synchronous heuristic scope check."""
        clean_text = message.strip().lower()

        # 1. Fast heuristics: check explicit out-of-scope patterns
        for pattern in OUT_OF_SCOPE_PATTERNS:
            if re.search(pattern, clean_text):
                return False, DEFAULT_REFUSAL_MESSAGE

        # 2. If short greetings / setup messages (e.g., "olá", "iniciar", "quero criar um sistema")
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
        """Evaluates scope using fast heuristics first, falling back to online LLM when needed."""
        # 1. First run fast heuristics
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

        # 2. Check with Online LLM if configured and keys are present
        provider = settings.detect_active_provider()
        if provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                return await cls._evaluate_with_gemini(message)
            except Exception as e:
                logger.warning(f"Gemini scope evaluation failed: {e}. Using heuristic evaluation.")
        elif provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return await cls._evaluate_with_openai(message)
            except Exception as e:
                logger.warning(f"OpenAI scope evaluation failed: {e}. Using heuristic evaluation.")

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
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        prompt = (
            "Você é um classificador rigoroso de escopo para um Agente Arquiteto de Software corporativo.\n"
            "O escopo permitido é EXCLUSIVAMENTE: arquitetura de software, desenho de sistemas, "
            "modelagem Archi/ArchiMate, APIs, bancos de dados, integrações, requisitos funcionais e não funcionais de TI.\n"
            "Responda em formato JSON: {\"in_scope\": true/false, \"reason\": \"breve justificativa\"}.\n\n"
            f"Mensagem do usuário: \"{message}\""
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            import json
            parsed = json.loads(raw_text)
            in_scope = bool(parsed.get("in_scope", True))
            return in_scope, None if in_scope else DEFAULT_REFUSAL_MESSAGE

    @classmethod
    async def _evaluate_with_openai(cls, message: str) -> Tuple[bool, Optional[str]]:
        import httpx
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
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            import json
            parsed = json.loads(data["choices"][0]["message"]["content"])
            in_scope = bool(parsed.get("in_scope", True))
            return in_scope, None if in_scope else DEFAULT_REFUSAL_MESSAGE
