"""Request and response models for Agent Chat and Workflow Interactions."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.proposal import ArchitectureProposal, PrerequisitesInfo
from app.models.archimate import ArchiMateModel, ValidationReport
from app.models.persona import PersonaType


class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str
    timestamp: Optional[str] = None


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1, description="Natural language description of the requested system")
    constraints: Optional[List[str]] = Field(default_factory=list, description="Optional constraints or preferences")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Conversation history for multi-turn prerequisite collection")
    prerequisites: Optional[PrerequisitesInfo] = Field(default=None, description="Accumulated or explicit project prerequisites")
    persona: Optional[PersonaType] = Field(default=PersonaType.ARQUITETO, description="Selected persona: 'arquiteto' or 'engenheiro'")


class BrainstormRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message during the brainstorming/refinement phase")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Conversation history of the brainstorm")
    prerequisites: Optional[PrerequisitesInfo] = Field(default=None, description="Confirmed project prerequisites (Sigla, Feature, ARQCOR)")
    persona: Optional[PersonaType] = Field(default=PersonaType.ARQUITETO, description="Selected persona")


class BrainstormResponse(BaseModel):
    reply: str
    isReadyForModeling: bool = Field(default=False, description="True if the user agreed to proceed to model generation ('Ok?')")
    prerequisites: Optional[PrerequisitesInfo] = None
    persona: PersonaType = PersonaType.ARQUITETO
    ragSourcesUsed: Optional[List[str]] = Field(default_factory=list)


class RefineRequest(BaseModel):
    proposal: ArchitectureProposal = Field(..., description="Current proposal to be refined")
    feedback: str = Field(..., min_length=2, description="User instruction, e.g. 'mudar banco para MySQL'")
    persona: Optional[PersonaType] = Field(default=PersonaType.ARQUITETO, description="Selected persona")


class ApproveRequest(BaseModel):
    proposal: ArchitectureProposal = Field(..., description="The user-approved architecture proposal")


class ChatResponse(BaseModel):
    message: str
    inScope: bool = Field(default=True, description="False if request is rejected by the scope guardrail")
    proposal: Optional[ArchitectureProposal] = None
    validation: Optional[ValidationReport] = None
    archimateModel: Optional[ArchiMateModel] = None
    diagramSvg: Optional[str] = None
    prerequisites: Optional[PrerequisitesInfo] = None
    missingPrerequisites: Optional[List[str]] = None
    persona: Optional[PersonaType] = PersonaType.ARQUITETO
