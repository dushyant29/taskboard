import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
from fastapi.testclient import TestClient
from app.main import Base, app, engine

Base.metadata.create_all(engine)
c = TestClient(app)


def test_crud():
    r = c.post("/api/tasks", json={"title": "ship it"})
    assert r.status_code == 201
    tid = r.json()["id"]
    assert c.patch(f"/api/tasks/{tid}").json()["done"] is True
    assert any(t["id"] == tid for t in c.get("/api/tasks").json())
    assert c.delete(f"/api/tasks/{tid}").status_code == 204


def test_health():
    assert c.get("/healthz").status_code == 200
    assert c.get("/readyz").status_code == 200
