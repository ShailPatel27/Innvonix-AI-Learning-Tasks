import sys
from pathlib import Path

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_chat_model


@tool
def estimate_reading_time(word_count: int) -> str:
    """Estimate reading time for a document, assuming 220 words per minute."""
    minutes = max(1, round(word_count / 220))
    return f"About {minutes} minute(s) to read."


@tool
def lookup_course(topic: str) -> str:
    """Find a suggested lesson for a topic in the learning curriculum."""
    lessons = {
        "langgraph": "Start with state, nodes, edges, and conditional routing.",
        "rag": "Start with document loading, chunking, embeddings, and retrieval.",
        "pydantic": "Start with BaseModel, Field constraints, and validators.",
    }
    return lessons.get(topic.lower(), "No matching lesson was found.")


tools = [estimate_reading_time, lookup_course]
model = get_chat_model().bind_tools(tools)


def call_model(state: MessagesState):
    return {"messages": [model.invoke(state["messages"])]}


builder = StateGraph(MessagesState)
builder.add_node("assistant", call_model)
builder.add_node("tools", ToolNode(tools))
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")
builder.set_entry_point("assistant")
chat = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "tool-chat-demo"}}
    while True:
        question = input("You: ").strip()
        if question.lower() in {"quit", "exit"}:
            break
        result = chat.invoke({"messages": [HumanMessage(content=question)]}, config)
        print("Assistant:", result["messages"][-1].content)
