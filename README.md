# Tamil Nadu Government Schemes Multi-RAG AI

## Overview

A Retrieval-Augmented Generation (RAG) application that answers questions about Tamil Nadu government rural development schemes using locally stored and indexed scheme documents.

The application combines semantic search with keyword search to retrieve relevant information and uses an OpenAI language model to generate answers grounded in the retrieved context.

## Features

- Ingest scheme information from official Tamil Nadu Rural Development and Panchayat Raj (TNRD) web pages.
- Clean and split documents into searchable chunks.
- Generate embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
- Store and search document embeddings using FAISS.
- Combine semantic and keyword retrieval using Reciprocal Rank Fusion (RRF).
- Generate context-grounded answers using OpenAI through LangChain.
- Display answers, retrieved schemes, and source links in Streamlit.
- Use `.env` for local API-key configuration.

## Technology Stack

- Python
- LangChain
- Streamlit
- FAISS
- Hugging Face Sentence Transformers
- BM25 keyword retrieval
- OpenAI
- Python dotenv

## Project Structure

- `ingestion/` — Collect scheme information.
- `documents/` — Clean documents and split them into chunks.
- `vectorstore/` — Build the FAISS index.
- `retrieval/` — Semantic, keyword, hybrid retrieval, and RAG pipeline.
- `generation/` — Prompt template and answer generation.
- `ui/` — Streamlit application.
- `config/` — Configuration files.
- `data/raw/` — Raw source data.
- `data/processed/` — Cleaned documents and chunks.
- `data/faiss/` — Locally generated FAISS index.
- `tests/` — Automated tests.

## Setup

### 1. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure the API key

Create a local `.env` file in the project root:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

Replace the placeholder with your own API key. Never commit `.env` or share the key publicly.

### 4. Prepare the scheme data

Run the ingestion, cleaning, chunking, and FAISS-building scripts in their intended order. The generated local data and vector index are excluded from Git and may need to be regenerated after cloning.

### 5. Start the application

From the project root, run:

```powershell
python -m streamlit run ui/app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## How It Works

1. The user enters a question in Streamlit.
2. FAISS retrieves semantically similar document chunks.
3. BM25 retrieves keyword-matching chunks.
4. Reciprocal Rank Fusion combines the retrieval results.
5. Retrieved content is passed to the LangChain prompt.
6. The OpenAI model generates an answer based on the supplied context.
7. The UI displays the answer, retrieved schemes, and source URLs.

## Limitations

- Answers depend on the coverage and quality of the ingested documents.
- Generated answers may be incomplete; verify important eligibility, benefit, and application details with the relevant government department.
- The local vector index must be built before retrieval can work.
- This project does not guarantee that a scheme is currently active.

## Security

- Keep API keys in `.env`.
- Keep `.env` out of Git.
- Commit `.env.example` only if it contains placeholders and no real credentials.
- Do not commit generated indexes or private credentials.

## Disclaimer

This application is an informational aid. Consult official government sources for authoritative and up-to-date scheme information.
