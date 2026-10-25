"""LLM Provider abstraction and Built-in Architectural Reasoning Engine.

Supports:
1. Prerequisite extraction & validation (Iniciativa, Sigla, Feature, ARQCOR).
2. Standardized component naming:
   - Backend (sboot, pyweb): [sigla-tecnologia]-[sigla-sistema]-[modulo]-[tipo]-[dominio]
   - Other catalog techs (ng, streamlit, sbatch, dataflowbatch, gcs, genaigke, pubsub):
     [sigla-tecnologia]-[sigla-sistema]-[modulo]-[dominio]
3. Built-in Expert Engine (zero-cost, offline, robust rule-based NLP architecture reasoning).
4. External LLM Providers (Google Gemini, OpenAI, Ollama) with schema & naming normalization.
"""

import json
import logging
import re
import unicodedata
from typing import Dict, Any, List, Optional, Tuple
import httpx
from app.config import settings
from app.models.proposal import PrerequisitesInfo

logger = logging.getLogger(__name__)

# Official Technology Mapping
TECH_CATALOG: Dict[str, Dict[str, Any]] = {
    "ng": {
        "sigla": "ng",
        "name": "Frontend Angular 20",
        "alternative": "Streamlit",
        "category": "Frontend",
        "layer": "Channel",
        "archimateType": "ApplicationComponent",
        "has_backend_type": False,
        "justification": "Framework SPA corporativo (Angular 20) na camada de Canal (Channel Layer) para interfaces web ricas e escaláveis.",
    },
    "streamlit": {
        "sigla": "streamlit",
        "name": "Streamlit (Frontend de Baixa Complexidade)",
        "alternative": "Frontend Angular 20",
        "category": "Frontend",
        "layer": "Channel",
        "archimateType": "ApplicationComponent",
        "has_backend_type": False,
        "justification": "Framework ágil na camada de Canal (Channel Layer) para interfaces web de baixa complexidade e dashboards.",
    },
    "sboot": {
        "sigla": "sboot",
        "name": "Spring Boot Java",
        "alternative": "Backend em Python (pyweb)",
        "category": "Backend",
        "layer": "Application",
        "archimateType": "ApplicationComponent",
        "has_backend_type": True,
        "justification": "Ecossistema corporativo Java com Spring Boot para microsserviços robustos, seguros e de alta performance.",
    },
    "pyweb": {
        "sigla": "pyweb",
        "name": "Backend em Python",
        "alternative": "Spring Boot Java (sboot)",
        "category": "Backend",
        "layer": "Application",
        "archimateType": "ApplicationComponent",
        "has_backend_type": True,
        "justification": "Serviço backend em Python com alta produtividade, ideal para APIs REST, orquestração e integração com dados/IA.",
    },
    "sbatch": {
        "sigla": "sbatch",
        "name": "Spring Batch",
        "alternative": "Google Cloud Dataflow (dataflowbatch)",
        "category": "Backend",
        "layer": "Application",
        "archimateType": "ApplicationComponent",
        "has_backend_type": False,
        "justification": "Processamento em lote (batch) transacional e resiliente baseado em Spring Batch.",
    },
    "dataflowbatch": {
        "sigla": "dataflowbatch",
        "name": "Google Cloud Dataflow",
        "alternative": "Spring Batch (sbatch)",
        "category": "Backend",
        "layer": "Application",
        "archimateType": "ApplicationComponent",
        "has_backend_type": False,
        "justification": "Processamento distribuído de dados em lote (Dataflow Batch) gerenciado e escalável na nuvem.",
    },
    "gcs": {
        "sigla": "gcs",
        "name": "Google Cloud Storage",
        "alternative": "Banco de Dados de Documentos",
        "category": "Infrastructure",
        "layer": "Technology",
        "archimateType": "SystemSoftware",
        "has_backend_type": False,
        "justification": "Armazenamento de objetos altamente durável e escalável no Google Cloud Storage (GCS).",
    },
    "genaigke": {
        "sigla": "genaigke",
        "name": "GenAI no GKE (Agente)",
        "alternative": "Vertex AI Agent",
        "category": "Backend",
        "layer": "Application",
        "archimateType": "ApplicationComponent",
        "has_backend_type": False,
        "justification": "Agente de Inteligência Artificial Generativa implantado em cluster GKE para raciocínio e automação.",
    },
    "pubsub": {
        "sigla": "pubsub",
        "name": "Google Cloud Pub/Sub (Tópico e Subscription)",
        "alternative": "Apache Kafka",
        "category": "Messaging",
        "layer": "Technology",
        "archimateType": "SystemSoftware",
        "has_backend_type": False,
        "justification": "Mensageria assíncrona gerenciada com tópicos e subscriptions no Google Cloud Pub/Sub.",
    },
}

STOPWORDS_PT = {
    "de", "da", "do", "dos", "das", "em", "no", "na", "nos", "nas", "para", "por", "com", "sem",
    "um", "uma", "uns", "umas", "o", "a", "os", "as", "e", "ou", "que", "se", "ao", "aos",
    "sistema", "projeto", "feature", "features", "feat", "funcionalidade", "iniciativa", "arqcor",
    "modulo", "módulo", "sigla", "qual", "quais", "como", "onde", "quando", "porque",
    "quero", "preciso", "desenvolver", "criar", "construir", "fazer", "web", "app", "aplicacao",
    "aplicação", "servico", "serviço", "componente", "novo", "nova", "gestao", "gestão",
    "gerenciamento", "controle", "processamento", "plataforma", "solucao", "solução", "tela",
    "front", "frontend", "backend", "api", "java", "python", "spring", "boot", "angular",
    "streamlit", "batch", "dataflow", "gcs", "pubsub", "genai", "gke", "agente", "banco",
    "dados", "cliente", "clientes", "usuario", "usuarios", "usuário", "usuários", "deve",
    "devera", "deverá", "armazenar", "salvar", "guardar", "futuro", "gerar", "permitir",
    "possibilitar", "realizar", "efetuar", "ter", "haver", "ser", "esta", "este", "isso",
    "cadastro", "cadastrar", "consulta", "consultar", "alteracao", "alteração", "exclusao",
    "exclusão", "manutencao", "manutenção", "calculo", "cálculo", "monitoramento",
}

CHANNEL_KEYWORDS = ["portal", "painel", "dashboard", "console", "canal", "jornada"]


def strip_accents(text: str) -> str:
    """Removes accents and diacritics from text."""
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c))


def slugify_domain(raw_text: str, fallback: str = "sistema-negocio", max_words: int = 3) -> str:
    """Creates a clean 1-to-3 word hyphenated domain slug that makes business sense."""
    if not raw_text:
        return fallback
    cleaned = strip_accents(raw_text.lower())
    tokens = re.findall(r"[a-z0-9]+", cleaned)
    meaningful = [
        t for t in tokens
        if t not in STOPWORDS_PT
        and len(t) > 1
        and not t.isdigit()
        and not re.match(r"^(?:feat|arq|inc|us|ep|id|comp|rel)\d*$", t)
    ]
    if not meaningful:
        meaningful = [
            t for t in tokens
            if len(t) > 1
            and t not in {"de", "da", "do", "para", "com", "feat", "feature", "sigla", "arqcor", "iniciativa"}
            and not t.isdigit()
        ][:max_words]
    if not meaningful:
        return fallback
    selected = meaningful[:max_words]
    return "-".join(selected)


def infer_contextual_domains(
    description: str,
    prerequisites: Optional[PrerequisitesInfo] = None,
    sigla: str = "",
) -> Dict[str, str]:
    """Infers meaningful, context-aware domain names for each component role:
    - 'channel': for Frontend (ng/streamlit) and BFF (e.g. 'portal-esg')
    - 'atom': for Atomic backend and DB, independent of portal/UI (e.g. 'sistema-esg' or 'base-esg' or 'risco-ambiental')
    - 'orch': for Orchestrator (e.g. 'integracao-esg' or atom domain)
    - 'batch': for Batch / Dataflow (e.g. 'relatorio-esg' or atom domain)
    - 'storage': for GCS (e.g. 'arquivos-esg' or 'relatorio-esg')
    - 'messaging': for Pub/Sub (e.g. 'eventos-esg' or atom domain)
    """
    # Remove labeled prerequisite lines (e.g. "Sigla: SESG", "ARQCOR: ARQ-1", "Feature: feat") from raw text
    cleaned_lines = []
    for line in (description or "").splitlines():
        if re.match(r"^\s*(?:qual\s+)?(?:sigla|arqcor|iniciativa)\b\s*[:=\-]", line, re.IGNORECASE):
            continue
        m_feat_line = re.match(r"^\s*(?:qual\s+)?(?:feature|funcionalidade)\b\s*[:=\-]\s*(.+)$", line, re.IGNORECASE)
        if m_feat_line:
            f_val = m_feat_line.group(1).strip()
            # Keep feature value only if it is not a generic placeholder like 'feat' or 'FEAT-01'
            if not re.match(r"^(?:feat(?:ure)?[\s\-_\d]*|f\d+|us\d+)$", f_val, re.IGNORECASE):
                cleaned_lines.append(f_val)
            continue
        cleaned_lines.append(line)

    if prerequisites:
        if prerequisites.feature and not re.match(r"^(?:feat(?:ure)?[\s\-_\d]*|f\d+|us\d+)$", prerequisites.feature.strip(), re.IGNORECASE):
            cleaned_lines.append(prerequisites.feature)
        if prerequisites.iniciativa and not re.match(r"^(?:ini(?:ciativa)?[\s\-_\d]*)$", prerequisites.iniciativa.strip(), re.IGNORECASE):
            cleaned_lines.append(prerequisites.iniciativa)

    narrative = strip_accents(" ".join(cleaned_lines).lower())
    sigla_low = (sigla or "").lower().strip()

    # 1. Detect channel keyword (e.g. "portal", "painel", "dashboard")
    channel_word: Optional[str] = None
    for cw in CHANNEL_KEYWORDS:
        if re.search(rf"\b{cw}\b", narrative):
            channel_word = cw
            break

    # 2. Detect explicit "sistema <X>" or "portal <X>" or core subject
    explicit_sistema_subject: Optional[str] = None
    m_sis = re.search(
        r"\bsistema\s+(?:de\s+|do\s+|da\s+|para\s+)?([a-z0-9]+(?:\s+[a-z0-9]+){0,2})",
        narrative,
    )
    if m_sis:
        cand_tokens = [
            t for t in m_sis.group(1).split()
            if t not in STOPWORDS_PT and t not in CHANNEL_KEYWORDS and t != sigla_low and len(t) > 1 and not t.isdigit()
        ]
        if cand_tokens:
            explicit_sistema_subject = "-".join(cand_tokens[:2])

    # Extract general meaningful business tokens from narrative
    all_tokens = re.findall(r"[a-z0-9]+", narrative)
    domain_tokens: List[str] = []
    for t in all_tokens:
        if (
            t not in STOPWORDS_PT
            and t not in CHANNEL_KEYWORDS
            and t != sigla_low
            and len(t) > 1
            and not t.isdigit()
            and not re.match(r"^(?:feat|arq|inc|us|ep|id)\d*$", t)
            and t not in domain_tokens
        ):
            domain_tokens.append(t)

    # Determine primary business subject (1 to 3 words)
    if explicit_sistema_subject:
        core_subject = explicit_sistema_subject
    elif domain_tokens:
        core_subject = "-".join(domain_tokens[:2])
    else:
        core_subject = "negocio"

    core_words = core_subject.split("-")
    short_subject = "-".join(core_words[:2])

    # Build atom_domain (Core/Atomic service domain — never uses 'portal')
    if explicit_sistema_subject:
        atom_domain = f"sistema-{short_subject}" if len(core_words) <= 2 else "-".join(core_words[:3])
    elif len(core_words) == 1:
        atom_domain = f"sistema-{core_words[0]}"
    else:
        atom_domain = "-".join(core_words[:3])

    # Build channel_domain (Frontend & BFF domain — uses 'portal-<subject>' if channel_word detected)
    if channel_word:
        channel_domain = f"{channel_word}-{short_subject}"
    else:
        channel_domain = atom_domain if not atom_domain.startswith("sistema-") else f"portal-{short_subject}"

    # Contextual secondary domains
    has_relatorio = "relatorio" in narrative or "relatorios" in narrative
    batch_domain = f"relatorio-{core_words[0]}" if has_relatorio else atom_domain
    storage_domain = f"arquivos-{core_words[0]}" if not has_relatorio else f"relatorio-{core_words[0]}"
    orch_domain = atom_domain
    messaging_domain = f"eventos-{core_words[0]}" if len(core_words) == 1 else atom_domain

    return {
        "channel": channel_domain,
        "atom": atom_domain,
        "orch": orch_domain,
        "batch": batch_domain,
        "storage": storage_domain,
        "messaging": messaging_domain,
        "default": atom_domain,
    }


