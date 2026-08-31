import pytest
from httpx import ASGITransport, AsyncClient
from app.src.main import app
from app.src import models
from app.src.db import engine


@pytest.mark.asyncio
async def test_crud_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # create
        payload = {"title": "Test task", "description": "desc"}
        r = await ac.post("/tasks", json=payload)
        assert r.status_code == 200
        data = r.json()
        task_id = data["id"]

        # get
        r = await ac.get(f"/tasks/{task_id}")
        assert r.status_code == 200

        # list
        r = await ac.get("/tasks")
        assert r.status_code == 200
        assert len(r.json()) >= 1

        # update
        r = await ac.put(f"/tasks/{task_id}", json={"completed": True})
        assert r.status_code == 200
        assert r.json()["completed"] is True

        # delete
        r = await ac.delete(f"/tasks/{task_id}")
        assert r.status_code == 200
        assert r.json()["deleted"] is True
