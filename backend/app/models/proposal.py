"""Modelos de dados para Propostas de Arquitetura (Etapas 2, 3, 4, 5)."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.archimate import ArchiMateLayer, ArchiMateElementType, ArchiMateRelationshipType


class PrerequisitesInfo(BaseModel):
    sigla: Optional[str] = Field(default=None, description="Qual Sigla do projeto? (4 letras)")
    feature: Optional[str] = Field(default=None, description="Qual feature?")
    arqcor: Optional[str] = Field(default=None, description="Qual ARQCOR?")
    iniciativa: Optional[str] = Field(default=None, description="Iniciativa (opcional)")

    @property
    def is_complete(self) -> bool:
        return len(self.missing_fields()) == 0

    def missing_fields(self) -> List[str]:
        missing = []
        if not self.sigla or len(self.sigla.strip()) != 4 or not self.sigla.strip().isalpha():
            missing.append("Qual Sigla do projeto?")
        if not self.feature or not self.feature.strip():
            missing.append("Qual feature?")
        if not self.arqcor or not self.arqcor.strip():
            missing.append("Qual ARQCOR?")
        return missing


class ComponentItem(BaseModel):
    id: str = Field(..., description="Identificador do componente, ex: COMP-1")
    name: str = Field(..., description="Nome do componente, ex: Frontend Web")
    category: str = Field(
        ...,
        description="Categoria: Frontend, Backend, BFF, Database, Cache, Messaging, External, Auth, Observability, Infrastructure"
    )
    responsibility: str = Field(..., description="Responsabilidade arquitetural primária")
    suggestedTechnology: str = Field(..., description="Stack tecnológica recomendada")
    alternativeTechnology: Optional[str] = Field(default=None, description="Opção tecnológica alternativa")
    justification: str = Field(..., description="Justificativa técnica para a escolha")
    layer: ArchiMateLayer = Field(default=ArchiMateLayer.APPLICATION, description="Camada ArchiMate")
    archimateType: ArchiMateElementType = Field(default=ArchiMateElementType.APPLICATION_COMPONENT, description="Tipo de Elemento ArchiMate")


class IntegrationItem(BaseModel):
    id: str = Field(..., description="Identificador da integração, ex: INT-1")
    sourceComponentId: str = Field(..., description="ID do componente de origem")
    targetComponentId: str = Field(..., description="ID do componente de destino")
    relationshipType: ArchiMateRelationshipType = Field(
        default=ArchiMateRelationshipType.SERVING,
        description="Tipo de Relacionamento ArchiMate (Serving, Access, Flow, etc.)"
    )
    protocol: str = Field(default="HTTP/REST", description="Protocolo/mecanismo de comunicação (ex: HTTPS, JDBC, AMQP)")
    communicationPattern: str = Field(default="Synchronous", description="Síncrono ou Assíncrono")
    purpose: str = Field(..., description="Finalidade específica desta integração")


class NonFunctionalRequirement(BaseModel):
    category: str = Field(..., description="Categoria: Segurança, Escalabilidade, Disponibilidade, Desempenho, Observabilidade")
    description: str = Field(..., description="Descrição do requisito e mitigação na arquitetura")


class ArchitecturalDecision(BaseModel):
    decision: str = Field(..., description="Título/tema da decisão arquitetural")
    rationale: str = Field(..., description="Por que esta decisão foi escolhida em vez das alternativas")
    status: str = Field(default="Recomendado", description="Recomendado, Alternativa ou Padrão")


class ArchitectureProposal(BaseModel):
    id: str = Field(..., description="ID único da proposta")
    title: str = Field(..., description="Título da Arquitetura do Sistema")
    summary: str = Field(..., description="Resumo executivo da arquitetura")
    architecturalStyle: str = Field(
        ...,
        description="ex: Monolito Modular, BFF com Microsserviços, Arquitetura em Camadas (N-Tier), Event-Driven"
    )
    styleJustification: str = Field(..., description="Justificativa da escolha do estilo (evitando complexidade acidental)")
    components: List[ComponentItem] = Field(default_factory=list)
    integrations: List[IntegrationItem] = Field(default_factory=list)
    decisions: List[ArchitecturalDecision] = Field(default_factory=list)
    nonFunctionalRequirements: List[NonFunctionalRequirement] = Field(default_factory=list)
    prerequisites: Optional[PrerequisitesInfo] = Field(default=None, description="Pré-requisitos do projeto (Sigla, Feature, ARQCOR)")
    status: str = Field(default="proposed", description="'proposed', 'modified', 'approved', 'generated'")
    version: int = Field(default=1)
