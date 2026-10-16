"""Data models for Architectural Proposals (Etapas 2, 3, 4, 5)."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.archimate import ArchiMateLayer, ArchiMateElementType, ArchiMateRelationshipType


class ComponentItem(BaseModel):
    id: str = Field(..., description="Component identifier, e.g. COMP-1")
    name: str = Field(..., description="Name of the component, e.g. Frontend Web")
    category: str = Field(
        ...,
        description="Category: Frontend, Backend, BFF, Database, Cache, Messaging, External, Auth, Observability, Infrastructure"
    )
    responsibility: str = Field(..., description="Primary architectural responsibility")
    suggestedTechnology: str = Field(..., description="Recommended technology stack")
    alternativeTechnology: Optional[str] = Field(default=None, description="Alternative technology option")
    justification: str = Field(..., description="Technical justification for the choice")
    layer: ArchiMateLayer = Field(default=ArchiMateLayer.APPLICATION, description="ArchiMate Layer")
    archimateType: ArchiMateElementType = Field(default=ArchiMateElementType.APPLICATION_COMPONENT, description="ArchiMate Element Type")


class IntegrationItem(BaseModel):
    id: str = Field(..., description="Integration identifier, e.g. INT-1")
    sourceComponentId: str = Field(..., description="Source component ID")
    targetComponentId: str = Field(..., description="Target component ID")
    relationshipType: ArchiMateRelationshipType = Field(
        default=ArchiMateRelationshipType.SERVING,
        description="ArchiMate Relationship Type (Serving, Access, Flow, etc.)"
    )
    protocol: str = Field(default="HTTP/REST", description="Communication protocol/mechanism (e.g. HTTPS, JDBC, AMQP)")
    communicationPattern: str = Field(default="Synchronous", description="Synchronous or Asynchronous")
    purpose: str = Field(..., description="Specific purpose of this integration")


class NonFunctionalRequirement(BaseModel):
    category: str = Field(..., description="Category: Segurança, Escalabilidade, Disponibilidade, Desempenho, Observabilidade")
    description: str = Field(..., description="Requirement description and architecture mitigation")


class ArchitecturalDecision(BaseModel):
    decision: str = Field(..., description="Architectural decision title/topic")
    rationale: str = Field(..., description="Why this decision was chosen instead of alternatives")
    status: str = Field(default="Recomendado", description="Recomendado, Alternativa, or Padrão")


class ArchitectureProposal(BaseModel):
    id: str = Field(..., description="Proposal unique ID")
    title: str = Field(..., description="System Architecture Title")
    summary: str = Field(..., description="Executive architectural summary")
    architecturalStyle: str = Field(
        ...,
        description="e.g. Monolito Modular, BFF com Microsserviços, Arquitetura em Camadas (N-Tier), Event-Driven"
    )
    styleJustification: str = Field(..., description="Justification for why this style was selected (avoiding unnecessary complexity)")
    components: List[ComponentItem] = Field(default_factory=list)
    integrations: List[IntegrationItem] = Field(default_factory=list)
    decisions: List[ArchitecturalDecision] = Field(default_factory=list)
    nonFunctionalRequirements: List[NonFunctionalRequirement] = Field(default_factory=list)
    status: str = Field(default="proposed", description="'proposed', 'modified', 'approved', 'generated'")
    version: int = Field(default=1)