def build_component_name(
    tech_sigla: str,
    system_sigla: str,
    modulo: str = "base",
    tipo: Optional[str] = None,
    dominio: str = "sistema-negocio",
) -> str:
    """Formats component name according to the strict architectural standard:
    - Backend (sboot, pyweb): [sigla-tecnologia]-[sigla-sistema]-[modulo]-[tipo]-[dominio]
    - Others: [sigla-tecnologia]-[sigla-sistema]-[modulo]-[dominio]
    """
    tech_clean = strip_accents(tech_sigla.lower().strip())
    sys_clean = re.sub(r"[^a-z]", "", strip_accents(system_sigla.lower().strip()))[:4]
    if len(sys_clean) < 4:
        sys_clean = (sys_clean + "xxxx")[:4]
    mod_clean = re.sub(r"[^a-z0-9-]", "", strip_accents(modulo.lower().strip())) or "base"

    # If dominio is already a valid hyphenated slug (e.g. 'portal-esg' or 'sistema-esg'), preserve its tokens
    raw_dom_tokens = re.findall(r"[a-z0-9]+", strip_accents((dominio or "").lower()))
    preserved_prefixes = {"portal", "painel", "dashboard", "sistema", "base", "relatorio", "eventos", "arquivos", "integracao"}
    filtered_dom = [
        t for t in raw_dom_tokens
        if (t in preserved_prefixes or t not in STOPWORDS_PT)
        and len(t) > 1
        and not t.isdigit()
        and not re.match(r"^(?:feat|arq|inc|us|ep|id)\d*$", t)
    ]
    if filtered_dom:
        dom_clean = "-".join(filtered_dom[:3])
    else:
        dom_clean = slugify_domain(dominio, fallback="sistema-negocio", max_words=3)

    if tech_clean in ("sboot", "pyweb"):
        tipo_clean = (tipo or "atom").lower().strip()
        if tipo_clean not in ("atom", "bff", "orch"):
            tipo_clean = "atom"
        return f"{tech_clean}-{sys_clean}-{mod_clean}-{tipo_clean}-{dom_clean}"
    else:
        return f"{tech_clean}-{sys_clean}-{mod_clean}-{dom_clean}"


class PrerequisiteExtractor:
    """Extracts and validates the 4 mandatory prerequisites:
    1. Qual iniciativa?
    2. Qual Sigla do projeto? (4 letters)
    3. Qual feature?
    4. Qual ARQCOR?
    """

    @classmethod
    def extract(
        cls,
        current_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
        existing: Optional[PrerequisitesInfo] = None,
    ) -> PrerequisitesInfo:
        info = PrerequisitesInfo(
            iniciativa=existing.iniciativa if existing else None,
            sigla=existing.sigla if existing else None,
            feature=existing.feature if existing else None,
            arqcor=existing.arqcor if existing else None,
        )

        user_messages: List[str] = []
        if history:
            for msg in history:
                role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "role", None)
                content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
                if role == "user" and content:
                    user_messages.append(content)
        if current_message:
            user_messages.append(current_message)

        # 1. Labeled extraction across all user messages in chronological order
        for text in user_messages:
            cls._extract_labeled_fields(text, info)

        # 2. If there was a previous turn (or user sent structured lines/items), try positional/contextual extraction
        if not info.is_complete and current_message:
            cls._extract_contextual_fields(current_message, user_messages, info)

        # Normalize sigla to 4 lowercase letters if valid
        if info.sigla:
            sigla_clean = re.sub(r"[^a-zA-Z]", "", info.sigla.strip()).lower()
            if len(sigla_clean) == 4:
                info.sigla = sigla_clean
            else:
                info.sigla = None

        return info

    @classmethod
    def _extract_labeled_fields(cls, text: str, info: PrerequisitesInfo) -> None:
        # Iniciativa
        m_ini = re.search(
            r"(?:qual\s+)?iniciativa(?:\s+do\s+projeto)?\s*(?:[:=\-\?]|(?:\s+(?:é|e)\s+))\s*([^\n;|]+)",
            text,
            re.IGNORECASE,
        )
        if m_ini:
            val = cls._clean_value(m_ini.group(1), stop_keys=["sigla", "feature", "funcionalidade", "arqcor"])
            if val:
                info.iniciativa = val

        # Sigla (4 letters)
        m_sigla = re.search(
            r"(?:qual\s+)?sigla(?:\s+do\s+(?:projeto|sistema))?\s*(?:[:=\-\?]|(?:\s+(?:é|e)\s+))\s*([a-zA-Z]{4})\b",
            text,
            re.IGNORECASE,
        )
        if m_sigla:
            info.sigla = m_sigla.group(1).lower()
        else:
            # Also match e.g. "projeto de sigla SESG" or "sigla SESG"
            m_sigla_alt = re.search(
                r"\bsigla\s+(?:do\s+(?:projeto|sistema)\s+)?([a-zA-Z]{4})\b",
                text,
                re.IGNORECASE,
            )
            if m_sigla_alt and m_sigla_alt.group(1).lower() not in {"qual", "para", "como", "deve", "sera", "será"}:
                info.sigla = m_sigla_alt.group(1).lower()

        # Feature
        m_feat = re.search(
            r"(?:qual\s+)?(?:feature|funcionalidade)\s*(?:[:=\-\?]|(?:\s+(?:é|e)\s+))\s*([^\n;|]+)",
            text,
            re.IGNORECASE,
        )
        if m_feat:
            val = cls._clean_value(m_feat.group(1), stop_keys=["iniciativa", "sigla", "arqcor"])
            if val:
                info.feature = val

        # ARQCOR
        m_arq = re.search(
            r"(?:qual\s+)?arqcor\s*(?:[:=\-\?]|(?:\s+(?:é|e)\s+))?\s*([A-Za-z0-9_\-\./ ]+?)(?=\n|,|;|\||$|\b(?:iniciativa|sigla|feature|funcionalidade)\b)",
            text,
            re.IGNORECASE,
        )
        if m_arq:
            val = m_arq.group(1).strip(" .,:;-")
            if val and val.lower() not in {"qual", "o", "a", "do", "da", "de"}:
                info.arqcor = val

    @classmethod
    def _extract_contextual_fields(
        cls,
        current_message: str,
        all_user_messages: List[str],
        info: PrerequisitesInfo,
    ) -> None:
        """Handles multi-line or comma-separated answers when replying to the agent's questions."""
        lines = [
            re.sub(r"^\s*(?:\d+[\.\)\-]|[\-\*•])\s*", "", ln).strip()
            for ln in current_message.strip().splitlines()
            if ln.strip()
        ]

        # If user answered in 4 lines corresponding to the 4 questions
        if len(lines) == 4 and not any(":" in ln for ln in lines):
            if not info.iniciativa:
                info.iniciativa = lines[0].strip(" .,;")
            if not info.sigla:
                s_cand = re.sub(r"[^a-zA-Z]", "", lines[1].strip())
                if len(s_cand) == 4:
                    info.sigla = s_cand.lower()
            if not info.feature:
                info.feature = lines[2].strip(" .,;")
            if not info.arqcor:
                info.arqcor = lines[3].strip(" .,;")
            return

        # If user answered in 4 comma/semicolon-separated parts on a single line (when replying in follow-up)
        if len(all_user_messages) > 1 and len(lines) == 1 and not (":" in lines[0]):
            parts = [p.strip() for p in re.split(r"[,;]", lines[0]) if p.strip()]
            missing = info.missing_fields()
            if len(parts) == 4 and len(missing) == 4:
                info.iniciativa = parts[0]
                s_cand = re.sub(r"[^a-zA-Z]", "", parts[1])
                if len(s_cand) == 4:
                    info.sigla = s_cand.lower()
                info.feature = parts[2]
                info.arqcor = parts[3]
                return
            elif len(parts) == len(missing) and len(missing) > 0:
                for part, miss_q in zip(parts, missing):
                    cls._assign_by_question(info, miss_q, part)
                return
            elif len(missing) == 1:
                cls._assign_by_question(info, missing[0], lines[0])
                return

        # If follow-up message has some labeled fields and only 1 or 2 are left unlabeled,
        # check if feature was already described in the very first message
        if len(all_user_messages) > 1 and not info.feature and (info.iniciativa and info.sigla and info.arqcor):
            first_msg = all_user_messages[0].strip()
            if len(first_msg) >= 10:
                info.feature = first_msg[:120]

    @staticmethod
    def _assign_by_question(info: PrerequisitesInfo, question: str, value: str) -> None:
        val = value.strip(" .,;")
        if not val:
            return
        q_low = question.lower()
        if "iniciativa" in q_low:
            info.iniciativa = val
        elif "sigla" in q_low:
            s_cand = re.sub(r"[^a-zA-Z]", "", val)
            if len(s_cand) == 4:
                info.sigla = s_cand.lower()
        elif "feature" in q_low:
            info.feature = val
        elif "arqcor" in q_low:
            info.arqcor = val

    @staticmethod
    def _clean_value(raw: str, stop_keys: List[str]) -> str:
        val = raw.strip()
        # Cut off if another key starts on the same line (e.g. "Iniciativa: ESG, Sigla: SESG")
        pattern = r",?\s*\b(?:" + "|".join(stop_keys) + r")\b\s*[:=\-]"
        m = re.search(pattern, val, re.IGNORECASE)
        if m:
            val = val[:m.start()]
        return val.strip(" .,;-")

    @classmethod
    def build_missing_prompt(cls, info: PrerequisitesInfo) -> str:
        missing = info.missing_fields()
        collected = []
        if info.iniciativa:
            collected.append(f"• Iniciativa: {info.iniciativa}")
        if info.sigla:
            collected.append(f"• Sigla do projeto: {info.sigla.upper()}")
        if info.feature:
            collected.append(f"• Feature: {info.feature}")
        if info.arqcor:
            collected.append(f"• ARQCOR: {info.arqcor}")

        lines = [
            "Antes de continuar e criar o desenho de arquitetura, preciso que você informe os 4 pré-requisitos obrigatórios:"
        ]
        for q in missing:
            lines.append(f"- {q}")

        if collected:
            lines.append("\nItens já identificados até o momento:")
            lines.extend(collected)

        lines.append(
            "\nExemplo de resposta:\n"
            "Iniciativa: Sustentabilidade Corporativa\n"
            "Sigla: SESG\n"
            "Feature: Cálculo de risco ambiental\n"
            "ARQCOR: ARQ-2026"
        )
        return "\n".join(lines)


