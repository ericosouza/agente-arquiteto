"""REST API routes for AI Software Architecture Designer."""

from fastapi import APIRouter, HTTPException, Response
from app.config import settings
from app.models.chat import (
    AnalyzeRequest,
    RefineRequest,
    ApproveRequest,
    ChatResponse,
    BrainstormRequest,
    BrainstormResponse,
)
from app.models.persona import PersonaType
from app.models.observability import FinOpsSummary, SpanMetric
from app.services.cost_tracker import CostTracker
from typing import Optional
from app.models.archimate import ArchiMateModel, ValidationReport
from app.services.architect_agent import ArchitectAgent
from app.services.archimate_validator import ArchiMateValidator
from app.services.exporter import ArchiMateExporter
from app.services.scope_guardrail import ScopeGuardrail
from app.services.brainstorm_agent import BrainstormAgent

router = APIRouter(prefix="/api", tags=["Architecture"])


@router.get("/info")
async def get_system_info():
    """Returns AI Provider configuration status and execution instructions."""
    active_provider = settings.detect_active_provider()
    has_gemini = bool(settings.GEMINI_API_KEY)
    has_openai = bool(settings.OPENAI_API_KEY)
    has_anthropic = bool(settings.ANTHROPIC_API_KEY)

    return {
        "appName": settings.APP_NAME,
        "appVersion": settings.APP_VERSION,
        "activeProvider": active_provider,
        "providers": {
            "builtin": {
                "name": "Built-in Expert Engine (Offline / Gratuito)",
                "available": True,
                "configured": True,
                "description": "Motor de raciocínio arquitetural baseado em regras e padrões de engenharia. Funciona sem internet ou chaves de API.",
            },
            "gemini": {
                "name": "Google Gemini",
                "available": True,
                "configured": has_gemini,
                "model": settings.GEMINI_MODEL,
                "instructions": "Para utilizar, configure a variável GEMINI_API_KEY no arquivo .env",
            },
            "openai": {
                "name": "OpenAI (GPT-4o / GPT-4o-mini)",
                "available": True,
                "configured": has_openai,
                "model": settings.OPENAI_MODEL,
                "instructions": "Para utilizar, configure a variável OPENAI_API_KEY no arquivo .env",
            },
            "ollama": {
                "name": f"Ollama Local ({settings.OLLAMA_MODEL})",
                "available": True,
                "configured": True,
                "baseUrl": settings.OLLAMA_BASE_URL,
                "instructions": "Execute 'ollama run llama3.2' localmente.",
            },
        },
    }


@router.post("/architecture/scope-check")
async def check_scope(request: AnalyzeRequest):
    """Evaluates whether the user message is within the software architecture scope."""
    is_in_scope, refusal = await ScopeGuardrail.evaluate_scope(request.description)
    return {"inScope": is_in_scope, "refusalMessage": refusal}


