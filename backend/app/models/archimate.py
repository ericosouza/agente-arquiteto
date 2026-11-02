"""Metamodelo e Schemas Pydantic para ArchiMate 3.2.

Em conformidade com a especificação ArchiMate 3.2 da The Open Group.
Fornece validação estruturada, elementos, relacionamentos, camadas e representações de visualização.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ArchiMateLayer(str, Enum):
    CHANNEL = "Channel"
    BUSINESS = "Business"
    APPLICATION = "Application"
    TECHNOLOGY = "Technology"
    PHYSICAL = "Physical"
    STRATEGY = "Strategy"
    IMPLEMENTATION_MIGRATION = "Implementation_Migration"


class ArchiMateElementType(str, Enum):
    # Camada de Negócios (Business Layer)
    BUSINESS_ACTOR = "BusinessActor"
    BUSINESS_ROLE = "BusinessRole"
    BUSINESS_COLLABORATION = "BusinessCollaboration"
    BUSINESS_INTERFACE = "BusinessInterface"
    BUSINESS_PROCESS = "BusinessProcess"
    BUSINESS_FUNCTION = "BusinessFunction"
    BUSINESS_INTERACTION = "BusinessInteraction"
    BUSINESS_EVENT = "BusinessEvent"
    BUSINESS_SERVICE = "BusinessService"
    BUSINESS_OBJECT = "BusinessObject"
    CONTRACT = "Contract"
    REPRESENTATION = "Representation"

    # Camada de Aplicação (Application Layer)
    APPLICATION_COMPONENT = "ApplicationComponent"
    APPLICATION_COLLABORATION = "ApplicationCollaboration"
    APPLICATION_INTERFACE = "ApplicationInterface"
    APPLICATION_FUNCTION = "ApplicationFunction"
    APPLICATION_INTERACTION = "ApplicationInteraction"
    APPLICATION_PROCESS = "ApplicationProcess"
    APPLICATION_SERVICE = "ApplicationService"
    DATA_OBJECT = "DataObject"

    # Camada de Tecnologia (Technology Layer)
    NODE = "Node"
    DEVICE = "Device"
    SYSTEM_SOFTWARE = "SystemSoftware"
    TECHNOLOGY_COLLABORATION = "TechnologyCollaboration"
    TECHNOLOGY_INTERFACE = "TechnologyInterface"
    PATH = "Path"
    COMMUNICATION_NETWORK = "CommunicationNetwork"
    TECHNOLOGY_FUNCTION = "TechnologyFunction"
    TECHNOLOGY_PROCESS = "TechnologyProcess"
    TECHNOLOGY_INTERACTION = "TechnologyInteraction"
    TECHNOLOGY_EVENT = "TechnologyEvent"
    TECHNOLOGY_SERVICE = "TechnologyService"
    ARTIFACT = "Artifact"

    # Camada Física (Physical Layer)
    EQUIPMENT = "Equipment"
    FACILITY = "Facility"
    DISTRIBUTION_NETWORK = "DistributionNetwork"
    MATERIAL = "Material"


class ArchiMateRelationshipType(str, Enum):
    # Estruturais
    COMPOSITION = "Composition"
    AGGREGATION = "Aggregation"
    ASSIGNMENT = "Assignment"
    REALIZATION = "Realization"

    # Dependência
    SERVING = "Serving"
    ACCESS = "Access"
    INFLUENCE = "Influence"

    # Dinâmicos
    TRIGGERING = "Triggering"
    FLOW = "Flow"

    # Outros
    SPECIALIZATION = "Specialization"
    ASSOCIATION = "Association"


# Paleta de cores das camadas de acordo com as convenções do padrão ArchiMate
LAYER_COLORS = {
    ArchiMateLayer.CHANNEL: {
        "fill": "#FEF3C7",      # Âmbar quente / amarelo para a camada Channel
        "stroke": "#D97706",    # Borda âmbar
        "header": "#FDE68A",
        "text": "#78350F"
    },
    ArchiMateLayer.BUSINESS: {
        "fill": "#FFF9C4",      # Amarelo pastel suave
        "stroke": "#FBC02D",    # Âmbar / amarelo escuro
        "header": "#FFF59D",
        "text": "#374151"
    },
    ArchiMateLayer.APPLICATION: {
        "fill": "#E1F5FE",      # Azul céu claro / ciano
        "stroke": "#0288D1",    # Azul profundo
        "header": "#B3E5FC",
        "text": "#0F172A"
    },
    ArchiMateLayer.TECHNOLOGY: {
        "fill": "#E8F5E9",      # Verde pálido suave
        "stroke": "#388E3C",    # Verde floresta
        "header": "#C8E6C9",
        "text": "#14532D"
    },
    ArchiMateLayer.PHYSICAL: {
        "fill": "#F1F8E9",      # Verde oliva suave
        "stroke": "#689F38",
        "header": "#DCEDC8",
        "text": "#33691E"
    }
}


class ArchiMateProperty(BaseModel):
    key: str
    value: str


class ArchiMateElement(BaseModel):
    id: str = Field(..., description="Identificador único (ex: id-elem-frontend)")
    name: str = Field(..., description="Nome legível por humanos do elemento")
    type: ArchiMateElementType = Field(..., description="Tipo do elemento ArchiMate")
    layer: ArchiMateLayer = Field(..., description="Camada arquitetural do ArchiMate")
    documentation: Optional[str] = Field(default="", description="Descrição detalhada e responsabilidade")
    properties: Dict[str, str] = Field(default_factory=dict, description="Propriedades chave-valor (tecnologia, papel, etc.)")


class ArchiMateRelationship(BaseModel):
    id: str = Field(..., description="Identificador único (ex: id-rel-1)")
    name: Optional[str] = Field(default=None, description="Rótulo opcional para o relacionamento")
    type: ArchiMateRelationshipType = Field(..., description="Tipo do relacionamento ArchiMate")
    source: str = Field(..., description="ID do elemento de origem")
    target: str = Field(..., description="ID do elemento de destino")
    documentation: Optional[str] = Field(default="", description="Descrição da integração e propósito")
    properties: Dict[str, str] = Field(default_factory=dict, description="Metadados: protocolo, padrão de comunicação, finalidade")


class ArchiMateViewNode(BaseModel):
    elementId: str
    x: float
    y: float
    width: float
    height: float


class ArchiMateViewConnection(BaseModel):
    relationshipId: str
    sourceId: str
    targetId: str
    bendpoints: List[Dict[str, float]] = Field(default_factory=list)


class ArchiMateView(BaseModel):
    id: str
    name: str
    documentation: Optional[str] = ""
    nodes: List[ArchiMateViewNode] = Field(default_factory=list)
    connections: List[ArchiMateViewConnection] = Field(default_factory=list)


class ArchiMateModelMetadata(BaseModel):
    author: str = "AI Software Architecture Designer"
    createdAt: str
    standard: str = "The Open Group ArchiMate 3.2 Specification"
    description: Optional[str] = None
    architecturalStyle: Optional[str] = None


class ArchiMateModel(BaseModel):
    identifier: str = Field(..., description="Identificador único do modelo")
    name: str = Field(..., description="Nome do Sistema / Solução")
    documentation: str = Field(..., description="Visão geral da arquitetura da solução")
    version: str = Field(default="3.2", description="Versão da especificação ArchiMate")
    metadata: ArchiMateModelMetadata
    elements: List[ArchiMateElement] = Field(default_factory=list)
    relationships: List[ArchiMateRelationship] = Field(default_factory=list)
    views: List[ArchiMateView] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    severity: str = Field(..., description="'error', 'warning' ou 'info'")
    code: str
    message: str
    elementId: Optional[str] = None
    relationshipId: Optional[str] = None


class ValidationReport(BaseModel):
    isValid: bool
    totalElements: int
    totalRelationships: int
    errors: List[ValidationIssue] = Field(default_factory=list)
    warnings: List[ValidationIssue] = Field(default_factory=list)
    info: List[ValidationIssue] = Field(default_factory=list)
    summary: str
