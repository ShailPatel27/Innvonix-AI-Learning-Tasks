import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv

MODULE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(MODULE_DIR / ".env")
DOCS_DIR = MODULE_DIR / "07_RAG_Workflows" / "sample_docs"
COLLECTION = "langgraph_learning_docs"


def config() -> tuple[str, str]:
    host = os.getenv("TYPESENSE_HOST", "http://localhost:8108").rstrip("/")
    api_key = os.getenv("TYPESENSE_API_KEY")
    if not api_key:
        raise RuntimeError("Set TYPESENSE_API_KEY in M9_LangGraph/.env.")
    return host, api_key


def request(method: str, path: str, **kwargs):
    host, api_key = config()
    response = requests.request(
        method,
        f"{host}{path}",
        headers={"X-TYPESENSE-API-KEY": api_key},
        timeout=15,
        **kwargs,
    )
    response.raise_for_status()
    return response


def ensure_collection() -> None:
    response = requests.post(
        f"{config()[0]}/collections",
        headers={"X-TYPESENSE-API-KEY": config()[1]},
        json={
            "name": COLLECTION,
            "fields": [
                {"name": "source", "type": "string"},
                {"name": "content", "type": "string"},
            ],
        },
        timeout=15,
    )
    if response.status_code == 409:
        return
    response.raise_for_status()


def index_documents() -> int:
    ensure_collection()
    documents = [
        {"id": path.stem, "source": path.name, "content": path.read_text(encoding="utf-8")}
        for path in DOCS_DIR.glob("*.md")
    ]
    if not documents:
        return 0
    request(
        "POST",
        f"/collections/{COLLECTION}/documents/import",
        params={"action": "upsert"},
        data="\n".join(json.dumps(document) for document in documents),
        headers={"Content-Type": "text/plain"},
    )
    return len(documents)


def search(query: str) -> list[dict]:
    response = request(
        "GET",
        f"/collections/{COLLECTION}/documents/search",
        params={"q": query, "query_by": "content", "per_page": 5},
    )
    return response.json().get("hits", [])


if __name__ == "__main__":
    indexed = index_documents()
    print(f"Indexed or updated {indexed} sample documents in Typesense.")
    while True:
        query = input("Search (or 'quit'): ").strip()
        if query.lower() in {"quit", "exit"}:
            break
        for hit in search(query):
            document = hit["document"]
            print(f"\n[{document['source']}] score={hit.get('text_match', 'n/a')}\n{document['content']}")
