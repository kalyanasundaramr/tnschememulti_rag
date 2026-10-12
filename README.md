# Tamil Nadu Government Schemes Multi-RAG AI

A Streamlit-based AI application that answers questions about Tamil Nadu rural development schemes using locally indexed government documents, hybrid retrieval, and an interactive Knowledge Graph.

## Features

- **Document ingestion:** Collects and cleans scheme information from official government sources.
- **Vector search:** Uses FAISS and local sentence-transformer embeddings.
- **Keyword search:** Uses BM25 to find relevant passages.
- **Hybrid retrieval:** Combines vector and keyword rankings using Reciprocal Rank Fusion.
- **Tamil and English queries:** Translates queries where needed to improve cross-language retrieval.
- **Answer generation:** Uses OpenAI to generate answers grounded in retrieved document content.
- **Knowledge Graph:** Uses NetworkX to build relationships between schemes and infrastructure categories.
- **Interactive visualization:** Uses PyVis to explore graph relationships in Streamlit.
- **Automated tests:** Tests retrieval quality, answer generation, graph integrity, and the RAG pipeline.

## Technology Stack

- Python 3.12
- Streamlit
- LangChain
- OpenAI
- FAISS
- Sentence Transformers
- BM25
- NetworkX
- PyVis
- pytest

## Project Structure

```text
tnschememulti_rag/
├── config/
├── data/
│   ├── raw/
│   ├── processed/
│   └── faiss/
├── documents/
├── embeddings/
├── generation/
├── graph/
├── guardrails/
├── ingestion/
├── retrieval/
├── tests/
├── ui/
├── vectorstore/
├── .env
├── .gitignore
└── README.md
```

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file in the project root and configure your OpenAI API key:

```text
OPENAI_API_KEY=your_api_key_here
```

Never commit your real API key to GitHub.

## Run the Application

Start Streamlit from the project root:

```powershell
python -m streamlit run ui/app.py
```

Open the local URL printed in the terminal, usually `http://localhost:8501`.

Use the **Ask a question** tab to ask about schemes. Use the **Knowledge Graph** tab to explore scheme relationships and inspect source documents.

## Rebuild Data and Indexes

Run the project's ingestion, cleaning, chunking, and indexing scripts in the appropriate order when refreshing source data. Build the graph with:

```powershell
python graph/build_graph.py
```

The graph is saved to `data/processed/scheme_graph.json`.

## Run Tests

```powershell
python -m pytest tests -v -o addopts="" -p no:cacheprovider
```

The current test suite contains 10 passing tests.

## Important Limitations

- Answers depend on the available indexed source documents.
- Graph relationships currently indicate infrastructure categories mentioned in scheme text; they do not independently establish funding, eligibility, or current scheme status.
- Verify important eligibility and application details with the relevant government department.
- The graph is stored locally as JSON and uses NetworkX; this implementation does not require a Neo4j server.
