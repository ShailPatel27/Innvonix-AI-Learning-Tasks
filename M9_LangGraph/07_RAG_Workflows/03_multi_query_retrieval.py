import sys
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_chroma import Chroma
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import MODULE_DIR, get_chat_model, get_embeddings

VECTOR_DIR = MODULE_DIR / "data" / "rag_chroma"


def make_vector_store() -> Chroma:
    return Chroma(
        collection_name="langgraph_rag_lessons",
        embedding_function=get_embeddings(),
        persist_directory=str(VECTOR_DIR),
    )


class SearchQueries(BaseModel):
    queries: List[str] = Field(description="Three concise search queries with different wording")


def retrieve(question: str) -> list[Document]:
    query_model = get_chat_model().with_structured_output(SearchQueries)
    generated = query_model.invoke(
        f"Create three distinct search queries to find information for this question: {question}"
    )
    store = make_vector_store()
    found: dict[tuple[str, str], Document] = {}
    for query in [question, *generated.queries]:
        for document in store.similarity_search(query, k=3):
            key = (document.metadata.get("source", ""), document.page_content)
            found[key] = document
    return list(found.values())


if __name__ == "__main__":
    question = input("Question: ").strip()
    documents = retrieve(question)
    if not documents:
        print("No documents found. Run 02_ingest_and_retrieve.py first.")
    for document in documents:
        print(f"\n[{document.metadata.get('source', 'unknown')}]\n{document.page_content}")
