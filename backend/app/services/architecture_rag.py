"""Serviço de RAG de Arquitetura para o Agente Arquiteto de Software AI.

Fornece recuperação fundamentada sobre as normas arquiteturais oficiais do Banco BV:
- Catálogo de tecnologias (ng, streamlit, sboot, pyweb, sbatch, dataflowbatch, gcs, pubsub, genaigke)
- Regras de nomenclatura de componentes ([sigla-tech]-[sigla-sistema]-[modulo]-[tipo]-[dominio])
- Diretrizes oficiais de modelagem e camadas do ArchiMate 3.2
- Padrões de integração e esteiras de pipelines de dados
"""

import os
import glob
import re
from typing import List, Dict, Any, Optional

KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge"))


class ArchitectureRAGService:
    """Serviço de Geração Aumentada por Recuperação (RAG) sobre a base de conhecimento corporativo."""

    _chunks_cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def get_all_chunks(cls) -> List[Dict[str, Any]]:
        """Carrega e particiona todos os arquivos markdown do diretório knowledge por seção."""
        if cls._chunks_cache is not None:
            return cls._chunks_cache

        chunks = []
        md_files = glob.glob(os.path.join(KNOWLEDGE_DIR, "*.md"))

        for file_path in md_files:
            file_name = os.path.basename(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue

            # Divide pelos cabeçalhos markdown (# e ## e ###)
            sections = re.split(r"(?m)^(?=#{1,3}\s+)", content)
            for sec in sections:
                clean_sec = sec.strip()
                if not clean_sec:
                    continue

                # Extrai a linha do título/cabeçalho
                first_line = clean_sec.splitlines()[0].replace("#", "").strip()
                chunks.append({
                    "source": file_name,
                    "title": first_line,
                    "content": clean_sec,
                })

        cls._chunks_cache = chunks
        return chunks

    @classmethod
    def search(cls, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Executa busca léxica e de densidade de termos com pontuação de relevância."""
        chunks = cls.get_all_chunks()
        if not chunks:
            return []

        query_tokens = set(re.findall(r"\b\w{3,}\b", query.lower()))
        if not query_tokens:
            return chunks[:top_k]

        scored = []
        for chunk in chunks:
            text = (chunk["title"] + " " + chunk["content"]).lower()
            score = 0
            for token in query_tokens:
                # Correspondências no título recebem peso adicional
                if token in chunk["title"].lower():
                    score += 5
                # Correspondências exatas no corpo do texto
                count = text.count(token)
                score += min(count, 5)

            if score > 0:
                scored.append((score, chunk))

        # Ordena por pontuação de relevância decrescente
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored[:top_k]]

        # Se houver poucos resultados, anexa os primeiros trechos para garantir contexto
        if len(results) < top_k:
            for c in chunks:
                if c not in results:
                    results.append(c)
                if len(results) >= top_k:
                    break

        return results

    @classmethod
    def get_technology_catalog_summary(cls) -> str:
        """Retorna o resumo das tecnologias oficiais para o contexto do prompt."""
        summary_chunks = [
            c["content"] for c in cls.get_all_chunks()
            if "catalogo" in c["source"]
        ]
        return "\n\n".join(summary_chunks) if summary_chunks else ""

    @classmethod
    def get_naming_rules_summary(cls) -> str:
        """Retorna o resumo das regras de nomenclatura para o contexto do prompt."""
        naming_chunks = [
            c["content"] for c in cls.get_all_chunks()
            if "nomenclatura" in c["source"]
        ]
        return "\n\n".join(naming_chunks) if naming_chunks else ""
