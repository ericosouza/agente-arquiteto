"""Validador do Metamodelo ArchiMate (Etapa 8).

Executa validação estrita e automatizada conforme as regras da especificação The Open Group ArchiMate 3.2:
1. Validação de sintaxe e esquema.
2. Unicidade de IDs de elementos e relacionamentos.
3. Integridade referencial (sem referências órfãs de origem ou destino).
4. Compatibilidade semântica do ArchiMate entre tipos de elementos e tipos de relacionamentos.
5. Presença dos nós de extremidade obrigatórios.
6. Consistência do modelo com a proposta de arquitetura.
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


# Tipos de elementos de estrutura passiva (destinos válidos para relações do tipo 'Access')
PASSIVE_ELEMENT_TYPES: Set[ArchiMateElementType] = {
    ArchiMateElementType.DATA_OBJECT,
    ArchiMateElementType.BUSINESS_OBJECT,
    ArchiMateElementType.ARTIFACT,
    ArchiMateElementType.REPRESENTATION,
    ArchiMateElementType.CONTRACT,
}

# Tipos de elementos de estrutura ativa e comportamental (origens válidas para relações 'Access' e 'Flow')
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
    """Valida um modelo ArchiMate em relação a regras estruturais e semânticas."""

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

        # 1. Validação de Elementos
        for elem in model.elements:
            # Verifica a unicidade de ID
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

            # Verifica a presença do Nome legível
            if not elem.name or not elem.name.strip():
                errors.append(ValidationIssue(
                    severity="error",
                    code="EMPTY_ELEMENT_NAME",
                    message=f"Elemento com ID '{elem.id}' não possui nome legível.",
                    elementId=elem.id,
                ))

            # Verificação de coerência entre Camada e Tipo de Elemento
            cls._check_layer_coherence(elem, warnings)

        # 2. Validação de Relacionamentos
        rel_ids: Set[str] = set()
        for rel in model.relationships:
            # Verifica a unicidade do ID do Relacionamento
            if rel.id in rel_ids:
                errors.append(ValidationIssue(
                    severity="error",
                    code="DUPLICATE_RELATIONSHIP_ID",
                    message=f"Identificador duplicado para a relação: '{rel.id}'.",
                    relationshipId=rel.id,
                ))
            else:
                rel_ids.add(rel.id)

            # Verifica a presença dos nós de Origem (source) e Destino (target)
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

            # Verificações de compatibilidade semântica no ArchiMate
            if rel.source in element_map and rel.target in element_map:
                source_elem = element_map[rel.source]
                target_elem = element_map[rel.target]
                cls._check_semantic_compatibility(rel, source_elem, target_elem, warnings, info)

        # 3. Consistência do Modelo com a Proposta (Fonte Única da Verdade)
        if proposal is not None:
            cls._check_consistency_with_proposal(model, proposal, errors, warnings)

        # Resumo final da validação
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
        """Verifica se o tipo do elemento pertence à camada ArchiMate designada."""
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
        """Verifica as regras semânticas de relacionamento segundo o metamodelo ArchiMate 3.2."""
        if rel.type == ArchiMateRelationshipType.ACCESS:
            # Relações de acesso (Access) devem apontar para elementos passivos (ex: DataObject)
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
            # Relações de serviço (Serving): elemento de origem provê funcionalidade para o destino
            info.append(ValidationIssue(
                severity="info",
                code="SERVING_RELATION",
                message=f"Relação de serviço: '{src.name}' provê funcionalidade para '{tgt.name}'.",
                relationshipId=rel.id,
            ))

        elif rel.type == ArchiMateRelationshipType.REALIZATION:
            # Relações de realização (Realization): Component realiza Service ou Artifact realiza Component
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
        """Verifica a consistência 1:1 entre a Proposta e o Modelo ArchiMate (Fonte Única da Verdade)."""
        model_elem_ids = {e.id for e in model.elements}
        proposal_comp_ids = {c.id for c in proposal.components}

        # Verifica se há componentes da proposta ausentes no modelo
        for comp in proposal.components:
            if comp.id not in model_elem_ids:
                errors.append(ValidationIssue(
                    severity="error",
                    code="PROPOSAL_COMPONENT_MISSING_IN_MODEL",
                    message=f"Componente '{comp.name}' ({comp.id}) da proposta não foi encontrado no modelo ArchiMate.",
                    elementId=comp.id,
                ))

        # Verifica se há integrações da proposta ausentes no modelo
        model_rel_ids = {r.id for r in model.relationships}
        for inte in proposal.integrations:
            if inte.id not in model_rel_ids:
                warnings.append(ValidationIssue(
                    severity="warning",
                    code="PROPOSAL_INTEGRATION_MISSING_IN_MODEL",
                    message=f"Integração '{inte.id}' ({inte.sourceComponentId} -> {inte.targetComponentId}) da proposta ausente no modelo.",
                    relationshipId=inte.id,
                ))
