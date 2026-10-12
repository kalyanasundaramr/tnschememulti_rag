
import json
import re
from pathlib import Path

from rank_bm25 import BM25Okapi

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = PROJECT_ROOT / "data" / "processed" / "scheme_chunks.json"


def tokenize(text: str) -> list[str]:
    """Convert text into lowercase word tokens."""
    return re.findall(r"\b\w+\b", text.lower())


def load_chunks() -> list[dict]:
    """Load the existing scheme chunks."""
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {CHUNKS_FILE}"
        )

    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))

    if not chunks:
        raise ValueError("No scheme chunks are available.")

    return chunks


def search_keywords(question: str, k: int = 3) -> list[dict]:
    """Return scheme chunks ranked by BM25 keyword relevance."""
    if not question or not question.strip():
        raise ValueError("Please enter a non-empty question.")

    if k < 1:
        raise ValueError("k must be at least 1.")

    chunks = load_chunks()
    tokenized_chunks = [
        tokenize(chunk["content"]) for chunk in chunks
    ]

    bm25 = BM25Okapi(tokenized_chunks)
    scores = bm25.get_scores(tokenize(question))

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True,
    )

    results = []

    for index in ranked_indices[:k]:
        result = chunks[index].copy()
        result["bm25_score"] = float(scores[index])
        results.append(result)

    return results


if __name__ == "__main__":
    question = "Which scheme provides basic infrastructure facilities in rural habitations?"

    print(f"Question: {question}")

    for rank, result in enumerate(
        search_keywords(question, k=3), start=1
    ):
        print(f"\nResult {rank}")
        print(f"Scheme: {result['scheme_name']}")
        print(f"BM25 score: {result['bm25_score']:.4f}")
        print(f"Source: {result['source_url']}")
        print(f"Content: {result['content'][:350]}")
        print("-" * 60)
