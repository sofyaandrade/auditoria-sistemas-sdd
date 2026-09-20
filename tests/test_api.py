def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_task_crud(client):
    created = client.post(
        "/tasks", json={"title": "Entregar projeto", "description": "DevOps"}
    )
    assert created.status_code == 201
    task_id = created.json()["id"]

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/tasks/{task_id}")
    assert fetched.json()["title"] == "Entregar projeto"

    updated = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert updated.status_code == 200
    assert updated.json()["completed"] is True

    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_missing_task(client):
    assert client.patch("/tasks/999", json={"completed": True}).status_code == 404
    assert client.delete("/tasks/999").status_code == 404
