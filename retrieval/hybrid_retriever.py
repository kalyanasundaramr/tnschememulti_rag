
from retrieval.vector_retriever import search_schemes
from retrieval.keyword_retriever import search_keywords
from retrieval.query_translator import translate_query_to_english


def reciprocal_rank_fusion(
    vector_results,
    keyword_results,
    k: int = 60,
):
    """Combine ranked results using Reciprocal Rank Fusion."""
    fused = {}

    def add_results(results, source_name):
        for rank, item in enumerate(results, start=1):
            if source_name == "vector":
                document = item[0]
                metadata = document.metadata
                content = document.page_content
            else:
                metadata = item
                content = item["content"]

            key = (
                metadata.get("source_url", ""),
                metadata.get("start_index", 0),
                content,
            )

            if key not in fused:
                fused[key] = {
                    "scheme_name": metadata.get("scheme_name", ""),
                    "source_url": metadata.get("source_url", ""),
                    "start_index": metadata.get("start_index", 0),
                    "content": content,
                    "rrf_score": 0.0,
                    "retrieved_by": [],
                }

            fused[key]["rrf_score"] += 1.0 / (k + rank)

            if source_name not in fused[key]["retrieved_by"]:
                fused[key]["retrieved_by"].append(source_name)

    add_results(vector_results, "vector")
    add_results(keyword_results, "keyword")

    return sorted(
        fused.values(),
        key=lambda item: item["rrf_score"],
        reverse=True,
    )



def search_hybrid(question: str, limit: int = 5):
    """Retrieve hybrid results and prefer one result per scheme."""
    if not question or not question.strip():
        raise ValueError("Please enter a non-empty question.")

    if limit < 1:
        raise ValueError("limit must be at least 1.")

    search_question = translate_query_to_english(question)
    vector_results = search_schemes(search_question, k=limit * 3)
    keyword_results = search_keywords(search_question, k=limit * 3)

    fused_results = reciprocal_rank_fusion(
        vector_results,
        keyword_results,
    )

    unique_schemes = []
    seen_schemes = set()

    for result in fused_results:
        scheme_key = result["scheme_name"].strip().casefold()

        if scheme_key in seen_schemes:
            continue

        seen_schemes.add(scheme_key)
        unique_schemes.append(result)

        if len(unique_schemes) >= limit:
            break

    return unique_schemes



if __name__ == "__main__":
    question = "Which scheme improves village roads and rural connectivity?"

    print(f"Question: {question}")

    for rank, result in enumerate(
        search_hybrid(question, limit=5), start=1
    ):
        print(f"\nResult {rank}")
        print(f"Scheme: {result['scheme_name']}")
        print(f"RRF score: {result['rrf_score']:.6f}")
        print(f"Retrieved by: {', '.join(result['retrieved_by'])}")
        print(f"Source: {result['source_url']}")
        print(f"Content: {result['content'][:300]}")
        print("-" * 60)
