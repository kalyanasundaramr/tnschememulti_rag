
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from generation.prompt_template import ANSWER_PROMPT

load_dotenv()


def generate_answer(question: str, context: str) -> str:
    """Generate a grounded answer using retrieved scheme context."""

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your .env file."
        )

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if not context.strip():
        return (
            "The available scheme documents do not provide "
            "enough information to answer this question."
        )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )

    chain = ANSWER_PROMPT | llm

    response = chain.invoke(
        {
            "question": question,
            "context": context,
        }
    )

    return response.content


if __name__ == "__main__":
    sample_context = """
    Scheme: Tamil Nadu Rural Roads Improvement Scheme (TNRRIS)
    Source: https://tnrd.tn.gov.in/schemes/road_scheme_new.html

    Roads connecting unconnected habitations, irrespective of
    population, are given first priority.
    """

    question = "Which roads receive first priority under TNRRIS?"

    print("Question:", question)
    print("\nAnswer:")
    print(generate_answer(question, sample_context))
