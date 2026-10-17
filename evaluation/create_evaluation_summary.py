
import json
import math
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
EVALUATION_DIR = ROOT_DIR / "data" / "evaluation"


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    retrieval_file = (
        EVALUATION_DIR
        / "retrieval_results_20261017_201450.json"
    )
    faithfulness_file = (
        EVALUATION_DIR
        / "faithfulness_results_20261017_203619.json"
    )

    if not retrieval_file.exists():
        raise FileNotFoundError(
            f"Retrieval report not found: {retrieval_file}"
        )

    if not faithfulness_file.exists():
        raise FileNotFoundError(
            f"Faithfulness report not found: {faithfulness_file}"
        )

    retrieval = load_json(retrieval_file)
    faithfulness = load_json(faithfulness_file)

    # Calculate average from valid individual RAGAS scores.
    scores = [
        float(item["faithfulness"])
        for item in faithfulness.get("results", [])
        if isinstance(item.get("faithfulness"), (int, float))
        and math.isfinite(float(item["faithfulness"]))
    ]

    average_faithfulness = (
        round(sum(scores) / len(scores), 4)
        if scores
        else None
    )

    summary = {
        "generated_at": datetime.now().astimezone().isoformat(
            timespec="seconds"
        ),
        "project": "Tamil Nadu Agriculture RAG Assistant",
        "retrieval_evaluation": {
            "total_questions": retrieval["total_questions"],
            "successful_questions": retrieval["successful_questions"],
            "failed_questions": retrieval["failed_questions"],
            "hit_rate_at_5": retrieval["hit_rate_at_5"],
            "mean_reciprocal_rank": retrieval[
                "mean_reciprocal_rank"
            ],
        },
        "faithfulness_evaluation": {
            "questions_attempted": faithfulness[
                "questions_attempted"
            ],
            "questions_evaluated": faithfulness[
                "questions_evaluated"
            ],
            "average_faithfulness": average_faithfulness,
            "valid_scores_used": len(scores),
        },
        "source_reports": {
            "retrieval": retrieval_file.name,
            "faithfulness": faithfulness_file.name,
        },
        "interpretation": {
            "hit_rate_at_5": (
                "Expected scheme appeared in the top five results "
                "for 75% of test questions."
            ),
            "mrr": (
                "Mean reciprocal rank measures how highly the "
                "expected scheme was ranked."
            ),
            "faithfulness": (
                "RAGAS faithfulness measures how well generated "
                "answers are supported by the supplied context."
            ),
        },
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = (
        EVALUATION_DIR
        / f"combined_evaluation_summary_{timestamp}.json"
    )

    output_file.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n--- Combined Evaluation Summary ---")
    print(f"Project: {summary['project']}")

    print(
        "Retrieval questions: "
        f"{retrieval['successful_questions']}/"
        f"{retrieval['total_questions']}"
    )

    print(
        f"Hit-rate@5: {retrieval['hit_rate_at_5']:.2%}"
    )

    print(
        "Mean Reciprocal Rank (MRR): "
        f"{retrieval['mean_reciprocal_rank']:.4f}"
    )

    print(
        "Faithfulness questions: "
        f"{faithfulness['questions_evaluated']}/"
        f"{faithfulness['questions_attempted']}"
    )

    if average_faithfulness is not None:
        print(
            "Average faithfulness: "
            f"{average_faithfulness:.2%}"
        )
    else:
        print("Average faithfulness: No valid scores available.")

    print(f"Valid faithfulness scores used: {len(scores)}")
    print(f"\nReport saved to:\n{output_file}")


if __name__ == "__main__":
    main()
