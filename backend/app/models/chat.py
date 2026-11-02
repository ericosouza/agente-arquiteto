"""Modelos de requisição e resposta para o Chat do Agente e interações do fluxo de trabalho."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.proposal import ArchitectureProposal, PrerequisitesInfo
from app.models.archimate import ArchiMateModel, ValidationReport
from app.models.persona import PersonaType


class ChatMessage(BaseModel):
    id: Optional[str] = None
    role: str = Field(..., description="'user', 'assistant' ou 'system'")
    content: str
    timestamp: Optional[str] = None


class AnalyzeRequest(BaseModel):
    description: str = Field(..., min_length=1, description="Descrição em linguagem natural do sistema solicitado")
    constraints: Optional[List[str]] = Field(default_factory=list, description="Restrições ou preferências opcionais")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Histórico da conversa para coleta de pré-requisitos em múltiplos turnos")
    prerequisites: Optional[PrerequisitesInfo] = Field(default=None, description="Pré-requisitos do projeto acumulados ou explícitos")
    persona: Optional[PersonaType] = Field(default=PersonaType.ARQUITETO, description="Persona selecionada: 'arquiteto' ou 'engenheiro'")


class BrainstormRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Mensagem do usuário durante a fase de brainstorming/refinamento")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Histórico da conversa de brainstorming")
    prerequisites: Optional[PrerequisitesInfo] = Field(default=None, description="Pré-requisitos confirmados do projeto (Sigla, Feature, ARQCOR)")
    persona: Optional[PersonaType] = Field(default=PersonaType.ARQUITETO, description="Persona selecionada")


class BrainstormResponse(BaseModel):
    reply: str
    isReadyForModeling: bool = Field(default=False, description="Verdadeiro se o usuário concordou em prosseguir para a geração do modelo ('Ok?')")
    prerequisites: Optional[PrerequisitesInfo] = None
    persona: PersonaType = PersonaType.ARQUITETO
    ragSourcesUsed: Optional[List[str]] = Field(default_factory=list)


class RefineRequest(BaseModel):
    proposal: ArchitectureProposal = Field(..., description="Proposta atual a ser refinada")
    feedback: str = Field(..., min_length=2, description="Instrução do usuário, ex: 'mudar banco para MySQL'")
    persona: Optional[PersonaType] = Field(default=PersonaType.ARQUITETO, description="Persona selecionada")


class ApproveRequest(BaseModel):
    proposal: ArchitectureProposal = Field(..., description="Proposta de arquitetura aprovada pelo usuário")


class ChatResponse(BaseModel):
    message: str
    inScope: bool = Field(default=True, description="Falso se a requisição for rejeitada pelo guardrail de escopo")
    proposal: Optional[ArchitectureProposal] = None
    validation: Optional[ValidationReport] = None
    archimateModel: Optional[ArchiMateModel] = None
    diagramSvg: Optional[str] = None
    prerequisites: Optional[PrerequisitesInfo] = None
    missingPrerequisites: Optional[List[str]] = None
    persona: Optional[PersonaType] = PersonaType.ARQUITETO
