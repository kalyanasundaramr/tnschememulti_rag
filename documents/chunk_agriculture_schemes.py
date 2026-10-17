
import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "tn_agriculture_schemes_clean.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "tn_agriculture_scheme_chunks.json"
)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Cleaned data not found: {INPUT_FILE}")

    schemes = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    documents = []

    for scheme in schemes:
        content = scheme.get("content", "").strip()

        if not content:
            continue

        documents.append(
            Document(
                page_content=content,
                metadata={
                    "scheme_name": scheme["scheme_name"],
                    "scheme_name_tamil": scheme["scheme_name_tamil"],
                    "department": scheme["department"],
                    "source_url": scheme["source_url"],
                },
            )
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )

    chunks = splitter.split_documents(documents)
    records = []

    for chunk_id, chunk in enumerate(chunks):
        records.append({
            "chunk_id": chunk_id,
            "scheme_name": chunk.metadata["scheme_name"],
            "scheme_name_tamil": chunk.metadata["scheme_name_tamil"],
            "department": chunk.metadata["department"],
            "source_url": chunk.metadata["source_url"],
            "start_index": chunk.metadata.get("start_index", 0),
            "content": chunk.page_content,
        })

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Source scheme documents: {len(documents)}")
    print(f"Generated chunks: {len(records)}")
    print(f"Chunk size: {CHUNK_SIZE} characters")
    print(f"Chunk overlap: {CHUNK_OVERLAP} characters")
    print(f"Saved chunks to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
