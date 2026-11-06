"""Modelos de dados de Observabilidade e FinOps para monitoramento de consumo de tokens e custos de LLM."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    promptTokens: int = Field(default=0, description="Tokens utilizados no prompt de entrada")
    completionTokens: int = Field(default=0, description="Tokens utilizados na resposta/saída")
    totalTokens: int = Field(default=0, description="Total de tokens consumidos")


class CostBreakdown(BaseModel):
    usd: float = Field(default=0.0, description="Custo em Dólares Americanos (USD)")
    brl: float = Field(default=0.0, description="Custo convertido para Reais Brasileiros (BRL)")


class SpanMetric(BaseModel):
    spanId: str
    traceId: str
    name: str = Field(..., description="Nome da etapa (ex: scope_guardrail, brainstorm, archimate_generation)")
    model: str
    persona: Optional[str] = None
    latencyMs: float = Field(default=0.0, description="Duração da chamada em milissegundos")
    usage: TokenUsage
    cost: CostBreakdown
    timestamp: str
    status: str = Field(default="ok", description="'ok' ou 'error'")
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
