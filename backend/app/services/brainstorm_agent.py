"""Brainstorming Agent with Online LLM & Architecture RAG Service.

Facilitates the interactive refinement step of the architecture workflow,
incorporating the selected Persona (Architect vs Engineer) and retrieving
official BV technology and ArchiMate patterns to avoid repetitive templates.
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
    """Conversational brainstorming agent for architecture refinement."""

    @classmethod
    async def chat(
        cls,
        message: str,
        history: Optional[List[Dict[str, str]]] = None,
        prerequisites: Optional[PrerequisitesInfo] = None,
        persona: PersonaType = PersonaType.ARQUITETO,
    ) -> Tuple[str, bool]:
        """Interacts with user to brainstorm and refine architectural choices.
        
        Returns:
            (response_text, is_ready_for_modeling)
        """
        # 1. Retrieve relevant architectural context from BV RAG
        rag_chunks = ArchitectureRAGService.search(message, top_k=3)
        context_text = "\n\n".join([f"[{c['title']}]: {c['content']}" for c in rag_chunks])

        # 2. Check if the user is signaling approval ("Ok?", "pode gerar", "aprovado", "vamos em frente")
        ok_signals = [
            "ok", "está ok", "esta ok", "pode gerar", "pode modelar", "gerar modelo",
            "vamos em frente", "aprovado", "concordo", "perfeito", "prosseguir",
            "pode criar", "desenhar", "finalizar brainstorm"
        ]
        user_clean = message.strip().lower()
        is_ok = any(sig in user_clean for sig in ok_signals)

        # 3. Call Online LLM with Persona and RAG context
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
                reply = await cls._call_gemini(message, history, system_instruction)
                return reply, is_ok
            except Exception as e:
                logger.warning(f"Gemini brainstorm call failed: {e}. Falling back to rule-based assistant.")
        elif provider == "openai" and settings.OPENAI_API_KEY:
            try:
                reply = await cls._call_openai(message, history, system_instruction)
                return reply, is_ok
            except Exception as e:
                logger.warning(f"OpenAI brainstorm call failed: {e}. Falling back to rule-based assistant.")

        # Fallback if offline
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
        cls, message: str, history: Optional[List[Dict[str, str]]], system_instruction: str
    ) -> str:
        import httpx
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        contents = []

        if history:
            for h in history:
                role = "user" if h.get("role") == "user" else "model"
                contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})

        contents.append({"role": "user", "parts": [{"text": message}]})

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 1024,
            }
        }
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    @classmethod
    async def _call_openai(
        cls, message: str, history: Optional[List[Dict[str, str]]], system_instruction: str
    ) -> str:
        import httpx
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
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
