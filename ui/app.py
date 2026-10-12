
import streamlit as st

from retrieval.rag_pipeline import ask_scheme_question

st.set_page_config(
    page_title="Tamil Nadu Government Schemes AI",
    page_icon="🌾",
    layout="wide",
)

st.title("🌾 Tamil Nadu Government Schemes AI")
st.write(
    "Ask questions about Tamil Nadu rural development schemes. "
    "Answers are generated from locally indexed scheme documents."
)

with st.sidebar:
    st.header("About")
    st.write("Retrieval: FAISS + BM25 hybrid search")
    st.write("Answer generation: OpenAI")
    st.caption(
        "Verify important eligibility and application details "
        "with the relevant government department."
    )

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

            except Exception as exc:
                st.error(
                    "Unable to answer this question. "
                    "Check your API configuration and project logs."
                )
                st.exception(exc)
