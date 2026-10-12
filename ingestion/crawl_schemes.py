
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://tnrd.tn.gov.in/"
LIST_URL = urljoin(BASE_URL, "schemes_states.html")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "tnrd_schemes.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TamilNaduSchemesResearch/1.0)"
}


def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()

    return soup.get_text(separator="\n", strip=True)


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with requests.Session() as session:
        session.headers.update(HEADERS)

        response = session.get(LIST_URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        schemes = []
        seen_urls = set()

        for link in soup.find_all("a", href=True):
            name = link.get_text(" ", strip=True)
            detail_url = urljoin(LIST_URL, link["href"])

            parsed = urlparse(detail_url)
            if parsed.netloc != urlparse(BASE_URL).netloc:
                continue

            if not name or detail_url in seen_urls:
                continue

            seen_urls.add(detail_url)

            # Keep only links within the discovered schemes directory.
            if "/schemes/" not in parsed.path:
                continue

            record = {
                "scheme_name": name,
                "source_url": detail_url,
                "content": "",
                "status": "pending",
            }

            try:
                detail_response = session.get(
                    detail_url,
                    timeout=30,
                )
                detail_response.raise_for_status()

                content = extract_text(detail_response.text)

                if content:
                    record["content"] = content
                    record["status"] = "success"
                else:
                    record["status"] = "empty_content"

                print(
                    f"[{record['status']}] {name}: "
                    f"{len(content)} characters"
                )

            except requests.RequestException as exc:
                record["status"] = "error"
                record["error"] = str(exc)
                print(f"[error] {name}: {exc}")

            schemes.append(record)
            time.sleep(0.5)

    OUTPUT_FILE.write_text(
        json.dumps(schemes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    successful = sum(item["status"] == "success" for item in schemes)

    print("\nCrawling complete.")
    print(f"Scheme pages discovered: {len(schemes)}")
    print(f"Pages with extracted text: {successful}")
    print(f"Saved results to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
