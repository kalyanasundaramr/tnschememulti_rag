
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
    # Initialise chat history once per user session.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Provide a button to clear the conversation.
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

    # Display previous questions and answers.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept a new question.
    question = st.chat_input(
        "Ask about Tamil Nadu government schemes..."
    )

    if question:
        # Display and save the user's question.
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        # Generate the answer using your existing RAG pipeline.
        with st.chat_message("assistant"):
            with st.spinner(
                "Searching scheme documents and generating an answer..."
            ):
                try:
                    # Exclude the current question, which was just added to history.
                    previous_messages = st.session_state.messages[:-1]
                    result = ask_scheme_question(
                question.strip(),
                chat_history=previous_messages,
            )

                    answer = result["answer"]
                    st.markdown(answer)

                    if result.get("retrieved_schemes"):
                        with st.expander("Retrieved schemes"):
                            for scheme in result["retrieved_schemes"]:
                                st.write(f"- {scheme}")

                    if result.get("sources"):
                        with st.expander("Source documents"):
                            for source in result["sources"]:
                                st.markdown(f"- [{source}]({source})")

                    # Save the assistant's answer.
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                except Exception as exc:
                    st.error(
                        "Unable to answer this question. "
                        "Check your API configuration and project logs."
                    )
                    st.exception(exc)

with tab2:
    st.subheader("Explore scheme relationships")
    st.write(
        "Blue nodes represent schemes. Green nodes represent "
        "categories mentioned in the source documents."
    )

    render_knowledge_graph(height=700)
