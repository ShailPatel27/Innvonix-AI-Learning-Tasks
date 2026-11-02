from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class ProjectState(TypedDict):
    request: str
    plan: list[str]
    result: str


def make_plan(state: ProjectState):
    return {"plan": ["Clarify the goal", "Complete the requested work", "Review the result"]}


def complete_work(state: ProjectState):
    return {"result": f"Completed: {state['request']}"}


def create_report(state: ProjectState):
    return {"result": f"{state['result']} | Steps: {', '.join(state['plan'])}"}


builder = StateGraph(ProjectState)
builder.add_node("plan", make_plan)
builder.add_node("work", complete_work)
builder.add_node("report", create_report)
builder.add_edge(START, "plan")
builder.add_edge("plan", "work")
builder.add_edge("work", "report")
builder.add_edge("report", END)
graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({"request": "Prepare a project summary", "plan": [], "result": ""})
    print(result["result"])
