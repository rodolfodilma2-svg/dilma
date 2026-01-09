import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
from srodolfobarbosa.deus import app

client = TestClient(app)


def test_root():
    res = client.get("/")
    assert res.status_code == 200
    assert "NEXO" in res.text


def test_insights_pending_protected():
    res = client.post("/insights/pending", data={"token": "wrong"})
    assert res.status_code == 403


def test_admin_exec_pending_sandbox(tmp_path, monkeypatch):
    # create a pending action file in repo
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent
    pending_dir = repo_root / "pending_actions"
    pending_dir.mkdir(exist_ok=True)
    f = pending_dir / "test_exec.py"
    f.write_text("resultado = 1 + 2")

    monkeypatch.setenv("ADMIN_TOKEN", "secrettoken")

    res = client.post(
        "/admin/exec_pending", data={"filename": "test_exec.py", "token": "secrettoken"}
    )
    assert res.status_code == 200
    assert res.json().get("status") == "ok"
    assert res.json().get("resultado") == "3"
