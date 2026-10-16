"""Architect Agent Workflow Orchestrator.

Implements the multi-step workflow:
1. Natural language description interpretation & requirement extraction (Etapa 1).
2. Architectural analysis and component identification (Etapa 2).
3. Technology selection with technical rationales (Etapa 3).
4. Confirmation table structuring (Etapa 4).
5. Integration definition with protocols and patterns (Etapa 5).
6. ArchiMate diagram generation with official notation (Etapa 6).
7. Structured ArchiMate model creation (Etapa 7).
8. Automated validation against ArchiMate metamodel (Etapa 8).
"""

from datetime import datetime, timezone
from typing import Tuple, Optional, List
from app.models.proposal import ArchitectureProposal
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
from app.services.llm_provider import LLMService
from app.services.archimate_validator import ArchiMateValidator
from app.services.diagram_generator import DiagramGenerator


class ArchitectAgent:
    """Intelligent Software Architecture Agent."""

    @classmethod
    async def analyze_and_propose(
        cls,
        description: str,
        constraints: Optional[List[str]] = None
    ) -> ArchitectureProposal:
        """Step 1 to 5: Receives user prompt, analyzes requirements, chooses stack, builds proposal."""
        raw_proposal = await LLMService.analyze_and_propose(description, constraints)
        return ArchitectureProposal.model_validate(raw_proposal)

    @classmethod
    async def refine_proposal(
        cls,
        proposal: ArchitectureProposal,
        feedback: str
    ) -> ArchitectureProposal:
        """Incorporates user changes (name, tech, add/remove components, integrations)."""
        proposal_dict = proposal.model_dump()
        refined_dict = await LLMService.refine_proposal(proposal_dict, feedback)
        return ArchitectureProposal.model_validate(refined_dict)

    @classmethod
    def generate_archimate_model_from_proposal(
        cls,
        proposal: ArchitectureProposal
    ) -> Tuple[ArchiMateModel, str, ValidationReport]:
        """Steps 6, 7 & 8: Converts approved proposal into ArchiMate model, validates, renders SVG."""
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Elements construction
        elements: List[ArchiMateElement] = []
        element_ids = set()

        # Add Business Layer Actor
        business_actor_id = "ACTOR-USER"
        elements.append(ArchiMateElement(
            id=business_actor_id,
            name="Usuário do Sistema",
            type=ArchiMateElementType.BUSINESS_ACTOR,
            layer=ArchiMateLayer.BUSINESS,
            documentation="Usuário final que interage com a solução via navegador web.",
            properties={"role": "Consumidor / Operador", "category": "Business"}
        ))
        element_ids.add(business_actor_id)

        # Convert proposal components to ArchiMate elements
        for comp in proposal.components:
            elements.append(ArchiMateElement(
                id=comp.id,
                name=comp.name,
                type=comp.archimateType,
                layer=comp.layer,
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

        # Connect Business Actor to Frontend Web (Serving relation)
        frontend_comp = next((c for c in proposal.components if c.category == "Frontend"), None)
        if frontend_comp:
            relationships.append(ArchiMateRelationship(
                id="REL-USER-FE",
                name="Acesso Web",
                type=ArchiMateRelationshipType.SERVING,
                source=frontend_comp.id,
                target=business_actor_id,
                documentation="Interface web atende as necessidades do usuário final.",
                properties={
                    "protocol": "HTTPS",
                    "communicationPattern": "Synchronous",
                    "purpose": "Interação humana com as interfaces do sistema"
                }
            ))

        # Convert proposal integrations to ArchiMate relationships
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

        # 4. Generate visual diagram and calculate layout view coordinates (Etapa 6)
        diagram_svg, updated_model = DiagramGenerator.layout_and_render_svg(model)

        # 5. Automated Validation against ArchiMate Metamodel (Etapa 8)
        validation_report = ArchiMateValidator.validate_model(updated_model, proposal)

        return updated_model, diagram_svg, validation_report
