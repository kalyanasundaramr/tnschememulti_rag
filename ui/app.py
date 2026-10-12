
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

from retrieval.rag_pipeline import ask_scheme_question
from graph.visualize_graph import render_knowledge_graph


st.set_page_config(
    page_title="Tamil Nadu Government Schemes AI",
    page_icon="🌾",
    layout="wide",
)

st.title("🌾 Tamil Nadu Government Schemes AI")

st.write(
    "Ask questions about Tamil Nadu rural development schemes. "
    "Find information from locally indexed government documents and "
    "explore their Knowledge Graph."
)

with st.sidebar:
    st.header("About")
    st.write("**Document retrieval:** FAISS + BM25 hybrid search")
    st.write("**Knowledge Graph:** NetworkX + PyVis")
    st.write("**Answer generation:** OpenAI")
    st.caption(
        "Verify important eligibility and application details "
        "with the relevant government department."
    )

tab1, tab2 = st.tabs(["Ask a question", "Knowledge Graph"])

with tab1:
    question = st.text_area(
        "Enter your question",
        placeholder="Example: Which scheme improves village roads?",
        height=100,
    )

    if st.button("Find scheme information", type="primary"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Searching scheme documents and generating an answer..."):
                try:
                    result = ask_scheme_question(question.strip())

                    st.subheader("Answer")
                    st.markdown(result["answer"])

                    st.subheader("Retrieved schemes")
                    for scheme in result["retrieved_schemes"]:
                        st.write(f"- {scheme}")

                    st.subheader("Source documents")
                    for source in result["sources"]:
                        st.markdown(f"- [{source}]({source})")

                except Exception:
                    st.error(
                        "Unable to answer this question. "
                        "Check your API configuration and project logs."
                    )
                    st.exception(None)

with tab2:
    st.subheader("Explore scheme relationships")
    st.write(
        "Blue nodes represent schemes. Green nodes represent infrastructure "
        "categories mentioned in the source documents."
    )

    render_knowledge_graph(height=700)
