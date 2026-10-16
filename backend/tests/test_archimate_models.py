"""Tests for ArchiMate models and serialization."""

import pytest
from app.models.archimate import (
    ArchiMateLayer,
    ArchiMateElementType,
    ArchiMateRelationshipType,
    ArchiMateElement,
    ArchiMateRelationship,
    ArchiMateModel,
    ArchiMateModelMetadata,
)


def test_archimate_element_creation():
    elem = ArchiMateElement(
        id="elem-1",
        name="Catálogo de Produtos",
        type=ArchiMateElementType.APPLICATION_COMPONENT,
        layer=ArchiMateLayer.APPLICATION,
        documentation="Responsável por gerenciar o ciclo de vida dos produtos.",
        properties={"technology": "FastAPI", "responsibility": "Gerenciamento de produtos"},
    )

    assert elem.id == "elem-1"
    assert elem.type == ArchiMateElementType.APPLICATION_COMPONENT
    assert elem.layer == ArchiMateLayer.APPLICATION
    assert elem.properties["technology"] == "FastAPI"


def test_archimate_relationship_creation():
    rel = ArchiMateRelationship(
        id="rel-1",
        name="HTTP/REST",
        type=ArchiMateRelationshipType.SERVING,
        source="elem-1",
        target="elem-2",
        documentation="Disponibiliza operações de CRUD para o cliente.",
        properties={"protocol": "HTTPS", "communicationPattern": "Synchronous"},
    )

    assert rel.id == "rel-1"
    assert rel.type == ArchiMateRelationshipType.SERVING
    assert rel.source == "elem-1"
    assert rel.target == "elem-2"


def test_archimate_model_creation():
    model = ArchiMateModel(
        identifier="model-test-01",
        name="Sistema de Produtos",
        documentation="Arquitetura de catálogo",
        version="3.2",
        metadata=ArchiMateModelMetadata(
            author="Architect Agent",
            createdAt="2026-10-09T10:00:00Z",
            standard="The Open Group ArchiMate 3.2 Specification",
        ),
        elements=[
            ArchiMateElement(
                id="elem-fe",
                name="Frontend Web",
                type=ArchiMateElementType.APPLICATION_COMPONENT,
                layer=ArchiMateLayer.APPLICATION,
            ),
            ArchiMateElement(
                id="elem-be",
                name="Backend API",
                type=ArchiMateElementType.APPLICATION_COMPONENT,
                layer=ArchiMateLayer.APPLICATION,
            ),
        ],
        relationships=[
            ArchiMateRelationship(
                id="rel-fe-be",
                type=ArchiMateRelationshipType.SERVING,
                source="elem-be",
                target="elem-fe",
            )
        ],
    )

    assert model.identifier == "model-test-01"
    assert len(model.elements) == 2
    assert len(model.relationships) == 1
    assert model.version == "3.2"
