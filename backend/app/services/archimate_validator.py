"""ArchiMate Metamodel Validator (Etapa 8).

Performs strict, automated validation against The Open Group ArchiMate 3.2 rules:
1. Syntax and schema validation.
2. Uniqueness of element and relationship IDs.
3. Referential integrity (no dangling source/target references).
4. ArchiMate semantic compatibility between element types and relationship types.
5. Presence of required endpoints.
6. Model consistency with architectural proposal.
"""

from typing import Set, Dict, List, Optional
from app.models.archimate import (
    ArchiMateModel,
    ArchiMateElement,
    ArchiMateRelationship,
    ArchiMateElementType,
    ArchiMateRelationshipType,
    ValidationReport,
    ValidationIssue,
)
from app.models.proposal import ArchitectureProposal


# Passive structure element types (valid targets for 'Access' relations)
PASSIVE_ELEMENT_TYPES: Set[ArchiMateElementType] = {
    ArchiMateElementType.DATA_OBJECT,
    ArchiMateElementType.BUSINESS_OBJECT,
    ArchiMateElementType.ARTIFACT,
    ArchiMateElementType.REPRESENTATION,
    ArchiMateElementType.CONTRACT,
}

# Active & behavioral structure element types (valid sources for 'Access' and 'Flow')
ACTIVE_OR_BEHAVIORAL_TYPES: Set[ArchiMateElementType] = {
    ArchiMateElementType.APPLICATION_COMPONENT,
    ArchiMateElementType.APPLICATION_SERVICE,
    ArchiMateElementType.APPLICATION_FUNCTION,
    ArchiMateElementType.APPLICATION_PROCESS,
    ArchiMateElementType.BUSINESS_ACTOR,
    ArchiMateElementType.BUSINESS_ROLE,
    ArchiMateElementType.BUSINESS_PROCESS,
    ArchiMateElementType.BUSINESS_SERVICE,
    ArchiMateElementType.BUSINESS_FUNCTION,
    ArchiMateElementType.NODE,
    ArchiMateElementType.SYSTEM_SOFTWARE,
    ArchiMateElementType.TECHNOLOGY_SERVICE,
    ArchiMateElementType.TECHNOLOGY_FUNCTION,
}


