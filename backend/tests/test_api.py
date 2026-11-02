"""Tests for FastAPI endpoints: Scope Guardrail, Prerequisites (Sigla, Feature, ARQCOR),
Personas, Brainstorm RAG, Model Generation and XML/JSON Exporters.
"""

import types
import pytest
from app.api.routes import (
    get_system_info,
    check_scope,
    brainstorm_architecture,
    analyze_architecture,
    refine_architecture,
    approve_architecture,
    export_json,
    export_xml,
)
from app.models.chat import (
    AnalyzeRequest,
    BrainstormRequest,
    RefineRequest,
    ApproveRequest,
)
from app.models.persona import PersonaType


def run_sync(coro):
    """Executes a coroutine chain synchronously in environments where loopback socketpair is restricted."""
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


def test_api_info_endpoint():
    data = run_sync(get_system_info())
    assert "activeProvider" in data
    assert "providers" in data
    assert "builtin" in data["providers"]
    assert data["providers"]["builtin"]["configured"] is True


def test_api_scope_guardrail_blocks_out_of_scope():
    req = AnalyzeRequest(description="Qual a receita de bolo de chocolate?")
    res = run_sync(check_scope(req))
    assert res["inScope"] is False
    assert "escopo" in res["refusalMessage"].lower()


def test_api_scope_guardrail_allows_in_scope():
    req = AnalyzeRequest(description="Gostaria de criar um sistema com backend em Spring Boot e mensageria PubSub")
    res = run_sync(check_scope(req))
    assert res["inScope"] is True
    assert res["refusalMessage"] is None


def test_api_brainstorm_endpoint():
    req = BrainstormRequest(
        message="Como arquitetar a esteira de mensageria para a feature de risco?",
        persona=PersonaType.ARQUITETO,
        history=[],
    )
    res = run_sync(brainstorm_architecture(req))
    assert res.reply is not None
    assert len(res.reply) > 20
    assert res.persona == PersonaType.ARQUITETO
    assert len(res.ragSourcesUsed) > 0

    # Test confirmation with 'Ok'
    req_ok = BrainstormRequest(
        message="Ok, pode prosseguir para a modelagem!",
        persona=PersonaType.ENGENHEIRO,
        history=[{"role": "assistant", "content": "Proposta de esteira apresentada."}],
    )
    res_ok = run_sync(brainstorm_architecture(req_ok))
    assert res_ok.isReadyForModeling is True


def test_api_analyze_blocks_without_prerequisites():
    req = AnalyzeRequest(
        description="Quero desenvolver um sistema web de cadastro de produtos.",
        constraints=[],
    )
    res = run_sync(analyze_architecture(req))
    assert res.proposal is None
    assert len(res.missingPrerequisites) == 3
    assert "Qual Sigla do projeto?" in res.message
    assert "Qual feature?" in res.message
    assert "Qual ARQCOR?" in res.message


def test_api_analyze_refine_approve_and_export_flow():
    # 1. Analyze with the 3 mandatory prerequisites
    req_analyze = AnalyzeRequest(
        description=(
            "Sigla: SESG\n"
            "Feature: Risco Ambiental\n"
            "ARQCOR: ARQ-2026\n"
            "Sistema web em Spring Boot e Angular."
        ),
        constraints=[],
        persona=PersonaType.ARQUITETO,
    )
    res_analyze = run_sync(analyze_architecture(req_analyze))
    assert res_analyze.proposal is not None
    assert res_analyze.diagramSvg is not None
    assert "sboot-sesg-base-atom-risco-ambiental" in res_analyze.diagramSvg
    proposal = res_analyze.proposal

    # 2. Refine proposal
    req_refine = RefineRequest(
        proposal=proposal,
        feedback="Adicione um spring batch (sbatch) e um pubsub para eventos",
        persona=PersonaType.ENGENHEIRO,
    )
    res_refine = run_sync(refine_architecture(req_refine))
    refined_proposal = res_refine.proposal
    assert len(refined_proposal.components) > len(proposal.components)
    assert "sbatch-sesg-base-" in res_refine.diagramSvg
    assert "pubsub-sesg-base-" in res_refine.diagramSvg

    # 3. Approve proposal
    req_approve = ApproveRequest(proposal=refined_proposal)
    res_approve = run_sync(approve_architecture(req_approve))
    assert res_approve.archimateModel is not None
    assert res_approve.diagramSvg is not None
    assert "<svg" in res_approve.diagramSvg
    assert res_approve.validation.isValid is True

    # 4. Export JSON & XML
    model = res_approve.archimateModel
    json_response = run_sync(export_json(model))
    assert json_response.media_type == "application/json"
    assert b"elements" in json_response.body

    xml_response = run_sync(export_xml(model))
    assert xml_response.media_type == "application/xml"
    assert b"<?xml" in xml_response.body
    assert b"http://www.opengroup.org/xsd/archimate/3.0/" in xml_response.body
