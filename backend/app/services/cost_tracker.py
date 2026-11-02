"""Serviço de Rastreamento de Custos, FinOps e Observabilidade.

Monitora tokens, calcula custos em USD e BRL com base nas tabelas de preços oficiais dos provedores,
registra spans por etapa do agente de arquitetura e expõe resumos consolidados de FinOps.
Compatível com OpenTelemetry e coletores locais ou em nuvem como Arize Phoenix e LangSmith.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import uuid4
import os
import logging
from app.models.observability import TokenUsage, CostBreakdown, SpanMetric, FinOpsSummary

logger = logging.getLogger("cost_tracker")

# Tabela de preços por 1.000.000 (1M) de tokens em USD
MODEL_PRICING_PER_1M: Dict[str, Dict[str, float]] = {
    # Modelos Google Gemini
    "gemini-2.0-flash": {"prompt": 0.10, "completion": 0.40},
    "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "gemini-1.5-pro": {"prompt": 1.25, "completion": 5.00},
    # Modelos OpenAI
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    # Modelos Anthropic Claude
    "claude-3-5-sonnet-20241022": {"prompt": 3.00, "completion": 15.00},
    # Motores Locais e Offline (Custo = $0,00)
    "builtin": {"prompt": 0.0, "completion": 0.0},
    "ollama": {"prompt": 0.0, "completion": 0.0},
    "llama3.2": {"prompt": 0.0, "completion": 0.0},
}

DEFAULT_USD_TO_BRL = 5.80


class CostTracker:
    """Gerencia o rastreamento de tokens, cálculos de FinOps e spans de observabilidade."""

    _spans: List[SpanMetric] = []
    _active_trace_id: str = uuid4().hex
    _usd_to_brl_rate: float = float(os.getenv("USD_TO_BRL_RATE", DEFAULT_USD_TO_BRL))
    _phoenix_endpoint: str = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")

    @classmethod
    def get_active_trace_id(cls) -> str:
        return cls._active_trace_id

    @classmethod
    def new_trace(cls) -> str:
        """Inicia uma nova sessão de rastreamento (trace)."""
        cls._active_trace_id = uuid4().hex
        return cls._active_trace_id

    @classmethod
    def calculate_cost(cls, model: str, prompt_tokens: int, completion_tokens: int) -> CostBreakdown:
        """Calcula o custo da chamada em USD e BRL com base na tabela de preços."""
        model_key = model.lower()
        pricing = None
        for key, p in MODEL_PRICING_PER_1M.items():
            if key in model_key:
                pricing = p
                break

        if not pricing:
            pricing = {"prompt": 0.10, "completion": 0.40}  # padrão de fallback

        cost_usd = (prompt_tokens * pricing["prompt"] / 1_000_000.0) + (
            completion_tokens * pricing["completion"] / 1_000_000.0
        )
        cost_brl = cost_usd * cls._usd_to_brl_rate

        return CostBreakdown(usd=round(cost_usd, 6), brl=round(cost_brl, 4))

    @classmethod
    def record_span(
        cls,
        name: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        persona: Optional[str] = None,
        trace_id: Optional[str] = None,
        status: str = "ok",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SpanMetric:
        """Registra um span de execução com contagem de tokens, custo e latência."""
        total_tokens = prompt_tokens + completion_tokens
        usage = TokenUsage(
            promptTokens=prompt_tokens,
            completionTokens=completion_tokens,
            totalTokens=total_tokens,
        )
        cost = cls.calculate_cost(model, prompt_tokens, completion_tokens)

        span = SpanMetric(
            spanId=uuid4().hex[:12],
            traceId=trace_id or cls._active_trace_id,
            name=name,
            model=model,
            persona=persona,
            latencyMs=round(latency_ms, 2),
            usage=usage,
            cost=cost,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            metadata=metadata or {},
        )

        cls._spans.append(span)
        logger.info(
            f"[FinOps] Span '{name}' registrado: {total_tokens} tokens | "
            f"${cost.usd:.5f} (R$ {cost.brl:.4f}) | {latency_ms:.1f}ms | model={model}"
        )
        return span

    @classmethod
    def get_summary(cls, active_provider: str = "builtin") -> FinOpsSummary:
        """Calcula as métricas totais consolidadas de FinOps para a sessão atual."""
        total_usd = sum(s.cost.usd for s in cls._spans)
        total_brl = sum(s.cost.brl for s in cls._spans)
        total_tokens = sum(s.usage.totalTokens for s in cls._spans)
        total_prompt = sum(s.usage.promptTokens for s in cls._spans)
        total_comp = sum(s.usage.completionTokens for s in cls._spans)

        return FinOpsSummary(
            totalCostUsd=round(total_usd, 6),
            totalCostBrl=round(total_brl, 4),
            totalTokens=total_tokens,
            totalPromptTokens=total_prompt,
            totalCompletionTokens=total_comp,
            totalCalls=len(cls._spans),
            exchangeRateUsdToBrl=cls._usd_to_brl_rate,
            activeProvider=active_provider,
            spans=list(cls._spans),
        )

    @classmethod
    def get_spans(cls, trace_id: Optional[str] = None) -> List[SpanMetric]:
        """Retorna os spans gravados, opcionalmente filtrados por trace_id."""
        if trace_id:
            return [s for s in cls._spans if s.traceId == trace_id]
        return list(cls._spans)

    @classmethod
    def reset(cls) -> None:
        """Limpa os spans registrados e inicia uma nova sessão de rastreamento."""
        cls._spans.clear()
        cls.new_trace()
