import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import TypedDict

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_chat_model, text_content

retrieval_path = Path(__file__).with_name("03_multi_query_retrieval.py")
spec = spec_from_file_location("multi_query_retrieval", retrieval_path)
retrieval_module = module_from_spec(spec)
spec.loader.exec_module(retrieval_module)
retrieve_documents = retrieval_module.retrieve


class AnswerReview(BaseModel):
    supported: bool = Field(description="Whether the draft is supported by the context")
    feedback: str = Field(description="What evidence is missing, or why the answer is supported")


class RAGState(TypedDict):
    question: str
    documents: list[Document]
    context: str
    answer: str
    supported: bool
    feedback: str
    attempts: int


def retrieve(state: RAGState):
    documents = retrieve_documents(state["question"])
    context = "\n\n".join(
        f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in documents
    )
    return {"documents": documents, "context": context, "attempts": 0}


def draft(state: RAGState):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer using only the supplied evidence. Cite source filenames. If evidence is missing, say so."),
            ("human", "Question: {question}\n\nEvidence:\n{context}\n\nReviewer feedback: {feedback}"),
        ]
    )
    result = (prompt | get_chat_model()).invoke(state)
    return {"answer": text_content(result.content), "attempts": state["attempts"] + 1}


def review(state: RAGState):
    reviewer = get_chat_model().with_structured_output(AnswerReview)
    result = reviewer.invoke(
        f"Check whether every factual claim in this answer is supported by the evidence. "
        f"Set supported=true only when the answer is grounded.\n\nEvidence:\n{state['context']}"
        f"\n\nAnswer:\n{state['answer']}"
    )
    return {"supported": result.supported, "feedback": result.feedback}


def route_after_review(state: RAGState):
    if state["supported"] or state["attempts"] >= 2:
        return "finish"
    return "draft"


builder = StateGraph(RAGState)
builder.add_node("retrieve", retrieve)
builder.add_node("draft", draft)
builder.add_node("review", review)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "draft")
builder.add_edge("draft", "review")
builder.add_conditional_edges("review", route_after_review, {"draft": "draft", "finish": END})
rag = builder.compile()


if __name__ == "__main__":
    question = input("Question: ").strip()
    result = rag.invoke(
        {
            "question": question,
            "documents": [],
            "context": "",
            "answer": "",
            "supported": False,
            "feedback": "",
            "attempts": 0,
        }
    )
    print(result["answer"])
    if not result["supported"]:
        print(f"\nReview note: {result['feedback']}")
