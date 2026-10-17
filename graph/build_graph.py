
import json
import os
from pathlib import Path

import networkx as nx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


ROOT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "tn_agriculture_schemes_clean.json"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "processed"
    / "tn_agriculture_scheme_graph.json"
)

load_dotenv()


class GraphRelationship(BaseModel):
    source_entity: str = Field(
        description="Name of the source entity"
    )
    source_type: str = Field(
        description="scheme, department, beneficiary, benefit, crop, or component"
    )
    relationship: str = Field(
        description="Short relationship label supported by the source"
    )
    target_entity: str = Field(
        description="Name of the target entity"
    )
    target_type: str = Field(
        description="scheme, department, beneficiary, benefit, crop, or component"
    )
    evidence: str = Field(
        description="Brief supporting text copied or closely paraphrased from the scheme"
    )


class SchemeGraphExtraction(BaseModel):
    relationships: list[GraphRelationship] = Field(
        description="Relationships explicitly supported by the scheme content"
    )


def build_graph():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Agriculture scheme data not found: {INPUT_FILE}"
        )

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your .env file."
        )

    records = json.loads(
        INPUT_FILE.read_text(encoding="utf-8")
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    ).with_structured_output(SchemeGraphExtraction)

    graph = nx.MultiDiGraph()
    processed = 0
    failed = 0

    for index, record in enumerate(records, start=1):
        scheme_name = record.get("scheme_name", "").strip()
        content = record.get("content", "").strip()

        if not scheme_name or not content:
            continue

        department = record.get("department", "").strip()
        source_url = record.get("source_url", "").strip()

        # Add the scheme node from the source data.
        scheme_id = f"scheme::{scheme_name.casefold()}"

        graph.add_node(
            scheme_id,
            label=scheme_name,
            node_type="scheme",
            source_url=source_url,
        )

        # Add the department directly when the source identifies it.
        if department:
            department_id = f"department::{department.casefold()}"

            graph.add_node(
                department_id,
                label=department,
                node_type="department",
            )

            graph.add_edge(
                scheme_id,
                department_id,
                relationship="administered_by",
                evidence=f"Department: {department}",
                source_url=source_url,
            )

        prompt = f"""
Extract factual entities and relationships from this Tamil Nadu
agriculture scheme record.

Return only relationships supported by the provided text.
Do not invent eligibility rules, beneficiaries, benefits, or amounts.
Preserve entity names and details in the language used in the source.
If the record does not support a relationship, return an empty list.

Scheme name: {scheme_name}
Department: {department}
Source URL: {source_url}

Scheme content:
{content[:12000]}
"""

        try:
            extraction = llm.invoke(prompt)

            for item in extraction.relationships:
                source_name = item.source_entity.strip()
                target_name = item.target_entity.strip()
                relationship = item.relationship.strip()

                if not source_name or not target_name or not relationship:
                    continue

                source_id = (
                    f"{item.source_type.strip().casefold()}::"
                    f"{source_name.casefold()}"
                )
                target_id = (
                    f"{item.target_type.strip().casefold()}::"
                    f"{target_name.casefold()}"
                )

                graph.add_node(
                    source_id,
                    label=source_name,
                    node_type=item.source_type.strip().casefold(),
                )
                graph.add_node(
                    target_id,
                    label=target_name,
                    node_type=item.target_type.strip().casefold(),
                )

                graph.add_edge(
                    source_id,
                    target_id,
                    relationship=relationship,
                    evidence=item.evidence.strip(),
                    source_url=source_url,
                    scheme=scheme_name,
                )

            processed += 1
            print(
                f"[{index}/{len(records)}] Processed: {scheme_name}"
            )

        except Exception as exc:
            failed += 1
            print(
                f"[{index}/{len(records)}] Failed: "
                f"{scheme_name} — {exc}"
            )

    nodes = [
        {"id": node_id, **attributes}
        for node_id, attributes in graph.nodes(data=True)
    ]

    edges = [
        {"source": source, "target": target, **attributes}
        for source, target, attributes in graph.edges(data=True)
    ]

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(
        json.dumps(
            {"nodes": nodes, "edges": edges},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nAgriculture Knowledge Graph build complete.")
    print(f"Input scheme records: {len(records)}")
    print(f"Records processed: {processed}")
    print(f"Records failed: {failed}")
    print(f"Graph nodes: {graph.number_of_nodes()}")
    print(f"Graph edges: {graph.number_of_edges()}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    build_graph()
