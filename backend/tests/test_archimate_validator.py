"""Tests for ArchiMate automated validator (Etapa 8)."""

import pytest
from app.models.archimate import (
    ArchiMateModel,
    ArchiMateModelMetadata,
    ArchiMateElement,
    ArchiMateRelationship,
    ArchiMateLayer,
    ArchiMateElementType,
    ArchiMateRelationshipType,
)
from app.services.archimate_validator import ArchiMateValidator


@pytest.fixture
def valid_archimate_model():
    return ArchiMateModel(
        identifier="model-valid",
        name="Sistema Válido",
        documentation="Documentação válida",
        version="3.2",
        metadata=ArchiMateModelMetadata(
            author="Test",
            createdAt="2026-10-09T10:00:00Z",
        ),
        elements=[
            ArchiMateElement(
                id="ELEM-1",
                name="Frontend Web",
                type=ArchiMateElementType.APPLICATION_COMPONENT,
                layer=ArchiMateLayer.APPLICATION,
            ),
            ArchiMateElement(
                id="ELEM-2",
                name="Backend API",
                type=ArchiMateElementType.APPLICATION_COMPONENT,
                layer=ArchiMateLayer.APPLICATION,
            ),
            ArchiMateElement(
                id="ELEM-3",
                name="Banco PostgreSQL",
                type=ArchiMateElementType.SYSTEM_SOFTWARE,
                layer=ArchiMateLayer.TECHNOLOGY,
            ),
        ],
        relationships=[
            ArchiMateRelationship(
                id="REL-1",
                type=ArchiMateRelationshipType.SERVING,
                source="ELEM-2",
                target="ELEM-1",
            ),
            ArchiMateRelationship(
                id="REL-2",
                type=ArchiMateRelationshipType.SERVING,
                source="ELEM-3",
                target="ELEM-2",
            ),
        ],
    )


def test_validator_passes_valid_model(valid_archimate_model):
    report = ArchiMateValidator.validate_model(valid_archimate_model)
    assert report.isValid is True
    assert len(report.errors) == 0
    assert report.totalElements == 3
    assert report.totalRelationships == 2


def test_validator_detects_duplicate_element_id(valid_archimate_model):
    # Add an element with duplicate ID
    valid_archimate_model.elements.append(
        ArchiMateElement(
            id="ELEM-1",  # duplicate ID
            name="Outro Frontend",
            type=ArchiMateElementType.APPLICATION_COMPONENT,
            layer=ArchiMateLayer.APPLICATION,
        )
    )

    report = ArchiMateValidator.validate_model(valid_archimate_model)
    assert report.isValid is False
    assert any(err.code == "DUPLICATE_ELEMENT_ID" for err in report.errors)


def test_validator_detects_dangling_relationship_source(valid_archimate_model):
    valid_archimate_model.relationships.append(
        ArchiMateRelationship(
            id="REL-DANGLING",
            type=ArchiMateRelationshipType.SERVING,
            source="ELEM-GHOST",  # Non-existent ID
            target="ELEM-1",
        )
    )

    report = ArchiMateValidator.validate_model(valid_archimate_model)
    assert report.isValid is False
    assert any(err.code == "DANGLING_RELATIONSHIP_SOURCE" for err in report.errors)


def test_validator_detects_dangling_relationship_target(valid_archimate_model):
    valid_archimate_model.relationships.append(
        ArchiMateRelationship(
            id="REL-DANGLING-TGT",
            type=ArchiMateRelationshipType.SERVING,
            source="ELEM-1",
            target="ELEM-GHOST-TGT",  # Non-existent target
        )
    )

    report = ArchiMateValidator.validate_model(valid_archimate_model)
    assert report.isValid is False
    assert any(err.code == "DANGLING_RELATIONSHIP_TARGET" for err in report.errors)