@router.post("/architecture/brainstorm", response_model=BrainstormResponse)
async def brainstorm_architecture(request: BrainstormRequest):
    """Interactive refinement & brainstorming step with the selected Persona and BV RAG."""
    try:
        persona = request.persona or PersonaType.ARQUITETO
        history_dicts = [
            {"role": m.role, "content": m.content} for m in (request.history or [])
        ]
        reply, is_ready = await BrainstormAgent.chat(
            message=request.message,
            history=history_dicts,
            prerequisites=request.prerequisites,
            persona=persona,
        )
        return BrainstormResponse(
            reply=reply,
            isReadyForModeling=is_ready,
            prerequisites=request.prerequisites,
            persona=persona,
            ragSourcesUsed=["catalogo_tecnologias_bv.md", "padroes_nomenclatura_bv.md"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no brainstorm arquitetural: {str(e)}")


@router.post("/architecture/analyze", response_model=ChatResponse)
async def analyze_architecture(request: AnalyzeRequest):
    """Workflow: Guardrail de Escopo -> Pré-requisitos (Sigla, Feature, ARQCOR) -> Persona & Geração."""
    try:
        # 1. Guardrail de Escopo
        is_in_scope, refusal = await ScopeGuardrail.evaluate_scope(request.description)
        if not is_in_scope:
            return ChatResponse(
                message=refusal,
                inScope=False,
                proposal=None,
                prerequisites=request.prerequisites,
                missingPrerequisites=[],
                persona=request.persona,
            )

        # 2. Extração e validação dos pré-requisitos (Sigla, Feature, ARQCOR)
        prereq = ArchitectAgent.extract_prerequisites(
            request.description,
            request.history,
            request.prerequisites,
        )

        if not prereq.is_complete:
            missing_msg = ArchitectAgent.build_missing_prerequisites_message(prereq)
            return ChatResponse(
                message=missing_msg,
                inScope=True,
                proposal=None,
                prerequisites=prereq,
                missingPrerequisites=prereq.missing_fields(),
                persona=request.persona,
            )

        # 3. Contexto consolidado
        user_texts = [
            m.content for m in (request.history or []) if m.role == "user" and m.content
        ]
        user_texts.append(request.description)
        full_description = "\n".join(user_texts)

        # 4. Geração com a Persona Selecionada
        proposal = await ArchitectAgent.analyze_and_propose(
            full_description, request.constraints, prereq
        )
        model, diagram_svg, validation = ArchitectAgent.generate_archimate_model_from_proposal(
            proposal
        )
        persona_label = "Arquiteto de Software" if request.persona == PersonaType.ARQUITETO else "Engenheiro de Software"
        message = (
            f"Como **{persona_label}**, validei os pré-requisitos corporativos (Sigla: '{prereq.sigla.upper()}', "
            f"Feature: '{prereq.feature}', ARQCOR: '{prereq.arqcor}').\n\n"
            f"Mapeei o pipeline de dados e gerei a arquitetura para **'{proposal.title}'** com "
            f"{len(proposal.components)} componentes padronizados e {len(proposal.integrations)} integrações."
        )

        return ChatResponse(
            message=message,
            inScope=True,
            proposal=proposal,
            archimateModel=model,
            diagramSvg=diagram_svg,
            validation=validation,
            prerequisites=prereq,
            missingPrerequisites=[],
            persona=request.persona,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar análise arquitetural: {str(e)}")


@router.post("/architecture/refine", response_model=ChatResponse)
async def refine_architecture(request: RefineRequest):
    """Refines proposed architecture and immediately updates the ArchiMate model and SVG diagram."""
    try:
        updated_proposal = await ArchitectAgent.refine_proposal(
            request.proposal, request.feedback
        )
        model, diagram_svg, validation = ArchitectAgent.generate_archimate_model_from_proposal(
            updated_proposal
        )
        persona_label = "Arquiteto de Software" if request.persona == PersonaType.ARQUITETO else "Engenheiro de Software"
        message = (
            f"Como **{persona_label}**, incorporei os ajustes solicitados ('{request.feedback}'). "
            f"Versão v{updated_proposal.version} gerada com sucesso com {len(updated_proposal.components)} componentes."
        )
        return ChatResponse(
            message=message,
            inScope=True,
            proposal=updated_proposal,
            archimateModel=model,
            diagramSvg=diagram_svg,
            validation=validation,
            prerequisites=updated_proposal.prerequisites,
            persona=request.persona,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar arquitetura: {str(e)}")


@router.post("/architecture/approve", response_model=ChatResponse)
async def approve_architecture(request: ApproveRequest):
    """Generates official ArchiMate model, automated validation report and SVG diagram."""
    try:
        model, diagram_svg, validation = ArchitectAgent.generate_archimate_model_from_proposal(
            request.proposal
        )

        message = (
            f"Arquitetura aprovada com sucesso! O modelo ArchiMate 3.2 foi gerado "
            f"com {len(model.elements)} elementos e {len(model.relationships)} conexões. "
            f"Status da validação: {'Válido e Aprovado' if validation.isValid else 'Contém Avisos/Erros'}."
        )

        return ChatResponse(
            message=message,
            inScope=True,
            proposal=request.proposal,
            archimateModel=model,
            diagramSvg=diagram_svg,
            validation=validation,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar modelo ArchiMate: {str(e)}")


@router.post("/architecture/validate", response_model=ValidationReport)
async def validate_model(model: ArchiMateModel):
    """Validates an existing ArchiMate model against the metamodel rules."""
    return ArchiMateValidator.validate_model(model)


@router.post("/architecture/export/json")
async def export_json(model: ArchiMateModel):
    """Exports structured ArchiMate 3.2 JSON file for download."""
    json_str = ArchiMateExporter.to_json_string(model)
    filename = f"{model.identifier or 'archimate_model'}.json"
    return Response(
        content=json_str,
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/architecture/export/xml")
async def export_xml(model: ArchiMateModel):
    """Exports The Open Group ArchiMate Model Exchange File Format (.xml / .archimate)."""
    xml_str = ArchiMateExporter.to_opengroup_xml(model)
    filename = f"{model.identifier or 'archimate_model'}.archimate"
    return Response(
        content=xml_str,
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/observability/finops/summary", response_model=FinOpsSummary)
async def get_finops_summary():
    """Returns FinOps cost metrics, token usage, and spans."""
    active_provider = settings.detect_active_provider()
    return CostTracker.get_summary(active_provider=active_provider)


@router.get("/observability/finops/traces")
async def get_finops_traces(trace_id: Optional[str] = None):
    """Returns the list of recorded spans for debugging or Phoenix inspection."""
    return CostTracker.get_spans(trace_id=trace_id)


@router.post("/observability/finops/reset")
async def reset_finops():
    """Resets the in-memory FinOps session counter."""
    CostTracker.reset()
    return {"status": "ok", "message": "FinOps metrics reset successfully"}
