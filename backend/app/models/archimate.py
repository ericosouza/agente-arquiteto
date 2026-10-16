"""ArchiMate 3.2 Metamodel & Pydantic Schemas.

Complies with The Open Group ArchiMate 3.2 Specification.
Provides structured validation, elements, relationships, layers, and view representations.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ArchiMateLayer(str, Enum):
    BUSINESS = "Business"
    APPLICATION = "Application"
    TECHNOLOGY = "Technology"
    PHYSICAL = "Physical"
    STRATEGY = "Strategy"
    IMPLEMENTATION_MIGRATION = "Implementation_Migration"


class ArchiMateElementType(str, Enum):
    # Business Layer
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

    # Application Layer
    APPLICATION_COMPONENT = "ApplicationComponent"
    APPLICATION_COLLABORATION = "ApplicationCollaboration"
    APPLICATION_INTERFACE = "ApplicationInterface"
    APPLICATION_FUNCTION = "ApplicationFunction"
    APPLICATION_INTERACTION = "ApplicationInteraction"
    APPLICATION_PROCESS = "ApplicationProcess"
    APPLICATION_SERVICE = "ApplicationService"
    DATA_OBJECT = "DataObject"

    # Technology Layer
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

    # Physical Layer
    EQUIPMENT = "Equipment"
    FACILITY = "Facility"
    DISTRIBUTION_NETWORK = "DistributionNetwork"
    MATERIAL = "Material"


class ArchiMateRelationshipType(str, Enum):
    # Structural
    COMPOSITION = "Composition"
    AGGREGATION = "Aggregation"
    ASSIGNMENT = "Assignment"
    REALIZATION = "Realization"

    # Dependency
    SERVING = "Serving"
    ACCESS = "Access"
    INFLUENCE = "Influence"

    # Dynamic
    TRIGGERING = "Triggering"
    FLOW = "Flow"

    # Other
    SPECIALIZATION = "Specialization"
    ASSOCIATION = "Association"


# Layer Color Palette according to ArchiMate standard conventions
LAYER_COLORS = {
    ArchiMateLayer.BUSINESS: {
        "fill": "#FFF9C4",      # Warm pastel yellow
        "stroke": "#FBC02D",    # Deep yellow / amber
        "header": "#FFF59D",
        "text": "#374151"
    },
    ArchiMateLayer.APPLICATION: {
        "fill": "#E1F5FE",      # Light sky blue / cyan
        "stroke": "#0288D1",    # Deep blue
        "header": "#B3E5FC",
        "text": "#0F172A"
    },
    ArchiMateLayer.TECHNOLOGY: {
        "fill": "#E8F5E9",      # Soft pale green
        "stroke": "#388E3C",    # Forest green
        "header": "#C8E6C9",
        "text": "#14532D"
    },
    ArchiMateLayer.PHYSICAL: {
        "fill": "#F1F8E9",      # Olive light green
        "stroke": "#689F38",
        "header": "#DCEDC8",
        "text": "#33691E"
    }
}


class ArchiMateProperty(BaseModel):
    key: str
    value: str


class ArchiMateElement(BaseModel):
    id: str = Field(..., description="Unique identifier (e.g. id-elem-frontend)")
    name: str = Field(..., description="Human-readable name of the element")
    type: ArchiMateElementType = Field(..., description="ArchiMate element type")
    layer: ArchiMateLayer = Field(..., description="ArchiMate architectural layer")
    documentation: Optional[str] = Field(default="", description="Detailed description/responsibility")
    properties: Dict[str, str] = Field(default_factory=dict, description="Key-value properties (technology, responsibility, etc.)")


class ArchiMateRelationship(BaseModel):
    id: str = Field(..., description="Unique identifier (e.g. id-rel-1)")
    name: Optional[str] = Field(default=None, description="Optional label for the relationship")
    type: ArchiMateRelationshipType = Field(..., description="ArchiMate relationship type")
    source: str = Field(..., description="ID of the source element")
    target: str = Field(..., description="ID of the target element")
    documentation: Optional[str] = Field(default="", description="Description of the integration/purpose")
    properties: Dict[str, str] = Field(default_factory=dict, description="Metadata: protocol, communicationPattern, purpose")


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
    identifier: str = Field(..., description="Model unique ID")
    name: str = Field(..., description="System / Solution Name")
    documentation: str = Field(..., description="General overview of the solution architecture")
    version: str = Field(default="3.2", description="ArchiMate specification version")
    metadata: ArchiMateModelMetadata
    elements: List[ArchiMateElement] = Field(default_factory=list)
    relationships: List[ArchiMateRelationship] = Field(default_factory=list)
    views: List[ArchiMateView] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    severity: str = Field(..., description="'error', 'warning', or 'info'")
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
