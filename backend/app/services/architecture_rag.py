"""Architecture RAG Service for AI Software Architecture Designer.

Provides grounded retrieval over official Banco BV architecture standards:
- Technology catalog (ng, streamlit, sboot, pyweb, sbatch, dataflowbatch, gcs, pubsub, genaigke)
- Component naming rules ([sigla-tech]-[sigla-sistema]-[modulo]-[dominio])
- ArchiMate 3.2 official modeling and layer guidelines
- Integration patterns and data pipelines
"""

import os
import glob
import re
from typing import List, Dict, Any, Optional

KNOWLEDGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge"))


class ArchitectureRAGService:
    """Retrieval-Augmented Generation service over corporate architectural knowledge."""

    _chunks_cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def get_all_chunks(cls) -> List[Dict[str, Any]]:
        """Loads and splits all markdown files in knowledge directory by section."""
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

            # Split by markdown headers (# and ## and ###)
            sections = re.split(r"(?m)^(?=#{1,3}\s+)", content)
            for sec in sections:
                clean_sec = sec.strip()
                if not clean_sec:
                    continue

                # Extract header line
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
        """Performs lexical and keyword-density retrieval with scoring."""
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
                # Title matches give extra weight
                if token in chunk["title"].lower():
                    score += 5
                # Exact matches in text
                count = text.count(token)
                score += min(count, 5)

            if score > 0:
                scored.append((score, chunk))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [item[1] for item in scored[:top_k]]

        # If few matches, append first chunks to guarantee context
        if len(results) < top_k:
            for c in chunks:
                if c not in results:
                    results.append(c)
                if len(results) >= top_k:
                    break

        return results

    @classmethod
    def get_technology_catalog_summary(cls) -> str:
        """Returns the summary of official technologies for prompt context."""
        summary_chunks = [
            c["content"] for c in cls.get_all_chunks()
            if "catalogo" in c["source"]
        ]
        return "\n\n".join(summary_chunks) if summary_chunks else ""

    @classmethod
    def get_naming_rules_summary(cls) -> str:
        """Returns naming rules summary for prompt context."""
        naming_chunks = [
            c["content"] for c in cls.get_all_chunks()
            if "nomenclatura" in c["source"]
        ]
        return "\n\n".join(naming_chunks) if naming_chunks else ""
