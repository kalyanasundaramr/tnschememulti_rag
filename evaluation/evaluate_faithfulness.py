
import csv
import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import Faithfulness

from retrieval.rag_pipeline import ask_scheme_question

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "evaluation"
QUESTIONS_FILE = DATA_DIR / "evaluation_questions.json"

# Start small to control API usage. Increase after validating results.
MAX_QUESTIONS = 20

load_dotenv(ROOT_DIR / ".env")

DATA_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=DATA_DIR / "faithfulness_evaluation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is missing from your .env file.")

    questions = json.loads(
        QUESTIONS_FILE.read_text(encoding="utf-8")
    )[:MAX_QUESTIONS]

    records = []

    for index, item in enumerate(questions, start=1):
        question = item["question"]
        print(f"\n[{index}/{len(questions)}] {question}")

        try:
            
            result = ask_scheme_question(question)

            contexts = [result["context"]]
            records.append({
                "user_input": question,
                "response": result["answer"],
                "retrieved_contexts": contexts,
            })

            print("Answer:", result["answer"][:300])
            print("Retrieved context pieces:", len(contexts))

        except Exception as exc:
            logging.exception("Failed question: %s", question)
            print(f"ERROR: {exc}")

    if not records:
        raise RuntimeError(
            "No questions were evaluated. Check the log file for errors."
        )

    dataset = EvaluationDataset.from_list(records)

    judge_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

    evaluator_llm = LangchainLLMWrapper(judge_llm)

    print("\nRunning RAGAS faithfulness evaluation...")
    result = evaluate(
        dataset=dataset,
        metrics=[Faithfulness(llm=evaluator_llm)],
    )

    result_df = result.to_pandas()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path = DATA_DIR / f"faithfulness_results_{timestamp}.csv"
    json_path = DATA_DIR / f"faithfulness_results_{timestamp}.json"

    result_df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    report = {
        "timestamp": timestamp,
        "questions_attempted": len(questions),
        "questions_evaluated": len(records),
        "metric": "faithfulness",
        "results": result_df.to_dict(orient="records"),
    }

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    print("\n--- Faithfulness Evaluation Summary ---")
    print(f"Questions attempted: {len(questions)}")
    print(f"Questions evaluated: {len(records)}")
    if "faithfulness" in result_df.columns:
        print(
            "Average faithfulness:",
            round(float(result_df["faithfulness"].mean()), 4),
        )
    print(f"CSV report: {csv_path}")
    print(f"JSON report: {json_path}")


if __name__ == "__main__":
    main()
