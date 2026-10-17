# Tamil Nadu Government Schemes Multi-RAG AI

A Streamlit-based AI application that answers questions about **Tamil Nadu Agriculture schemes** using official government scheme data, hybrid retrieval, conversational context, and an interactive Knowledge Graph. The application supports Tamil and English queries and generates answers grounded in retrieved source content.

## Features

- **Agriculture scheme ingestion:** Retrieves scheme data from the Tamil Nadu Agriculture API. Collected 77 unique active schemes across 103 active classes checked.
- **Data processing:** Cleans and combines Tamil and English scheme information and generates 197 text chunks.
- **Vector search:** Uses FAISS and local Sentence Transformer embeddings.
- **Keyword search:** Uses BM25 to identify relevant scheme passages.
- **Hybrid retrieval:** Combines vector and keyword rankings using Reciprocal Rank Fusion.
- **Tamil and English support:** Supports cross-language retrieval and responses in the user's query language.
- **Conversational chat history:** Maintains recent conversation context for follow-up questions and provides a clear-chat option.
- **Answer generation:** Uses OpenAI to generate answers grounded in retrieved scheme information.
- **LLM-based Knowledge Graph:** Uses structured LLM extraction and NetworkX to represent relationships involving schemes, beneficiaries, departments, and benefits.
- **Interactive visualization:** Uses PyVis to explore scheme relationships in Streamlit.
- **Retrieval evaluation:** Measures Hit-rate@5 and Mean Reciprocal Rank (MRR).
- **Faithfulness evaluation:** Uses RAGAS to assess whether generated answers are supported by retrieved context.
- **Automated tests:** Tests retrieval, answer generation, graph integrity, and the RAG pipeline.

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
- Pydantic
- RAGAS
- pytest

## Project Structure

```text
tnschememulti_rag/
├── config/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── faiss/
│   └── evaluation/
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
├── requirements.txt
└── README.md
```

## Setup

### 1. Create and activate a virtual environment

Run these commands in Windows PowerShell from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If Python is not available through the `python` command, use the full path to your installed Python interpreter.

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure the OpenAI API key

Create a `.env` file in the project root:

```text
OPENAI_API_KEY=your_api_key_here
```

Never commit your real API key to GitHub. Ensure `.env` is included in `.gitignore`.

## Run the Application

Start Streamlit from the project root:

```powershell
python -m streamlit run ui/app.py
```

Open the local URL printed in the terminal, usually:

`http://localhost:8501`

Use the chat interface to ask questions about Tamil Nadu Agriculture schemes. Ask follow-up questions to continue the conversation without repeating the full context. Use the Knowledge Graph visualization to explore extracted scheme relationships.

## Data Ingestion and Indexing

The agriculture data pipeline retrieves scheme information from the configured Tamil Nadu Agriculture API sources and processes it for retrieval.

The general processing sequence is:

1. Crawl scheme data.
2. Clean and combine Tamil and English scheme information.
3. Split scheme records into text chunks.
4. Generate embeddings and build the FAISS index.
5. Prepare the BM25 keyword index.
6. Build the Knowledge Graph.

Key scripts include:

- `ingestion/crawl_schemes.py`
- `documents/clean_agriculture_schemes.py`
- `documents/chunk_agriculture_schemes.py`
- `vectorstore/build_faiss.py`
- `retrieval/vector_retriever.py`
- `retrieval/keyword_retriever.py`
- `retrieval/hybrid_retriever.py`
- `graph/build_graph.py`

Run the scripts in the order required by their dependencies when refreshing the dataset. Confirm the configured paths and settings before rebuilding indexes.

**Data coverage note:** The current crawl collected 77 unique active schemes across 103 active classes checked. Exhaustive coverage of every available scheme has not been independently verified. The earlier Rural Development dataset and index are preserved separately.

## Knowledge Graph

The graph is built using structured LLM-based extraction and NetworkX.

The latest generated graph contains:

- **181 nodes**
- **392 edges**
- **77 scheme records**

The graph represents relationships extracted from scheme records, including beneficiaries, departments, and benefits. Graph information is connected with retrieved scheme results in the RAG pipeline.

The graph is stored locally as JSON. No Neo4j server is required.

Check `graph/build_graph.py` for the current output path and configuration before rebuilding the graph.

## Evaluation Results

The initial evaluation run produced the following results:

| Metric | Result |
|---|---:|
| Labelled retrieval questions | 20 |
| Successfully evaluated questions | 20 |
| Hit-rate@5 | 75.00% |
| Mean Reciprocal Rank (MRR) | 0.4783 |
| RAGAS faithfulness | 92.67% |

### Evaluation scripts

- `evaluation/evaluate_retrieval.py` — calculates Hit-rate@5 and MRR.
- `evaluation/evaluate_faithfulness.py` — evaluates answer faithfulness using RAGAS.
- `evaluation/create_evaluation_summary.py` — combines evaluation metrics into a JSON report.

Latest combined report:

`data/evaluation/combined_evaluation_summary_20261017_204410.json`

### Interpreting the results

The retrieval evaluation indicates that at least one relevant result appeared in the top five for 75% of the labelled questions. The five retrieval misses should be investigated to improve retrieval coverage.

The faithfulness score measures support from the retrieved context; it does not independently prove that an answer is factually correct or that the source data is current.

## Run Tests

Run the automated test suite:

```powershell
python -m pytest tests -v -o addopts="" -p no:cacheprovider
```

The previously reported test suite contains 10 passing tests. Run the command again after making changes to confirm the current test status.

## Caching and Performance

The application uses Streamlit resource caching to reduce repeated initialization of embedding models and retrieval resources. Processed chunks and the BM25 index are also cached.

This reduces unnecessary rebuilding and improves responsiveness during repeated interactions.

## Important Limitations and Future Improvements

- Answers depend on the available indexed source documents.
- Scheme coverage must be validated against all available Agriculture API categories and records.
- Investigate the five missed retrieval questions and improve retrieval where necessary.
- Validate Knowledge Graph relationships against the original scheme records.
- Verify that the application consistently uses the Agriculture dataset rather than the preserved Rural Development index.
- Faithfulness scores are not a substitute for independent factual verification.
- Confirm eligibility, benefits, application procedures, and current scheme status with the relevant government department.
- The graph is stored locally as JSON and uses NetworkX; a Neo4j server is not required.

## Project Status

The four main review comments have been implemented:

1. Tamil Nadu Agriculture scheme data ingestion.
2. Cached retrieval resources.
3. Conversational chat history and follow-up context.
4. LLM-based Knowledge Graph relationship extraction.

Initial retrieval and faithfulness evaluations have also been completed. Further work focuses on improving retrieval coverage, validating data and graph quality, confirming dataset selection in the UI, and maintaining updated documentation.
