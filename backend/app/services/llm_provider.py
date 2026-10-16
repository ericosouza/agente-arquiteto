"""LLM Provider abstraction and Built-in Architectural Reasoning Engine.

Supports:
1. Built-in Expert Engine (zero-cost, offline, robust rule-based NLP architecture reasoning).
2. Google Gemini API.
3. OpenAI API.
4. Anthropic Claude API.
5. Ollama (local open-source models).
"""

import json
import logging
import re
from typing import Dict, Any, List, Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)


class BuiltinExpertEngine:
    """Expert Rule-Based Architectural Reasoning Engine.

    Acts as an experienced enterprise solutions architect:
    - Analyzes requirement complexity to avoid premature over-engineering.
    - Decides between Modular Monolith, Layered N-Tier, or BFF/Microservices.
    - Recommends proven, cost-effective technology stacks.
    - Specifies complete integrations with protocols, patterns, and justifications.
    """

    @classmethod
    def analyze_requirement(cls, description: str, constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        text = description.lower()
        constraints_text = " ".join(constraints).lower() if constraints else ""

        # Domain Entity & Capability Detection
        has_search = any(w in text for w in ["pesquis", "consult", "busc", "filtr", "procur"])
        has_crud = any(w in text for w in ["cadastro", "cadastr", "altera", "exclus", "crud", "manut"])
        has_auth = any(w in text for w in ["login", "autentic", "usuário", "usuario", "senha", "jwt", "permiss"]) or "auth" in constraints_text
        has_cache_need = any(w in text for w in ["alto volume", "rápido", "latência", "cache", "frequente", "alta escala"])
        has_async_need = any(w in text for w in ["assíncron", "fila", "mensageria", "evento", "notifica", "email", "job", "processamento em lote"])
        has_microservices_hint = any(w in text for w in ["microsserviço", "microserviço", "distribuíd", "alta escala"]) or "microservices" in constraints_text

        # Determine Main Entity Name (e.g. "Produtos", "Usuários", "Pedidos")
        entity_name = "Produtos"
        if "produto" in text or "itens" in text or "catálogo" in text:
            entity_name = "Produtos"
        elif "pedido" in text or "compra" in text or "venda" in text:
            entity_name = "Pedidos"
        elif "cliente" in text or "usuário" in text or "usuario" in text:
            entity_name = "Clientes"
        elif "veículo" in text or "carro" in text:
            entity_name = "Veículos"

        # Determine Architectural Style (Favor simplicity to avoid unnecessary complexity)
        if has_microservices_hint or (has_async_need and has_cache_need and len(text) > 250):
            style = "BFF com Microsserviços e Mensageria"
            style_justification = (
                "Para requisitos que demandam desacoplamento distribuído e processamento assíncrono, "
                "a arquitetura com BFF e microsserviços especializados isola domínios e facilita escala independente."
            )
            is_microservices = True
        else:
            style = "Monolito Modular com Frontend SPA"
            style_justification = (
                "Para a complexidade inicial informada, um Monolito Modular evita o overhead operacional "
                "de microsserviços (redes distribuídas, transações distribuídas, tracing complexo), mantendo baixo custo, "
                "alta coesão interna e simplicidade de manutenção."
            )
            is_microservices = False

        # Build Components
        components = []
        integrations = []

        # 1. Frontend
        frontend_tech = "React com TypeScript"
        if "angular" in text or "angular" in constraints_text:
            frontend_tech = "Angular"
        elif "vue" in text or "vue" in constraints_text:
            frontend_tech = "Vue.js"

        components.append({
            "id": "COMP-FE",
            "name": f"Frontend Web SPA ({frontend_tech.split()[0]})",
            "category": "Frontend",
            "responsibility": f"Interface com o usuário para {('cadastro, consulta e ' if has_crud else '')}gestão de {entity_name.lower()}.",
            "suggestedTechnology": frontend_tech,
            "alternativeTechnology": "Angular" if "React" in frontend_tech else "React com TypeScript",
            "justification": f"Framework maduro para Single Page Application com tipagem estática e rica experiência do usuário.",
            "layer": "Application",
            "archimateType": "ApplicationComponent",
        })

        # 2. Backend Service(s)
        backend_tech = "Python com FastAPI"
        if "spring" in text or "java" in text or "java" in constraints_text:
            backend_tech = "Java com Spring Boot"
        elif "c#" in text or "asp.net" in text or ".net" in text or "dotnet" in constraints_text:
            backend_tech = "C# com ASP.NET Core"
        elif "node" in text or "nest" in text:
            backend_tech = "Node.js com NestJS"

        if is_microservices:
            # BFF Component
            components.append({
                "id": "COMP-BFF",
                "name": "Backend For Frontend (BFF)",
                "category": "BFF",
                "responsibility": "Orquestração de chamadas, agregação de payloads e adaptação para o Frontend.",
                "suggestedTechnology": "Node.js com NestJS" if "FastAPI" in backend_tech else "Python com FastAPI",
                "alternativeTechnology": backend_tech,
                "justification": "Isola o cliente web de múltiplos contratos de backend e centraliza validações de borda.",
                "layer": "Application",
                "archimateType": "ApplicationComponent",
            })

            # Domain Service
            components.append({
                "id": "COMP-BE-CORE",
                "name": f"Serviço de {entity_name}",
                "category": "Backend",
                "responsibility": f"Lógica de negócio, regras de validação e persistência de {entity_name.lower()}.",
                "suggestedTechnology": backend_tech,
                "alternativeTechnology": "Java com Spring Boot" if "Python" in backend_tech else "Python com FastAPI",
                "justification": "Alta performance para APIs RESTful, facilidade de implementação e suporte robusto a transações.",
                "layer": "Application",
                "archimateType": "ApplicationComponent",
            })

            # Integration: FE -> BFF
            integrations.append({
                "id": "INT-FE-BFF",
                "sourceComponentId": "COMP-FE",
                "targetComponentId": "COMP-BFF",
                "relationshipType": "Serving",
                "protocol": "HTTP/REST (HTTPS)",
                "communicationPattern": "Synchronous",
                "purpose": f"Consumo de telas de consulta e cadastro de {entity_name.lower()}.",
            })

            # Integration: BFF -> Domain Service
            integrations.append({
                "id": "INT-BFF-CORE",
                "sourceComponentId": "COMP-BFF",
                "targetComponentId": "COMP-BE-CORE",
                "relationshipType": "Serving",
                "protocol": "gRPC ou HTTP/REST",
                "communicationPattern": "Synchronous",
                "purpose": f"Encaminhamento de comandos de negócio e consulta de dados de {entity_name.lower()}.",
            })
            core_backend_id = "COMP-BE-CORE"
        else:
            # Monolith Backend
            components.append({
                "id": "COMP-BE",
                "name": f"API Backend de {entity_name}",
                "category": "Backend",
                "responsibility": f"Endpoints REST, regras de negócio e persistência de dados de {entity_name.lower()}.",
                "suggestedTechnology": backend_tech,
                "alternativeTechnology": "Java com Spring Boot" if "Python" in backend_tech else "Python com FastAPI",
                "justification": "Arquitetura limpa com documentação automática OpenAPI, validações estritas e rápida execução.",
                "layer": "Application",
                "archimateType": "ApplicationComponent",
            })

            # Integration: FE -> BE
            integrations.append({
                "id": "INT-FE-BE",
                "sourceComponentId": "COMP-FE",
                "targetComponentId": "COMP-BE",
                "relationshipType": "Serving",
                "protocol": "HTTP/REST (HTTPS)",
                "communicationPattern": "Synchronous",
                "purpose": f"Envio e consulta de {entity_name.lower()} via endpoints REST JSON.",
            })
            core_backend_id = "COMP-BE"

        # 3. Database
        db_tech = "PostgreSQL"
        if "mysql" in text or "mysql" in constraints_text:
            db_tech = "MySQL"
        elif "mongo" in text or "mongodb" in constraints_text:
            db_tech = "MongoDB"
        elif "sql server" in text:
            db_tech = "SQL Server"

        components.append({
            "id": "COMP-DB",
            "name": f"Banco de Dados ({db_tech})",
            "category": "Database",
            "responsibility": f"Armazenamento relacional e integridade ACID dos registros de {entity_name.lower()}.",
            "suggestedTechnology": db_tech,
            "alternativeTechnology": "MySQL" if db_tech == "PostgreSQL" else "PostgreSQL",
            "justification": "SGBD relacional de código aberto mais avançado do mercado, com suporte a índices B-Tree e JSONB.",
            "layer": "Technology",
            "archimateType": "SystemSoftware",
        })

        # Integration: Backend -> DB
        integrations.append({
            "id": "INT-BE-DB",
            "sourceComponentId": core_backend_id,
            "targetComponentId": "COMP-DB",
            "relationshipType": "Access",
            "protocol": "TCP / Driver Nativo (Porta 5432)",
            "communicationPattern": "Synchronous",
            "purpose": f"Execução de queries SQL de inserção, atualização e consultas com filtros de {entity_name.lower()}.",
        })

        # 4. Cache (if requested or justified by search)
        if has_cache_need or (has_search and is_microservices):
            components.append({
                "id": "COMP-CACHE",
                "name": "Cache em Memória (Redis)",
                "category": "Cache",
                "responsibility": f"Cache de consultas frequentes de {entity_name.lower()} por categoria e preço para reduzir carga no banco.",
                "suggestedTechnology": "Redis",
                "alternativeTechnology": "Memcached",
                "justification": "Estrutura chave-valor em memória com latência sub-milissegundo para alívio de queries de leitura repetitivas.",
                "layer": "Technology",
                "archimateType": "SystemSoftware",
            })
            integrations.append({
                "id": "INT-BE-CACHE",
                "sourceComponentId": core_backend_id,
                "targetComponentId": "COMP-CACHE",
                "relationshipType": "Access",
                "protocol": "RESP (Redis Protocol - Porta 6379)",
                "communicationPattern": "Synchronous",
                "purpose": f"Armazenar em cache o catálogo de {entity_name.lower()} com TTL (Time-To-Live).",
            })

        # 5. Messaging / Events (if justified)
        if has_async_need:
            msg_tech = "RabbitMQ"
            if "kafka" in text or "kafka" in constraints_text:
                msg_tech = "Apache Kafka"

            components.append({
                "id": "COMP-MSG",
                "name": f"Broker de Mensageria ({msg_tech})",
                "category": "Messaging",
                "responsibility": f"Fila de eventos de alteração de {entity_name.lower()} e desacoplamento de notificações.",
                "suggestedTechnology": msg_tech,
                "alternativeTechnology": "RabbitMQ" if msg_tech == "Apache Kafka" else "Apache Kafka",
                "justification": "Garante entrega resiliente de mensagens e processamento assíncrono desacoplado.",
                "layer": "Technology",
                "archimateType": "SystemSoftware",
            })
            integrations.append({
                "id": "INT-BE-MSG",
                "sourceComponentId": core_backend_id,
                "targetComponentId": "COMP-MSG",
                "relationshipType": "Flow",
                "protocol": "AMQP (Porta 5672)" if msg_tech == "RabbitMQ" else "Kafka TCP",
                "communicationPattern": "Asynchronous",
                "purpose": f"Publicação de eventos de domínio (ex: {entity_name[:-1]}Criado, {entity_name[:-1]}Atualizado).",
            })

        # Non-Functional Requirements
        nfrs = [
            {
                "category": "Segurança",
                "description": "Comunicação criptografada via HTTPS/TLS 1.3, sanitização de inputs contra SQL Injection e políticas CORS restritivas no backend.",
            },
            {
                "category": "Desempenho",
                "description": f"Indexação adequada no banco de dados para campos de busca frequente (nome, categoria, preço) garantindo resposta < 200ms.",
            },
            {
                "category": "Disponibilidade",
                "description": "Containerização dos componentes com Docker para reinício automático e facilidade de deploy com health checks.",
            },
            {
                "category": "Escalabilidade",
                "description": "Separação stateless do backend e frontend, permitindo escalabilidade horizontal das instâncias de aplicação conforme a demanda.",
            },
        ]

        # Architectural Decisions
        decisions = [
            {
                "decision": f"Estilo Arquitetural: {style}",
                "rationale": style_justification,
                "status": "Recomendado",
            },
            {
                "decision": f"Persistência Primária com {db_tech}",
                "rationale": f"Garante integridade referencial e transacional para {entity_name.lower()}, com excelente suporte a índices e baixo custo operacional.",
                "status": "Recomendado",
            },
            {
                "decision": "Desacoplamento de Frontend SPA e API RESTful",
                "rationale": "Permite evolução independente da interface visual e da lógica de negócio, além de viabilizar futuros clientes móveis ou integrações.",
                "status": "Recomendado",
            },
        ]

        return {
            "id": "PROP-" + str(abs(hash(description)) % 100000),
            "title": f"Arquitetura de Software: Sistema de {entity_name}",
            "summary": (
                f"Proposta arquitetural projetada para atender aos requisitos de {entity_name.lower()}. "
                f"Utiliza {style} priorizando simplicidade de implantação, robustez técnica e conformidade com boas práticas de engenharia de software."
            ),
            "architecturalStyle": style,
            "styleJustification": style_justification,
            "components": components,
            "integrations": integrations,
            "decisions": decisions,
            "nonFunctionalRequirements": nfrs,
            "status": "proposed",
            "version": 1,
        }

    @classmethod
    def refine_proposal(cls, proposal_dict: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Incorporates user feedback into the existing proposal."""
        fb = feedback.lower()
        components = proposal_dict.get("components", [])
        integrations = proposal_dict.get("integrations", [])
        decisions = proposal_dict.get("decisions", [])

        # Technology substitution commands
        if "postgres" in fb:
            for c in components:
                if c["category"] == "Database":
                    c["name"] = "Banco de Dados (PostgreSQL)"
                    c["suggestedTechnology"] = "PostgreSQL"
                    c["justification"] = "Alterado conforme solicitação do usuário para PostgreSQL."
        elif "mysql" in fb:
            for c in components:
                if c["category"] == "Database":
                    c["name"] = "Banco de Dados (MySQL)"
                    c["suggestedTechnology"] = "MySQL"
                    c["justification"] = "Alterado conforme solicitação do usuário para MySQL."
        elif "mongo" in fb or "mongodb" in fb:
            for c in components:
                if c["category"] == "Database":
                    c["name"] = "Banco de Dados (MongoDB)"
                    c["suggestedTechnology"] = "MongoDB"
                    c["justification"] = "Alterado conforme solicitação do usuário para MongoDB (NoSQL baseado em documentos)."

        if "angular" in fb:
            for c in components:
                if c["category"] == "Frontend":
                    c["name"] = "Frontend Web (Angular)"
                    c["suggestedTechnology"] = "Angular"
        elif "vue" in fb:
            for c in components:
                if c["category"] == "Frontend":
                    c["name"] = "Frontend Web (Vue.js)"
                    c["suggestedTechnology"] = "Vue.js"
        elif "react" in fb:
            for c in components:
                if c["category"] == "Frontend":
                    c["name"] = "Frontend Web (React)"
                    c["suggestedTechnology"] = "React com TypeScript"

        if "spring" in fb or "java" in fb:
            for c in components:
                if c["category"] == "Backend":
                    c["name"] = "Backend API (Spring Boot)"
                    c["suggestedTechnology"] = "Java com Spring Boot"
        elif "fastapi" in fb or "python" in fb:
            for c in components:
                if c["category"] == "Backend":
                    c["name"] = "Backend API (FastAPI)"
                    c["suggestedTechnology"] = "Python com FastAPI"
        elif "nest" in fb or "node" in fb:
            for c in components:
                if c["category"] == "Backend":
                    c["name"] = "Backend API (NestJS)"
                    c["suggestedTechnology"] = "Node.js com NestJS"
        elif "asp.net" in fb or "c#" in fb or ".net" in fb:
            for c in components:
                if c["category"] == "Backend":
                    c["name"] = "Backend API (ASP.NET Core)"
                    c["suggestedTechnology"] = "C# com ASP.NET Core"

        # Add Redis / Cache if requested
        has_cache = any(c["category"] == "Cache" for c in components)
        if ("adicion" in fb or "inclu" in fb) and ("cache" in fb or "redis" in fb) and not has_cache:
            cache_id = "COMP-CACHE"
            components.append({
                "id": cache_id,
                "name": "Cache em Memória (Redis)",
                "category": "Cache",
                "responsibility": "Armazenamento em cache de consultas para redução de latência.",
                "suggestedTechnology": "Redis",
                "alternativeTechnology": "Memcached",
                "justification": "Adicionado conforme instrução do usuário.",
                "layer": "Technology",
                "archimateType": "SystemSoftware",
            })
            # Connect to backend
            be_comp = next((c for c in components if c["category"] == "Backend"), None)
            if be_comp:
                integrations.append({
                    "id": f"INT-{be_comp['id']}-CACHE",
                    "sourceComponentId": be_comp["id"],
                    "targetComponentId": cache_id,
                    "relationshipType": "Access",
                    "protocol": "RESP (Porta 6379)",
                    "communicationPattern": "Synchronous",
                    "purpose": "Consulta e invalidação de cache.",
                })

        # Add Messaging / RabbitMQ / Kafka if requested
        has_msg = any(c["category"] == "Messaging" for c in components)
        if ("adicion" in fb or "inclu" in fb) and ("fila" in fb or "mensageria" in fb or "kafka" in fb or "rabbitmq" in fb) and not has_msg:
            msg_tech = "Apache Kafka" if "kafka" in fb else "RabbitMQ"
            msg_id = "COMP-MSG"
            components.append({
                "id": msg_id,
                "name": f"Broker de Mensageria ({msg_tech})",
                "category": "Messaging",
                "responsibility": "Comunicação assíncrona orientada a eventos.",
                "suggestedTechnology": msg_tech,
                "alternativeTechnology": "RabbitMQ" if msg_tech == "Apache Kafka" else "Apache Kafka",
                "justification": "Adicionado para suportar processamento assíncrono.",
                "layer": "Technology",
                "archimateType": "SystemSoftware",
            })
            be_comp = next((c for c in components if c["category"] == "Backend"), None)
            if be_comp:
                integrations.append({
                    "id": f"INT-{be_comp['id']}-MSG",
                    "sourceComponentId": be_comp["id"],
                    "targetComponentId": msg_id,
                    "relationshipType": "Flow",
                    "protocol": "AMQP / Kafka TCP",
                    "communicationPattern": "Asynchronous",
                    "purpose": "Publicação de eventos assíncronos.",
                })

        decisions.append({
            "decision": f"Ajuste solicitado pelo usuário",
            "rationale": f"Incorporação da instrução: '{feedback}'.",
            "status": "Recomendado",
        })

        proposal_dict["version"] = proposal_dict.get("version", 1) + 1
        proposal_dict["status"] = "modified"
        return proposal_dict


class LLMService:
    """Orchestrates LLM calls across external providers and the builtin expert engine."""

    @classmethod
    async def analyze_and_propose(cls, description: str, constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        provider = settings.detect_active_provider()
        logger.info(f"Active LLM provider: {provider}")

        if provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                return await cls._call_gemini_for_proposal(description, constraints)
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}. Falling back to Builtin Expert Engine.")

        elif provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return await cls._call_openai_for_proposal(description, constraints)
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}. Falling back to Builtin Expert Engine.")

        elif provider == "ollama":
            try:
                return await cls._call_ollama_for_proposal(description, constraints)
            except Exception as e:
                logger.warning(f"Ollama call failed: {e}. Falling back to Builtin Expert Engine.")

        # Default fallback: Built-in Expert Engine
        return BuiltinExpertEngine.analyze_requirement(description, constraints)

    @classmethod
    async def refine_proposal(cls, proposal_dict: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        provider = settings.detect_active_provider()
        if provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                return await cls._call_gemini_for_refinement(proposal_dict, feedback)
            except Exception as e:
                logger.warning(f"Gemini refinement failed: {e}. Falling back to Builtin Expert Engine.")

        elif provider == "openai" and settings.OPENAI_API_KEY:
            try:
                return await cls._call_openai_for_refinement(proposal_dict, feedback)
            except Exception as e:
                logger.warning(f"OpenAI refinement failed: {e}. Falling back to Builtin Expert Engine.")

        return BuiltinExpertEngine.refine_proposal(proposal_dict, feedback)

    @classmethod
    async def _call_gemini_for_proposal(cls, description: str, constraints: Optional[List[str]]) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        system_instruction = (
            "Você é um arquiteto de soluções de software sênior. Responda ESTRITAMENTE em formato JSON puro "
            "sem markdown ou blocos de código adicionais. Não crie complexidade desnecessária."
        )
        prompt = f"""
        Descrição da necessidade do sistema: "{description}"
        Restrições: {constraints or []}

        Gere a proposta arquitetural seguindo a estrutura JSON:
        {{
          "id": "PROP-1",
          "title": "Nome da Solução",
          "summary": "Resumo executivo",
          "architecturalStyle": "Monolito Modular ou BFF com Microsserviços",
          "styleJustification": "Justificativa de por que este estilo foi escolhido evitando complexidade desnecessária",
          "components": [
            {{
              "id": "COMP-1",
              "name": "Nome do Componente",
              "category": "Frontend | Backend | BFF | Database | Cache | Messaging",
              "responsibility": "Responsabilidade arquitetural clara",
              "suggestedTechnology": "Tecnologia principal sugerida",
              "alternativeTechnology": "Tecnologia alternativa",
              "justification": "Justificativa técnica",
              "layer": "Business | Application | Technology",
              "archimateType": "ApplicationComponent | SystemSoftware | Node | DataObject"
            }}
          ],
          "integrations": [
            {{
              "id": "INT-1",
              "sourceComponentId": "COMP-1",
              "targetComponentId": "COMP-2",
              "relationshipType": "Serving | Access | Flow",
              "protocol": "HTTP/REST, JDBC, etc.",
              "communicationPattern": "Synchronous ou Asynchronous",
              "purpose": "Finalidade objetiva da integração"
            }}
          ],
          "decisions": [
            {{
              "decision": "Título da decisão",
              "rationale": "Justificativa técnica",
              "status": "Recomendado"
            }}
          ],
          "nonFunctionalRequirements": [
            {{
              "category": "Segurança | Desempenho | Disponibilidade | Escalabilidade",
              "description": "Descrição do requisito e mitigação"
            }}
          ],
          "status": "proposed",
          "version": 1
        }}
        """

        payload = {
            "contents": [{"parts": [{"text": f"{system_instruction}\n\n{prompt}"}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(cls._clean_json(raw_text))

    @classmethod
    async def _call_gemini_for_refinement(cls, proposal: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        prompt = f"""
        Proposta atual:
        {json.dumps(proposal, ensure_ascii=False)}

        Feedback/Ajustes solicitados pelo usuário:
        "{feedback}"

        Incorpore os ajustes na proposta mantendo a mesma estrutura JSON. Atualize a versão e mude o status para 'modified'.
        Responda APENAS o JSON válido.
        """
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(cls._clean_json(raw_text))

    @classmethod
    async def _call_openai_for_proposal(cls, description: str, constraints: Optional[List[str]]) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        prompt = f"""
        Descrição da necessidade do sistema: "{description}"
        Restrições: {constraints or []}
        Atue como Arquiteto de Software sênior. Responda em JSON válido com campos: id, title, summary, architecturalStyle, styleJustification, components, integrations, decisions, nonFunctionalRequirements, status, version.
        """
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": "Você é um arquiteto de software. Responda exclusivamente em JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)

    @classmethod
    async def _call_openai_for_refinement(cls, proposal: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        prompt = f"""
        Proposta atual: {json.dumps(proposal, ensure_ascii=False)}
        Instrução de alteração do usuário: "{feedback}"
        Incorpore as alterações e devolva o JSON atualizado.
        """
        payload = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": "Você é um arquiteto de software. Responda em JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)

    @classmethod
    async def _call_ollama_for_proposal(cls, description: str, constraints: Optional[List[str]]) -> Dict[str, Any]:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        prompt = f"""
        Como arquiteto de software, projete a solução para: "{description}".
        Responda em formato JSON contendo: id, title, summary, architecturalStyle, styleJustification, components, integrations, decisions, nonFunctionalRequirements.
        """
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            raw_text = resp.json().get("response", "{}")
            return json.loads(cls._clean_json(raw_text))

    @staticmethod
    def _clean_json(text: str) -> str:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()
