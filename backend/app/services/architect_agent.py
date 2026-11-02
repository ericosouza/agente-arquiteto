"""Orquestrador do Fluxo de Trabalho do Agente Arquiteto.

Implementa o fluxo de trabalho em etapas:
1. Verificação e validação do guardrail de escopo.
2. Conferência dos pré-requisitos obrigatórios (Sigla, Feature, ARQCOR).
3. Ativação da Persona selecionada (Arquiteto vs Engenheiro) e consulta à base RAG de Arquitetura.
4. Mapeamento de pipeline de dados e identificação de componentes.
5. Seleção de tecnologias com padrões oficiais de nomenclatura do BV.
6. Geração de diagrama ArchiMate com notação visual oficial e cálculo de layout.
7. Criação do modelo estruturado ArchiMate 3.2.
8. Validação automatizada contra o metamodelo ArchiMate.
"""

from datetime import datetime, timezone
from typing import Tuple, Optional, List, Any
from app.models.proposal import ArchitectureProposal, PrerequisitesInfo
from app.models.persona import PersonaType
from app.models.archimate import (
    ArchiMateModel,
    ArchiMateModelMetadata,
    ArchiMateElement,
    ArchiMateRelationship,
    ArchiMateLayer,
    ArchiMateElementType,
    ArchiMateRelationshipType,
    ValidationReport,
)
from app.services.llm_provider import LLMService, PrerequisiteExtractor
from app.services.archimate_validator import ArchiMateValidator
from app.services.diagram_generator import DiagramGenerator


class ArchitectAgent:
    """Agente Inteligente de Arquitetura de Software."""

    @classmethod
    def extract_prerequisites(
        cls,
        description: str,
        history: Optional[List[Any]] = None,
        existing: Optional[PrerequisitesInfo] = None,
    ) -> PrerequisitesInfo:
        """Extrai e valida os pré-requisitos obrigatórios (Sigla, Feature, ARQCOR)."""
        return PrerequisiteExtractor.extract(description, history, existing)

    @classmethod
    def build_missing_prerequisites_message(cls, info: PrerequisitesInfo) -> str:
        """Constrói a resposta solicitando ao usuário os pré-requisitos ausentes."""
        return PrerequisiteExtractor.build_missing_prompt(info)

    @classmethod
    def propose_sync(
        cls,
        description: str,
        constraints: Optional[List[str]] = None,
        prerequisites: Optional[PrerequisitesInfo] = None,
    ) -> ArchitectureProposal:
        """Gera sincronamente uma proposta utilizando o motor especialista embutido (ideal para testes offline)."""
        from app.services.llm_provider import BuiltinExpertEngine
        raw_proposal = BuiltinExpertEngine.analyze_requirement(description, constraints, prerequisites)
        return ArchitectureProposal.model_validate(raw_proposal)

    @classmethod
    async def analyze_and_propose(
        cls,
        description: str,
        constraints: Optional[List[str]] = None,
        prerequisites: Optional[PrerequisitesInfo] = None,
        persona: PersonaType = PersonaType.ARQUITETO,
    ) -> ArchitectureProposal:
        """Analisa os requisitos com a Persona selecionada e contexto do RAG, gerando a proposta."""
        raw_proposal = await LLMService.analyze_and_propose(description, constraints, prerequisites, persona)
        return ArchitectureProposal.model_validate(raw_proposal)

    @classmethod
    def refine_sync(
        cls,
        proposal: ArchitectureProposal,
        feedback: str,
    ) -> ArchitectureProposal:
        """Refina sincronamente uma proposta utilizando o motor especialista embutido (ideal para testes offline)."""
        from app.services.llm_provider import BuiltinExpertEngine
        proposal_dict = proposal.model_dump()
        refined_dict = BuiltinExpertEngine.refine_proposal(proposal_dict, feedback)
        return ArchitectureProposal.model_validate(refined_dict)

    @classmethod
    async def refine_proposal(
        cls,
        proposal: ArchitectureProposal,
        feedback: str,
        persona: PersonaType = PersonaType.ARQUITETO,
    ) -> ArchitectureProposal:
        """Incorpora as alterações do usuário aplicando a Persona selecionada."""
        proposal_dict = proposal.model_dump()
        refined_dict = await LLMService.refine_proposal(proposal_dict, feedback, persona)
        return ArchitectureProposal.model_validate(refined_dict)

    @classmethod
    def generate_archimate_model_from_proposal(
        cls,
        proposal: ArchitectureProposal
    ) -> Tuple[ArchiMateModel, str, ValidationReport]:
        """Converte a proposta aprovada em modelo ArchiMate, valida regras e renderiza o SVG."""
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Construção dos Elementos
        elements: List[ArchiMateElement] = []
        element_ids = set()

        for comp in proposal.components:
            target_layer = (
                ArchiMateLayer.CHANNEL
                if comp.category == "Frontend" or comp.layer == ArchiMateLayer.CHANNEL
                else comp.layer
            )
            elements.append(ArchiMateElement(
                id=comp.id,
                name=comp.name,
                type=comp.archimateType,
                layer=target_layer,
                documentation=comp.responsibility,
                properties={
                    "technology": comp.suggestedTechnology,
                    "category": comp.category,
                    "justification": comp.justification,
                }
            ))
            element_ids.add(comp.id)

        # 2. Construção dos Relacionamentos
        relationships: List[ArchiMateRelationship] = []

        for inte in proposal.integrations:
            if inte.sourceComponentId in element_ids and inte.targetComponentId in element_ids:
                relationships.append(ArchiMateRelationship(
                    id=inte.id,
                    name=inte.protocol.split()[0] if inte.protocol else None,
                    type=inte.relationshipType,
                    source=inte.sourceComponentId,
                    target=inte.targetComponentId,
                    documentation=inte.purpose,
                    properties={
                        "protocol": inte.protocol,
                        "communicationPattern": inte.communicationPattern,
                        "purpose": inte.purpose,
                    }
                ))

        # 3. Criação do Modelo ArchiMate 3.2
        model = ArchiMateModel(
            identifier=f"model-{proposal.id.lower()}",
            name=proposal.title,
            documentation=proposal.summary,
            version="3.2",
            metadata=ArchiMateModelMetadata(
                author="AI Software Architecture Designer",
                createdAt=now_iso,
                standard="The Open Group ArchiMate 3.2 Specification",
                description=proposal.summary,
                architecturalStyle=proposal.architecturalStyle,
            ),
            elements=elements,
            relationships=relationships,
            views=[],
        )

        # 4. Geração do diagrama visual e cálculo das coordenadas de layout
        diagram_svg, updated_model = DiagramGenerator.layout_and_render_svg(model)

        # 5. Validação automatizada contra o metamodelo ArchiMate
        validation_report = ArchiMateValidator.validate_model(updated_model, proposal)

        return updated_model, diagram_svg, validation_report
