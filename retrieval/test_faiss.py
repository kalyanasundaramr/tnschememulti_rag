
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_DIR = PROJECT_ROOT / "data" / "faiss" / "tnrd_schemes"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    if not (INDEX_DIR / "index.faiss").exists():
        raise FileNotFoundError(f"FAISS index not found: {INDEX_DIR}")

    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    vectorstore = FAISS.load_local(
        str(INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )

    question = "Which scheme provides basic infrastructure facilities in rural habitations?"

    print(f"Question: {question}\n")

    results = vectorstore.similarity_search_with_score(question, k=3)

    for rank, (document, score) in enumerate(results, start=1):
        print(f"Result {rank}")
        print(f"Scheme: {document.metadata.get('scheme_name')}")
        print(f"Distance score: {score:.4f}")
        print(f"Source: {document.metadata.get('source_url')}")
        print(f"Content: {document.page_content[:350]}")
        print("-" * 60)


if __name__ == "__main__":
    main()
