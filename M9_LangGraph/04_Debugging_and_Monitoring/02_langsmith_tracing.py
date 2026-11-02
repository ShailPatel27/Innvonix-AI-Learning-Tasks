import os
import sys
from pathlib import Path
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_chat_model

if os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_TRACING"] = "true"


class AnswerState(TypedDict):
    question: str
    answer: str


def answer(state: AnswerState):
    result = get_chat_model().invoke(state["question"])
    return {"answer": result.content}


builder = StateGraph(AnswerState)
builder.add_node("answer", answer)
builder.add_edge(START, "answer")
builder.add_edge("answer", END)
app = builder.compile()


if __name__ == "__main__":
    if not os.getenv("LANGSMITH_API_KEY"):
        print("Set LANGSMITH_API_KEY in M9_LangGraph/.env to view traces.")
    question = input("Question: ")
    result = app.invoke({"question": question, "answer": ""})
    print(result["answer"])
