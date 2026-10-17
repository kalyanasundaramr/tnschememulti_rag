
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT / "data" / "raw" / "tn_agriculture_schemes.json"
)
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "tn_agriculture_schemes_clean.json"
)


def clean_text(value):
    """Normalize text while preserving Tamil characters."""

    if value is None:
        return ""

    text = str(value)

    replacements = {
        "â€™": "’",
        "â€˜": "‘",
        "â€œ": "“",
        "â€": "”",
        "Â ": " ",
        "Â": "",
        "\xa0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Raw data not found: {INPUT_FILE}")

    schemes = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    cleaned_schemes = []

    for scheme in schemes:
        # Combine important fields into searchable document content.
        content_fields = [
            ("Scheme", scheme.get("Scheme_Name", "")),
            ("Scheme name in Tamil", scheme.get("Scheme_Name_Tamil", "")),
            ("Department", scheme.get("dept", "")),
            ("Department in Tamil", scheme.get("dept_tamil", "")),
            ("Category", scheme.get("class_name", "")),
            ("Category in Tamil", scheme.get("class_name_tamil", "")),
            ("Component", scheme.get("component", "")),
            ("Component in Tamil", scheme.get("component_tamil", "")),
            ("Subsidy details", scheme.get("pattern_of_subsidy", "")),
            ("Subsidy details in Tamil",
             scheme.get("pattern_of_subsidy_tamil", "")),
            ("Eligibility", scheme.get("eligible", "")),
            ("Eligibility in Tamil", scheme.get("eligible_tamil", "")),
            ("Subsidy type", scheme.get("subsidy_type", "")),
            ("Required documents", scheme.get("doc_req", "")),
            ("Required documents in Tamil", scheme.get("doc_req_tamil", "")),
            ("Description", scheme.get("scheme_descri", "")),
            ("Description in Tamil", scheme.get("scheme_descri_tamil", "")),
            ("Scheme book", scheme.get("scheme_book", "")),
            ("Scheme book in Tamil", scheme.get("scheme_book_tamil", "")),
        ]

        content = "\n".join(
            f"{label}: {clean_text(value)}"
            for label, value in content_fields
            if clean_text(value)
        )

       
        department = clean_text(scheme.get("dept", ""))
        department_tamil = clean_text(scheme.get("dept_tamil", ""))

        # Correct abbreviated department values.
        if department.casefold() == "h":
            department = "Horticulture Department"

        if department_tamil.casefold() == "h":
            department_tamil = "தோட்டக்கலைத் துறை"

        cleaned_schemes.append({
            "scheme_name": clean_text(scheme.get("Scheme_Name", "")),
            "scheme_name_tamil": clean_text(
                scheme.get("Scheme_Name_Tamil", "")
            ),
            "department": department,
            "department_tamil": department_tamil,
            "category": clean_text(scheme.get("class_name", "")),
            "category_tamil": clean_text(
                scheme.get("class_name_tamil", "")
            ),
            "source_url": clean_text(scheme.get("source_url", "")),
            "status": clean_text(scheme.get("active_status", "")),
            "content": content,
        })


    # Validate records before writing the output.
    missing_names = [
        item for item in cleaned_schemes
        if not item["scheme_name"]
    ]
    empty_content = [
        item for item in cleaned_schemes
        if not item["content"]
    ]

    if missing_names or empty_content:
        raise ValueError(
            f"Validation failed: {len(missing_names)} missing names, "
            f"{len(empty_content)} empty content records."
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(cleaned_schemes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Input records: {len(schemes)}")
    print(f"Cleaned records: {len(cleaned_schemes)}")
    print(
        "Processed characters:",
        sum(len(item["content"]) for item in cleaned_schemes),
    )
    print("Missing scheme names:", len(missing_names))
    print("Empty content records:", len(empty_content))
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
