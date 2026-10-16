"""Tests for FastAPI endpoints."""

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
async def test_api_analyze_and_approve_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Analyze
        analyze_payload = {
            "description": "Quero desenvolver um sistema web de cadastro de produtos com busca e persistência.",
            "constraints": []
        }
        resp = await ac.post("/api/architecture/analyze", json=analyze_payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "proposal" in data
        assert data["proposal"] is not None
        proposal = data["proposal"]

        # 2. Refine
        refine_payload = {
            "proposal": proposal,
            "feedback": "Mudar banco para PostgreSQL e adicionar cache Redis"
        }
        resp_refine = await ac.post("/api/architecture/refine", json=refine_payload)
        assert resp_refine.status_code == 200
        refined_proposal = resp_refine.json()["proposal"]

        # 3. Approve
        approve_payload = {
            "proposal": refined_proposal
        }
        resp_approve = await ac.post("/api/architecture/approve", json=approve_payload)
        assert resp_approve.status_code == 200
        approve_data = resp_approve.json()

        assert "archimateModel" in approve_data
        assert "diagramSvg" in approve_data
        assert "<svg" in approve_data["diagramSvg"]
        assert "validation" in approve_data
        assert approve_data["validation"]["isValid"] is True

        # 4. Export JSON
        model = approve_data["archimateModel"]
        resp_export_json = await ac.post("/api/architecture/export/json", json=model)
        assert resp_export_json.status_code == 200
        assert resp_export_json.headers["content-type"] == "application/json"

        # 5. Export XML
        resp_export_xml = await ac.post("/api/architecture/export/xml", json=model)
        assert resp_export_xml.status_code == 200
        assert "application/xml" in resp_export_xml.headers["content-type"]
