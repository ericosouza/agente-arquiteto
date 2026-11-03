"""Testes da política de CORS: origens não listadas não podem ler as respostas da API."""

from fastapi.testclient import TestClient
from app.config import settings
from app.main import app

client = TestClient(app)


def test_cors_nao_aceita_curinga_por_padrao():
    assert "*" not in settings.CORS_ORIGINS


def test_origem_desconhecida_nao_recebe_cabecalho_cors():
    resp = client.get("/api/info", headers={"Origin": "https://site-malicioso.example"})
    assert "access-control-allow-origin" not in resp.headers


def test_preflight_de_origem_desconhecida_e_rejeitado():
    resp = client.options(
        "/api/info",
        headers={"Origin": "https://site-malicioso.example", "Access-Control-Request-Method": "GET"},
    )
    assert resp.status_code == 400
    assert "access-control-allow-origin" not in resp.headers


def test_origem_do_frontend_local_e_permitida():
    resp = client.get("/api/info", headers={"Origin": "http://localhost:5173"})
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"
