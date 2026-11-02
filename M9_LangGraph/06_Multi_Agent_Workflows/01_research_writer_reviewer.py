import sys
from pathlib import Path
from typing import Literal, TypedDict

from pydantic import BaseModel
from langgraph.graph import END, START, StateGraph

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_chat_model


class Review(BaseModel):
    approved: bool
    feedback: str


class TeamState(TypedDict):
    question: str
    research: str
    draft: str
    feedback: str
    approved: bool
    revisions: int


model = get_chat_model()


def researcher(state: TeamState):
    response = model.invoke(
        "Act as a researcher. Give concise, factual notes for this question. "
        "If facts are uncertain, say so.\n\n" + state["question"]
    )
    return {"research": response.content}


def writer(state: TeamState):
    prompt = (
        "Act as a clear technical writer. Answer the user's question using the research notes. "
        "Avoid unsupported claims.\n\nQuestion: " + state["question"]
        + "\n\nResearch notes:\n" + state["research"]
    )
    if state["feedback"]:
        prompt += "\n\nReviewer feedback to address:\n" + state["feedback"]
    response = model.invoke(prompt)
    return {"draft": response.content, "revisions": state["revisions"] + 1}


def reviewer(state: TeamState):
    review_model = model.with_structured_output(Review)
    review = review_model.invoke(
        "Check whether the draft answers the question, follows the research notes, and avoids unsupported claims. "
        "Approve only if it is adequate.\n\nQuestion: " + state["question"]
        + "\n\nResearch:\n" + state["research"]
        + "\n\nDraft:\n" + state["draft"]
    )
    return {"approved": review.approved, "feedback": review.feedback}


def next_step(state: TeamState) -> Literal["writer", "finish"]:
    if state["approved"] or state["revisions"] >= 2:
        return "finish"
    return "writer"


builder = StateGraph(TeamState)
builder.add_node("researcher", researcher)
builder.add_node("writer", writer)
builder.add_node("reviewer", reviewer)
builder.add_edge(START, "researcher")
builder.add_edge("researcher", "writer")
builder.add_edge("writer", "reviewer")
builder.add_conditional_edges("reviewer", next_step, {"writer": "writer", "finish": END})
team = builder.compile()


if __name__ == "__main__":
    question = input("Question for the team: ")
    result = team.invoke(
        {
            "question": question,
            "research": "",
            "draft": "",
            "feedback": "",
            "approved": False,
            "revisions": 0,
        }
    )
    print(result["draft"])
    print(f"Reviewer approved: {result['approved']}")
