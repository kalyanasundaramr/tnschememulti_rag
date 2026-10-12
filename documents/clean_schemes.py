
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "tnrd_schemes.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "tnrd_schemes_clean.json"


def clean_text(text):
    # Fix common UTF-8/Windows-1252 display artifacts.
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
        cleaned = {
            "scheme_name": clean_text(scheme.get("scheme_name", "")),
            "source_url": scheme.get("source_url", ""),
            "content": clean_text(scheme.get("content", "")),
            "status": scheme.get("status", ""),
        }

        if scheme.get("error"):
            cleaned["error"] = scheme["error"]

        cleaned_schemes.append(cleaned)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(cleaned_schemes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Input records: {len(schemes)}")
    print(f"Output records: {len(cleaned_schemes)}")
    print(
        "Processed characters:",
        sum(len(s["content"]) for s in cleaned_schemes),
    )
    print(f"Saved cleaned data to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
