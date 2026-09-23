from __future__ import annotations

import os
from uuid import uuid4

import httpx


BASE_URL = os.getenv("RELAY_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")


def register_agent(client: httpx.Client, name: str) -> tuple[dict, dict[str, str]]:
    response = client.post("/api/v1/agents", json={"name": name})
    assert response.status_code == 201, response.text
    data = response.json()
    return data, {"Authorization": f"Bearer {data['token']}"}


def test_first_acceptance_scenario_against_live_api_and_database():
    suffix = uuid4().hex

    with httpx.Client(base_url=BASE_URL, timeout=10) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json() == {"status": "ok"}

        sender, sender_headers = register_agent(client, f"sender-{suffix}")
        recipient, recipient_headers = register_agent(client, f"uppercase-{suffix}")

        task_response = client.post(
            "/api/v1/tasks",
            headers={**sender_headers, "Idempotency-Key": f"acceptance-{suffix}"},
            json={"to": recipient["agent_id"], "input": "hello from integration test"},
        )
        assert task_response.status_code == 201, task_response.text
        task = task_response.json()

        claim_response = client.post(
            "/api/v1/tasks/claim",
            headers=recipient_headers,
            json={"worker_id": f"integration-worker-{suffix}", "wait_seconds": 0},
        )
        assert claim_response.status_code == 200, claim_response.text
        claim = claim_response.json()
        assert claim["task_id"] == task["task_id"]
        assert claim["input"] == "hello from integration test"
        assert claim["attempt"] == 1

        completion_response = client.post(
            f"/api/v1/tasks/{task['task_id']}/complete",
            headers=recipient_headers,
            json={
                "claim_token": claim["claim_token"],
                "output": claim["input"].upper(),
            },
        )
        assert completion_response.status_code == 200, completion_response.text
        assert completion_response.json() == {"task_id": task["task_id"], "status": "completed"}

        result_response = client.get(f"/api/v1/tasks/{task['task_id']}", headers=sender_headers)
        assert result_response.status_code == 200, result_response.text
        result = result_response.json()
        assert result["status"] == "completed"
        assert result["output"] == "HELLO FROM INTEGRATION TEST"
        assert result["from"] == sender["agent_id"]
        assert result["to"] == recipient["agent_id"]