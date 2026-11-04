import sys
from pathlib import Path
from typing import TypedDict

from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_chat_model, text_content

DOCS_DIR = Path(__file__).resolve().parent / "sample_docs"


class RAGState(TypedDict):
    question: str
    context: str
    answer: str


def retrieve(state: RAGState):
    passages = []
    for path in DOCS_DIR.glob("*.md"):
        passages.append(f"Source: {path.name}\n{path.read_text(encoding='utf-8')}")
    return {"context": "\n\n".join(passages)}


def generate(state: RAGState):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer only from the context. If it is insufficient, say so. Cite the source filename."),
            ("human", "Question: {question}\n\nContext:\n{context}"),
        ]
    )
    response = (prompt | get_chat_model()).invoke(state)
    return {"answer": text_content(response.content)}


builder = StateGraph(RAGState)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)
rag = builder.compile()


if __name__ == "__main__":
    question = input("Question: ")
    result = rag.invoke({"question": question, "context": "", "answer": ""})
    print(result["answer"])
