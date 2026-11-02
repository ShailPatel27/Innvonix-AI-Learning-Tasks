from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class RequestState(TypedDict):
    request: str
    category: str
    response: str


def classify(state: RequestState):
    text = state["request"].lower()
    category = "billing" if any(word in text for word in ("invoice", "payment", "charge")) else "general"
    return {"category": category}


def route(state: RequestState) -> Literal["billing", "general"]:
    return state["category"]


def answer_billing(state: RequestState):
    return {"response": "I will route this to the billing team."}


def answer_general(state: RequestState):
    return {"response": "I will route this to the general support team."}


builder = StateGraph(RequestState)
builder.add_node("classify", classify)
builder.add_node("billing", answer_billing)
builder.add_node("general", answer_general)
builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", route, {"billing": "billing", "general": "general"})
builder.add_edge("billing", END)
builder.add_edge("general", END)
graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({"request": "I have a question about an invoice", "category": "", "response": ""})
    print(result["category"], "->", result["response"])
