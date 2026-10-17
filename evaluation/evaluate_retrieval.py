
import csv
import json
import logging
from datetime import datetime
from pathlib import Path

from retrieval.hybrid_retriever import search_hybrid

ROOT_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = ROOT_DIR / "data" / "evaluation" / "evaluation_questions.json"
OUTPUT_DIR = ROOT_DIR / "data" / "evaluation"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=OUTPUT_DIR / "retrieval_evaluation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def normalize_name(name):
    """Normalize scheme names for comparison."""
    return " ".join(name.casefold().split())


def evaluate_retrieval():
    questions = json.loads(
        QUESTIONS_FILE.read_text(encoding="utf-8")
    )

    results = []
    successful = 0
    failed = 0

    for index, item in enumerate(questions, start=1):
        question = item["question"]
        expected = {
            normalize_name(name)
            for name in item["expected_schemes"]
        }

        print(f"\n[{index}/{len(questions)}] {question}")

        try:
            retrieved = search_hybrid(question, limit=5)

            ranked_names = [
                result.get("scheme_name", "")
                for result in retrieved
            ]

            relevant_ranks = [
                rank
                for rank, name in enumerate(ranked_names, start=1)
                if normalize_name(name) in expected
            ]

            hit = bool(relevant_ranks)
            reciprocal_rank = (
                1.0 / min(relevant_ranks)
                if relevant_ranks
                else 0.0
            )

            results.append({
                "question": question,
                "expected_schemes": item["expected_schemes"],
                "retrieved_schemes": ranked_names,
                "hit_at_5": int(hit),
                "reciprocal_rank": reciprocal_rank,
                "status": "success",
            })

            successful += 1

            print("Retrieved:", ranked_names)
            print(f"Hit@5: {int(hit)}")
            print(f"Reciprocal rank: {reciprocal_rank:.3f}")

        except Exception as exc:
            failed += 1
            logging.exception("Evaluation failed for: %s", question)

            results.append({
                "question": question,
                "expected_schemes": item["expected_schemes"],
                "retrieved_schemes": [],
                "hit_at_5": 0,
                "reciprocal_rank": 0.0,
                "status": f"error: {exc}",
            })

            print(f"ERROR: {exc}")

    hit_rate = (
        sum(result["hit_at_5"] for result in results) / successful
        if successful else 0.0
    )

    mrr = (
        sum(result["reciprocal_rank"] for result in results) / successful
        if successful else 0.0
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report = {
        "timestamp": timestamp,
        "total_questions": len(questions),
        "successful_questions": successful,
        "failed_questions": failed,
        "hit_rate_at_5": round(hit_rate, 4),
        "mean_reciprocal_rank": round(mrr, 4),
        "results": results,
    }

    json_path = OUTPUT_DIR / f"retrieval_results_{timestamp}.json"
    csv_path = OUTPUT_DIR / f"retrieval_results_{timestamp}.csv"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with csv_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "question",
                "expected_schemes",
                "retrieved_schemes",
                "hit_at_5",
                "reciprocal_rank",
                "status",
            ],
        )
        writer.writeheader()

        for result in results:
            row = result.copy()
            row["expected_schemes"] = "; ".join(
                row["expected_schemes"]
            )
            row["retrieved_schemes"] = "; ".join(
                row["retrieved_schemes"]
            )
            writer.writerow(row)

    print("\n--- Retrieval Evaluation Summary ---")
    print(f"Total questions: {len(questions)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Hit-rate@5: {hit_rate:.2%}")
    print(f"MRR: {mrr:.4f}")
    print(f"JSON report: {json_path}")
    print(f"CSV report: {csv_path}")


if __name__ == "__main__":
    evaluate_retrieval()
