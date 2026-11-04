import sys
from pathlib import Path
from typing import TypedDict

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_chat_model, text_content


class SummaryState(TypedDict):
    text: str
    summary: str
    keywords: list[str]


model = get_chat_model()


def summarize(state: SummaryState):
    response = model.invoke(f"Summarize this in two sentences:\n\n{state['text']}")
    return {"summary": text_content(response.content)}


def extract_keywords(state: SummaryState):
    response = model.invoke(f"Return five keywords separated by commas:\n\n{state['summary']}")
    keywords = [word.strip() for word in text_content(response.content).split(",") if word.strip()]
    return {"keywords": keywords}


builder = StateGraph(SummaryState)
builder.add_node("summarize", summarize)
builder.add_node("keywords", extract_keywords)
builder.add_edge(START, "summarize")
builder.add_edge("summarize", "keywords")
builder.add_edge("keywords", END)
app = builder.compile()


if __name__ == "__main__":
    text = "LangGraph represents applications as graphs. Nodes run functions, edges connect steps, and state carries data between them."
    for update in app.stream(
        {"text": text, "summary": "", "keywords": []},
        stream_mode="updates",
    ):
        for node, values in update.items():
            for key, value in values.items():
                if isinstance(value, list):
                    value = ", ".join(str(item) for item in value)
                print(f"[{node}] {value}")
