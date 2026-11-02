"""Architect Agent Workflow Orchestrator.

Implements the multi-step workflow:
1. Scope guardrail check and validation.
2. Mandatory prerequisites verification (Sigla, Feature, ARQCOR).
3. Selected Persona (Architect vs Engineer) and Architecture RAG grounding.
4. Data pipeline mapping and component identification.
5. Technology selection with official BV naming standards.
6. ArchiMate diagram generation with official notation and layout.
7. Structured ArchiMate 3.2 model creation.
8. Automated validation against ArchiMate metamodel.
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
    """Intelligent Software Architecture Agent."""

    @classmethod
    def extract_prerequisites(
        cls,
        description: str,
        history: Optional[List[Any]] = None,
        existing: Optional[PrerequisitesInfo] = None,
    ) -> PrerequisitesInfo:
        """Extracts and validates the mandatory prerequisites (Sigla, Feature, ARQCOR)."""
        return PrerequisiteExtractor.extract(description, history, existing)

    @classmethod
    def build_missing_prerequisites_message(cls, info: PrerequisitesInfo) -> str:
        """Builds the response asking the user for any missing prerequisites."""
        return PrerequisiteExtractor.build_missing_prompt(info)

    @classmethod
    def propose_sync(
        cls,
        description: str,
        constraints: Optional[List[str]] = None,
        prerequisites: Optional[PrerequisitesInfo] = None,
    ) -> ArchitectureProposal:
        """Synchronously generates a proposal using Builtin Expert Engine (ideal for offline tests)."""
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
        """Analyzes requirements with the selected Persona & RAG, builds proposal."""
        raw_proposal = await LLMService.analyze_and_propose(description, constraints, prerequisites, persona)
        return ArchitectureProposal.model_validate(raw_proposal)

    @classmethod
    def refine_sync(
        cls,
        proposal: ArchitectureProposal,
        feedback: str,
    ) -> ArchitectureProposal:
        """Synchronously refines a proposal using Builtin Expert Engine (ideal for offline tests)."""
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
        """Incorporates user changes with the selected Persona."""
        proposal_dict = proposal.model_dump()
        refined_dict = await LLMService.refine_proposal(proposal_dict, feedback, persona)
        return ArchitectureProposal.model_validate(refined_dict)

    @classmethod
    def generate_archimate_model_from_proposal(
        cls,
        proposal: ArchitectureProposal
    ) -> Tuple[ArchiMateModel, str, ValidationReport]:
        """Converts approved proposal into ArchiMate model, validates, renders SVG."""
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Elements construction
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

        # 2. Relationships construction
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

        # 3. Create ArchiMate Model
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

        # 4. Generate visual diagram and calculate layout view coordinates
        diagram_svg, updated_model = DiagramGenerator.layout_and_render_svg(model)

        # 5. Automated Validation against ArchiMate Metamodel
        validation_report = ArchiMateValidator.validate_model(updated_model, proposal)

        return updated_model, diagram_svg, validation_report
