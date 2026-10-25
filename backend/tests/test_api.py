"""Tests for FastAPI endpoints including 4-prerequisite check and diagram refinement."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_api_info_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/info")

    assert response.status_code == 200
    data = response.json()
    assert "activeProvider" in data
    assert "providers" in data
    assert "builtin" in data["providers"]


@pytest.mark.asyncio
async def test_api_analyze_blocks_without_4_prerequisites():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        analyze_payload = {
            "description": "Quero desenvolver um sistema web de cadastro de produtos.",
            "constraints": [],
        }
        resp = await ac.post("/api/architecture/analyze", json=analyze_payload)
        assert resp.status_code == 200
        data = resp.json()
        # Proposal must be None until all 4 prerequisites are provided
        assert data["proposal"] is None
        assert len(data["missingPrerequisites"]) == 4
        assert "Qual iniciativa?" in data["message"]
        assert "Qual Sigla do projeto?" in data["message"]
        assert "Qual feature?" in data["message"]
        assert "Qual ARQCOR?" in data["message"]


@pytest.mark.asyncio
async def test_api_analyze_refine_and_approve_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Analyze with the 4 mandatory prerequisites
        analyze_payload = {
            "description": (
                "Iniciativa: Sustentabilidade\n"
                "Sigla: SESG\n"
                "Feature: Risco Ambiental\n"
                "ARQCOR: ARQ-2026\n"
                "Sistema web em Spring Boot e Angular."
            ),
            "constraints": [],
        }
        resp = await ac.post("/api/architecture/analyze", json=analyze_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["proposal"] is not None
        assert data["diagramSvg"] is not None
        assert "sboot-sesg-base-atom-risco-ambiental" in data["diagramSvg"]
        proposal = data["proposal"]

        # 2. Refine after first diagram creation — verify diagramSvg and proposal are updated!
        refine_payload = {
            "proposal": proposal,
            "feedback": "Adicione um spring batch (sbatch) e um pubsub para eventos",
        }
        resp_refine = await ac.post("/api/architecture/refine", json=refine_payload)
        assert resp_refine.status_code == 200
        refine_data = resp_refine.json()
        refined_proposal = refine_data["proposal"]
        assert len(refined_proposal["components"]) > len(proposal["components"])
        assert refine_data["diagramSvg"] is not None
        assert "sbatch-sesg-base-" in refine_data["diagramSvg"]
        assert "pubsub-sesg-base-" in refine_data["diagramSvg"]

        # 3. Approve
        approve_payload = {"proposal": refined_proposal}
        resp_approve = await ac.post("/api/architecture/approve", json=approve_payload)
        assert resp_approve.status_code == 200
        approve_data = resp_approve.json()

        assert "archimateModel" in approve_data
        assert "diagramSvg" in approve_data
        assert "<svg" in approve_data["diagramSvg"]
        assert approve_data["validation"]["isValid"] is True

        # 4. Export JSON & XML
        model = approve_data["archimateModel"]
        resp_export_json = await ac.post("/api/architecture/export/json", json=model)
        assert resp_export_json.status_code == 200
        assert resp_export_json.headers["content-type"] == "application/json"

        resp_export_xml = await ac.post("/api/architecture/export/xml", json=model)
        assert resp_export_xml.status_code == 200
        assert "application/xml" in resp_export_xml.headers["content-type"]
