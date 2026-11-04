import base64
import mimetypes
import sys
from pathlib import Path
from typing import TypedDict

from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, START, StateGraph
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import MODULE_DIR, get_chat_model, get_embeddings, text_content

HERE = Path(__file__).resolve().parent
PDF_DIR = HERE / "pdfs"
IMAGE_DIR = HERE / "images"
VECTOR_DIR = MODULE_DIR / "data" / "multimodal_chroma"
IMAGE_TYPES = {".png", ".jpg", ".jpeg"}


def make_store() -> Chroma:
    return Chroma(
        collection_name="langgraph_multimodal_lessons",
        embedding_function=get_embeddings(),
        persist_directory=str(VECTOR_DIR),
    )


def describe_image(path: Path) -> str:
    image_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    response = get_chat_model().invoke(
        [
            HumanMessage(
                content=[
                    {"type": "text", "text": "Describe the useful visual information in this image for later document search."},
                    {"type": "image_url", "image_url": {"url": f"data:{image_type};base64,{encoded}"}},
                ]
            )
        ]
    )
    return text_content(response.content)


def ingest() -> int:
    splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
    documents = []
    for path in PDF_DIR.glob("*.pdf"):
        for page_number, page in enumerate(PdfReader(path).pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                documents.extend(
                    splitter.create_documents(
                        [text],
                        metadatas=[{"source": path.name, "page": page_number, "kind": "pdf"}],
                    )
                )
    for path in IMAGE_DIR.iterdir():
        if path.is_file() and path.suffix.lower() in IMAGE_TYPES:
            documents.extend(
                splitter.create_documents(
                    [describe_image(path)],
                    metadatas=[{"source": path.name, "kind": "image"}],
                )
            )
    if documents:
        make_store().add_documents(documents)
    return len(documents)


class QueryState(TypedDict):
    question: str
    context: str
    answer: str


def retrieve(state: QueryState):
    store = make_store()
    matches = store.similarity_search(state["question"], k=4)
    context = "\n\n".join(
        f"Source: {doc.metadata.get('source')} ({doc.metadata.get('kind')}, page {doc.metadata.get('page', 'n/a')})\n{doc.page_content}"
        for doc in matches
    )
    return {"context": context}


def answer(state: QueryState):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer from the retrieved context only and cite its source. Say when the context is insufficient."),
            ("human", "Question: {question}\n\nContext:\n{context}"),
        ]
    )
    result = (prompt | get_chat_model()).invoke(state)
    return {"answer": text_content(result.content)}


builder = StateGraph(QueryState)
builder.add_node("retrieve", retrieve)
builder.add_node("answer", answer)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "answer")
builder.add_edge("answer", END)
rag = builder.compile()


if __name__ == "__main__":
    count = ingest()
    print(f"Indexed {count} chunks. Add PDFs to pdfs/ and images to images/ before ingesting.")
    while True:
        question = input("Question (or 'quit'): ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        result = rag.invoke({"question": question, "context": "", "answer": ""})
        print(result["answer"])