class BuiltinExpertEngine:
    """Expert Rule-Based Architectural Reasoning Engine with Standardized Component Naming."""

    @classmethod
    def analyze_requirement(
        cls,
        description: str,
        constraints: Optional[List[str]] = None,
        prerequisites: Optional[PrerequisitesInfo] = None,
    ) -> Dict[str, Any]:
        text = description.lower()
        constraints_text = " ".join(constraints).lower() if constraints else ""
        combined_text = f"{text} {constraints_text}"
        if prerequisites:
            combined_text += f" {(prerequisites.iniciativa or '').lower()} {(prerequisites.feature or '').lower()}"

        # Extract or fallback prerequisites
        sigla = (prerequisites.sigla if prerequisites and prerequisites.sigla else None)
        if not sigla:
            # Try to find a 4-letter sigla in description or default to 'base'
            extracted = PrerequisiteExtractor.extract(description)
            sigla = extracted.sigla or "proj"
        sigla = sigla.lower()[:4]

        iniciativa = (prerequisites.iniciativa if prerequisites and prerequisites.iniciativa else "Iniciativa Corporativa")
        feature_text = (prerequisites.feature if prerequisites and prerequisites.feature else description)
        arqcor = (prerequisites.arqcor if prerequisites and prerequisites.arqcor else "ARQCOR-PADRAO")

        # Determine module (default "base")
        modulo = "base"
        m_mod = re.search(r"\bm[oó]dulo\s*[:=\-]?\s*([a-zA-Z0-9_-]+)", combined_text)
        if m_mod and m_mod.group(1).lower() not in {"de", "do", "da", "para", "com"}:
            modulo = strip_accents(m_mod.group(1).lower())

        # Determine contextual business domains per architectural role
        domains = infer_contextual_domains(description, prerequisites, sigla=sigla)
        channel_dom = domains["channel"]
        atom_dom = domains["atom"]
        orch_dom = domains["orch"]
        batch_dom = domains["batch"]
        storage_dom = domains["storage"]
        msg_dom = domains["messaging"]
        dominio = atom_dom

        # Capability / Technology detection
        wants_streamlit = any(w in combined_text for w in ["streamlit", "baixa complexidade", "dashboard simples", "prototipo", "protótipo"])
        wants_no_frontend = any(w in combined_text for w in ["sem front", "sem interface", "apenas backend", "somente api", "somente batch"])
        wants_python_be = any(w in combined_text for w in ["python", "pyweb", "fastapi", "flask", "django"])
        wants_sbatch = any(w in combined_text for w in ["sbatch", "spring batch", "job batch", "processamento batch", "lote java"])
        wants_dataflow = any(w in combined_text for w in ["dataflow", "data flow", "dataflowbatch", "pipeline de dados", "etl"])
        wants_gcs = any(w in combined_text for w in ["gcs", "cloud storage", "bucket", "object storage", "upload de arquivo", "armazenar arquivo", "anexo"])
        wants_genai = any(w in combined_text for w in ["genai", "genaigke", "agente", "inteligencia artificial", "inteligência artificial", "llm", "ia generativa", "gke"])
        wants_pubsub = any(w in combined_text for w in ["pubsub", "pub/sub", "topico", "tópico", "subscription", "mensageria", "fila", "evento", "assincron", "assíncron", "notifica"])
        wants_orch = any(w in combined_text for w in ["orch", "orquestra", "integra", "sistema externo", "outros sistemas", "parceiro", "terceiro", "erp", "legado"]) or wants_genai

        backend_tech_sigla = "pyweb" if wants_python_be else "sboot"
        backend_info = TECH_CATALOG[backend_tech_sigla]

        components: List[Dict[str, Any]] = []
        integrations: List[Dict[str, Any]] = []

        # 1. Frontend (in Channel Layer) + BFF (in Application Layer)
        bff_id: Optional[str] = None
        if not wants_no_frontend:
            fe_sigla = "streamlit" if wants_streamlit else "ng"
            fe_info = TECH_CATALOG[fe_sigla]
            fe_id = "COMP-FE"
            fe_name = build_component_name(fe_sigla, sigla, modulo, None, channel_dom)

            components.append({
                "id": fe_id,
                "name": fe_name,
                "category": "Frontend",
                "responsibility": f"Interface de canal ({fe_info['name']}) para '{channel_dom}'.",
                "suggestedTechnology": fe_info["name"],
                "alternativeTechnology": fe_info["alternative"],
                "justification": fe_info["justification"],
                "layer": "Channel",
                "archimateType": fe_info["archimateType"],
            })

            # BFF is mandatory to serve the Frontend ("bff - backend for frontend, que é o unico componente que serve o front")
            bff_id = "COMP-BFF"
            bff_name = build_component_name(backend_tech_sigla, sigla, modulo, "bff", channel_dom)
            components.append({
                "id": bff_id,
                "name": bff_name,
                "category": "BFF",
                "responsibility": f"Backend for Frontend (único componente que serve o canal '{channel_dom}').",
                "suggestedTechnology": backend_info["name"],
                "alternativeTechnology": backend_info["alternative"],
                "justification": "Isola o frontend (Channel Layer) e agrega chamadas aos serviços de domínio e orquestradores.",
                "layer": "Application",
                "archimateType": "ApplicationComponent",
            })

            integrations.append({
                "id": "INT-FE-BFF",
                "sourceComponentId": fe_id,
                "targetComponentId": bff_id,
                "relationshipType": "Serving",
                "protocol": "HTTPS / REST",
                "communicationPattern": "Synchronous",
                "purpose": f"Exposição de dados e operações para o frontend {fe_name}.",
            })

        # 2. Backend Atômico (atom - componente que se conecta com banco de dados, domínio independente do portal)
        atom_id = "COMP-ATOM"
        atom_name = build_component_name(backend_tech_sigla, sigla, modulo, "atom", atom_dom)
        components.append({
            "id": atom_id,
            "name": atom_name,
            "category": "Backend",
            "responsibility": f"Componente atômico de negócio responsável pelas regras de domínio e conexão com banco de dados ({atom_dom}).",
            "suggestedTechnology": backend_info["name"],
            "alternativeTechnology": backend_info["alternative"],
            "justification": "Componente atômico reutilizável dedicado à persistência transacional e domínio de negócio.",
            "layer": "Application",
            "archimateType": "ApplicationComponent",
        })

        if bff_id:
            integrations.append({
                "id": "INT-BFF-ATOM",
                "sourceComponentId": bff_id,
                "targetComponentId": atom_id,
                "relationshipType": "Serving",
                "protocol": "HTTP/REST",
                "communicationPattern": "Synchronous",
                "purpose": f"Consumo de operações de negócio do domínio {atom_dom}.",
            })

        # 3. Backend Orquestrador (orch - para fazer integração com outros sistemas)
        orch_id: Optional[str] = None
        if wants_orch:
            orch_id = "COMP-ORCH"
            orch_name = build_component_name(backend_tech_sigla, sigla, modulo, "orch", orch_dom)
            components.append({
                "id": orch_id,
                "name": orch_name,
                "category": "Backend",
                "responsibility": f"Componente orquestrador responsável pela integração com outros sistemas e coordenação de fluxos de '{orch_dom}'.",
                "suggestedTechnology": backend_info["name"],
                "alternativeTechnology": backend_info["alternative"],
                "justification": "Centraliza integrações externas, resiliência (circuit breaker) e composição de serviços.",
                "layer": "Application",
                "archimateType": "ApplicationComponent",
            })
            if bff_id:
                integrations.append({
                    "id": "INT-BFF-ORCH",
                    "sourceComponentId": bff_id,
                    "targetComponentId": orch_id,
                    "relationshipType": "Serving",
                    "protocol": "HTTP/REST",
                    "communicationPattern": "Synchronous",
                    "purpose": "Acionamento de fluxos orquestrados e integrações externas.",
                })
            integrations.append({
                "id": "INT-ORCH-ATOM",
                "sourceComponentId": orch_id,
                "targetComponentId": atom_id,
                "relationshipType": "Serving",
                "protocol": "HTTP/REST",
                "communicationPattern": "Synchronous",
                "purpose": "Consulta e persistência de estado no componente atômico.",
            })

        # 4. Database (Always MySQL as standard, connected exclusively to the atomic component `atom`)
        db_tech = "MySQL"
        db_id = "COMP-DB"
        components.append({
            "id": db_id,
            "name": f"mysql-{sigla}-{modulo}-{atom_dom}",
            "category": "Database",
            "responsibility": f"Persistência relacional MySQL e integridade de dados do domínio {atom_dom}.",
            "suggestedTechnology": db_tech,
            "alternativeTechnology": "PostgreSQL",
            "justification": "Banco de dados relacional padrão (MySQL) conectado exclusivamente ao serviço atômico (atom).",
            "layer": "Technology",
            "archimateType": "SystemSoftware",
        })
        integrations.append({
            "id": "INT-ATOM-DB",
            "sourceComponentId": atom_id,
            "targetComponentId": db_id,
            "relationshipType": "Access",
            "protocol": "JDBC / MySQL (Porta 3306)",
            "communicationPattern": "Synchronous",
            "purpose": f"Leitura e escrita de dados no MySQL pelo componente atômico {atom_name}.",
        })

        # 5. Optional Catalog Components (genaigke, pubsub, gcs, sbatch, dataflowbatch)
        if wants_genai:
            genai_info = TECH_CATALOG["genaigke"]
            genai_id = "COMP-GENAI"
            genai_name = build_component_name("genaigke", sigla, modulo, None, atom_dom)
            components.append({
                "id": genai_id,
                "name": genai_name,
                "category": genai_info["category"],
                "responsibility": f"Agente GenAI no GKE para processamento inteligente de {atom_dom}.",
                "suggestedTechnology": genai_info["name"],
                "alternativeTechnology": genai_info["alternative"],
                "justification": genai_info["justification"],
                "layer": genai_info["layer"],
                "archimateType": genai_info["archimateType"],
            })
            caller_id = orch_id or bff_id or atom_id
            integrations.append({
                "id": "INT-ORCH-GENAI",
                "sourceComponentId": caller_id,
                "targetComponentId": genai_id,
                "relationshipType": "Serving",
                "protocol": "HTTPS / gRPC",
                "communicationPattern": "Synchronous",
                "purpose": "Invocação do agente GenAI no GKE para inferência e análise.",
            })

        if wants_pubsub:
            ps_info = TECH_CATALOG["pubsub"]
            ps_id = "COMP-PUBSUB"
            ps_name = build_component_name("pubsub", sigla, modulo, None, msg_dom)
            components.append({
                "id": ps_id,
                "name": ps_name,
                "category": ps_info["category"],
                "responsibility": f"Tópico e Subscription do Pub/Sub para eventos assíncronos de {msg_dom}.",
                "suggestedTechnology": ps_info["name"],
                "alternativeTechnology": ps_info["alternative"],
                "justification": ps_info["justification"],
                "layer": ps_info["layer"],
                "archimateType": ps_info["archimateType"],
            })
            producer_id = orch_id or atom_id
            integrations.append({
                "id": "INT-BE-PUBSUB",
                "sourceComponentId": producer_id,
                "targetComponentId": ps_id,
                "relationshipType": "Flow",
                "protocol": "Google Cloud Pub/Sub (gRPC/HTTPS)",
                "communicationPattern": "Asynchronous",
                "purpose": f"Publicação e consumo de eventos de {msg_dom}.",
            })

        if wants_gcs:
            gcs_info = TECH_CATALOG["gcs"]
            gcs_id = "COMP-GCS"
            gcs_name = build_component_name("gcs", sigla, modulo, None, storage_dom)
            components.append({
                "id": gcs_id,
                "name": gcs_name,
                "category": gcs_info["category"],
                "responsibility": f"Bucket no Google Cloud Storage para armazenamento de arquivos de {storage_dom}.",
                "suggestedTechnology": gcs_info["name"],
                "alternativeTechnology": gcs_info["alternative"],
                "justification": gcs_info["justification"],
                "layer": gcs_info["layer"],
                "archimateType": gcs_info["archimateType"],
            })
            storage_caller = atom_id
            integrations.append({
                "id": "INT-ATOM-GCS",
                "sourceComponentId": storage_caller,
                "targetComponentId": gcs_id,
                "relationshipType": "Access",
                "protocol": "HTTPS / GCS API",
                "communicationPattern": "Synchronous",
                "purpose": "Leitura e gravação de objetos/arquivos no Cloud Storage.",
            })

        if wants_sbatch:
            sb_info = TECH_CATALOG["sbatch"]
            sb_id = "COMP-SBATCH"
            sb_name = build_component_name("sbatch", sigla, modulo, None, batch_dom)
            components.append({
                "id": sb_id,
                "name": sb_name,
                "category": sb_info["category"],
                "responsibility": f"Job Spring Batch para processamento em lote de {batch_dom}.",
                "suggestedTechnology": sb_info["name"],
                "alternativeTechnology": sb_info["alternative"],
                "justification": sb_info["justification"],
                "layer": sb_info["layer"],
                "archimateType": sb_info["archimateType"],
            })
            integrations.append({
                "id": "INT-SBATCH-ATOM",
                "sourceComponentId": sb_id,
                "targetComponentId": atom_id,
                "relationshipType": "Serving",
                "protocol": "HTTP/REST ou JDBC",
                "communicationPattern": "Asynchronous",
                "purpose": "Processamento batch consumindo/atualizando dados do domínio.",
            })

        if wants_dataflow:
            df_info = TECH_CATALOG["dataflowbatch"]
            df_id = "COMP-DATAFLOW"
            df_name = build_component_name("dataflowbatch", sigla, modulo, None, batch_dom)
            components.append({
                "id": df_id,
                "name": df_name,
                "category": df_info["category"],
                "responsibility": f"Pipeline Google Cloud Dataflow para processamento massivo de dados de {batch_dom}.",
                "suggestedTechnology": df_info["name"],
                "alternativeTechnology": df_info["alternative"],
                "justification": df_info["justification"],
                "layer": df_info["layer"],
                "archimateType": df_info["archimateType"],
            })
            target_for_df = "COMP-GCS" if wants_gcs else db_id
            integrations.append({
                "id": "INT-DATAFLOW-STORAGE",
                "sourceComponentId": df_id,
                "targetComponentId": target_for_df,
                "relationshipType": "Access",
                "protocol": "Cloud Connector / TCP",
                "communicationPattern": "Asynchronous",
                "purpose": "Ingestão e transformação em lote de dados.",
            })

        style = "Arquitetura Padronizada BFF + Microsserviços (Atom/Orch)"
        style_justification = (
            f"Arquitetura estruturada para a iniciativa '{iniciativa}' (Sigla: {sigla.upper()}, ARQCOR: {arqcor}), "
            f"seguindo o padrão corporativo de nomenclatura [sigla-tecnologia]-{sigla}-{modulo}-[tipo]-{dominio}, "
            f"com separação clara entre BFF (atendimento ao front), Atômico (acesso a banco) e Orquestrador."
        )

        nfrs = [
            {
                "category": "Padronização e Governança (ARQCOR)",
                "description": f"Conformidade com o ARQCOR {arqcor} e nomenclatura corporativa na sigla {sigla.upper()}.",
            },
            {
                "category": "Segurança",
                "description": "Autenticação OAuth2/OIDC no BFF, comunicação TLS 1.3 e isolamento do banco de dados restrito ao componente atômico (atom).",
            },
            {
                "category": "Escalabilidade",
                "description": "Componentes stateless em containers permitindo auto-scaling horizontal independente por papel (bff, atom, orch).",
            },
            {
                "category": "Observabilidade",
                "description": "Tracing distribuído OpenTelemetry, logs estruturados correlacionados pela sigla do sistema e métricas de latência.",
            },
        ]

        decisions = [
            {
                "decision": f"Padrão de Componentes da Sigla {sigla.upper()}",
                "rationale": f"Todos os componentes adotam o padrão [sigla-tecnologia]-{sigla}-{modulo}-[tipo]-{dominio}.",
                "status": "Recomendado",
            },
            {
                "decision": "Isolamento de Camadas com BFF e Componente Atômico (atom)",
                "rationale": "O BFF é o único ponto de contato do Frontend, enquanto o componente Atômico (atom) encapsula exclusivamente o acesso ao banco de dados.",
                "status": "Recomendado",
            },
        ]

        prereq_dict = {
            "iniciativa": iniciativa,
            "sigla": sigla,
            "feature": feature_text,
            "arqcor": arqcor,
        }

        return {
            "id": f"PROP-{sigla.upper()}-{abs(hash(description)) % 10000}",
            "title": f"[{sigla.upper()}] {iniciativa} — {feature_text[:60]}",
            "summary": (
                f"Iniciativa: {iniciativa} | Sigla: {sigla.upper()} | Feature: {feature_text} | ARQCOR: {arqcor}. "
                f"Proposta arquitetural seguindo o padrão corporativo para o domínio '{dominio}'."
            ),
            "architecturalStyle": style,
            "styleJustification": style_justification,
            "components": components,
            "integrations": integrations,
            "decisions": decisions,
            "nonFunctionalRequirements": nfrs,
            "prerequisites": prereq_dict,
            "status": "proposed",
            "version": 1,
        }

    @classmethod
    def _extract_existing_metadata(cls, proposal_dict: Dict[str, Any]) -> Tuple[str, str, str]:
        """Extracts (sigla, modulo, dominio) from existing proposal prerequisites or component names."""
        prereq = proposal_dict.get("prerequisites") or {}
        sigla = (prereq.get("sigla") or "").lower().strip()
        modulo = "base"
        dominio = ""

        for comp in proposal_dict.get("components", []):
            parts = comp.get("name", "").split("-")
            if len(parts) >= 4 and parts[0] in TECH_CATALOG:
                if not sigla and len(parts[1]) == 4:
                    sigla = parts[1]
                modulo = parts[2] or "base"
                if parts[0] in ("sboot", "pyweb") and len(parts) >= 5:
                    dominio = "-".join(parts[4:])
                else:
                    dominio = "-".join(parts[3:])
                break

        if not sigla or len(sigla) != 4:
            sigla = "proj"
        if not dominio:
            feat = prereq.get("feature") or proposal_dict.get("title") or "risco-ambiental"
            dominio = slugify_domain(feat, fallback="risco-ambiental", max_words=3)

        return sigla, modulo, dominio

    @classmethod
    def refine_proposal(cls, proposal_dict: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Incorporates user feedback into the existing proposal (add, modify, or remove components/techs)."""
        fb = feedback.lower()
        fb_norm = strip_accents(fb)
        components: List[Dict[str, Any]] = list(proposal_dict.get("components", []))
        integrations: List[Dict[str, Any]] = list(proposal_dict.get("integrations", []))
        decisions: List[Dict[str, Any]] = list(proposal_dict.get("decisions", []))

        sigla, modulo, dominio = cls._extract_existing_metadata(proposal_dict)

        # Check if user requested to change sigla, modulo, or dominio
        m_sigla = re.search(r"\bsigla\s+(?:para\s+|por\s+|:?\s*)([a-zA-Z]{4})\b", feedback, re.IGNORECASE)
        if m_sigla and m_sigla.group(1).lower() not in {"para", "como", "nova", "novo"}:
            sigla = m_sigla.group(1).lower()
            if proposal_dict.get("prerequisites"):
                proposal_dict["prerequisites"]["sigla"] = sigla

        m_mod = re.search(r"\bm[oó]dulo\s+(?:para\s+|por\s+|:?\s*)([a-zA-Z0-9_-]+)", feedback, re.IGNORECASE)
        if m_mod and m_mod.group(1).lower() not in {"para", "como", "novo", "nova"}:
            modulo = strip_accents(m_mod.group(1).lower())

        m_dom = re.search(r"\bdom[ií]nio\s+(?:para\s+|por\s+|:?\s*)([a-zA-Z0-9À-ÿ\s-]+)", feedback, re.IGNORECASE)
        if m_dom:
            dominio = slugify_domain(m_dom.group(1), fallback=dominio, max_words=3)

        # Determine current backend tech (sboot or pyweb)
        current_be_sigla = "sboot"
        for c in components:
            if c["name"].startswith("pyweb-"):
                current_be_sigla = "pyweb"
                break

        is_remove = any(w in fb_norm for w in ["remov", "exclu", "tirar", "tire", "delet", "retir", "sem "])
        is_replace = any(w in fb_norm for w in ["troc", "substitu", "mud", "alter", "em vez de", "ao inves"])
        is_add = any(w in fb_norm for w in ["adicion", "inclu", "coloc", "coloq", "cri", "inser", "mais um", "novo", "nova", "preciso de", "teremos"])

        changes_made = False

        # 1. Handle Component Removal
        if is_remove:
            removed_ids = set()
            for c in list(components):
                c_name_low = c["name"].lower()
                c_cat_low = c["category"].lower()
                c_tech_low = c["suggestedTechnology"].lower()
                match_remove = False
                for key in ["pubsub", "gcs", "storage", "genaigke", "genai", "agente", "sbatch", "dataflowbatch", "dataflow", "streamlit", "angular", "orch", "orquestrador", "bff", "atom", "cache", "redis", "banco", "database"]:
                    if key in fb_norm and (key in c_name_low or key in c_cat_low or key in c_tech_low):
                        match_remove = True
                        break
                if c["id"].lower() in fb or c_name_low in fb:
                    match_remove = True
                if match_remove:
                    removed_ids.add(c["id"])
                    components.remove(c)
                    changes_made = True

            if removed_ids:
                integrations = [
                    i for i in integrations
                    if i["sourceComponentId"] not in removed_ids and i["targetComponentId"] not in removed_ids
                ]

        # 2. Handle Technology / Component Replacement or Addition
        # 2a. Frontend changes (ng <-> streamlit)
        if "streamlit" in fb_norm and not is_remove:
            fe_comp = next((c for c in components if c["category"] == "Frontend"), None)
            info = TECH_CATALOG["streamlit"]
            fe_dom = dominio
            if fe_comp:
                fe_parts = fe_comp["name"].split("-")
                if len(fe_parts) >= 4:
                    fe_dom = "-".join(fe_parts[3:])
            new_name = build_component_name("streamlit", sigla, modulo, None, fe_dom)
            if fe_comp:
                fe_comp["name"] = new_name
                fe_comp["suggestedTechnology"] = info["name"]
                fe_comp["alternativeTechnology"] = info["alternative"]
                fe_comp["justification"] = info["justification"]
                fe_comp["layer"] = "Channel"
            else:
                fe_id = f"COMP-FE-{len(components)+1}"
                components.insert(0, {
                    "id": fe_id,
                    "name": new_name,
                    "category": "Frontend",
                    "responsibility": f"Interface de baixa complexidade (Streamlit) para o domínio {fe_dom}.",
                    "suggestedTechnology": info["name"],
                    "alternativeTechnology": info["alternative"],
                    "justification": info["justification"],
                    "layer": "Channel",
                    "archimateType": "ApplicationComponent",
                })
                target_be = next((c for c in components if c["category"] == "BFF" or "-bff-" in c["name"]), None) or next((c for c in components if c["category"] == "Backend"), None)
                if target_be:
                    integrations.append({
                        "id": f"INT-{fe_id}-{target_be['id']}",
                        "sourceComponentId": fe_id,
                        "targetComponentId": target_be["id"],
                        "relationshipType": "Serving",
                        "protocol": "HTTPS / REST",
                        "communicationPattern": "Synchronous",
                        "purpose": "Consumo do BFF pelo Frontend Streamlit.",
                    })
            changes_made = True

        elif ("angular" in fb_norm or re.search(r"\bng\b", fb_norm)) and not is_remove:
            fe_comp = next((c for c in components if c["category"] == "Frontend"), None)
            info = TECH_CATALOG["ng"]
            fe_dom = dominio
            if fe_comp:
                fe_parts = fe_comp["name"].split("-")
                if len(fe_parts) >= 4:
                    fe_dom = "-".join(fe_parts[3:])
            new_name = build_component_name("ng", sigla, modulo, None, fe_dom)
            if fe_comp:
                fe_comp["name"] = new_name
                fe_comp["suggestedTechnology"] = info["name"]
                fe_comp["alternativeTechnology"] = info["alternative"]
                fe_comp["justification"] = info["justification"]
                fe_comp["layer"] = "Channel"
            else:
                fe_id = f"COMP-FE-{len(components)+1}"
                components.insert(0, {
                    "id": fe_id,
                    "name": new_name,
                    "category": "Frontend",
                    "responsibility": f"Frontend Angular 20 para o domínio {fe_dom}.",
                    "suggestedTechnology": info["name"],
                    "alternativeTechnology": info["alternative"],
                    "justification": info["justification"],
                    "layer": "Channel",
                    "archimateType": "ApplicationComponent",
                })
                target_be = next((c for c in components if c["category"] == "BFF" or "-bff-" in c["name"]), None) or next((c for c in components if c["category"] == "Backend"), None)
                if target_be:
                    integrations.append({
                        "id": f"INT-{fe_id}-{target_be['id']}",
                        "sourceComponentId": fe_id,
                        "targetComponentId": target_be["id"],
                        "relationshipType": "Serving",
                        "protocol": "HTTPS / REST",
                        "communicationPattern": "Synchronous",
                        "purpose": "Consumo do BFF pelo Frontend Angular 20.",
                    })
            changes_made = True

        # 2b. Backend stack swap or addition (pyweb <-> sboot)
        wants_pyweb = any(w in fb_norm for w in ["python", "pyweb", "fastapi", "flask"])
        wants_sboot = any(w in fb_norm for w in ["sboot", "spring boot", "java"]) and "sbatch" not in fb_norm and "spring batch" not in fb_norm

        if (wants_pyweb or wants_sboot) and not is_remove:
            target_be_sigla = "pyweb" if wants_pyweb else "sboot"
            current_be_sigla = target_be_sigla
            be_info = TECH_CATALOG[target_be_sigla]

            # If replacing existing backend technology (or if not explicitly adding a new component)
            if is_replace or not is_add:
                for c in components:
                    if c["category"] in ("Backend", "BFF") and (c["name"].startswith("sboot-") or c["name"].startswith("pyweb-") or c["category"] in ("Backend", "BFF")):
                        parts = c["name"].split("-")
                        tipo_c = "bff" if (c["category"] == "BFF" or "-bff-" in c["name"]) else ("orch" if "-orch-" in c["name"] else "atom")
                        dom_c = "-".join(parts[4:]) if (len(parts) >= 5 and parts[0] in ("sboot", "pyweb")) else dominio
                        c["name"] = build_component_name(target_be_sigla, sigla, modulo, tipo_c, dom_c)
                        c["suggestedTechnology"] = be_info["name"]
                        c["alternativeTechnology"] = be_info["alternative"]
                        c["justification"] = f"Atualizado para {be_info['name']} conforme solicitação do usuário."
                        changes_made = True

        # 2c. Specific backend role addition (orch, bff, atom)
        if not is_remove:
            if any(w in fb_norm for w in ["orch", "orquestrador", "orquestracao", "integracao externa", "outros sistemas"]):
                has_orch = any("-orch-" in c["name"] for c in components)
                if not has_orch or is_add:
                    custom_dom = cls._extract_custom_domain(feedback, fallback=dominio)
                    orch_id = f"COMP-ORCH-{len(components)+1}"
                    be_info = TECH_CATALOG[current_be_sigla]
                    orch_name = build_component_name(current_be_sigla, sigla, modulo, "orch", custom_dom)
                    components.append({
                        "id": orch_id,
                        "name": orch_name,
                        "category": "Backend",
                        "responsibility": f"Orquestrador para integração com outros sistemas no domínio {custom_dom}.",
                        "suggestedTechnology": be_info["name"],
                        "alternativeTechnology": be_info["alternative"],
                        "justification": "Adicionado conforme solicitação para orquestrar integrações.",
                        "layer": "Application",
                        "archimateType": "ApplicationComponent",
                    })
                    bff_c = next((c for c in components if c["category"] == "BFF" or "-bff-" in c["name"]), None)
                    atom_c = next((c for c in components if "-atom-" in c["name"]), None)
                    if bff_c:
                        integrations.append({
                            "id": f"INT-{bff_c['id']}-{orch_id}",
                            "sourceComponentId": bff_c["id"],
                            "targetComponentId": orch_id,
                            "relationshipType": "Serving",
                            "protocol": "HTTP/REST",
                            "communicationPattern": "Synchronous",
                            "purpose": f"Orquestração de chamadas via {orch_name}.",
                        })
                    if atom_c:
                        integrations.append({
                            "id": f"INT-{orch_id}-{atom_c['id']}",
                            "sourceComponentId": orch_id,
                            "targetComponentId": atom_c["id"],
                            "relationshipType": "Serving",
                            "protocol": "HTTP/REST",
                            "communicationPattern": "Synchronous",
                            "purpose": f"Integração do orquestrador com o serviço atômico {atom_c['name']}.",
                        })
                    changes_made = True

            if any(w in fb_norm for w in ["atom", "atomico", "servico de", "microsservico de", "novo servico", "novo backend"]) and is_add:
                custom_dom = cls._extract_custom_domain(feedback, fallback=dominio)
                atom_id = f"COMP-ATOM-{len(components)+1}"
                be_info = TECH_CATALOG[current_be_sigla]
                atom_name = build_component_name(current_be_sigla, sigla, modulo, "atom", custom_dom)
                if not any(c["name"] == atom_name for c in components):
                    components.append({
                        "id": atom_id,
                        "name": atom_name,
                        "category": "Backend",
                        "responsibility": f"Componente atômico responsável pelo domínio {custom_dom} e acesso ao banco de dados.",
                        "suggestedTechnology": be_info["name"],
                        "alternativeTechnology": be_info["alternative"],
                        "justification": "Novo serviço atômico adicionado conforme solicitação.",
                        "layer": "Application",
                        "archimateType": "ApplicationComponent",
                    })
                    bff_c = next((c for c in components if c["category"] == "BFF" or "-bff-" in c["name"]), None)
                    db_c = next((c for c in components if c["category"] == "Database"), None)
                    if bff_c:
                        integrations.append({
                            "id": f"INT-{bff_c['id']}-{atom_id}",
                            "sourceComponentId": bff_c["id"],
                            "targetComponentId": atom_id,
                            "relationshipType": "Serving",
                            "protocol": "HTTP/REST",
                            "communicationPattern": "Synchronous",
                            "purpose": f"Chamada do BFF para o serviço atômico {atom_name}.",
                        })
                    if db_c:
                        integrations.append({
                            "id": f"INT-{atom_id}-{db_c['id']}",
                            "sourceComponentId": atom_id,
                            "targetComponentId": db_c["id"],
                            "relationshipType": "Access",
                            "protocol": "JDBC / TCP",
                            "communicationPattern": "Synchronous",
                            "purpose": f"Acesso a dados pelo serviço atômico {atom_name}.",
                        })
                    changes_made = True

            if "bff" in fb_norm and not any(c["category"] == "BFF" or "-bff-" in c["name"] for c in components):
                bff_id = f"COMP-BFF-{len(components)+1}"
                be_info = TECH_CATALOG[current_be_sigla]
                bff_name = build_component_name(current_be_sigla, sigla, modulo, "bff", dominio)
                components.append({
                    "id": bff_id,
                    "name": bff_name,
                    "category": "BFF",
                    "responsibility": "Backend for Frontend (único componente que serve o front).",
                    "suggestedTechnology": be_info["name"],
                    "alternativeTechnology": be_info["alternative"],
                    "justification": "Adicionado conforme solicitação para servir o frontend.",
                    "layer": "Application",
                    "archimateType": "ApplicationComponent",
                })
                fe_c = next((c for c in components if c["category"] == "Frontend"), None)
                atom_c = next((c for c in components if "-atom-" in c["name"]), None)
                if fe_c:
                    integrations.append({
                        "id": f"INT-{fe_c['id']}-{bff_id}",
                        "sourceComponentId": fe_c["id"],
                        "targetComponentId": bff_id,
                        "relationshipType": "Serving",
                        "protocol": "HTTPS / REST",
                        "communicationPattern": "Synchronous",
                        "purpose": "Comunicação exclusiva Frontend -> BFF.",
                    })
                if atom_c:
                    integrations.append({
                        "id": f"INT-{bff_id}-{atom_c['id']}",
                        "sourceComponentId": bff_id,
                        "targetComponentId": atom_c["id"],
                        "relationshipType": "Serving",
                        "protocol": "HTTP/REST",
                        "communicationPattern": "Synchronous",
                        "purpose": "Consumo de regras de negócio no componente atômico.",
                    })
                changes_made = True

        # 2d. Add or Replace Catalog Techs: sbatch, dataflowbatch, gcs, genaigke, pubsub
        if not is_remove:
            # Spring Batch (sbatch)
            if any(w in fb_norm for w in ["sbatch", "spring batch"]) or ("batch" in fb_norm and "dataflow" not in fb_norm and "data flow" not in fb_norm):
                custom_dom = cls._extract_custom_domain(feedback, fallback=dominio)
                sb_info = TECH_CATALOG["sbatch"]
                sb_name = build_component_name("sbatch", sigla, modulo, None, custom_dom)
                existing_df = next((c for c in components if c["name"].startswith("dataflowbatch-")), None)
                if is_replace and existing_df:
                    existing_df["name"] = sb_name
                    existing_df["suggestedTechnology"] = sb_info["name"]
                    existing_df["alternativeTechnology"] = sb_info["alternative"]
                    existing_df["justification"] = sb_info["justification"]
                    changes_made = True
                elif not any(c["name"].startswith("sbatch-") for c in components) or is_add:
                    sb_id = f"COMP-SBATCH-{len(components)+1}"
                    components.append({
                        "id": sb_id,
                        "name": sb_name,
                        "category": sb_info["category"],
                        "responsibility": f"Processamento em lote (Spring Batch) para o domínio {custom_dom}.",
                        "suggestedTechnology": sb_info["name"],
                        "alternativeTechnology": sb_info["alternative"],
                        "justification": sb_info["justification"],
                        "layer": sb_info["layer"],
                        "archimateType": sb_info["archimateType"],
                    })
                    target_c = next((c for c in components if "-atom-" in c["name"] or c["category"] == "Backend"), None)
                    if target_c:
                        integrations.append({
                            "id": f"INT-{sb_id}-{target_c['id']}",
                            "sourceComponentId": sb_id,
                            "targetComponentId": target_c["id"],
                            "relationshipType": "Serving",
                            "protocol": "HTTP/REST / Batch",
                            "communicationPattern": "Asynchronous",
                            "purpose": f"Execução de lote integrada ao componente {target_c['name']}.",
                        })
                    changes_made = True

            # Dataflow Batch (dataflowbatch)
            if any(w in fb_norm for w in ["dataflowbatch", "dataflow", "data flow", "pipeline de dados", "etl"]):
                custom_dom = cls._extract_custom_domain(feedback, fallback=dominio)
                df_info = TECH_CATALOG["dataflowbatch"]
                df_name = build_component_name("dataflowbatch", sigla, modulo, None, custom_dom)
                existing_sb = next((c for c in components if c["name"].startswith("sbatch-")), None)
                if is_replace and existing_sb:
                    existing_sb["name"] = df_name
                    existing_sb["suggestedTechnology"] = df_info["name"]
                    existing_sb["alternativeTechnology"] = df_info["alternative"]
                    existing_sb["justification"] = df_info["justification"]
                    changes_made = True
                elif not any(c["name"].startswith("dataflowbatch-") for c in components) or is_add:
                    df_id = f"COMP-DATAFLOW-{len(components)+1}"
                    components.append({
                        "id": df_id,
                        "name": df_name,
                        "category": df_info["category"],
                        "responsibility": f"Processamento de dados em lote (Dataflow) para {custom_dom}.",
                        "suggestedTechnology": df_info["name"],
                        "alternativeTechnology": df_info["alternative"],
                        "justification": df_info["justification"],
                        "layer": df_info["layer"],
                        "archimateType": df_info["archimateType"],
                    })
                    target_c = next((c for c in components if c["name"].startswith("gcs-") or c["category"] == "Database"), None)
                    if target_c:
                        integrations.append({
                            "id": f"INT-{df_id}-{target_c['id']}",
                            "sourceComponentId": df_id,
                            "targetComponentId": target_c["id"],
                            "relationshipType": "Access",
                            "protocol": "Cloud Dataflow Connector",
                            "communicationPattern": "Asynchronous",
                            "purpose": "Processamento e carga de dados em lote.",
                        })
                    changes_made = True

            # Google Cloud Storage (gcs)
            if any(w in fb_norm for w in ["gcs", "cloud storage", "bucket", "storage", "arquivo", "upload", "anexo", "laudo"]):
                custom_dom = cls._extract_custom_domain(feedback, fallback=dominio)
                gcs_info = TECH_CATALOG["gcs"]
                gcs_name = build_component_name("gcs", sigla, modulo, None, custom_dom)
                if not any(c["name"].startswith("gcs-") for c in components) or is_add:
                    gcs_id = f"COMP-GCS-{len(components)+1}"
                    components.append({
                        "id": gcs_id,
                        "name": gcs_name,
                        "category": gcs_info["category"],
                        "responsibility": f"Armazenamento de objetos no Google Cloud Storage para {custom_dom}.",
                        "suggestedTechnology": gcs_info["name"],
                        "alternativeTechnology": gcs_info["alternative"],
                        "justification": gcs_info["justification"],
                        "layer": gcs_info["layer"],
                        "archimateType": gcs_info["archimateType"],
                    })
                    caller_c = next((c for c in components if "-atom-" in c["name"] or "-orch-" in c["name"] or c["category"] == "Backend"), None)
                    if caller_c:
                        integrations.append({
                            "id": f"INT-{caller_c['id']}-{gcs_id}",
                            "sourceComponentId": caller_c["id"],
                            "targetComponentId": gcs_id,
                            "relationshipType": "Access",
                            "protocol": "HTTPS / GCS API",
                            "communicationPattern": "Synchronous",
                            "purpose": "Leitura e escrita de arquivos no bucket GCS.",
                        })
                    changes_made = True

            # GenAI no GKE (genaigke)
            if any(w in fb_norm for w in ["genaigke", "genai", "agente", "gke", "ia generativa", "llm", "inteligencia artificial"]):
                custom_dom = cls._extract_custom_domain(feedback, fallback=dominio)
                gai_info = TECH_CATALOG["genaigke"]
                gai_name = build_component_name("genaigke", sigla, modulo, None, custom_dom)
                if not any(c["name"].startswith("genaigke-") for c in components) or is_add:
                    gai_id = f"COMP-GENAI-{len(components)+1}"
                    components.append({
                        "id": gai_id,
                        "name": gai_name,
                        "category": gai_info["category"],
                        "responsibility": f"Agente GenAI no GKE atuando no domínio {custom_dom}.",
                        "suggestedTechnology": gai_info["name"],
                        "alternativeTechnology": gai_info["alternative"],
                        "justification": gai_info["justification"],
                        "layer": gai_info["layer"],
                        "archimateType": gai_info["archimateType"],
                    })
                    caller_c = next((c for c in components if "-orch-" in c["name"] or "-bff-" in c["name"] or c["category"] == "Backend"), None)
                    if caller_c:
                        integrations.append({
                            "id": f"INT-{caller_c['id']}-{gai_id}",
                            "sourceComponentId": caller_c["id"],
                            "targetComponentId": gai_id,
                            "relationshipType": "Serving",
                            "protocol": "HTTPS / gRPC",
                            "communicationPattern": "Synchronous",
                            "purpose": "Acionamento do Agente GenAI no GKE.",
                        })
                    changes_made = True

            # Pub/Sub (pubsub) / Messaging
            if any(w in fb_norm for w in ["pubsub", "pub/sub", "topico", "subscription", "mensageria", "fila", "evento", "kafka", "rabbitmq"]):
                custom_dom = cls._extract_custom_domain(feedback, fallback=dominio)
                ps_info = TECH_CATALOG["pubsub"]
                ps_name = build_component_name("pubsub", sigla, modulo, None, custom_dom)
                existing_msg = next((c for c in components if c["category"] == "Messaging" or c["name"].startswith("pubsub-")), None)
                if existing_msg and not is_add:
                    existing_msg["name"] = ps_name
                    existing_msg["suggestedTechnology"] = ps_info["name"]
                    existing_msg["justification"] = ps_info["justification"]
                else:
                    ps_id = f"COMP-PUBSUB-{len(components)+1}"
                    components.append({
                        "id": ps_id,
                        "name": ps_name,
                        "category": ps_info["category"],
                        "responsibility": f"Tópico e Subscription do Pub/Sub para eventos de {custom_dom}.",
                        "suggestedTechnology": ps_info["name"],
                        "alternativeTechnology": ps_info["alternative"],
                        "justification": ps_info["justification"],
                        "layer": ps_info["layer"],
                        "archimateType": ps_info["archimateType"],
                    })
                    caller_c = next((c for c in components if "-orch-" in c["name"] or "-atom-" in c["name"] or c["category"] == "Backend"), None)
                    if caller_c:
                        integrations.append({
                            "id": f"INT-{caller_c['id']}-{ps_id}",
                            "sourceComponentId": caller_c["id"],
                            "targetComponentId": ps_id,
                            "relationshipType": "Flow",
                            "protocol": "Google Cloud Pub/Sub",
                            "communicationPattern": "Asynchronous",
                            "purpose": f"Publicação e assinatura de mensagens no tópico {ps_name}.",
                        })
                changes_made = True

            # Database technology changes
            if any(w in fb_norm for w in ["postgres", "mysql", "mongo", "mongodb", "oracle", "sql server", "cloud sql"]):
                new_db_tech = "PostgreSQL"
                if "mysql" in fb_norm:
                    new_db_tech = "MySQL"
                elif "mongo" in fb_norm:
                    new_db_tech = "MongoDB"
                elif "oracle" in fb_norm:
                    new_db_tech = "Oracle Database"
                elif "sql server" in fb_norm:
                    new_db_tech = "SQL Server"

                db_comp = next((c for c in components if c["category"] == "Database"), None)
                if db_comp:
                    db_comp["suggestedTechnology"] = new_db_tech
                    db_comp["justification"] = f"Banco de dados alterado para {new_db_tech} conforme solicitação."
                    changes_made = True

            # Cache / Redis
            if any(w in fb_norm for w in ["cache", "redis", "memcached"]):
                has_cache = any(c["category"] == "Cache" for c in components)
                if not has_cache:
                    cache_id = f"COMP-CACHE-{len(components)+1}"
                    components.append({
                        "id": cache_id,
                        "name": f"cache-{sigla}-{modulo}-{dominio}",
                        "category": "Cache",
                        "responsibility": f"Cache distribuído em memória para {dominio}.",
                        "suggestedTechnology": "Redis (Memorystore)",
                        "alternativeTechnology": "Memcached",
                        "justification": "Adicionado conforme instrução do usuário para otimização de leitura.",
                        "layer": "Technology",
                        "archimateType": "SystemSoftware",
                    })
                    be_c = next((c for c in components if "-atom-" in c["name"] or c["category"] == "Backend"), None)
                    if be_c:
                        integrations.append({
                            "id": f"INT-{be_c['id']}-{cache_id}",
                            "sourceComponentId": be_c["id"],
                            "targetComponentId": cache_id,
                            "relationshipType": "Access",
                            "protocol": "RESP (Porta 6379)",
                            "communicationPattern": "Synchronous",
                            "purpose": "Consulta e invalidação de cache.",
                        })
                    changes_made = True

        # 3. Propagate sigla/modulo/dominio updates to existing standardized components if requested
        if m_sigla or m_mod or m_dom:
            for c in components:
                parts = c["name"].split("-")
                if len(parts) >= 4 and parts[0] in TECH_CATALOG:
                    tech_p = parts[0]
                    tipo_p = parts[3] if (tech_p in ("sboot", "pyweb") and len(parts) >= 5) else None
                    dom_p = dominio if m_dom else ("-".join(parts[4:]) if tipo_p else "-".join(parts[3:]))
                    c["name"] = build_component_name(tech_p, sigla, modulo, tipo_p, dom_p)
            changes_made = True

        # 4. Fallback: If user requested an addition/modification with a domain concept not matched above,
        # add a new atomic/orchestrator service or component with that domain so the diagram always reflects the change
        if not changes_made:
            custom_dom = cls._extract_custom_domain(feedback, fallback="")
            if custom_dom and custom_dom != dominio:
                new_id = f"COMP-ATOM-{len(components)+1}"
                be_info = TECH_CATALOG[current_be_sigla]
                new_name = build_component_name(current_be_sigla, sigla, modulo, "atom", custom_dom)
                components.append({
                    "id": new_id,
                    "name": new_name,
                    "category": "Backend",
                    "responsibility": f"Componente adicionado para atender à solicitação: '{feedback}'.",
                    "suggestedTechnology": be_info["name"],
                    "alternativeTechnology": be_info["alternative"],
                    "justification": f"Adicionado em resposta ao pedido de alteração: '{feedback}'.",
                    "layer": "Application",
                    "archimateType": "ApplicationComponent",
                })
                bff_c = next((c for c in components if c["category"] == "BFF" or "-bff-" in c["name"]), None)
                db_c = next((c for c in components if c["category"] == "Database"), None)
                if bff_c:
                    integrations.append({
                        "id": f"INT-{bff_c['id']}-{new_id}",
                        "sourceComponentId": bff_c["id"],
                        "targetComponentId": new_id,
                        "relationshipType": "Serving",
                        "protocol": "HTTP/REST",
                        "communicationPattern": "Synchronous",
                        "purpose": f"Integração com {new_name}.",
                    })
                if db_c:
                    integrations.append({
                        "id": f"INT-{new_id}-{db_c['id']}",
                        "sourceComponentId": new_id,
                        "targetComponentId": db_c["id"],
                        "relationshipType": "Access",
                        "protocol": "JDBC / TCP",
                        "communicationPattern": "Synchronous",
                        "purpose": f"Acesso a dados por {new_name}.",
                    })

        decisions.append({
            "decision": f"Refinamento Arquitetural (v{proposal_dict.get('version', 1) + 1})",
            "rationale": f"Aplicada a alteração solicitada pelo usuário: '{feedback}'.",
            "status": "Recomendado",
        })

        proposal_dict["components"] = components
        proposal_dict["integrations"] = integrations
        proposal_dict["decisions"] = decisions
        proposal_dict["version"] = proposal_dict.get("version", 1) + 1
        proposal_dict["status"] = "modified"
        return proposal_dict

    @staticmethod
    def _extract_custom_domain(feedback: str, fallback: str) -> str:
        """Extracts a domain slug from user refinement text (e.g. 'para calculo de impostos')."""
        m = re.search(r"\b(?:para|de|do|da|sobre|dominio|domínio)\s+([a-zA-Z0-9À-ÿ\s\-]{3,40})", feedback, re.IGNORECASE)
        if m:
            cand = slugify_domain(m.group(1), fallback="", max_words=3)
            if cand:
                return cand
        cand_all = slugify_domain(feedback, fallback="", max_words=3)
        return cand_all or fallback

    @classmethod
    def normalize_proposal_dict(
        cls,
        raw: Dict[str, Any],
        prerequisites: Optional[PrerequisitesInfo] = None,
        description: str = "",
    ) -> Dict[str, Any]:
        """Normalizes LLM outputs so component names, layers, and DB strictly match rules."""
        if prerequisites:
            raw["prerequisites"] = {
                "iniciativa": prerequisites.iniciativa,
                "sigla": prerequisites.sigla,
                "feature": prerequisites.feature,
                "arqcor": prerequisites.arqcor,
            }
        sigla, modulo, dominio = cls._extract_existing_metadata(raw)
        if prerequisites and prerequisites.sigla:
            sigla = prerequisites.sigla.lower()[:4]

        domains = infer_contextual_domains(
            description or raw.get("summary", "") or raw.get("title", ""),
            prerequisites,
            sigla=sigla,
        )

        valid_layers = {"Channel", "Business", "Application", "Technology", "Physical", "Strategy", "Implementation_Migration"}
        valid_elem_types = {
            "BusinessActor", "BusinessRole", "BusinessService", "BusinessProcess",
            "ApplicationComponent", "ApplicationService", "ApplicationInterface", "DataObject",
            "Node", "SystemSoftware", "TechnologyService", "TechnologyInterface", "Artifact",
        }
        valid_rel_types = {
            "Composition", "Aggregation", "Assignment", "Realization",
            "Serving", "Access", "Flow", "Triggering", "Association",
        }

        # Filter out any BusinessActor / Business layer elements
        filtered_components = []
        removed_ids = set()
        for comp in raw.get("components", []):
            if comp.get("layer") == "Business" or comp.get("archimateType") == "BusinessActor":
                removed_ids.add(comp.get("id"))
                continue
            filtered_components.append(comp)
        raw["components"] = filtered_components

        for comp in raw.get("components", []):
            cat = comp.get("category", "")
            name_val = comp.get("name", "").strip()

            # Force Frontend into Channel Layer
            if cat == "Frontend" or name_val.startswith("ng-") or name_val.startswith("streamlit-"):
                comp["category"] = "Frontend"
                comp["layer"] = "Channel"
                comp["archimateType"] = "ApplicationComponent"
            elif comp.get("layer") not in valid_layers or comp.get("layer") == "Business":
                comp["layer"] = "Technology" if cat in ("Database", "Cache", "Messaging", "Infrastructure") else "Application"

            if comp.get("archimateType") not in valid_elem_types:
                comp["archimateType"] = "SystemSoftware" if comp["layer"] == "Technology" else "ApplicationComponent"

            # Enforce MySQL for Database unless user explicitly asked for another DB in refinement
            if cat == "Database":
                comp["suggestedTechnology"] = "MySQL"
                comp["layer"] = "Technology"
                comp["archimateType"] = "SystemSoftware"
                continue

            parts = name_val.split("-")
            is_valid_catalog_name = len(parts) >= 4 and parts[0] in TECH_CATALOG
            # Check if LLM used a bad generic domain like 'feat' or 'feature' or 'portal' on an atomic service
            if is_valid_catalog_name:
                tech_p = parts[0]
                tipo_p = parts[3] if (tech_p in ("sboot", "pyweb") and len(parts) >= 5) else None
                dom_p = "-".join(parts[4:]) if tipo_p else "-".join(parts[3:])
                if re.match(r"^(?:feat(?:ure)?|dominio|negocio|padrao|default)$", dom_p):
                    target_dom = domains["channel"] if (cat in ("Frontend", "BFF") or tipo_p == "bff") else domains["atom"]
                    comp["name"] = build_component_name(tech_p, sigla, modulo, tipo_p, target_dom)
                elif tipo_p == "atom" and dom_p.startswith("portal-"):
                    comp["name"] = build_component_name(tech_p, sigla, modulo, "atom", domains["atom"])
            else:
                tech_low = f"{name_val} {comp.get('suggestedTechnology', '')} {cat}".lower()
                inferred_tech: Optional[str] = None
                if "streamlit" in tech_low:
                    inferred_tech = "streamlit"
                elif "angular" in tech_low or cat == "Frontend":
                    inferred_tech = "ng"
                elif "spring batch" in tech_low or "sbatch" in tech_low:
                    inferred_tech = "sbatch"
                elif "dataflow" in tech_low:
                    inferred_tech = "dataflowbatch"
                elif "gcs" in tech_low or "cloud storage" in tech_low:
                    inferred_tech = "gcs"
                elif "genai" in tech_low or "gke" in tech_low:
                    inferred_tech = "genaigke"
                elif "pubsub" in tech_low or "pub/sub" in tech_low or cat == "Messaging":
                    inferred_tech = "pubsub"
                elif "python" in tech_low or "fastapi" in tech_low or "pyweb" in tech_low:
                    inferred_tech = "pyweb"
                elif "spring" in tech_low or "java" in tech_low or "sboot" in tech_low or cat in ("Backend", "BFF"):
                    inferred_tech = "sboot"

                if inferred_tech:
                    tipo = None
                    if inferred_tech in ("sboot", "pyweb"):
                        if cat == "BFF" or "bff" in tech_low:
                            tipo = "bff"
                        elif "orch" in tech_low or "orquestra" in tech_low:
                            tipo = "orch"
                        else:
                            tipo = "atom"
                    role_dom = domains["channel"] if (inferred_tech in ("ng", "streamlit") or tipo == "bff") else domains["atom"]
                    comp["name"] = build_component_name(inferred_tech, sigla, modulo, tipo, role_dom)

        raw["integrations"] = [
            rel for rel in raw.get("integrations", [])
            if rel.get("sourceComponentId") not in removed_ids and rel.get("targetComponentId") not in removed_ids
        ]
        for rel in raw.get("integrations", []):
            if rel.get("relationshipType") not in valid_rel_types:
                rel["relationshipType"] = "Serving"
            if rel.get("communicationPattern") not in ("Synchronous", "Asynchronous"):
                rel["communicationPattern"] = "Synchronous"

        return raw


class LLMService:
    """Orchestrates LLM calls across external providers and the builtin expert engine."""

    NAMING_RULES_PROMPT = """
    REGRAS OBRIGATÓRIAS DE NOMENCLATURA, CAMADAS E TECNOLOGIAS:
    1. Todo componente deve ter o campo "name" seguindo o modelo:
       - Para projetos Backend (sboot ou pyweb): [sigla-tecnologia]-[sigla-sistema]-[modulo]-[tipo]-[dominio]
         Exemplos:
         * BFF (serve o portal/front): sboot-sesg-base-bff-portal-esg
         * Atômico (conecta ao banco, independente do portal): sboot-sesg-base-atom-sistema-esg
       - Para demais tecnologias (ng, streamlit, sbatch, dataflowbatch, gcs, genaigke, pubsub): [sigla-tecnologia]-[sigla-sistema]-[modulo]-[dominio]
         Exemplo Frontend: ng-sesg-base-portal-esg

    2. Mapeamento de [sigla-tecnologia]:
       - ng: frontend angular 20 (layer: "Channel")
       - streamlit: frontend de baixa complexidade (layer: "Channel")
       - sboot: spring boot java (layer: "Application")
       - sbatch: spring batch (layer: "Application")
       - dataflowbatch: data flow (layer: "Application")
       - gcs: google cloud storage (layer: "Technology")
       - genaigke: GenAI no GKE (agente) (layer: "Application")
       - pyweb: backend em python (layer: "Application")
       - pubsub: tópico e subscription do pubsub (layer: "Technology")

    3. Regras de [dominio]:
       - O domínio NUNCA deve ser uma palavra genérica como "feat" ou "feature". Deve ter de 1 a 3 palavras separadas por hífen com sentido de negócio extraído do prompt.
       - Para Frontend (ng/streamlit) e BFF (bff), use um domínio voltado ao canal/portal (ex: "portal-esg").
       - Para o componente Atômico (atom), como ele não serve apenas o portal, use um domínio de negócio/sistema (ex: "sistema-esg", "base-esg", "risco-ambiental").

    4. Banco de Dados e Camadas:
       - Banco de dados: usar SEMPRE "MySQL" (layer: "Technology", archimateType: "SystemSoftware"), conectado apenas ao componente "atom".
       - Camadas: NÃO crie "Business Layer" nem "BusinessActor". Coloque o Frontend na camada "Channel" (Channel Layer), os serviços na "Application" e banco/infra na "Technology".
    """

    @classmethod
    async def analyze_and_propose(
        cls,
        description: str,
        constraints: Optional[List[str]] = None,
        prerequisites: Optional[PrerequisitesInfo] = None,
    ) -> Dict[str, Any]:
        provider = settings.detect_active_provider()
        logger.info(f"Active LLM provider: {provider}")

        if provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                raw = await cls._call_gemini_for_proposal(description, constraints, prerequisites)
                return BuiltinExpertEngine.normalize_proposal_dict(raw, prerequisites, description=description)
            except Exception as e:
                logger.warning(f"Gemini API call failed: {e}. Falling back to Builtin Expert Engine.")

        elif provider == "openai" and settings.OPENAI_API_KEY:
            try:
                raw = await cls._call_openai_for_proposal(description, constraints, prerequisites)
                return BuiltinExpertEngine.normalize_proposal_dict(raw, prerequisites, description=description)
            except Exception as e:
                logger.warning(f"OpenAI API call failed: {e}. Falling back to Builtin Expert Engine.")

        elif provider == "ollama":
            try:
                raw = await cls._call_ollama_for_proposal(description, constraints, prerequisites)
                return BuiltinExpertEngine.normalize_proposal_dict(raw, prerequisites, description=description)
            except Exception as e:
                logger.warning(f"Ollama call failed: {e}. Falling back to Builtin Expert Engine.")

        return BuiltinExpertEngine.analyze_requirement(description, constraints, prerequisites)

    @classmethod
    async def refine_proposal(cls, proposal_dict: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        provider = settings.detect_active_provider()
        prereq_dict = proposal_dict.get("prerequisites")
        prereq = PrerequisitesInfo(**prereq_dict) if isinstance(prereq_dict, dict) else None

        if provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                raw = await cls._call_gemini_for_refinement(proposal_dict, feedback)
                return BuiltinExpertEngine.normalize_proposal_dict(raw, prereq)
            except Exception as e:
                logger.warning(f"Gemini refinement failed: {e}. Falling back to Builtin Expert Engine.")

        elif provider == "openai" and settings.OPENAI_API_KEY:
            try:
                raw = await cls._call_openai_for_refinement(proposal_dict, feedback)
                return BuiltinExpertEngine.normalize_proposal_dict(raw, prereq)
            except Exception as e:
                logger.warning(f"OpenAI refinement failed: {e}. Falling back to Builtin Expert Engine.")

        elif provider == "ollama":
            try:
                raw = await cls._call_ollama_for_refinement(proposal_dict, feedback)
                return BuiltinExpertEngine.normalize_proposal_dict(raw, prereq)
            except Exception as e:
                logger.warning(f"Ollama refinement failed: {e}. Falling back to Builtin Expert Engine.")

        return BuiltinExpertEngine.refine_proposal(proposal_dict, feedback)

    @classmethod
    async def _call_gemini_for_proposal(
        cls,
        description: str,
        constraints: Optional[List[str]],
        prerequisites: Optional[PrerequisitesInfo] = None,
    ) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        prereq_str = (
            f"Iniciativa: {prerequisites.iniciativa}, Sigla: {prerequisites.sigla}, Feature: {prerequisites.feature}, ARQCOR: {prerequisites.arqcor}"
            if prerequisites else "Extraia do texto"
        )
        prompt = f"""
        Você é um arquiteto de soluções sênior. Responda ESTRITAMENTE em JSON puro.
        {cls.NAMING_RULES_PROMPT}

        Pré-requisitos informados: {prereq_str}
        Descrição da necessidade: "{description}"
        Restrições: {constraints or []}

        Gere a proposta arquitetural seguindo a estrutura JSON com os campos:
        id, title, summary, architecturalStyle, styleJustification, components, integrations, decisions, nonFunctionalRequirements, status ("proposed"), version (1).
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
    async def _call_gemini_for_refinement(cls, proposal: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
        prompt = f"""
        {cls.NAMING_RULES_PROMPT}

        Proposta atual:
        {json.dumps(proposal, ensure_ascii=False)}

        Feedback/Ajustes solicitados pelo usuário:
        "{feedback}"

        Incorpore os ajustes na proposta mantendo a mesma estrutura JSON e respeitando a regra de nomenclatura de componentes.
        Atualize a versão (+1) e mude o status para 'modified'. Responda APENAS o JSON válido.
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
    async def _call_openai_for_proposal(
        cls,
        description: str,
        constraints: Optional[List[str]],
        prerequisites: Optional[PrerequisitesInfo] = None,
    ) -> Dict[str, Any]:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        prereq_str = (
            f"Iniciativa: {prerequisites.iniciativa}, Sigla: {prerequisites.sigla}, Feature: {prerequisites.feature}, ARQCOR: {prerequisites.arqcor}"
            if prerequisites else "Extraia do texto"
        )
        prompt = f"""
        {cls.NAMING_RULES_PROMPT}
        Pré-requisitos: {prereq_str}
        Descrição da necessidade do sistema: "{description}"
        Restrições: {constraints or []}
        Responda em JSON válido com campos: id, title, summary, architecturalStyle, styleJustification, components, integrations, decisions, nonFunctionalRequirements, status, version.
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
        {cls.NAMING_RULES_PROMPT}
        Proposta atual: {json.dumps(proposal, ensure_ascii=False)}
        Instrução de alteração do usuário: "{feedback}"
        Incorpore as alterações nos componentes e integrações e devolva o JSON atualizado.
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
    async def _call_ollama_for_proposal(
        cls,
        description: str,
        constraints: Optional[List[str]],
        prerequisites: Optional[PrerequisitesInfo] = None,
    ) -> Dict[str, Any]:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        prereq_str = (
            f"Iniciativa: {prerequisites.iniciativa}, Sigla: {prerequisites.sigla}, Feature: {prerequisites.feature}, ARQCOR: {prerequisites.arqcor}"
            if prerequisites else ""
        )
        prompt = f"""
        {cls.NAMING_RULES_PROMPT}
        Pré-requisitos: {prereq_str}
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

    @classmethod
    async def _call_ollama_for_refinement(cls, proposal: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        prompt = f"""
        {cls.NAMING_RULES_PROMPT}
        Proposta atual: {json.dumps(proposal, ensure_ascii=False)}
        Instrução de alteração do usuário: "{feedback}"
        Incorpore as alterações nos componentes e integrações mantendo o formato JSON.
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
