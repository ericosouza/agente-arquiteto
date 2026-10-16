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
    """Step 1 to 4: Receives natural language description and generates initial proposal."""
    try:
        proposal = await ArchitectAgent.analyze_and_propose(
            request.description, request.constraints
        )
        message = (
            f"Analisei os requisitos para '{proposal.title}'. "
            f"Identifiquei {len(proposal.components)} componentes e {len(proposal.integrations)} integrações. "
            f"Adotei o estilo '{proposal.architecturalStyle}'. "
            f"Por favor, revise a proposta na tabela abaixo antes da geração do diagrama ArchiMate."
        )
        return ChatResponse(
            message=message,
            proposal=proposal,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar análise arquitetural: {str(e)}")


@router.post("/architecture/refine", response_model=ChatResponse)
async def refine_architecture(request: RefineRequest):
    """Refines proposed architecture based on user instructions."""
    try:
        updated_proposal = await ArchitectAgent.refine_proposal(
            request.proposal, request.feedback
        )
        message = (
            f"Atualizei a arquitetura com base no seu pedido ('{request.feedback}'). "
            f"Versão {updated_proposal.version} pronta para confirmação."
        )
        return ChatResponse(
            message=message,
            proposal=updated_proposal,
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