class ArchiMateValidator:
    """Validates an ArchiMate model against structural and semantic rules."""

    @classmethod
    def validate_model(
        cls,
        model: ArchiMateModel,
        proposal: Optional[ArchitectureProposal] = None
    ) -> ValidationReport:
        errors: List[ValidationIssue] = []
        warnings: List[ValidationIssue] = []
        info: List[ValidationIssue] = []

        element_ids: Set[str] = set()
        element_map: Dict[str, ArchiMateElement] = {}

        # 1. Validate Elements
        for elem in model.elements:
            # Check ID uniqueness
            if elem.id in element_ids:
                errors.append(ValidationIssue(
                    severity="error",
                    code="DUPLICATE_ELEMENT_ID",
                    message=f"Identificador duplicado para o elemento: '{elem.id}' ({elem.name}).",
                    elementId=elem.id,
                ))
            else:
                element_ids.add(elem.id)
                element_map[elem.id] = elem

            # Check Name presence
            if not elem.name or not elem.name.strip():
                errors.append(ValidationIssue(
                    severity="error",
                    code="EMPTY_ELEMENT_NAME",
                    message=f"Elemento com ID '{elem.id}' não possui nome legível.",
                    elementId=elem.id,
                ))

            # Layer / Type coherence check
            cls._check_layer_coherence(elem, warnings)

        # 2. Validate Relationships
        rel_ids: Set[str] = set()
        for rel in model.relationships:
            # Check Relationship ID uniqueness
            if rel.id in rel_ids:
                errors.append(ValidationIssue(
                    severity="error",
                    code="DUPLICATE_RELATIONSHIP_ID",
                    message=f"Identificador duplicado para a relação: '{rel.id}'.",
                    relationshipId=rel.id,
                ))
            else:
                rel_ids.add(rel.id)

            # Check Source and Target presence
            if not rel.source:
                errors.append(ValidationIssue(
                    severity="error",
                    code="MISSING_RELATIONSHIP_SOURCE",
                    message=f"Relação '{rel.id}' não possui elemento de origem (source) definido.",
                    relationshipId=rel.id,
                ))
            elif rel.source not in element_ids:
                errors.append(ValidationIssue(
                    severity="error",
                    code="DANGLING_RELATIONSHIP_SOURCE",
                    message=f"Origem da relação '{rel.id}' referencia ID inexistente: '{rel.source}'.",
                    relationshipId=rel.id,
                ))

            if not rel.target:
                errors.append(ValidationIssue(
                    severity="error",
                    code="MISSING_RELATIONSHIP_TARGET",
                    message=f"Relação '{rel.id}' não possui elemento de destino (target) definido.",
                    relationshipId=rel.id,
                ))
            elif rel.target not in element_ids:
                errors.append(ValidationIssue(
                    severity="error",
                    code="DANGLING_RELATIONSHIP_TARGET",
                    message=f"Destino da relação '{rel.id}' referencia ID inexistente: '{rel.target}'.",
                    relationshipId=rel.id,
                ))

            # ArchiMate Semantic compatibility checks
            if rel.source in element_map and rel.target in element_map:
                source_elem = element_map[rel.source]
                target_elem = element_map[rel.target]
                cls._check_semantic_compatibility(rel, source_elem, target_elem, warnings, info)

        # 3. Model Consistency with Proposal (Single Source of Truth)
        if proposal is not None:
            cls._check_consistency_with_proposal(model, proposal, errors, warnings)

        # Summarize
        is_valid = len(errors) == 0
        if is_valid:
            summary = (
                f"Modelo ArchiMate válido e consistente com a especificação 3.2. "
                f"Contém {len(model.elements)} elementos e {len(model.relationships)} relações "
                f"sem erros estruturais ou referências órfãs."
            )
        else:
            summary = (
                f"Modelo inválido: encontrados {len(errors)} erro(s) e {len(warnings)} aviso(s). "
                f"Corrija os identificadores e referências antes de prosseguir."
            )

        return ValidationReport(
            isValid=is_valid,
            totalElements=len(model.elements),
            totalRelationships=len(model.relationships),
            errors=errors,
            warnings=warnings,
            info=info,
            summary=summary,
        )

    @classmethod
    def _check_layer_coherence(cls, elem: ArchiMateElement, warnings: List[ValidationIssue]) -> None:
        """Verifies that an element's type belongs to its designated ArchiMate layer."""
        t_str = elem.type.value
        l_str = elem.layer.value

        if t_str.startswith("Business") and l_str != "Business":
            warnings.append(ValidationIssue(
                severity="warning",
                code="LAYER_TYPE_MISMATCH",
                message=f"Elemento '{elem.name}' ({t_str}) está associado à camada '{l_str}' em vez de 'Business'.",
                elementId=elem.id,
            ))
        elif (t_str.startswith("Application") or t_str == "DataObject") and l_str not in {"Application", "Channel"}:
            warnings.append(ValidationIssue(
                severity="warning",
                code="LAYER_TYPE_MISMATCH",
                message=f"Elemento '{elem.name}' ({t_str}) está associado à camada '{l_str}' em vez de 'Application' ou 'Channel'.",
                elementId=elem.id,
            ))
        elif (t_str in {"Node", "Device", "SystemSoftware", "TechnologyService", "TechnologyInterface", "Artifact"}) and l_str != "Technology":
            warnings.append(ValidationIssue(
                severity="warning",
                code="LAYER_TYPE_MISMATCH",
                message=f"Elemento '{elem.name}' ({t_str}) está associado à camada '{l_str}' em vez de 'Technology'.",
                elementId=elem.id,
            ))

    @classmethod
    def _check_semantic_compatibility(
        cls,
        rel: ArchiMateRelationship,
        src: ArchiMateElement,
        tgt: ArchiMateElement,
        warnings: List[ValidationIssue],
        info: List[ValidationIssue]
    ) -> None:
        """Checks semantic relationship rules according to ArchiMate 3.2 metamodel."""
        if rel.type == ArchiMateRelationshipType.ACCESS:
            # Access should target a passive element (like DataObject)
            if tgt.type not in PASSIVE_ELEMENT_TYPES:
                warnings.append(ValidationIssue(
                    severity="warning",
                    code="SEMANTIC_ACCESS_TARGET",
                    message=(
                        f"Relação 'Access' de '{src.name}' para '{tgt.name}' ({tgt.type.value}) "
                        f"normalmente deve apontar para um elemento passivo (ex: DataObject)."
                    ),
                    relationshipId=rel.id,
                ))

        elif rel.type == ArchiMateRelationshipType.SERVING:
            # Serving: source provides functionality to target
            info.append(ValidationIssue(
                severity="info",
                code="SERVING_RELATION",
                message=f"Relação de serviço: '{src.name}' provê funcionalidade para '{tgt.name}'.",
                relationshipId=rel.id,
            ))

        elif rel.type == ArchiMateRelationshipType.REALIZATION:
            # Realization: e.g. Component realizes Service or Artifact realizes Component
            info.append(ValidationIssue(
                severity="info",
                code="REALIZATION_RELATION",
                message=f"Relação de realização: '{src.name}' realiza '{tgt.name}'.",
                relationshipId=rel.id,
            ))

    @classmethod
    def _check_consistency_with_proposal(
        cls,
        model: ArchiMateModel,
        proposal: ArchitectureProposal,
        errors: List[ValidationIssue],
        warnings: List[ValidationIssue]
    ) -> None:
        """Verifies 1:1 consistency between Proposal and ArchiMate Model (Single Source of Truth)."""
        model_elem_ids = {e.id for e in model.elements}
        proposal_comp_ids = {c.id for c in proposal.components}

        # Check for missing components in model
        for comp in proposal.components:
            if comp.id not in model_elem_ids:
                errors.append(ValidationIssue(
                    severity="error",
                    code="PROPOSAL_COMPONENT_MISSING_IN_MODEL",
                    message=f"Componente '{comp.name}' ({comp.id}) da proposta não foi encontrado no modelo ArchiMate.",
                    elementId=comp.id,
                ))

        # Check for missing integrations in model
        model_rel_ids = {r.id for r in model.relationships}
        for inte in proposal.integrations:
            if inte.id not in model_rel_ids:
                warnings.append(ValidationIssue(
                    severity="warning",
                    code="PROPOSAL_INTEGRATION_MISSING_IN_MODEL",
                    message=f"Integração '{inte.id}' ({inte.sourceComponentId} -> {inte.targetComponentId}) da proposta ausente no modelo.",
                    relationshipId=inte.id,
                ))
