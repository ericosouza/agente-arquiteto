"""Request and response models for Agent Chat and Workflow Interactions."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.proposal import ArchitectureProposal, PrerequisitesInfo
from app.models.archimate import ArchiMateModel, ValidationReport


class ChatMessage(BaseModel):
    id: str
    role: str = Field(..., description="'user', 'assistant', or 'system'")
    content: str
    timestamp: str


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1, description="Natural language description of the requested system")
    constraints: Optional[List[str]] = Field(default_factory=list, description="Optional constraints or preferences")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Conversation history for multi-turn prerequisite collection")
    prerequisites: Optional[PrerequisitesInfo] = Field(default=None, description="Accumulated or explicit project prerequisites")


class RefineRequest(BaseModel):
    proposal: ArchitectureProposal = Field(..., description="Current proposal to be refined")
    feedback: str = Field(..., min_length=2, description="User instruction, e.g. 'mudar banco para MySQL'")


class ApproveRequest(BaseModel):
    proposal: ArchitectureProposal = Field(..., description="The user-approved architecture proposal")


class ChatResponse(BaseModel):
    message: str
    proposal: Optional[ArchitectureProposal] = None
    validation: Optional[ValidationReport] = None
    archimateModel: Optional[ArchiMateModel] = None
    diagramSvg: Optional[str] = None
    prerequisites: Optional[PrerequisitesInfo] = None
    missingPrerequisites: Optional[List[str]] = None
