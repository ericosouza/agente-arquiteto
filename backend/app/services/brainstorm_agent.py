"""Agente de Brainstorming com LLM Online e Serviço de RAG de Arquitetura.

Facilita a etapa de refinamento interativo do fluxo de arquitetura,
incorporando a Persona selecionada (Arquiteto vs Engenheiro) e recuperando
as tecnologias oficiais do BV e padrões ArchiMate para evitar templates repetitivos.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
from app.models.persona import PersonaType, get_persona_system_prompt
from app.models.proposal import PrerequisitesInfo
from app.services.architecture_rag import ArchitectureRAGService

logger = logging.getLogger(__name__)


class BrainstormAgent:
    """Agente conversacional de brainstorming para refinamento de arquitetura."""

    @classmethod
    async def chat(
        cls,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        prerequisites: Optional[PrerequisitesInfo] = None,
        persona: PersonaType = PersonaType.ARQUITETO,
    ) -> Tuple[str, bool]:
        """Interage com o usuário para debater e refinar escolhas arquiteturais.
        
        Retorna:
            (texto_resposta, esta_pronto_para_modelagem)
        """
        # 1. Recupera o contexto arquitetural relevante da base RAG do BV
        rag_chunks = ArchitectureRAGService.search(message, top_k=3)
        context_text = "\n\n".join([f"[{c['title']}]: {c['content']}" for c in rag_chunks])

        # 2. Verifica se o usuário está sinalizando aprovação ("Ok?", "pode gerar", "aprovado", "vamos em frente")
        ok_signals = [
            "ok", "está ok", "esta ok", "pode gerar", "pode modelar", "gerar modelo",
            "vamos em frente", "aprovado", "concordo", "perfeito", "prosseguir",
            "pode criar", "desenhar", "finalizar brainstorm"
        ]
        user_clean = message.strip().lower()
        is_ok = any(sig in user_clean for sig in ok_signals)

        # 3. Executa a chamada à LLM Online com a Persona e o contexto do RAG
        provider = settings.detect_active_provider()
        persona_prompt = get_persona_system_prompt(persona)

        prereq_desc = ""
        if prerequisites:
            prereq_desc = (
                f"Sigla: {prerequisites.sigla or 'N/A'} | "
                f"Feature: {prerequisites.feature or 'N/A'} | "
                f"ARQCOR: {prerequisites.arqcor or 'N/A'}"
            )

        system_instruction = f"""
{persona_prompt}

CONTEXTO TÉCNICO CORPORATIVO (RAG BV):
{context_text}

METADADOS DO PROJETO ATUAL:
{prereq_desc}

INSTRUÇÕES DO AGENTE DE BRAINSTORMING:
1. Responda de forma consultiva, propondo alternativas inteligentes e bem fundamentadas.
2. Evite respostas genéricas ou templates repetitivos; analise a necessidade específica do usuário.
3. Se o usuário estiver com dúvidas, apresente os prós e contras das tecnologias do catálogo BV.
4. Quando a proposta parecer madura ou o usuário sinalizar que concorda, conclua convidando-o a avançar:
   "Se estiver de acordo com essas diretrizes, podemos clicar em 'Prosseguir para Modelagem' (ou responder 'OK') para gerar o modelo ArchiMate oficial."
""".strip()

        if provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                reply = await cls._call_gemini(message, history, system_instruction, persona=persona)
                return reply, is_ok
            except Exception as e:
                logger.warning(f"Chamada ao Gemini falhou no brainstorm: {e}. Acionando assistente baseado em regras.")
        elif provider == "openai" and settings.OPENAI_API_KEY:
            try:
                reply = await cls._call_openai(message, history, system_instruction, persona=persona)
                return reply, is_ok
            except Exception as e:
                logger.warning(f"Chamada à OpenAI falhou no brainstorm: {e}. Acionando assistente baseado em regras.")

        # Fallback se estiver offline ou sem credencial de nuvem
        from app.services.cost_tracker import CostTracker
        persona_val = persona.value if hasattr(persona, "value") else str(persona)
        CostTracker.record_span(
            name="brainstorm_refinement",
            model="builtin",
            prompt_tokens=max(len(message) // 4, 40),
            completion_tokens=180,
            latency_ms=12.0,
            persona=persona_val,
        )
        fallback_reply = (
            f"Como {persona.value.capitalize()} do Banco BV, analisei sua solicitação para a feature '{prerequisites.feature if prerequisites else ''}'.\n\n"
            f"Com base nas diretrizes do banco, sugiro estruturarmos a solução combinando:\n"
            f"• Frontend corporativo (Angular 20 'ng' ou Streamlit)\n"
            f"• Camada de backend em Spring Boot ('sboot') ou Python ('pyweb') para orquestração\n"
            f"• Integração assíncrona orientada a eventos via Pub/Sub ('pubsub') e persistência segura no Cloud Storage ('gcs')\n\n"
            f"Gostaria de refinar algum ponto específico ou podemos avançar para a geração do modelo formal no Archi?"
        )
        return fallback_reply, is_ok

    @classmethod
    async def _call_gemini(
        cls,
        message: str,
        history: Optional[List[Dict[str, str]]],
        system_instruction: str,
        persona: Any = None,
    ) -> str:
        import time
        import httpx
        from app.services.cost_tracker import CostTracker

        url, headers = settings.get_gemini_request_config()
        contents = []

        if history:
            for h in history:
                role = "user" if h.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})

        contents.append({"role": "user", "parts": [{"text": message}]})

        payload = {
            "contents": contents,
            "systemInstruction": {"role": "system", "parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1024,
            }
        }
        t0 = time.perf_counter()
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            latency_ms = (time.perf_counter() - t0) * 1000
            usage = data.get("usageMetadata", {})
            CostTracker.record_span(
                name="brainstorm_refinement",
                model=settings.GEMINI_MODEL,
                prompt_tokens=usage.get("promptTokenCount", max((len(system_instruction) + len(message)) // 4, 80)),
                completion_tokens=usage.get("candidatesTokenCount", 250),
                latency_ms=latency_ms,
                persona=getattr(persona, "value", str(persona)) if persona else None,
            )
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    @classmethod
    async def _call_openai(
        cls,
        message: str,
        history: Optional[List[Dict[str, str]]],
        system_instruction: str,
        persona: Any = None,
    ) -> str:
        import time
        import httpx
        from app.services.cost_tracker import CostTracker

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        messages = [{"role": "system", "content": system_instruction}]
        if history:
            for h in history:
                messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
        messages.append({"role": "user", "content": message})

        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 1024,
        }
        t0 = time.perf_counter()
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            latency_ms = (time.perf_counter() - t0) * 1000
            usage = data.get("usage", {})
            CostTracker.record_span(
                name="brainstorm_refinement",
                model=settings.OPENAI_MODEL,
                prompt_tokens=usage.get("prompt_tokens", max((len(system_instruction) + len(message)) // 4, 80)),
                completion_tokens=usage.get("completion_tokens", 250),
                latency_ms=latency_ms,
                persona=getattr(persona, "value", str(persona)) if persona else None,
            )
            return data["choices"][0]["message"]["content"].strip()
