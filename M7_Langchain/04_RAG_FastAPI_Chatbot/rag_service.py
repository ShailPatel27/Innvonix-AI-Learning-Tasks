import hashlib
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VECTOR_DB_PATH = Path(__file__).resolve().parent / ".chroma_db"
load_dotenv(PROJECT_ROOT / ".env")


def require_google_api_key():
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError("Set GOOGLE_API_KEY in .env.")


@lru_cache
def get_embeddings():
    require_google_api_key()
    return GoogleGenerativeAIEmbeddings(model="gemini-embedding-2", dimensions=32)


@lru_cache
def get_chat_model():
    require_google_api_key()
    return ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.2)


@lru_cache
def get_vector_store():
    return Chroma(
        collection_name="langchain_rag_chatbot",
        embedding_function=get_embeddings(),
        persist_directory=str(VECTOR_DB_PATH),
    )


def add_documents(documents: list[Document], source: str) -> int:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = splitter.split_documents(documents)

    for chunk in chunks:
        chunk.metadata["source"] = source

    ids = [
        hashlib.sha256(
            f"{source}:{chunk.metadata.get('page', '')}:{chunk.page_content}".encode("utf-8")
        ).hexdigest()
        for chunk in chunks
    ]
    vector_store = get_vector_store()
    vector_store.delete(where={"source": source})
    vector_store.add_documents(chunks, ids=ids)
    return len(chunks)


def indexed_chunk_count() -> int:
    return len(get_vector_store().get()["ids"])


def indexed_documents() -> list[dict[str, int | str]]:
    records = get_vector_store().get(include=["metadatas"])
    counts: dict[str, int] = {}
    for metadata in records["metadatas"] or []:
        source = metadata.get("source", "Unknown file")
        counts[source] = counts.get(source, 0) + 1
    return [
        {"file": filename, "chunks": count}
        for filename, count in sorted(counts.items())
    ]


def _content_as_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") for block in content if isinstance(block, dict)
        )
    return str(content)


def _rewrite_question(question: str, history: list[dict[str, str]]) -> str:
    if not history:
        return question

    previous_messages = "\n".join(
        f"{message['role']}: {message['content']}" for message in history[-8:]
    )
    prompt = (
        "Rewrite the latest user question as a standalone question using the conversation "
        "when needed. Keep its meaning and return only the rewritten question.\n\n"
        f"Conversation:\n{previous_messages}\n\nLatest question: {question}"
    )
    return _content_as_text(get_chat_model().invoke(prompt).content).strip() or question


def answer_question(question: str, history: list[dict[str, str]]):
    standalone_question = _rewrite_question(question, history)
    documents = get_vector_store().similarity_search(standalone_question, k=4)
    if not documents:
        raise ValueError("No documents are indexed yet. Upload a PDF, TXT, or Markdown file first.")

    source_blocks = []
    sources = []
    seen_sources = set()
    for document in documents:
        source = document.metadata.get("source", "Unknown file")
        page = document.metadata.get("page")
        citation = f"{source}, page {page}" if page is not None else source
        source_blocks.append(f"[Source: {citation}]\n{document.page_content}")

        source_key = (source, page)
        if source_key not in seen_sources:
            sources.append(
                {
                    "file": source,
                    "page": page,
                    "excerpt": document.page_content[:240],
                }
            )
            seen_sources.add(source_key)

    messages = [
        SystemMessage(
            content=(
                "Answer the user's question using the supplied document excerpts. "
                "If the excerpts do not contain the answer, say so clearly. "
                "Cite supporting excerpts with their [Source: ...] label."
            )
        )
    ]
    for message in history[-8:]:
        if message["role"] == "user":
            messages.append(HumanMessage(content=message["content"]))
        else:
            messages.append(AIMessage(content=message["content"]))

    messages.append(
        HumanMessage(
            content=(
                f"Question: {question}\n\n"
                "Document excerpts:\n\n"
                + "\n\n".join(source_blocks)
            )
        )
    )
    answer = _content_as_text(get_chat_model().invoke(messages).content)
    return answer, sources
