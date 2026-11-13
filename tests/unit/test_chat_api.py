
from fastapi.testclient import TestClient

from app.main import app
from app.api import chat as chat_api


client = TestClient(app)


def test_invalid_chat_request_does_not_call_rag_pipeline(monkeypatch):
    called = False

    def fake_ask(**kwargs):
        nonlocal called
        called = True
        return {}

    monkeypatch.setattr(
        chat_api.rag_pipeline,
        "ask",
        fake_ask
    )

    response = client.post(
        "/api/documents/chat",
        json={"question": "Hi"}
    )

    assert response.status_code == 422
    assert called is False


def test_valid_chat_request_returns_expected_response(monkeypatch):
    def fake_ask(question, top_k, document_id):
        return {
            "question": question,
            "answer": "The document explains artificial intelligence.",
            "sources": []
        }

    monkeypatch.setattr(
        chat_api.rag_pipeline,
        "ask",
        fake_ask
    )

    response = client.post(
        "/api/documents/chat",
        json={
            "question": "What is artificial intelligence?",
            "top_k": 3
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What is artificial intelligence?"
    assert data["answer"] == "The document explains artificial intelligence."
    assert data["sources"] == []


def test_chat_pipeline_exception_returns_500(monkeypatch):
    def fake_ask(**kwargs):
        raise RuntimeError("Simulated pipeline failure")

    monkeypatch.setattr(
        chat_api.rag_pipeline,
        "ask",
        fake_ask
    )

    response = client.post(
        "/api/documents/chat",
        json={
            "question": "Explain the document"
        }
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Unable to process your question. Please try again."
    )
