import pytest
from pydantic import ValidationError

from app.models.schemas import ChatRequest

def test_valid_chat_request():
    request = ChatRequest(
        question="What is the main objective?"
    )

    assert request.question == "What is the main objective?"
    assert request.document_id is None
    assert request.top_k == 3

def test_chat_request_with_all_fields():
    request = ChatRequest(
        question="Summarize the document",
        document_id="document-123",
        top_k=5
    )

    assert request.document_id == "document-123"
    assert request.top_k == 5

def test_question_must_have_at_least_three_characters():
    with pytest.raises(ValidationError):
        ChatRequest(question="Hi")

@pytest.mark.parametrize("top_k", [0, -1, 11, 100])
def test_top_k_rejects_values_outside_allowed_range(top_k):
    with pytest.raises(ValidationError):
        ChatRequest(
            question="Explain the document",
            top_k=top_k
        )

@pytest.mark.parametrize("top_k", [1, 3, 10])
def test_top_k_accepts_values_within_allowed_range(top_k):
    request = ChatRequest(
        question="Explain the document",
        top_k=top_k
    )

    assert request.top_k == top_k