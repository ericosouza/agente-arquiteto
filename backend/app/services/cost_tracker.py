"""FinOps and Observability Cost Tracker Service.

Tracks tokens, calculates costs in USD and BRL based on official provider pricing tables,
records spans per stage of the architecture agent, and exposes FinOps summaries.
Compatible with OpenTelemetry and Arize Phoenix / LangSmith local or cloud endpoints.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import uuid4
import os
import logging
from app.models.observability import TokenUsage, CostBreakdown, SpanMetric, FinOpsSummary

logger = logging.getLogger("cost_tracker")

# Pricing table per 1,000,000 (1M) tokens in USD
MODEL_PRICING_PER_1M: Dict[str, Dict[str, float]] = {
    # Google Gemini Models
    "gemini-2.0-flash": {"prompt": 0.10, "completion": 0.40},
    "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "gemini-1.5-pro": {"prompt": 1.25, "completion": 5.00},
    # OpenAI Models
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    # Anthropic Claude Models
    "claude-3-5-sonnet-20241022": {"prompt": 3.00, "completion": 15.00},
    # Local and Offline Engines (Cost = $0.00)
    "builtin": {"prompt": 0.0, "completion": 0.0},
    "ollama": {"prompt": 0.0, "completion": 0.0},
    "llama3.2": {"prompt": 0.0, "completion": 0.0},
}

DEFAULT_USD_TO_BRL = 5.80


class CostTracker:
    """Manages token tracking, FinOps calculations and observability spans."""

    _spans: List[SpanMetric] = []
    _active_trace_id: str = uuid4().hex
    _usd_to_brl_rate: float = float(os.getenv("USD_TO_BRL_RATE", DEFAULT_USD_TO_BRL))
    _phoenix_endpoint: str = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:6006/v1/traces")

    @classmethod
    def get_active_trace_id(cls) -> str:
        return cls._active_trace_id

    @classmethod
    def new_trace(cls) -> str:
        """Starts a new trace session."""
        cls._active_trace_id = uuid4().hex
        return cls._active_trace_id

    @classmethod
    def calculate_cost(cls, model: str, prompt_tokens: int, completion_tokens: int) -> CostBreakdown:
        """Calculates call cost in USD and BRL based on the pricing table."""
        model_key = model.lower()
        pricing = None
        for key, p in MODEL_PRICING_PER_1M.items():
            if key in model_key:
                pricing = p
                break

        if not pricing:
            pricing = {"prompt": 0.10, "completion": 0.40}  # fallback default

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
        """Records an execution span with tokens, cost and latency."""
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
            f"[FinOps] Span '{name}' recorded: {total_tokens} tokens | "
            f"${cost.usd:.5f} (R$ {cost.brl:.4f}) | {latency_ms:.1f}ms | model={model}"
        )
        return span

    @classmethod
    def get_summary(cls, active_provider: str = "builtin") -> FinOpsSummary:
        """Calculates total FinOps metrics for the current session."""
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
        """Returns recorded spans, optionally filtered by trace_id."""
        if trace_id:
            return [s for s in cls._spans if s.traceId == trace_id]
        return list(cls._spans)

    @classmethod
    def reset(cls) -> None:
        """Clears recorded spans and starts a new trace session."""
        cls._spans.clear()
        cls.new_trace()
