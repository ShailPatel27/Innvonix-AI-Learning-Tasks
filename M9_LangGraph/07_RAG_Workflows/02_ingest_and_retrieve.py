import hashlib
import sys
from pathlib import Path

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import MODULE_DIR, get_embeddings

DOCS_DIR = Path(__file__).resolve().parent / "sample_docs"
VECTOR_DIR = MODULE_DIR / "data" / "rag_chroma"


def make_vector_store():
    return Chroma(
        collection_name="langgraph_rag_lessons",
        embedding_function=get_embeddings(),
        persist_directory=str(VECTOR_DIR),
    )


def ingest_documents(store: Chroma) -> int:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    chunks = []
    ids = []
    for path in DOCS_DIR.glob("*.md"):
        text = path.read_text(encoding="utf-8")
        pieces = splitter.create_documents([text], metadatas=[{"source": path.name}])
        for index, piece in enumerate(pieces):
            chunks.append(piece)
            ids.append(hashlib.sha1(f"{path.name}:{index}".encode()).hexdigest())
    if chunks:
        store.add_documents(chunks, ids=ids)
    return len(chunks)


if __name__ == "__main__":
    vector_store = make_vector_store()
    count = ingest_documents(vector_store)
    print(f"Indexed {count} document chunks.")
    while True:
        question = input("Search (or 'quit'): ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        for document in vector_store.similarity_search(question, k=3):
            print(f"\n[{document.metadata.get('source', 'unknown')}]\n{document.page_content}")
