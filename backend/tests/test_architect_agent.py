"""Tests for Architect Agent workflow (Etapas 1-8)."""

import pytest
from app.services.architect_agent import ArchitectAgent
from app.models.proposal import ArchitectureProposal


@pytest.mark.asyncio
async def test_agent_analyze_product_catalog():
    description = (
        "Quero desenvolver um sistema web para cadastro, consulta, alteração e exclusão de produtos. "
        "O sistema deve permitir que usuários pesquisem produtos por nome, categoria e preço."
    )

    proposal = await ArchitectAgent.analyze_and_propose(description)

    assert isinstance(proposal, ArchitectureProposal)
    assert proposal.status == "proposed"
    assert len(proposal.components) >= 3
    assert len(proposal.integrations) >= 2

    # Check component categories
    categories = [c.category for c in proposal.components]
    assert "Frontend" in categories
    assert "Backend" in categories or "BFF" in categories
    assert "Database" in categories

    # Check non-functional requirements
    assert len(proposal.nonFunctionalRequirements) >= 3

    # Check architectural decisions
    assert len(proposal.decisions) >= 2


@pytest.mark.asyncio
async def test_agent_refine_proposal():
    description = "Sistema web de produtos simples"
    proposal = await ArchitectAgent.analyze_and_propose(description)

    # Refine to change database to MongoDB and add Redis
    feedback = "Mude o banco de dados para MongoDB e adicione Redis para cache"
    refined = await ArchitectAgent.refine_proposal(proposal, feedback)

    assert refined.version > proposal.version
    db_comp = next((c for c in refined.components if c.category == "Database"), None)
    assert db_comp is not None
    assert "MongoDB" in db_comp.suggestedTechnology

    cache_comp = next((c for c in refined.components if c.category == "Cache"), None)
    assert cache_comp is not None
    assert "Redis" in cache_comp.suggestedTechnology


@pytest.mark.asyncio
async def test_agent_generate_model_diagram_and_validation():
    description = "Sistema web simples de cadastro de produtos"
    proposal = await ArchitectAgent.analyze_and_propose(description)

    model, svg, validation = ArchitectAgent.generate_archimate_model_from_proposal(proposal)

    assert model.identifier is not None
    assert len(model.elements) >= len(proposal.components)
    assert len(model.relationships) >= len(proposal.integrations)

    # SVG validation
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "ArchiMate" in svg or "Notação Oficial" in svg

    # Metamodel validation
    assert validation.isValid is True
    assert len(validation.errors) == 0
