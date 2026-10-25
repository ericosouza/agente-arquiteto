"""Tests for Architect Agent workflow (Etapas 1-8), Prerequisites, Naming Standard, and Refinement."""

import pytest
from app.services.architect_agent import ArchitectAgent
from app.models.proposal import ArchitectureProposal, PrerequisitesInfo


def test_extract_prerequisites_incomplete_and_complete():
    # Incomplete prompt should identify missing fields
    incomplete_text = "Quero criar um sistema de risco ambiental com Spring Boot"
    prereq = ArchitectAgent.extract_prerequisites(incomplete_text)
    assert prereq.is_complete is False
    missing = prereq.missing_fields()
    assert "Qual iniciativa?" in missing
    assert "Qual Sigla do projeto?" in missing
    assert "Qual feature?" in missing
    assert "Qual ARQCOR?" in missing

    # Complete prompt with all 4 items
    complete_text = (
        "Iniciativa: Sustentabilidade ESG\n"
        "Sigla: SESG\n"
        "Feature: Risco Ambiental\n"
        "ARQCOR: ARQ-2026\n"
        "Sistema em Java Spring Boot com Angular."
    )
    prereq_ok = ArchitectAgent.extract_prerequisites(complete_text)
    assert prereq_ok.is_complete is True
    assert prereq_ok.sigla == "sesg"
    assert prereq_ok.iniciativa == "Sustentabilidade ESG"
    assert prereq_ok.feature == "Risco Ambiental"
    assert prereq_ok.arqcor == "ARQ-2026"


@pytest.mark.asyncio
async def test_agent_component_naming_standard():
    description = (
        "Iniciativa: Sustentabilidade\n"
        "Sigla: SESG\n"
        "Feature: Risco Ambiental\n"
        "ARQCOR: ARQ-100\n"
        "Preciso de um sistema em Spring Boot Java com Angular."
    )
    prereq = ArchitectAgent.extract_prerequisites(description)
    proposal = await ArchitectAgent.analyze_and_propose(description, prerequisites=prereq)

    assert isinstance(proposal, ArchitectureProposal)
    comp_names = [c.name for c in proposal.components]

    # Must contain the exact pattern requested: [sigla-tecnologia]-[sigla-sistema]-[modulo]-[tipo]-[dominio]
    assert "sboot-sesg-base-atom-risco-ambiental" in comp_names
    assert "sboot-sesg-base-bff-risco-ambiental" in comp_names
    assert "ng-sesg-base-risco-ambiental" in comp_names


@pytest.mark.asyncio
async def test_agent_portal_esg_smart_domains_channel_layer_and_mysql():
    description = (
        "preciso criar um portal web para cadastro de questões do sistema ESG para clientes do banco. "
        "O sistema deve armazenar questoes e respostas do cliente para no futuro eu gerar um relatorio.\n"
        "Iniciativa: ESG\n"
        "Sigla: SESG\n"
        "Feature: feat\n"
        "ARQCOR: ARQ-01"
    )
    prereq = ArchitectAgent.extract_prerequisites(description)
    proposal = await ArchitectAgent.analyze_and_propose(description, prerequisites=prereq)

    comp_map = {c.name: c for c in proposal.components}

    # Frontend & BFF must use 'portal-esg', while atomic uses 'sistema-esg'
    assert "ng-sesg-base-portal-esg" in comp_map
    assert "sboot-sesg-base-bff-portal-esg" in comp_map
    assert "sboot-sesg-base-atom-sistema-esg" in comp_map

    # Frontend must be in Channel layer
    fe_comp = comp_map["ng-sesg-base-portal-esg"]
    assert fe_comp.layer.value == "Channel"

    # Database must always be MySQL
    db_comp = next((c for c in proposal.components if c.category == "Database"), None)
    assert db_comp is not None
    assert db_comp.suggestedTechnology == "MySQL"

    # Model & SVG must contain Channel Layer and NOT contain Business Layer / Business Actor
    model, svg, validation = ArchitectAgent.generate_archimate_model_from_proposal(proposal)
    assert validation.isValid is True
    assert "Channel Layer" in svg
    assert "Business Layer" not in svg
    assert all(e.id != "ACTOR-USER" for e in model.elements)


@pytest.mark.asyncio
async def test_agent_refine_proposal_updates_components_and_diagram():
    description = (
        "Iniciativa: Sustentabilidade\n"
        "Sigla: SESG\n"
        "Feature: Risco Ambiental\n"
        "ARQCOR: ARQ-100"
    )
    prereq = ArchitectAgent.extract_prerequisites(description)
    proposal = await ArchitectAgent.analyze_and_propose(description, prerequisites=prereq)

    # Refine to add pubsub, gcs, genaigke and switch frontend to streamlit
    feedback = "Troque o frontend para streamlit e adicione pubsub, bucket gcs e agente genaigke"
    refined = await ArchitectAgent.refine_proposal(proposal, feedback)

    assert refined.version > proposal.version
    names = [c.name for c in refined.components]
    assert any(n.startswith("streamlit-sesg-base-") for n in names)
    assert any(n.startswith("pubsub-sesg-base-") for n in names)
    assert any(n.startswith("gcs-sesg-base-") for n in names)
    assert any(n.startswith("genaigke-sesg-base-") for n in names)

    model, svg, validation = ArchitectAgent.generate_archimate_model_from_proposal(refined)
    assert validation.isValid is True
    assert "streamlit-sesg-base-" in svg
    assert "pubsub-sesg-base-" in svg
    assert "gcs-sesg-base-" in svg
    assert "genaigke-sesg-base-" in svg
