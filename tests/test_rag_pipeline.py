
from unittest.mock import patch

from retrieval.rag_pipeline import ask_scheme_question


def test_no_retrieved_documents_returns_safe_response():
    with patch(
        "retrieval.rag_pipeline.search_hybrid",
        return_value=[],
    ):
        result = ask_scheme_question(
            "What is the eligibility for an unknown scheme?"
        )

    assert result["question"] == (
        "What is the eligibility for an unknown scheme?"
    )
    assert "not provide enough information" in result["answer"].lower()
    assert result["sources"] == []
    assert result["retrieved_schemes"] == []

def test_successful_retrieval_generates_answer_and_sources():
    fake_results = [
        {
            "scheme_name": "Tamil Nadu Rural Roads Improvement Scheme",
            "source_url": "https://example.gov.in/roads",
            "content": "Roads connecting unconnected habitations receive priority.",
        }
    ]

    with (
        patch("retrieval.rag_pipeline.search_hybrid", return_value=fake_results),
        patch(
            "retrieval.rag_pipeline.generate_answer",
            return_value="The scheme prioritizes roads connecting unconnected habitations.",
        ) as mock_generate,
    ):
        result = ask_scheme_question("Which roads receive priority?")

    assert "prioritizes roads" in result["answer"]
    assert result["sources"] == ["https://example.gov.in/roads"]
    assert result["retrieved_schemes"] == [
        "Tamil Nadu Rural Roads Improvement Scheme"
    ]
    mock_generate.assert_called_once()
