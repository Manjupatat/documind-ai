import re

import pytest

from app.services.rag_pipeline import rag_pipeline


GRAND_CHALLENGE_ID = "9b056381-7716-4279-9262-49b78bd687ac"
KSP_ID = "80e2e5b7-c453-41ce-b4f3-f0ede5efde00"


def ask_document(question: str, document_id: str):
    return rag_pipeline.ask(
        question=question,
        top_k=3,
        document_id=document_id
    )


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def assert_valid_citations(result):
    """Check that generated citation IDs exist in the returned sources."""
    answer = result["answer"]

    assert "[unverified citation]" not in answer

    cited_ids = set(re.findall(r"\[(S\d+)\]", answer))
    valid_ids = {
        source["source_id"]
        for source in result["sources"]
    }

    assert cited_ids.issubset(valid_ids)


def assert_sources_belong_to_document(result, document_id):
    for source in result["sources"]:
        assert source["document_id"] == document_id


def assert_abstained(result):
    answer = normalize(result["answer"])

    abstention_phrases = [
        "not contain enough information",
        "does not contain enough information",
        "couldn't find relevant information",
        "insufficient information",
        "cannot answer"
    ]

    assert any(phrase in answer for phrase in abstention_phrases), (
        f"Expected an abstention, but received: {result['answer']}"
    )


def test_grand_challenge_relevant_question():
    result = ask_document(
        "Which seven crops are given special emphasis in the programme?",
        GRAND_CHALLENGE_ID
    )

    answer = normalize(result["answer"])

    expected_crops = [
        "onion",
        "mango",
        "banana",
        "tomato",
        "grapes",
        "pomegranate",
        "pineapple"
    ]

    assert all(crop in answer for crop in expected_crops)
    assert_sources_belong_to_document(result, GRAND_CHALLENGE_ID)
    assert_valid_citations(result)


def test_ksp_relevant_question():
    result = ask_document(
        "What did the user ask the assistant to investigate?",
        KSP_ID
    )

    answer = normalize(result["answer"])

    # Accept the original typo as well as the correct spelling.
    assert "fraud" in answer or "farud" in answer

    assert_sources_belong_to_document(result, KSP_ID)
    assert_valid_citations(result)



def test_unsupported_software_engineering_question():
    result = ask_document(
        "What are the eligibility criteria for software engineering jobs?",
        GRAND_CHALLENGE_ID
    )

    assert_abstained(result)
    assert_sources_belong_to_document(result, GRAND_CHALLENGE_ID)
    assert_valid_citations(result)


def test_unrelated_japan_question():
    result = ask_document(
        "What is the capital city of Japan?",
        GRAND_CHALLENGE_ID
    )

    assert_abstained(result)
    assert_sources_belong_to_document(result, GRAND_CHALLENGE_ID)
    assert_valid_citations(result)


def test_document_isolation():
    # Crop information belongs to Grand Challenge, not the KSP document.
    result = ask_document(
        "Which seven crops are given special emphasis in the programme?",
        KSP_ID
    )

    assert_abstained(result)
    assert_sources_belong_to_document(result, KSP_ID)
    assert_valid_citations(result)
