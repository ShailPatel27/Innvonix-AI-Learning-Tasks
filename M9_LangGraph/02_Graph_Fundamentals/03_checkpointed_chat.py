from typing import Annotated

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.graph.message import add_messages


class ChatState(MessagesState):
    messages: Annotated[list, add_messages]


def reply(state: ChatState):
    user_message = state["messages"][-1].content
    previous_turns = sum(isinstance(message, HumanMessage) for message in state["messages"])
    return {"messages": [AIMessage(content=f"This is turn {previous_turns}. You said: {user_message}")]}


builder = StateGraph(ChatState)
builder.add_node("reply", reply)
builder.add_edge(START, "reply")
builder.add_edge("reply", END)
chat = builder.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":
    config = {"configurable": {"thread_id": "learning-session-1"}}
    for text in ("Hello", "What did I say before?"):
        result = chat.invoke({"messages": [HumanMessage(content=text)]}, config)
        print(result["messages"][-1].content)
