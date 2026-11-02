"""Observability and FinOps data models for tracking LLM token consumption and costs."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    promptTokens: int = Field(default=0, description="Tokens used in prompt/input")
    completionTokens: int = Field(default=0, description="Tokens used in response/output")
    totalTokens: int = Field(default=0, description="Total tokens consumed")


class CostBreakdown(BaseModel):
    usd: float = Field(default=0.0, description="Cost in US Dollars")
    brl: float = Field(default=0.0, description="Cost converted to Brazilian Reais")


class SpanMetric(BaseModel):
    spanId: str
    traceId: str
    name: str = Field(..., description="Stage name (e.g. scope_guardrail, brainstorm, archimate_generation)")
    model: str
    persona: Optional[str] = None
    latencyMs: float = Field(default=0.0, description="Duration in milliseconds")
    usage: TokenUsage
    cost: CostBreakdown
    timestamp: str
    status: str = Field(default="ok", description="'ok' or 'error'")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class FinOpsSummary(BaseModel):
    totalCostUsd: float = 0.0
    totalCostBrl: float = 0.0
    totalTokens: int = 0
    totalPromptTokens: int = 0
    totalCompletionTokens: int = 0
    totalCalls: int = 0
    exchangeRateUsdToBrl: float = 5.80
    activeProvider: str = "builtin"
    spans: List[SpanMetric] = Field(default_factory=list)
