"""Testes de segurança da rota catch-all da SPA (path traversal)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import montar_frontend, resolver_arquivo_spa

INDEX_HTML = "<html>index</html>"


def _criar_ambiente(tmp_path):
    dist = tmp_path / "frontend" / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text(INDEX_HTML)
    (dist / "favicon.svg").write_text("<svg/>")
    (dist / "assets" / "app.js").write_text("console.log(1)")
    segredo = tmp_path / "backend" / ".env"
    segredo.parent.mkdir(parents=True)
    segredo.write_text("GEMINI_API_KEY=segredo")
    app = FastAPI()
    montar_frontend(app, dist)
    return dist, segredo, TestClient(app)


def test_serve_arquivo_existente_dentro_do_dist(tmp_path):
    _, _, client = _criar_ambiente(tmp_path)
    resp = client.get("/favicon.svg")
    assert resp.status_code == 200
    assert resp.text == "<svg/>"
    assert client.get("/assets/app.js").text == "console.log(1)"


def test_rota_spa_desconhecida_retorna_index(tmp_path):
    _, _, client = _criar_ambiente(tmp_path)
    resp = client.get("/alguma/rota/da/spa")
    assert resp.status_code == 200
    assert resp.text == INDEX_HTML


def test_path_traversal_codificado_retorna_index(tmp_path):
    _, _, client = _criar_ambiente(tmp_path)
    for url in ("/..%2F..%2Fbackend%2F.env", "/%2E%2E/%2E%2E/backend/.env", "/assets/..%2F..%2F..%2Fbackend%2F.env"):
        resp = client.get(url)
        assert "segredo" not in resp.text, url
        if resp.status_code == 200:
            assert resp.text == INDEX_HTML, url


def test_caminho_absoluto_retorna_index(tmp_path):
    _, segredo, client = _criar_ambiente(tmp_path)
    for url in ("//etc/passwd", "/" + str(segredo)):
        resp = client.get(url)
        assert resp.status_code == 200, url
        assert resp.text == INDEX_HTML, url


def test_resolver_arquivo_spa_bloqueia_saida_do_dist(tmp_path):
    dist, segredo, _ = _criar_ambiente(tmp_path)
    index = dist.resolve() / "index.html"
    assert resolver_arquivo_spa(dist, "../../backend/.env") == index
    assert resolver_arquivo_spa(dist, str(segredo)) == index
    assert resolver_arquivo_spa(dist, "/etc/passwd") == index
    assert resolver_arquivo_spa(dist, "../dist-irmao/x") == index


def test_resolver_arquivo_spa_bloqueia_symlink_para_fora(tmp_path):
    dist, segredo, _ = _criar_ambiente(tmp_path)
    try:
        (dist / "link.env").symlink_to(segredo)
    except OSError:
        pytest.skip("Criação de links simbólicos requer privilégios de administrador no Windows")
    assert resolver_arquivo_spa(dist, "link.env") == dist.resolve() / "index.html"
