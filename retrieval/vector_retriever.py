
import streamlit as st
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INDEX_DIR = (
    PROJECT_ROOT
    / "data"
    / "faiss"
    / "tn_agriculture_schemes"
)


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@st.cache_resource
def load_embeddings():
    """Load and cache the embedding model."""
    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


@st.cache_resource
def load_vectorstore():
    """Load and cache the locally saved FAISS index."""
    if not (INDEX_DIR / "index.faiss").exists():
        raise FileNotFoundError(
            f"FAISS index not found at {INDEX_DIR}. "
            "Run vectorstore/build_faiss.py first."
        )

    embeddings = load_embeddings()

    return FAISS.load_local(
        str(INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def search_schemes(question: str, k: int = 3):
    """Return the most relevant scheme chunks for a question."""
    if not question or not question.strip():
        raise ValueError("Please enter a non-empty question.")

    if k < 1:
        raise ValueError("k must be at least 1.")

    vectorstore = load_vectorstore()
    return vectorstore.similarity_search_with_score(question, k=k)


if __name__ == "__main__":
    question = "Which schemes provide subsidies to farmers, and what benefits do they offer?"

    results = search_schemes(question, k=3)

    for rank, (document, score) in enumerate(results, start=1):
        print(f"\nResult {rank}")
        print(f"Scheme: {document.metadata.get('scheme_name')}")
        print(f"Distance score: {score:.4f}")
        print(f"Source: {document.metadata.get('source_url')}")
        print(f"Content: {document.page_content[:350]}")
