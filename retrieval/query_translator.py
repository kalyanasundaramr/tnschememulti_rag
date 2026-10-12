import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def translate_query_to_english(question: str) -> str:
    """Translate a question into English for scheme retrieval."""

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is missing from .env.")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    prompt = (
        "Translate this question into English for searching "
        "Tamil Nadu government scheme documents. Preserve its meaning. "
        "Return only the English translation.\n\n"
        f"Question: {question}"
    )

    response = llm.invoke(prompt)
    return str(response.content).strip()


if __name__ == "__main__":
    question = "கிராமப்புற சாலைகளை மேம்படுத்தும் திட்டம் எது?"
    print("Original:", question)
    print("English search query:", translate_query_to_english(question))