
import pytest

from generation.answer_generator import generate_answer


def test_empty_question_raises_error():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        generate_answer("", "Some scheme context")


def test_empty_context_returns_safe_message():
    answer = generate_answer("What is this scheme?", "   ")

    assert "not provide enough information" in answer.lower()
