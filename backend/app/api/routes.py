"""REST API routes for AI Software Architecture Designer."""

from fastapi import APIRouter, HTTPException, Response
from app.config import settings
from app.models.chat import (
    AnalyzeRequest,
    RefineRequest,
    ApproveRequest,
    ChatResponse,
)
from app.models.archimate import ArchiMateModel, ValidationReport
from app.services.architect_agent import ArchitectAgent
from app.services.archimate_validator import ArchiMateValidator
from app.services.exporter import ArchiMateExporter

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
                "name": "OpenAI (GPT-4o-mini)",
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


@router.post("/architecture/analyze", response_model=ChatResponse)
async def analyze_architecture(request: AnalyzeRequest):
    """Step 1 to 4: Validates the 4 mandatory prerequisites, then generates proposal & diagram."""
    try:
        prereq = ArchitectAgent.extract_prerequisites(
            request.description,
            request.history,
            request.prerequisites,
        )

        if not prereq.is_complete:
            missing_msg = ArchitectAgent.build_missing_prerequisites_message(prereq)
            return ChatResponse(
                message=missing_msg,
                proposal=None,
                prerequisites=prereq,
                missingPrerequisites=prereq.missing_fields(),
            )

        # Combine user messages from history + current prompt for full context
        user_texts = [
            m.content for m in (request.history or []) if m.role == "user" and m.content
        ]
        user_texts.append(request.description)
        full_description = "\n".join(user_texts)

        proposal = await ArchitectAgent.analyze_and_propose(
            full_description, request.constraints, prereq
        )
        model, diagram_svg, validation = ArchitectAgent.generate_archimate_model_from_proposal(
            proposal
        )
        message = (
            f"Pré-requisitos validados (Iniciativa: '{prereq.iniciativa}', Sigla: '{prereq.sigla.upper()}', "
            f"Feature: '{prereq.feature}', ARQCOR: '{prereq.arqcor}').\n"
            f"Criei o desenho de arquitetura para '{proposal.title}' com {len(proposal.components)} componentes "
            f"padronizados e {len(proposal.integrations)} integrações."
        )
        return ChatResponse(
            message=message,
            proposal=proposal,
            archimateModel=model,
            diagramSvg=diagram_svg,
            validation=validation,
            prerequisites=prereq,
            missingPrerequisites=[],
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
        message = (
            f"Atualizei a proposta e o desenho de arquitetura com base no seu pedido ('{request.feedback}'). "
            f"Versão v{updated_proposal.version} gerada com {len(updated_proposal.components)} componentes."
        )
        return ChatResponse(
            message=message,
            proposal=updated_proposal,
            archimateModel=model,
            diagramSvg=diagram_svg,
            validation=validation,
            prerequisites=updated_proposal.prerequisites,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar arquitetura: {str(e)}")


@router.post("/architecture/approve", response_model=ChatResponse)
async def approve_architecture(request: ApproveRequest):
    """Step 6, 7 & 8: Generates official ArchiMate model, automated validation and SVG diagram."""
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
