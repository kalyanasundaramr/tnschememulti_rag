
import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Read the new Tamil Nadu agriculture chunks
CHUNKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "tn_agriculture_scheme_chunks.json"
)

# Create a separate index; preserve the old TNRD index
INDEX_DIR = (
    PROJECT_ROOT
    / "data"
    / "faiss"
    / "tn_agriculture_schemes"
)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"Chunks file not found: {CHUNKS_FILE}"
        )

    chunks = json.loads(
        CHUNKS_FILE.read_text(encoding="utf-8")
    )

    if not chunks:
        raise ValueError("No agriculture chunks found to embed.")

    documents = [
        Document(
            page_content=item["content"],
            metadata={
                "chunk_id": item["chunk_id"],
                "scheme_name": item["scheme_name"],
                "scheme_name_tamil": item.get(
                    "scheme_name_tamil", ""
                ),
                "department": item["department"],
                "source_url": item["source_url"],
                "start_index": item["start_index"],
            },
        )
        for item in chunks
    ]

    print(f"Loading embedding model: {EMBEDDING_MODEL}")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print(
        f"Building agriculture FAISS index "
        f"from {len(documents)} chunks..."
    )

    vectorstore = FAISS.from_documents(
        documents,
        embeddings,
    )

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(INDEX_DIR))

    print(f"FAISS index saved to: {INDEX_DIR}")
    print(f"Indexed documents: {vectorstore.index.ntotal}")


if __name__ == "__main__":
    main()
