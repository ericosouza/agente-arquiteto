"""Tests for Flowchart Adherence: Scope Guardrail, Prerequisites, Personas and RAG."""

from app.services.scope_guardrail import ScopeGuardrail
from app.services.architecture_rag import ArchitectureRAGService
from app.models.persona import PersonaType
from app.models.proposal import PrerequisitesInfo


def test_scope_guardrail_in_scope():
    is_in, msg = ScopeGuardrail.check_scope_sync("Gostaria de criar um sistema com backend em Spring Boot e mensageria PubSub")
    assert is_in is True
    assert msg is None


def test_scope_guardrail_out_of_scope():
    is_in, msg = ScopeGuardrail.check_scope_sync("Qual a receita de bolo de chocolate?")
    assert is_in is False
    assert msg is not None
    assert "escopo" in msg.lower()


def test_prerequisites_check():
    prereq = PrerequisitesInfo(sigla="SESG", feature="Calculo de Risco", arqcor="ARQ-100")
    assert prereq.is_complete is True
    assert len(prereq.missing_fields()) == 0

    incomplete = PrerequisitesInfo(sigla="SESG", feature=None, arqcor=None)
    assert incomplete.is_complete is False
    assert len(incomplete.missing_fields()) == 2


def test_architecture_rag_search():
    chunks = ArchitectureRAGService.search("Spring Boot sboot backend", top_k=2)
    assert len(chunks) > 0
    assert any("catalogo" in c["source"] or "nomenclatura" in c["source"] for c in chunks)


def test_persona_types():
    assert PersonaType.ARQUITETO == "arquiteto"
    assert PersonaType.ENGENHEIRO == "engenheiro"
