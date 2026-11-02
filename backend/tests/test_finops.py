"""Tests for FinOps and Observability Cost Tracker."""

import types
from app.services.cost_tracker import CostTracker
from app.models.observability import CostBreakdown, FinOpsSummary
from app.api.routes import get_finops_summary, get_finops_traces, reset_finops


def run_sync(coro):
    stack = [coro]
    result = None
    while stack:
        current = stack[-1]
        try:
            val = current.send(None)
            if isinstance(val, types.CoroutineType):
                stack.append(val)
        except StopIteration as e:
            stack.pop()
            if stack:
                try:
                    val2 = stack[-1].send(e.value)
                    if isinstance(val2, types.CoroutineType):
                        stack.append(val2)
                except StopIteration as e2:
                    stack.pop()
                    if not stack:
                        result = e2.value
            else:
                result = e.value
    return result


def test_cost_tracker_calculation():
    # 1,000,000 prompt tokens of gemini-2.0-flash is $0.10
    # 1,000,000 completion tokens is $0.40
    cost = CostTracker.calculate_cost("gemini-2.0-flash", 1_000_000, 1_000_000)
    assert round(cost.usd, 2) == 0.50
    assert cost.brl > 2.0  # 0.50 * 5.80 = ~2.90

    # Builtin cost should be $0.00
    free_cost = CostTracker.calculate_cost("builtin", 50_000, 50_000)
    assert free_cost.usd == 0.0
    assert free_cost.brl == 0.0


def test_cost_tracker_record_and_summary():
    CostTracker.reset()
    assert len(CostTracker.get_spans()) == 0

    span1 = CostTracker.record_span(
        name="test_scope",
        model="gemini-2.0-flash",
        prompt_tokens=500,
        completion_tokens=50,
        latency_ms=120.0,
        persona="arquiteto",
    )
    assert span1.usage.totalTokens == 550
    assert span1.cost.usd > 0.0

    summary = CostTracker.get_summary(active_provider="gemini")
    assert summary.totalCalls == 1
    assert summary.totalTokens == 550
    assert summary.totalCostUsd > 0.0


def test_finops_api_endpoints():
    CostTracker.reset()

    # Call summary endpoint
    summary = run_sync(get_finops_summary())
    assert isinstance(summary, FinOpsSummary)
    assert summary.totalCalls == 0

    # Record a span
    CostTracker.record_span(
        name="test_api_span",
        model="gemini-2.0-flash",
        prompt_tokens=1000,
        completion_tokens=200,
        latency_ms=250.0,
    )

    summary2 = run_sync(get_finops_summary())
    assert summary2.totalCalls == 1
    assert summary2.totalTokens == 1200

    # Call traces endpoint
    traces = run_sync(get_finops_traces())
    assert len(traces) == 1
    assert traces[0].name == "test_api_span"

    # Reset
    res_reset = run_sync(reset_finops())
    assert res_reset["status"] == "ok"
    summary3 = run_sync(get_finops_summary())
    assert summary3.totalCalls == 0
