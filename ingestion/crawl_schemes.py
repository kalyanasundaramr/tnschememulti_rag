
import json
import time
from pathlib import Path

import requests

BASE_URL = "https://tnagriculture.in/people_app/"
CATEGORY_URL = BASE_URL + "Scheme/getClass/{}"
RESULT_URL = BASE_URL + "Scheme/result/{}/{}"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "tn_agriculture_schemes.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TamilNaduAgricultureResearch/1.0)"
}

# Category IDs discovered from the official agriculture scheme page.
# Add additional IDs after verifying them from the official page.
CATEGORY_IDS = [
    1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13,
    14, 16, 17, 18, 19, 20, 21, 22, 23, 24
]


def fetch_json(session, url):
    """Fetch JSON data from an official agriculture API endpoint."""
    response = session.post(url, data="", timeout=30)
    response.raise_for_status()

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError(
            f"Expected JSON from {url}; received non-JSON content."
        ) from exc

    if not isinstance(data, list):
        raise ValueError(f"Unexpected response format from {url}")

    return data


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    schemes_by_id = {}
    errors = []
    classes_found = 0

    with requests.Session() as session:
        session.headers.update(HEADERS)

        for category_id in CATEGORY_IDS:
            try:
                classes = fetch_json(
                    session,
                    CATEGORY_URL.format(category_id),
                )
                print(
                    f"Category {category_id}: "
                    f"{len(classes)} classes found"
                )
            except (requests.RequestException, ValueError) as exc:
                errors.append({
                    "category_id": category_id,
                    "stage": "get_classes",
                    "error": str(exc),
                })
                print(f"[ERROR] Category {category_id}: {exc}")
                continue

            for item in classes:
                class_id = item.get("class_id")
                active = str(item.get("active_status_crop", "")).lower()

                if not class_id or active != "active":
                    continue

                classes_found += 1

                try:
                    records = fetch_json(
                        session,
                        RESULT_URL.format(category_id, class_id),
                    )

                    for record in records:
                        status = str(
                            record.get("active_status", "")
                        ).lower()

                        if status != "active":
                            continue

                        # Preserve the official fields, including Tamil.
                        record["source_url"] = (
                            BASE_URL + "Scheme/result/"
                            f"{category_id}/{class_id}"
                        )
                        record["category_id"] = str(category_id)
                        record["class_id"] = str(class_id)
                        record["class_name"] = item.get("class_Name", "")
                        record["class_name_tamil"] = item.get(
                            "class_name_Tamil", ""
                        )

                        # Keep a stable key to avoid duplicate records
                        # returned by multiple category/class combinations.
                        key = str(record.get("id") or (
                            record.get("input_type_id", ""),
                            record.get("input_class_id", ""),
                            record.get("scheme_id", ""),
                            record.get("component_id", ""),
                            record.get("Scheme_Name", ""),
                        ))

                        schemes_by_id[key] = record

                    print(
                        f"  Class {item.get('class_Name', class_id)}: "
                        f"{len(records)} records received"
                    )

                except (requests.RequestException, ValueError) as exc:
                    errors.append({
                        "category_id": category_id,
                        "class_id": str(class_id),
                        "stage": "get_schemes",
                        "error": str(exc),
                    })
                    print(f"  [ERROR] Class {class_id}: {exc}")

                time.sleep(0.3)

    schemes = list(schemes_by_id.values())

    if not schemes:
        raise RuntimeError(
            "No active agriculture schemes were collected. "
            "Check the API responses and error messages."
        )

    OUTPUT_FILE.write_text(
        json.dumps(schemes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    error_file = RAW_DIR / "tn_agriculture_crawl_errors.json"
    error_file.write_text(
        json.dumps(errors, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nAgriculture crawling complete.")
    print(f"Active classes checked: {classes_found}")
    print(f"Unique active scheme records: {len(schemes)}")
    print(f"Errors: {len(errors)}")
    print(f"Scheme data: {OUTPUT_FILE}")
    print(f"Error report: {error_file}")


if __name__ == "__main__":
    main()
