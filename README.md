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
│
